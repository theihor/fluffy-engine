from constants import DRILL_DURATION, WHEELS_DURATION, STRICT_VALIDATION
from state import State, Cell, Booster


class SimpleAction:
    def __init__(self, value: str):
        self.value = value

    def validate(self, state: State, bot):
        pass

    def process(self, state: State, bot):
        if STRICT_VALIDATION and not self.validate(state, bot):
            raise RuntimeError("Not valid action {} for state {}".format(self, state))

    def __str__(self):
        return self.value


class MoveUp(SimpleAction):
    def __init__(self):
        super().__init__("W")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        # validate only +1 cell move
        if y >= state.height - 1:
            return False
        if bot.drill_duration <= 0 and state.cell(x, y + 1)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        state.setBotPos(x, y + 1)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            state.setBotPos(x, y + 2)


class MoveDown(SimpleAction):
    def __init__(self):
        super().__init__("S")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if y == 0:
            return False
        if bot.drill_duration <= 0 and state.cell(x, y - 1)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        state.setBotPos(x, y - 1)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            state.setBotPos(x, y - 2)


class MoveLeft(SimpleAction):
    def __init__(self):
        super().__init__("A")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if x == 0:
            return False
        if bot.drill_duration <= 0 and state.cell(x - 1, y)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        state.setBotPos(x - 1, y)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            state.setBotPos(x - 2, y)


class MoveRight(SimpleAction):
    def __init__(self):
        super().__init__("D")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if x >= state.width - 1:
            return False
        if bot.drill_duration <= 0 and state.cell(x + 1, y)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        state.setBotPos(x + 1, y)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            state.setBotPos(x + 2, y)


class DoNothing(SimpleAction):
    def __init__(self):
        super().__init__("Z")

    def validate(self, state: State, bot):
        return True

    def process(self, state: State, bot):
        pass


class TurnRight(SimpleAction):
    def __init__(self):
        super().__init__("E")

    def validate(self, state: State, bot):
        return True

    def process(self, state: State, bot):
        bot.turnRight()


class TurnLeft(SimpleAction):
    def __init__(self):
        super().__init__("Q")

    def validate(self, state: State, bot):
        return True

    def process(self, state: State, bot):
        bot.turnLeft()


class AttachWheels(SimpleAction):
    def __init__(self):
        super().__init__("F")

    def validate(self, state: State, bot):
        return state.boosters[Booster.WHEEL] > 0

    def process(self, state: State, bot):
        super().process(state, bot)
        bot.wheel_duration = WHEELS_DURATION + 1
        state.boosters[Booster.WHEEL] -= 1


class AttachDrill(SimpleAction):
    def __init__(self):
        super().__init__("L")

    def validate(self, state: State, bot):
        return state.boosters[Booster.DRILL] > 0

    def process(self, state: State, bot):
        super().process(state, bot)
        bot.drill_duration = DRILL_DURATION + 1
        state.boosters[Booster.DRILL] -= 1


class AttachManipulator(SimpleAction):
    def __init__(self, coords: tuple):
        (self.x, self.y) = coords

    def validate(self, state: State, bot):
        if state.boosters[Booster.MANIPULATOR] <= 0:
            return False
        return bot.is_attachable(self.x, self.y)

    def process(self, state: State, bot):
        super().process(state, bot)
        bot.attach(self.x, self.y)
        state.boosters[Booster.MANIPULATOR] -= 1

    def __str__(self):
        return "B({},{})".format(self.x, self.y)
