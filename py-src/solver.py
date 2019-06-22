import random

import decode
from constants import *
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


def selectCommand(state, command, bot_num):
    results = []
    bot = state.bots[bot_num]
    (x, y) = bot.pos
    current = len(bot.manipulators)
    if isinstance(command, MoveUp):
        current = numCleaned(state, (x, y + 1), bot_num)
    elif isinstance(command, MoveDown):
        current = numCleaned(state, (x, y - 1), bot_num)
    elif isinstance(command, MoveRight):
        current = numCleaned(state, (x + 1, y), bot_num)
    elif isinstance(command, MoveLeft):
        current = numCleaned(state, (x - 1, y), bot_num)
    results.append((current, command))
    bot.turnRight()
    right = numCleaned(state, bot.pos, bot_num)
    if TurnRight().validate(state, bot):
        results.append((right, TurnRight()))
    bot.turnLeft()
    bot.turnLeft()
    left = numCleaned(state, bot.pos, bot_num)
    if TurnLeft().validate(state, bot):
        results.append((left, TurnLeft()))
    bot.turnRight()
    command = max(results, key=lambda t: t[0])[1]
    return command


def pathToCommands(path, state, bot_num=0):
    commands = []
    for (pos, nextPos) in zip(path, path[1:]):
        commands.append(moveCommand(pos, nextPos))
    for command in commands:
        new = selectCommand(state, command, bot_num)
        if new != command:
            state.nextAction(new)
        state.nextAction(command)


def collectBoosters(st, bot):
    interesting = [
        Booster.WHEEL,
        Booster.MANIPULATOR,
        Booster.DRILL,
    ]
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda l, x, y: st.cell(x, y)[0] in interesting,
                                  availP=available(st, bot))
        if path is None:
            break
        pathToCommands(path, st)

        if st.boosters[Booster.MANIPULATOR] > 0:
            command = AttachManipulator(ATTACHER.get_position(bot))
        # TODO (all boosters)
        else:
            continue
        st.nextAction(command)


def available(state, bot=None):
    if bot is None:
        bot = state.bots[0]
    drill = bot.drill_duration
    wheel = bot.wheel_duration

    def drill_aval(l):
        # TODO (wheel handling)
        return drill > l

    return lambda l, x, y: drill_aval(l) or state.cell(x, y)[1] is not Cell.OBSTACLE


def closestRotSolver(st):
    bot = st.bots[0]
    collectBoosters(st, bot)
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda l, x, y: st.cell(x, y)[1] == Cell.ROT,
                                  availP=available(st))
        if st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
            path2 = pathfinder.bfsFind(st, bot.pos,
                                       lambda l, x, y: st.cell(x, y)[1] == Cell.ROT,
                                       availP=lambda l, x, y: DRILL_DURATION > l or st.cell(x, y)[1] is not Cell.OBSTACLE)
            if len(path2) < len(path):
                st.nextAction(AttachDrill())
                path = path2
        if path is None:
            break
        pathToCommands(path, st)
        if st.boosters[Booster.WHEEL] > 0 and bot.wheel_duration <= 0:
            if random.random() > WHEELS_PROC:
                print("Attach WHEELS at " + str(len(bot.actions)))
                st.nextAction(AttachWheels())
        if st.boosters[Booster.DRILL] > 0 and bot.drill_duration <= 0:
            if random.random() > DRILL_PROC:
                print("Attach DRILL at " + str(len(bot.actions)))
                st.nextAction(AttachDrill())
    return st.actions()


def numCleaned(st, pos, botnum):
    bot = st.bots[botnum]
    num = 0

    def inc():
        nonlocal num
        num += 1

    bot.repaintWith(pos, st, lambda x, y: inc())
    return num


def closestRotInBlob(st, blob=None, blobRanks=None):
    if blob is None:
        path = pathfinder.bfsFindClosest(st, st.botPos(),
                                         lambda l, x, y:
                                         st.cell(x, y)[1] == Cell.ROT,
                                         rank=lambda x, y:
                                         -numCleaned(st, (x, y), 0))
    else:
        path = pathfinder.bfsFindClosest(
            st, st.botPos(),
            lambda l, x, y: st.cell(x, y)[1] == Cell.ROT,
            availP=lambda x, y: (x, y) in blob,
            rank=lambda x, y:
            (blobRanks.get((x, y)) or 99999,
             -numCleaned(st, (x, y), 0)))
    if path is None:
        return None
    pathToCommands(path, st)
    return path[len(path) - 1]


def blobClosestRotSolver(st):
    blobs = pathfinder.blobSplit(st, 100000)

    def findBlob(pos):
        for blob in blobs:
            if pos in blob:
                return blob
        return None

    def optimizeBlob():
        for i in range(len(blobs)):
            if (len(blobs[i]) < 10):
                pos = next(iter(blobs[i]))
                otherPath = pathfinder.bfsFind(st, pos,
                                               lambda l, x, y:
                                               st.cell(x, y)[1] == Cell.ROT
                                               and (x, y) not
                                               in blobs[i])
                if otherPath is None:
                    return False
                otherPos = otherPath[len(otherPath) - 1]
                otherBlob = findBlob(otherPos)
                blobs[i] = otherBlob.union(blobs[i])
                blobs.remove(otherBlob)
                return True
        return False

    for it in range(1000):
        optimizeBlob()
    return solveWithBlobs(st, blobs)


# solve('/home/myth/projects/fluffy-engine/desc/prob-047.desc', '/home/myth/projects/fluffy-engine/sol/sol-047.sol', blobClosestRotSolver)


def solveWithBlobs(st, blobs):
    bot = st.bots[0]
    collectBoosters(st, bot)

    def findBlob(pos):
        for blob in blobs:
            if pos in blob:
                return blob
        return None

    curPos = st.botPos()
    while True:
        blob = findBlob(curPos)
        if blob is None:
            break
        blobRanks = {}

        def add(l, x, y):
            blobRanks[(x, y)] = l

        pathfinder.bfsFind(st, curPos,
                           lambda l, x, y: False,
                           register=add)
        while True:
            nextPos = closestRotInBlob(st, blob, {})
            if nextPos is None:
                break
        curPos = closestRotInBlob(st)
        if curPos is None:
            break
    return st.actions()
