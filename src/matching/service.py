import random, time
from itertools import combinations, permutations

from matching.exceptions import NoValidConfigurations, UserAlreadyInMatchGroup
from matching.models import Owner, SecretSantaGroup


def rotate(l):
    return l[1:] + l[:1]


class MatchingService:
    """
    Best effort matching based of shuffle. One shuffle (with constraints) should
    be good enough because we can match everyone using shift matching. But We
    have a constraint of who can match to who.
    """

    def __init__(self, queryset):
        self.canidate_set = list(queryset)
        for o in self.canidate_set:
            if o.secret_santa_group is not None:
                raise UserAlreadyInMatchGroup("Cant add user to multiple groups")
        random.shuffle(self.canidate_set)

    @classmethod
    def exclude(cls, queryset):
        for a, b in combinations(queryset, 2):
            a.excluded_from_matching_with.add(b)

    def verify_matching(self, option) -> bool:
        """
        O(n)
        """
        for a, b in zip(option, rotate(option)):
            if a in b.excluded_from_matching_with.all():
                return False
        return True

    def lock_in_canidates_into_managed_group(self):
        """
        This method doesn't verify you are correct!
        O(n)
        """
        group = SecretSantaGroup.objects.create()
        for a, b in zip(self.canidate_set, rotate(self.canidate_set)):
            a.secret_santa_group = group
            a.your_secret = b
            a.save()

    def match_users(self):
        # Verify canidate set is valid for shift matching
        for option in permutations(self.canidate_set):
            if self.verify_matching(option):
                self.canidate_set = option
                return self.lock_in_canidates_into_managed_group()
        raise NoValidConfigurations("Tried all permutations, no valid solution")
