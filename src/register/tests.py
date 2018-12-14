from django.test import TestCase

from register.models import PhoneNumber
from matching.models import Owner
from register.service import MessageLifecycle

# Create your tests here.


class TestMessaging(TestCase):
    def setUp(self):
        self.number = PhoneNumber.objects.create(parsed_number="5555555555")
        self.owner = Owner.objects.create(number=self.number)

    def test_messaging(self):
        chat = MessageLifecycle.load_from_number(self.number.parsed_number)
        print(chat.get_response())
        chat.recieved_message()
