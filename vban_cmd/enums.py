from enum import Enum, IntEnum, unique


@unique
class KindId(Enum):
    BASIC = 1
    BANANA = 2
    POTATO = 3


class NBS(IntEnum):
    zero = 0
    one = 1


BusModes = IntEnum(
    'BusModes',
    'normal amix bmix repeat composite tvmix upmix21 upmix41 upmix61 centeronly lfeonly rearonly',
    start=0,
)
