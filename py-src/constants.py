from enum import Enum, auto

from attachdecider import *

DRILL_DURATION = 30
WHEELS_DURATION = 50
STRICT_VALIDATION = False
ATTACHER = SimpleAttacher()


class Cell(Enum):
    ROT = auto()
    CLEAN = auto()
    OBSTACLE = auto()


class Booster(Enum):
    WHEEL = auto()
    DRILL = auto()
    MANIPULATOR = auto()
    MYSTERIOUS = auto()
    TELEPORT = auto()
    CLONE = auto()
