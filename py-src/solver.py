from constants import Booster
from state import State, Cell
import decode
from encoder import Encoder
from actions import MoveUp, MoveDown, MoveLeft, MoveRight, AttachManipulator
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


def collectBoosters(st, bot):
    global LR
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda l, x, y: st.cell(x, y)[0] == Booster.MANIPULATOR)
        if path is None:
            break
        commands = pathToCommands(path)
        for command in commands:
            st.nextAction(command)

        turns = 0
        while bot.manipulators[0] != (1, 0):
            turns += 1
            bot.turnLeft()
        idx = 2
        while not bot.is_attachable(1, idx * LR):
            idx += 1
        pos = (1, idx * LR)

        LR *= -1
        while turns > 0:
            turns -= 1
            bot.turnRight()
            pos = (pos[1], -pos[0])
        st.nextAction(AttachManipulator(pos))


def closestRotSolver(st):
    bot = st.bots[0]
    collectBoosters(st, bot)
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda l, x, y: st.cell(x, y)[1] == Cell.ROT)
        if path is None:
            break
        commands = pathToCommands(path)
        for command in commands:
            st.nextActions([command])
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
    commands = pathToCommands(path)
    for command in commands:
        st.nextAction(command)
    return path[len(path)-1]


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
                otherPos = otherPath[len(otherPath)-1]
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
