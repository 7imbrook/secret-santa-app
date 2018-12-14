import hashlib
import random
from contextlib import suppress
from collections import defaultdict
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from twilio.rest import Client
from twilio.twiml.messaging_response import Message, MessagingResponse

from matching.models import Owner, Messages
from register.constants import MessageStates
from register.models import VerificationAttempt, PhoneNumber


def spread_event_kwargs(f):
    def _inner(self, event, *args, **kwargs):
        kwargs.update(event.kwargs)
        return f(self, event, *args, **kwargs)

    return _inner


class ClaimNumberService:
    def __init__(self, phonenumber):
        self.phonenumber = phonenumber
        self.hash_code = 0

    @classmethod
    def create(cls, model):
        return cls(model)

    @staticmethod
    def hash(val):
        return hashlib.sha256(str(val).encode("utf-8")).hexdigest()

    @classmethod
    def verifiy(cls, verification, entered_code):
        if cls.hash(entered_code) == verification.hash:
            owner = Owner.objects.create(number=verification.number)
            return True
        else:
            return False

    @property
    def client(self):
        return Client(settings.TWILIO_KEYS.sid, settings.TWILIO_KEYS.token)

    def send_verification(self):
        try:
            self.phonenumber.owner
        except ObjectDoesNotExist:
            # Cool, we still need to set an owner
            code = random.randint(100_000, 999_999)
            self.hash_code = self.hash(code)
            message = self.client.messages.create(
                to=self.phonenumber.parsed_number,
                from_=settings.TWILIO_KEYS.number,
                body=f"This is your secret santa agent. What was that code we gave you?",
            )
            VerificationAttempt.objects.create(
                number=self.phonenumber, twilio_sid=message.sid, hash=self.hash_code
            )
            return code


class MessageLifecycle:

    PROMPTS = defaultdict(lambda: "Something went wrong, text Michael 🤯")

    def __init__(self, owner):
        self.owner = owner
        self.PROMPTS.update(
            {
                MessageStates.INITIAL: ["Tell me what your name is."],
                MessageStates.NAME: [
                    "What foundation would you like to have donated to? Just give enough context that someone could figure it out."
                ],
                MessageStates.FOUNDATION: [
                    "Thanks!",
                    "Anything you reply here will be fowarded to your secret santa.",
                    "I'll hold onto the messages you send before you get paired and send them off as well."
                ],
                MessageStates.FORWARDING: ["✉️", "Sent!"],
            }
        )

        self.recievers = {
            MessageStates.INITIAL: self.set_name,
            MessageStates.NAME: self.set_foundation,
            MessageStates.FOUNDATION: self.fowarding_messages,
            MessageStates.FORWARDING: self.fowarding_messages,
        }

    @classmethod
    def load_from_number(cls, number):
        number = PhoneNumber.objects.get(parsed_number=number)
        try:
            return cls(number.owner)
        except ObjectDoesNotExist:
            return None

    @property
    def state(self):
        return MessageStates(self.owner.state)

    def set_name(self, name):
        self.owner.owner_name = name
        self.owner.state = MessageStates.NAME.value
        self.owner.save()

    def set_foundation(self, foundation):
        self.owner.foundation_message = foundation
        self.owner.state = MessageStates.FOUNDATION.value
        self.owner.save()

    def fowarding_messages(self, message):
        forward = MessageForwarder(self.owner)
        forward.send_message(message)

    def recieved_message(self, message):
        self.recievers[self.state](message)

    def get_prompt(self):
        messages = self.PROMPTS[self.state]
        response = MessagingResponse()
        list(map(response.message, messages))
        if self.state is MessageStates.FOUNDATION:
            self.owner.state = MessageStates.FORWARDING.value
            self.owner.save()
        return response


class MessageForwarder:
    def __init__(self, owner):
        self.owner = owner

    @property
    def active(self):
        with suppress(ObjectDoesNotExist):
            if self.owner.secret_santa_group is not None:
                return self.owner.secret_santa_group.active
            else:
                return False

    @property
    def send_to(self):
        return self.owner.your_secret.number.parsed_number

    @property
    def client(self):
        return Client(settings.TWILIO_KEYS.sid, settings.TWILIO_KEYS.token)

    def send_message(self, message):
        m = Messages.objects.create(sender=self.owner, message=message)
        self.send_message_attemp(m)

    def send_all_unsent_messages(self):
        if self.active:
            for message_not_sent in Messages.objects.filter(
                sender=self.owner, sent=False
            ):
                self._send_message(message_not_sent)

    def send_message_attemp(self, m):
        if self.active:
            self._send_message(m)

    def trigger_secret_santa_message(self):
        recipiant = self.owner.your_secret.owner_name
        foundation = self.owner_name.your_secret.foundation_message
        you = self.owner.owner_name
        self.client.messages.create(
            to=self.owner.number.parsed_number,
            from_=settings.TWILIO_KEYS.number,
            body=f"It's time for secret santa {you}!! 🎅🏽🤫 You got {recipiant}! They wanted you to donate to '{foundation}'."
        )

    def _send_message(self, m):
        self.client.messages.create(
            to=self.send_to, from_=settings.TWILIO_KEYS.number, body=m.message
        )
        m.sent = True
        m.save()
