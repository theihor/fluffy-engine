from bot import Bot
from constants import DRILL_DURATION, WHEELS_DURATION, STRICT_VALIDATION
from state import State, Cell, Booster
from attachdecider import *

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

    def booster_action(self):
        return False


class MoveUp(SimpleAction):
    def __init__(self):
        super().__init__("W")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if y >= state.height - 1:
            return False

        close_obstacle = state.cell(x, y + 1)[1] == Cell.OBSTACLE

        if bot.wheel_duration > 0 and y < state.height - 2:
            far_obstacle = state.cell(x, y + 2)[1] == Cell.OBSTACLE
            if close_obstacle and far_obstacle:
                return bot.drill_duration > 1
            else: return not close_obstacle #and not far_obstacle
        else:
            if close_obstacle:
                return bot.drill_duration > 0
            else: return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        bot.pos = (x, y + 1)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            bot.pos = (x, y + 2)
            bot.process(state)


class MoveDown(SimpleAction):
    def __init__(self):
        super().__init__("S")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if y == 0:
            return False

        close_obstacle = state.cell(x, y - 1)[1] == Cell.OBSTACLE

        if bot.wheel_duration > 0 and y > 1:
            far_obstacle = state.cell(x, y - 2)[1] == Cell.OBSTACLE
            if close_obstacle and far_obstacle:
                return bot.drill_duration > 1
            else: return not close_obstacle #and not far_obstacle
        else:
            if close_obstacle:
                return bot.drill_duration > 0
            else: return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        bot.pos = (x, y - 1)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            bot.pos = (x, y - 2)
            bot.process(state)


class MoveLeft(SimpleAction):
    def __init__(self):
        super().__init__("A")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if x == 0: return False

        close_obstacle = state.cell(x - 1, y)[1] == Cell.OBSTACLE

        if bot.wheel_duration > 0 and x > 1:
            far_obstacle = state.cell(x - 2, y)[1] == Cell.OBSTACLE
            if close_obstacle and far_obstacle:
                return bot.drill_duration > 1
            else: return not close_obstacle #and not far_obstacle
        else:
            if close_obstacle:
                return bot.drill_duration > 0
            else: return True

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        bot.pos = (x - 1, y)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            bot.pos = (x - 2, y)
            bot.process(state)


class MoveRight(SimpleAction):
    def __init__(self):
        super().__init__("D")

    def validate(self, state: State, bot):
        (x, y) = bot.pos
        if x >= state.width - 1:
            return False

        close_obstacle = state.cell(x + 1, y)[1] == Cell.OBSTACLE

        if bot.wheel_duration > 0 and x < state.width - 2:
            far_obstacle = state.cell(x + 2, y)[1] == Cell.OBSTACLE
            if close_obstacle and far_obstacle:
                return bot.drill_duration > 1
            else: return not close_obstacle #and not far_obstacle
        else:
            if close_obstacle:
                return bot.drill_duration > 0
            else: return True


    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = bot.pos
        bot.pos = (x + 1, y)
        bot.process(state)
        if bot.wheel_duration > 0 and self.validate(state, bot):
            bot.pos = (x + 2, y)
            bot.process(state)


def moveCommand(posFrom, posTo):
    (xf, yf) = posFrom
    (xt, yt) = posTo
    if xt == xf:
        if yt < yf:
            return MoveDown()
        else:
            return MoveUp()
    if xt < xf:
        return MoveLeft()
    else:
        return MoveRight()


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


class BoosterAction(SimpleAction):
    def booster_action(self):
        return True

    # def validate(self, state, bot):
    #     if not super().validate(state, bot):
    #         return False
    #     # if state.lockBoosters > 0:
    #     #     return False
    #     return True



class AttachWheels(BoosterAction):
    def __init__(self):
        super().__init__("F")

    def validate(self, state: State, bot):
        return (state.boosters[Booster.WHEEL] > 0
                and not bot.drill_duration > 0
                and not bot.wheel_duration > 0)
        #     return False

    def process(self, state: State, bot):
        super().process(state, bot)
        bot.wheel_duration = WHEELS_DURATION + 1
        state.boosters[Booster.WHEEL] -= 1


class AttachDrill(BoosterAction):
    def __init__(self):
        super().__init__("L")

    def validate(self, state: State, bot):
        return (state.boosters[Booster.DRILL] > 0
                and not bot.wheel_duration > 0
                and not bot.drill_duration > 0)
        #     return False

    def process(self, state: State, bot):
        super().process(state, bot)
        bot.drill_duration = DRILL_DURATION + 1
        state.boosters[Booster.DRILL] -= 1


class AttachManipulator(BoosterAction):
    def __init__(self, coords: tuple):
        (self.x, self.y) = coords

    def validate(self, state: State, bot):
        # if not super().validate(state, bot):
        #     return False
        if state.boosters[Booster.MANIPULATOR] <= 0:
            return False
        (bx, by) = bot.pos
        (x, y) = (bx + self.x, by + self.y)
        if x < 0 or x >= state.width or y < 0 or y >= state.height:
            #print('Trying too attach too far')
            return False
        elif not state.visibleFrom(bx, by, (x, y)):
            #print('Attach pos is invisible: ', (bx, by), (x, y))
            return False
        return bot.is_attachable(self.x, self.y)

    def process(self, state: State, bot):
        super().process(state, bot)
        bot.attach(self.x, self.y)
        state.boosters[Booster.MANIPULATOR] -= 1
        bot.repaint(state)

    def __str__(self):
        return "B({},{})".format(self.x, self.y)


class Reset(BoosterAction):
    def __init__(self):
        super().__init__("R")

    def validate(self, state: State, bot):
        return (state.boosters[Booster.TELEPORT] > 0
                and bot.pos not in state.pods)

    def process(self, state: State, bot):
        super().process(state, bot)
        state.pods.add(bot.pos)
        state.boosters[Booster.TELEPORT] -= 1


class Shift(BoosterAction):
    def __init__(self, pos):
        self.pos = pos

    def validate(self, state: State, bot):
        return self.pos in state.pods

    def process(self, state: State, bot):
        super().process(state, bot)
        (x, y) = self.pos
        state.setBotPos(x, y)
        bot.process(state)

    def __str__(self):
        return "T({},{})".format(self.pos[0], self.pos[1])


class CloneAction(BoosterAction):
    def __init__(self):
        super().__init__("C")
        
    def validate(self, state: State, bot):
        # if not super().validate(state, bot):
        #     return False
        print("validate")
        if state.boosters[Booster.CLONE] <= 0:
            print(1)
            return False
        if state.cell(*bot.pos)[0] != Booster.MYSTERIOUS:
            print(str(state.cell(*bot.pos)))
            return False
        return True
    
    def process(self, state: State, bot):
        super().process(state, bot)
        print("CLONE!!!")
        state.bots.append(Bot(bot.pos))
        state.boosters[Booster.CLONE] -= 1


def attach_manipulators(state, bot):
    attached = False

    for i in range(state.boosters[Booster.MANIPULATOR]):
        attachers = [
            AttachManipulator(ExperimentalAttacher(forward).get_position(bot)),
            AttachManipulator(ExperimentalAttacher(forward_wide).get_position(bot)),
            AttachManipulator(SimpleAttacher().get_position(bot)),
            #   AttachManipulator(ExperimentalAttacher(experimental).get_position(bot)),
        ]
        for a in attachers:
            if a.validate(state, bot):
                state.nextAction(a)
                attached = True
                attach_manipulators(state, bot)
    return attached
