from constants import *


class Bot:
    def __init__(self, pos: tuple):
        self.pos = pos
        self.direction = Direction.RIGHT
        self.manipulators = [
            (1, 0),
            (1, 1),
            (1, -1),
        ]
        self.wheel_duration = 0
        self.drill_duration = 0
        self.actions = []

    def is_attachable(self, x: int, y: int):
        coords = self.manipulators + [(0, 0)]

        if any(pos[0] == x and pos[1] == y for pos in coords):
            return False

        def true(pos: tuple):
            return abs(pos[0] - x) + abs(pos[1] - y) == 1

        return any(true(pos) for pos in coords)

    def attach(self, x: int, y: int):
        if STRICT_VALIDATION and not self.is_attachable(x, y):
            raise RuntimeError("Can't attach manipulator")
        self.manipulators.append((x, y))

    def turnLeft(self):
        self.direction = left_of(self.direction)
        def new(pos):
            return -pos[1], pos[0]
        self.manipulators = [new(pos) for pos in self.manipulators]

    def turnRight(self):
        self.direction = right_of(self.direction)
        def new(pos):
            return pos[1], -pos[0]
        self.manipulators = [new(pos) for pos in self.manipulators]

    def process(self, state):
        bot_cell = state.cell(self.pos[0], self.pos[1])
        if bot_cell[0] is not None:
            state.removeBooster(self.pos)
            state.boosters[bot_cell[0]] += 1
        self.repaint(state)

    def repaint(self, state):
        def real(pos):
            return pos[0] + self.pos[0], pos[1] + self.pos[1]
        coords = [real(pos) for pos in self.manipulators] + [self.pos]
        state.paintCells(coords)

    def repaintWith(self, fromPos, state, func):
        def real(pos):
            return pos[0] + fromPos[0], pos[1] + fromPos[1]
        coords = [real(pos) for pos in self.manipulators] + [fromPos]
        for (x, y) in coords:
            state.tryPaintCellWith(fromPos[0], fromPos[1], x, y, func)

    def tickTime(self):
        if self.wheel_duration > 0:
            self.wheel_duration -= 1
        if self.drill_duration > 0:
            self.drill_duration -= 1
