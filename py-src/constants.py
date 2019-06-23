from enum import Enum, auto

from attachdecider import *


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


DRILL_DURATION = 30
WHEELS_DURATION = 50
STRICT_VALIDATION = False
ATTACHER = ExperimentalAttacher(forward)
TURN_BOT = False
# 0 - always use, 1 - never use
WHEELS_PROC = 0
DRILL_PROC = 0
# collect stage
COLLECTABLE = [
    # Booster.WHEEL,
    Booster.MANIPULATOR,
    # Booster.DRILL,
]
# paint stage
USABLE = [
    # Booster.WHEEL,
    # Booster.MANIPULATOR,
    # Booster.DRILL,
]
