from constants import STRICT_VALIDATION, Booster


class Bot:
    def __init__(self, pos: tuple):
        self.pos = pos
        self.manipulators = [
            (1, 0),
            (1, 1),
            (1, -1),
        ]

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
        def new(pos):
            return -pos[1], pos[0]
        self.manipulators = [new(pos) for pos in self.manipulators]

    def turnRight(self):
        def new(pos):
            return pos[1], -pos[0]
        self.manipulators = [new(pos) for pos in self.manipulators]

    def process(self, state):
        bot_cell = state.cell(self.pos[0], self.pos[1])
        if bot_cell[0] is not None:
            state.removeBooster(self.pos)
            state.boosters[bot_cell[0]] += 1

        def real(pos):
            return pos[0] + self.pos[0], pos[1] + self.pos[1]
        coords = [real(pos) for pos in self.manipulators] + [self.pos]
        for pos in coords:
            state.paintCell(pos[0], pos[1])
