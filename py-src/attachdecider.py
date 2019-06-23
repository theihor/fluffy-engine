class SimpleAttacher:
    LR = 1

    def get_position(self, bot):
        turns = 0
        while bot.manipulators[0] != (1, 0):
            turns += 1
            bot.turnLeft()
        idx = 2
        t = 0
        while not bot.is_attachable(1, idx * self.LR) and t < 100:
            idx += 1
            t += 1
        pos = (1, idx * self.LR)

        self.LR *= -1
        while turns > 0:
            turns -= 1
            bot.turnRight()
            pos = (pos[1], -pos[0])
        return pos


experimental = [
        (1, 2),
        (1, -2),
        (0, 2),
        (0, -2),
        (1, 3),
        (1, -3),
        (0, 3),
        (0, -3),
        (1, 4),
        (1, -4),
    ]


long_center = [
        (1, 2),
        (1, -2),
        (1, 3),
        (1, -3),
        (1, 4),
        (1, -4),
        (1, 5),
        (1, -5),
        (1, 6),
        (1, -6),
    ]


long_left = [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (1, 6),
        (1, 7),
        (1, 8),
        (1, -2),
        (1, -3),
    ]

long_right = [
        (1, -2),
        (1, -3),
        (1, -4),
        (1, -5),
        (1, -6),
        (1, -7),
        (1, -8),
        (1, 2),
        (1, 3),
    ]


forward_wide = [
        (2, 0),
        (3, 0),
        (1, 2),
        (1, -2),
        (2, 2),
        (2, -2),
        (1, 3),
        (1, -3),
        (4, 0),
    ]

forward = [
        (2, 0),
        (3, 0),
        (4, 0),
        (1, -2),
        (1, 2),
        (1, -3),
        (1, 3),
        (5, 0),
        (1, 4),
        (1, -4),
    ]


class ExperimentalAttacher:
    cnt = 0
    default = SimpleAttacher()

    def __init__(self, positions):
        self.positions = positions

    def get_position(self, bot):
        if self.cnt >= len(self.positions):
            return self.default.get_position(bot)
        pos = self.positions[self.cnt]
        self.cnt += 1
        turns = 0
        while bot.manipulators[0] != (1, 0):
            turns += 1
            bot.turnLeft()
        while turns > 0:
            turns -= 1
            bot.turnRight()
            pos = (pos[1], -pos[0])
        return pos
