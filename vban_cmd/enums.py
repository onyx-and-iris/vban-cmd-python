from enum import IntEnum


class NBS(IntEnum):
    zero = 0
    one = 1


BusModes = IntEnum(
    'BusModes',
    'normal amix bmix repeat composite tvmix upmix21 upmix41 upmix61 centeronly lfeonly rearonly',
    start=0,
)

EQGains = IntEnum('EQGains', 'bass mid treble', start=0)
