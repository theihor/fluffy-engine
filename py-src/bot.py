from constants import STRICT_VALIDATION


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
        pass

    def turnRight(self):
        pass

    def process(self, state):
        def real(pos):
            return pos[0] + self.pos[0], pos[1] + self.pos[1]
        coords = [real(pos) for pos in self.manipulators] + [self.pos]
        for pos in coords:
            state.paintCell(pos[0], pos[1])