from django.core.management.base import BaseCommand, CommandError
from register.models import PhoneNumber
from matching.models import Owner


class Command(BaseCommand):
    help = "Creates a dumby owner w/ phone number"

    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument(
            "--number", dest="number", help="Number to give the new owner"
        )

    def handle(self, *args, name, number, **options):
        p = PhoneNumber.objects.create(parsed_number=number)
        Owner.objects.create(owner_name=name, number=p)
        print("Done")
