from enum import Enum, auto

DRILL_DURATION = 30
WHEELS_DURATION = 50
STRICT_VALIDATION = False


class Cell(Enum):
    ROT = auto()
    CLEAN = auto()
    OBSTACLE = auto()


class Booster(Enum):
    WHEEL = auto()
    DRILL = auto()
    MANIPULATOR = auto()
    MYSTERIOUS = auto()


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
