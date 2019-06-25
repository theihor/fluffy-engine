from enum import Enum

from attachdecider import *


class Cell(Enum):
    ROT = 1
    CLEAN = 2
    OBSTACLE = 3


class Booster(Enum):
    WHEEL = 1
    DRILL = 2
    MANIPULATOR = 3
    MYSTERIOUS = 4
    TELEPORT = 5
    CLONE = 6


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

DRILL_DURATION = 30
WHEELS_DURATION = 50
STRICT_VALIDATION = False
ATTACHER = SimpleAttacher()
TURN_BOT = False
# 0 - always use, 1 - never use
WHEELS_PROC = 1
DRILL_PROC = 1
# collect stage
COLLECTABLE = [
    # Booster.WHEEL,
    Booster.MANIPULATOR,
    # Booster.TELEPORT,
    # Booster.DRILL,
    # Booster.CLONE,
    # Booster.MYSTERIOUS,
]
# paint stage
USABLE = [
    Booster.WHEEL,
    Booster.MANIPULATOR,
    Booster.DRILL,
    # Booster.CLONE,
    # Booster.TELEPORT,
]
