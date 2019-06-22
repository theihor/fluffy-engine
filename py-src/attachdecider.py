class SimpleAttacher:
    LR = 1

    def get_position(self, bot):
        turns = 0
        while bot.manipulators[0] != (1, 0):
            turns += 1
            bot.turnLeft()
        idx = 2
        while not bot.is_attachable(1, idx * self.LR):
            idx += 1
        pos = (1, idx * self.LR)

        self.LR *= -1
        while turns > 0:
            turns -= 1
            bot.turnRight()
            pos = (pos[1], -pos[0])
        return pos


class ExperimentalAttacher:
    cnt = 0
    positions = [
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

    def get_position(self, bot):
        if self.cnt >= len(self.positions):
            raise RuntimeError("Not enough positions hardcoded :(")
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
