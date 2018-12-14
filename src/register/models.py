from django.db import models


# Create your models here.
class PhoneNumber(models.Model):
    parsed_number = models.CharField(max_length=12, primary_key=True, unique=True)
    raw_number = models.CharField(max_length=12)


class VerificationAttempt(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=64)
    twilio_sid = models.CharField(max_length=64)
    number = models.ForeignKey(
        PhoneNumber, on_delete=models.DO_NOTHING, related_name="verification_attempts"
    )
