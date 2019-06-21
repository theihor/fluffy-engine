class Bot:
    def __init__(self, pos: tuple):
        self.pos = pos
        self.manipulators = [
            (1, 0),
            (1, 1),
            (1, -1),
        ]

    def is_attachable(self, x: int, y: int):
        coords = self.manipulators + [self.pos]

        def func(pos: tuple):
            abs(pos[0] - x) + abs(pos[1] - y)

        return any(func(pos) for pos in coords)

    def attach(self, x: int, y: int):
        pass

    def turnLeft(self):
        pass

    def turnRight(self):
        pass
