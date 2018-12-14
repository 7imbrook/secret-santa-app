from django.contrib import admin, messages
from matching.models import SecretSantaGroup, Owner
from matching.exceptions import MatchBaseException
from matching.service import MatchingService
from register.service import MessageForwarder
from register.constants import MessageStates
from django.conf import settings

# Register your models here.


class MatchingAdmin(admin.ModelAdmin):
    list_display = list(filter(None, [
        "owner_name",
        "excluded_gift_recipiants",
        "state",
        "secret_santa_group",
        None if settings.PROD else "your_secret",
    ]))
    ordering = ["owner_name"]
    actions = [
        "exclude_from_matching_each_other",
        "match_users_into_secret_santa_group",
        "remove_all_exclutions",
    ]

    def exclude_from_matching_each_other(self, request, queryset):
        "Makes a connection between the selected users to not match with each other"
        MatchingService.exclude(queryset)
        self.message_user(request, "Success")

    def match_users_into_secret_santa_group(self, request, queryset):
        "Kicks off the holiday sprite"
        if len(queryset) < 2:
            return self.message_user(request, "Need at least 2", level=messages.ERROR)
        message = "Go to Matching -> SecretSantaGroup to trigger the event"
        try:
            MatchingService(queryset).match_users()
            self.message_user(request, message)
        except MatchBaseException as e:
            self.message_user(request, str(e), level=messages.ERROR)

    def remove_all_exclutions(self, request, queryset):
        for owner in queryset:
            owner.excluded_from_matching_with.clear()
        self.message_user(request, "Cleared")


class GroupAdmin(admin.ModelAdmin):

    actions = ["start_the_holidays"]

    @staticmethod
    def send_group_start_notification(group):
        group.active = True
        group.save()
        forwarders = map(
            MessageForwarder, Owner.objects.filter(secret_santa_group=group)
        )
        for f in forwarders:
            f.trigger_secret_santa_message()
            f.send_all_unsent_messages()

    def start_the_holidays(self, request, queryset):
        for o in queryset:
            if o.state != MessageStates.FORWARDING.value:
                self.message_user(request, "Not everyone has set their foundation yet.", level=messages.ERROR)
                break
        else:
            list(map(self.send_group_start_notification, queryset))
            self.message_user(request, "Ho ho ho!")


admin.site.register(SecretSantaGroup, GroupAdmin)
admin.site.register(Owner, MatchingAdmin)
