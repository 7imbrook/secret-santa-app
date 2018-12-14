from enum import Enum


class StringEnum(Enum):
    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class MessageStates(StringEnum):
    INITIAL = "initial"
    FOUNDATION = "foundation"
    NAME = "name"
    FORWARDING = "forwarding"
