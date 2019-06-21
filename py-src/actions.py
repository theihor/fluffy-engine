from constants import DRILL_DURATION, WHEELS_DURATION, STRICT_VALIDATION
from state import State, Cell, Booster


class SimpleAction:
    def __init__(self, value: str):
        self.value = value

    def validate(self, state: State):
        pass

    def process(self, state: State):
        if STRICT_VALIDATION and not self.validate(state):
            raise RuntimeError("Not valid action {} for state {}".format(self, state))

    def __str__(self):
        return self.value


class MoveUp(SimpleAction):
    def __init__(self):
        super().__init__("W")

    def validate(self, state: State):
        (x, y) = state.botPos()
        # validate only +1 cell move
        if y >= state.height - 1:
            return False
        if state.cell(x, y + 1)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State):
        super().process(state)
        (x, y) = state.botPos()
        state.setBotPos(x, y + 1)
        state.repaint()
        if state.wheel_duration > 0 and self.validate(state):
            state.setBotPos(x, y + 2)


class MoveDown(SimpleAction):
    def __init__(self):
        super().__init__("S")

    def validate(self, state: State):
        (x, y) = state.botPos()
        if y == 0:
            return False
        if state.cell(x, y - 1)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State):
        super().process(state)
        (x, y) = state.botPos()
        state.setBotPos(x, y - 1)
        state.repaint()
        if state.wheel_duration > 0 and self.validate(state):
            state.setBotPos(x, y - 2)


class MoveLeft(SimpleAction):
    def __init__(self):
        super().__init__("A")

    def validate(self, state: State):
        (x, y) = state.botPos()
        if x == 0:
            return False
        if state.cell(x - 1, y)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State):
        super().process(state)
        (x, y) = state.botPos()
        state.setBotPos(x - 1, y)
        state.repaint()
        if state.wheel_duration > 0 and self.validate(state):
            state.setBotPos(x - 2, y)


class MoveRight(SimpleAction):
    def __init__(self):
        super().__init__("D")

    def validate(self, state: State):
        (x, y) = state.botPos()
        if x >= state.width - 1:
            return False
        if state.cell(x + 1, y)[1] == Cell.OBSTACLE:
            return False
        return True

    def process(self, state: State):
        super().process(state)
        (x, y) = state.botPos()
        state.setBotPos(x + 1, y)
        state.repaint()
        if state.wheel_duration > 0 and self.validate(state):
            state.setBotPos(x + 2, y)


class DoNothing(SimpleAction):
    def __init__(self):
        super().__init__("Z")

    def validate(self, state: State):
        return True

    def process(self, state: State):
        pass


class TurnRight(SimpleAction):
    def __init__(self):
        super().__init__("E")

    def validate(self, state: State):
        return True

    def process(self, state: State):
        state.bot.turnRight()


class TurnLeft(SimpleAction):
    def __init__(self):
        super().__init__("Q")

    def validate(self, state: State):
        return True

    def process(self, state: State):
        state.bot.turnLeft()


class AttachWheels(SimpleAction):
    def __init__(self):
        super().__init__("F")

    def validate(self, state: State):
        return state.boosters[Booster.WHEEL] > 0

    def process(self, state: State):
        super().process(state)
        state.wheel_duration = WHEELS_DURATION


class AttachDrill(SimpleAction):
    def __init__(self):
        super().__init__("L")

    def validate(self, state: State):
        return state.boosters[Booster.DRILL] > 0

    def process(self, state: State):
        super().process(state)
        state.drill_duration = DRILL_DURATION


class AttachManipulator(SimpleAction):
    def __init__(self, coords: tuple):
        (self.x, self.y) = coords

    def validate(self, state: State):
        if state.boosters[Booster.MANIPULATOR] <= 0:
            return False
        return state.bot.is_attachable(self.x, self.y)

    def process(self, state: State):
        super().process(state)
        state.bot.attach(self.x, self.y)

    def __str__(self):
        return "B({},{})".format(self.x, self.y)
