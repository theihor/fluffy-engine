import decode
from constants import ATTACHER
from encoder import Encoder
from actions import *
import pathfinder
import astar


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
    return max(results, key=lambda t: t[0])[1]


def pathToCommands(path, state, bot_num=0, augment=True):
    commands = []
    for (pos, nextPos) in zip(path, path[1:]):
        commands.append(moveCommand(pos, nextPos))
    for command in commands:
        if augment:
            new = selectCommand(state, command, bot_num)
            if new != command:
                state.nextAction(new)
        state.nextAction(command)


def collectBoosters(st, bot):
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda l, x, y: st.cell(x, y)[0] == Booster.MANIPULATOR)
        if path is None:
            break
        pathToCommands(path, st)

        cmd = AttachManipulator(ATTACHER.get_position(bot))
        st.nextAction(cmd)


def closestRotSolver(st):
    bot = st.bots[0]
    collectBoosters(st, bot)
    while True:
        path = pathfinder.bfsFind(st, bot.pos,
                                  lambda l, x, y: st.cell(x, y)[1] == Cell.ROT)
        if path is None:
            break
        pathToCommands(path, st)
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
    pathToCommands(path, st, augment=False)
    return path[len(path) - 1]


def blobClosestRotSolver(st):
    blobs = pathfinder.blobSplit(st, 15)

    def findBlob(pos):
        for blob in blobs:
            if pos in blob:
                return blob
        return None

    def optimizeBlob():
        for i in range(len(blobs)):
            if (len(blobs[i]) < 5):
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


def applyPath(st, path):
    pathToCommands(path, st, augment=False)


def addManipsToSet(s, blob, state, bot, pos):

    def add(x, y):
        if (x, y) in blob:
            s.add((x, y))
    bot.repaintWith(pos, state, add)


def cleanSetForBlob(state, blob):
    s = set()
    for (x, y) in blob:
        if state.cell(x, y)[1] == Cell.CLEAN:
            s.add((x, y))
    return s


class AStarNode(object):
    def __init__(self, bot, blob, state, pos, cleanSet, path):
        self.bot = bot
        self.blob = blob
        self.state = state
        self.pos = pos
        self.cleanSet = cleanSet
        self.path = path

    def neighbors(self):
        def end(x, y):
            return (self.state.cell(x, y)[1] == Cell.ROT
                    and (x, y) not in self.cleanSet)

        def avail(x, y):
            return (x, y) in self.blob
        paths = pathfinder.bfsFindMany(self.state, self.pos, end, availP=avail)
        if paths is None:
            return []
        nodes = []
        for path in paths:
            cleanSet = self.cleanSet.copy()
            for pos in path:
                # print('pos', self.pos)
                # print('path', path)
                # print('cleanSet', cleanSet)
                assert(pos != self.pos)
                addManipsToSet(cleanSet, self.blob, self.state, self.bot, pos)
            endPos = path[len(path)-1]
            assert(endPos not in self.cleanSet)
            node = AStarNode(self.bot, self.blob, self.state, endPos, cleanSet, self.path + path)
            nodes.append(node)
        return nodes

    def score(self):
        numManip = len(self.bot.manipulators)
        res = (len(self.blob) - len(self.cleanSet)) / (numManip + 1) + len(self.path)
        # print('path', self.path, 'rot', len(self.blob) - len(self.cleanSet))
        return res

    def final(self):
        return len(self.cleanSet) == len(self.blob)


class AStarSolver(astar.AStar):
    def neighbors(self, node):
        return node.neighbors()

    def distance_between(self, n1, n2):
        score1 = n1.score()
        score2 = n2.score()
        return abs(score1 - score2)

    def heuristic_cost_estimate(self, node, goal):
        return node.score()

    def is_goal_reached(self, node, goal):
        return node.final()


def solveWithBlobs(st, blobs):
    bot = st.bots[0]
    collectBoosters(st, bot)

    def findBlob(pos):
        for blob in blobs:
            if pos in blob:
                return blob
        return None

    curPos = st.botPos()
    blobInd = 0
    while True:
        blob = findBlob(curPos)
        if blob is None:
            break
        blobInd += 1
        print('blob', blobInd, 'of', len(blobs))
        # blobRanks = {}

        # def add(l, x, y):
        #     blobRanks[(x, y)] = l
        # pathfinder.bfsFind(st, curPos,
        #                    lambda l, x, y: False,
        #                    register=add)
        astar = AStarSolver()
        bot = st.bots[0]
        cs = cleanSetForBlob(st, blob)
        startNode = AStarNode(bot, blob, st, bot.pos, cs, [bot.pos])
        res = list(astar.astar(startNode, None))
        if res == [] or res is None:
            break
        node = res[len(res)-1]
        applyPath(st, node.path)
        # print('path', node.path)
        # while True:
        #     nextPos = closestRotInBlob(st, blob, {})
        #     if nextPos is None:
        #         break
        curPos = closestRotInBlob(st)
        if curPos is None:
            break
    return st.actions()
