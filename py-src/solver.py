import decode
from encoder import Encoder
from actions import *
import pathfinder


def solve(taskFile, solutionFile, solver):
    st = State.decode(decode.parse_task(taskFile))
    commands = solver(st)
    Encoder.encodeToFile(solutionFile, commands)


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


def pathToCommands(path):
    commands = []
    for (pos, nextPos) in zip(path, path[1:]):
        commands.append(moveCommand(pos, nextPos))
    return commands


# left-right direction
LR = 1


def attachCommand(bot):
    global LR
    turns = 0
    while bot.manipulators[0] != (1, 0):
        turns += 1
        bot.turnLeft()
    idx = 2
    while not bot.is_attachable(1, idx * LR):
        idx += 1
    pos = (idx * LR, 1)
    LR *= -1
    while turns > 0:
        turns -= 1
        bot.turnRight()
        pos = (pos[1], -pos[0])
    return AttachManipulator(pos)


def collectBoosters(st, bot):
    global LR
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda x, y: st.cell(x, y)[0] is not None)
        if path is None:
            break
        commands = pathToCommands(path)
        for command in commands:
            st.nextAction(command)
        if st.boosters[Booster.WHEEL] > 0 and bot.wheel_duration <= 0:
            command = AttachWheels()
        elif st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
            command = AttachDrill()
        elif st.boosters[Booster.MANIPULATOR] > 0:
            command = attachCommand(bot)
        # TODO (all boosters)
        else:
            return
        st.nextAction(command)


def closestRotSolver(st):
    bot = st.bots[0]
    collectBoosters(st, bot)
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda x, y: st.cell(x, y)[1] == Cell.ROT)
        if path is None:
            break
        commands = pathToCommands(path)
        for command in commands:
            st.nextActions([command])
    return st.actions()
