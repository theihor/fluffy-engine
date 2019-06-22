from constants import Booster
from state import State, Cell
import decode
from encoder import Encoder
from actions import MoveUp, MoveDown, MoveLeft, MoveRight, AttachManipulator
import pathfinder
import astar
import copy


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
    blobs = pathfinder.blobSplit(st, 20)

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


def applyPath(st, path):
    commands = pathToCommands(path)
    for command in commands:
        st.nextAction(command)


def addManipsToSet(s, state, bot, pos):
    bot.repaintWith(pos, state,
                    lambda x, y: s.add((x, y)))


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
        self.savedNeghbours = None

    def getNeighbors(self):
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
                addManipsToSet(self.cleanSet, self.state, self.bot, pos)
            endPos = path[len(path)-1]
            node = AStarNode(self.bot, self.blob, self.state, endPos, cleanSet, self.path + path)
            nodes.append(node)
        return nodes

    def neighbors(self):
        if self.savedNeghbours is None:
            self.savedNeghbours = self.getNeighbors()
        print('pos', self.pos, 'clean', self.cleanSet, 'neighbors', len(self.savedNeghbours))
        return self.savedNeghbours

    def score(self, leftBlobSize):
        numManip = len(self.bot.manipulators)
        res = (leftBlobSize - len(self.cleanSet)) / numManip + len(self.path)
        # print('path', self.path, 'score', res)
        return res

    def final(self):
        return len(self.neighbors()) == 0


class AStarSolver(astar.AStar):
    def __init__(self, state, blob):
        self.blob = blob
        leftBlobSize = 0
        for (x, y) in blob:
            if state.cell(x, y)[1] is Cell.ROT:
                leftBlobSize += 1
        self.leftBlobSize = leftBlobSize

    def neighbors(self, node):
        return node.neighbors()

    def distance_between(self, n1, n2):
        score1 = n1.score(self.leftBlobSize)
        score2 = n2.score(self.leftBlobSize)
        return abs(score1 - score2)

    def heuristic_cost_estimate(self, node, goal):
        return node.score(self.leftBlobSize)

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
    while True:
        blob = findBlob(curPos)
        if blob is None:
            break
        print('blob', blob)
        # blobRanks = {}

        # def add(l, x, y):
        #     blobRanks[(x, y)] = l
        # pathfinder.bfsFind(st, curPos,
        #                    lambda l, x, y: False,
        #                    register=add)
        astar = AStarSolver(st, blob)
        bot = st.bots[0]
        cs = cleanSetForBlob(st, blob)
        startNode = AStarNode(bot, blob, st, bot.pos, cs, [bot.pos])
        res = list(astar.astar(startNode, None))
        if res == [] or res is None:
            break
        node = res[len(res)-1]
        applyPath(st, node.path)
        print('path', node.path)
        # while True:
        #     nextPos = closestRotInBlob(st, blob, {})
        #     if nextPos is None:
        #         break
        curPos = closestRotInBlob(st)
        if curPos is None:
            break
    return st.actions()
