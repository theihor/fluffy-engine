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
        pass

    def turnLeft(self):
        pass

    def turnRight(self):
        pass
