from django.db import migrations
from django.core.exceptions import ObjectDoesNotExist

def clear_your_secret(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Owner = apps.get_model('matching', 'Owner')

    # we had deployed a version where the ALSO_CLEAR_YOUR_SECRET deletion wasn't set.
    # This checks to make sure you're not in a group and clears it.
    print("<>")
    for owner in Owner.objects.all():
        try:
            owner.secret_santa_group
        except ObjectDoesNotExist:
            owner.secret_santa_group = None
            owner.your_secret = None 
            owner.save()
            print("Migrated", owner.owner_name)

class Migration(migrations.Migration):

    dependencies = [
        ('matching', '0009_auto_20181214_0642'),
    ]

    operations = [
        migrations.RunPython(clear_your_secret),
    ]