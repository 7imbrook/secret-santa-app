class MatchBaseException(Exception):
    pass


class UserAlreadyInMatchGroup(MatchBaseException):
    pass


class NoValidConfigurations(MatchBaseException):
    pass
