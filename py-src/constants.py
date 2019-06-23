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
]
# paint stage
USABLE = [
    # Booster.WHEEL,
    # Booster.MANIPULATOR,
    # Booster.DRILL,
]
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
def left_of(d):
    return {Direction.RIGHT: Direction.UP,
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN,
            Direction.DOWN: Direction.RIGHT}[d]
def right_of(d):
    return {Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
            Direction.UP: Direction.RIGHT}[d]
