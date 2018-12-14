from django.db import models
from contextlib import suppress
from register.constants import MessageStates
from register.models import PhoneNumber

# Create your models here.


class SecretSantaGroup(models.Model):
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Group Active: {self.active}"


def ALSO_CLEAR_YOUR_SECRET(collector, field, sub_objs, using):
    collector.add_field_update(field, None, sub_objs)
    with suppress(Exception):
        for owner in sub_objs:
            owner.your_secret = None
            owner.save()


class Messages(models.Model):
    sender = models.ForeignKey("Owner", on_delete=models.CASCADE, db_constraint=False)
    sent = models.BooleanField(default=False)
    message = models.TextField()


class Owner(models.Model):

    STATES = [(state.value, state) for state in MessageStates]

    owner_name = models.CharField(max_length=140, null=True, blank=True)
    foundation_message = models.CharField(max_length=240, null=True, blank=True)
    number = models.OneToOneField(
        PhoneNumber, on_delete=models.CASCADE, related_name="owner"
    )
    state = models.CharField(
        max_length=20, choices=STATES, default=MessageStates.INITIAL.value
    )

    # Matching stuff
    excluded_from_matching_with = models.ManyToManyField(
        "Owner", symmetrical=True, blank=True
    )
    secret_santa_group = models.ForeignKey(
        SecretSantaGroup,
        on_delete=ALSO_CLEAR_YOUR_SECRET,
        null=True,
        blank=True,
        db_constraint=False,
    )

    your_secret = models.ForeignKey(
        "Owner", on_delete=models.SET_NULL, null=True, db_constraint=False, blank=True
    )

    # Admin Display "Function"
    excluded_gift_recipiants = property(
        lambda self: ", ".join(
            [o.owner_name for o in self.excluded_from_matching_with.all()]
        )
    )

    def __str__(self):
        return self.owner_name or "-"
