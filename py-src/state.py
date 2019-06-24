from constants import Booster, Cell
from bot import Bot
from math import ceil, floor
from collections import namedtuple
import heapq

from encoder import Encoder

VEdge = namedtuple("VEdge", ('x', 'y1', 'y2'))


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return False

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def cross_point(point, line):
    """Check whether the cell on point is crossed by line"""
    (ix, iy) = point

    cross_points = set()

    def point_on_line(p, l):
        # l must be vertical or horisontal
        # print("point " + str(p) + " on " + str(l))
        ((x1, y1), (x2, y2)) = l
        return (p[0] == x1 == x2 and min(y1, y2) <= p[1] <= max(y1, y2)) or \
               (p[1] == y1 == y2 and min(x1, x2) <= p[0] <= max(x1, x2))

    sides = []
    l = ((ix, iy), (ix, iy + 1)) # left-down -> left-up
    sides.append(l)
    l = ((ix, iy + 1), (ix + 1, iy + 1))  # left-up -> right-up
    sides.append(l)
    l = ((ix + 1, iy), (ix + 1, iy + 1))  # right-down -> right-up
    sides.append(l)
    l = ((ix, iy), (ix + 1, iy))  # left-down -> right-down
    sides.append(l)

    for side in sides:
        p = line_intersection(line, side)
        if p:
            r = point_on_line(p, side)
            #print(r)
            if r: cross_points.add(p)
    if len(cross_points) == 2:
        #print(str(point) + " crossed! " + str(cross_points))
        return True
    elif len(cross_points) <= 1:
        #print(str(point) + " not crossed!")
        return False
    else: raise RuntimeError("More than 2 cross points with square. WAT.")


class State(object):
    def __init__(self, contour, botPos: tuple, obstacles, boosters):
        self.bots = [Bot(botPos)]
        self.last_painted = 0
        self.total_rot_cells = 0
        # map [booster -> amount]
        self.boosters = {
            Booster.DRILL: 0,
            Booster.WHEEL: 0,
            Booster.MANIPULATOR: 0,
            Booster.MYSTERIOUS: 0,
            Booster.TELEPORT: 0,
            Booster.CLONE: 0,
        }
        self.createCells(contour)
        for obstacle in obstacles:
            if len(obstacle) > 0:
                self.fillContour(obstacle, (None, Cell.OBSTACLE))
        self.addBoosters(boosters)
        self.tickNum = 0
        self.repaint()
        self.save_log = False
        self.pods = set()

    def set_save_log(self):
        self.save_log = True
        self.cells_log = [row[:] for row in [[None] * self.width]
                          * self.height]
        self.bots = list(map(lambda b: Bot(b.pos, save_log=True), self.bots))

    def add_log(self, bot_num, action):
        bot = self.bots[bot_num]
        bot.log_action(action)
        (x, y) = bot.pos
        log = self.cells_log[y][x]
        if log is None:
            log = {}
            self.cells_log[y][x] = log
        botLog = log.get(bot_num)
        if botLog is None:
            botLog = []
            log[bot_num] = botLog
        botLog.append(len(bot.log) - 1)

    def addBoosters(self, boosters):
        for booster in boosters:
            (x, y) = booster[1]
            self.cells[y][x] = (booster[0], Cell.ROT)

    def decode(d):
        return State(d['map'], d['start'], d['obstacles'], d['boosters'])

    def createCells(self, contour):
        self.width = max(contour, key=lambda pos: pos[0])[0]
        self.height = max(contour, key=lambda pos: pos[1])[1]
        self.cells = [row[:] for row in [[(None, Cell.OBSTACLE)] * self.width]
                      * self.height]
        self.fillContour(contour, (None, Cell.ROT))

    def fillContour(self, contour, value):
        queue = []
        for (x1, y1), (x2, y2) in zip(contour, contour[1:] + [contour[0]]):
            if x1 == x2:
                edge = VEdge(x1, min(y1, y2), max(y1, y2))
                queue.append((edge.y1, edge))
                queue.append((edge.y2, ()))
        heapq.heapify(queue)
        curedges = []
        curY = queue[0][0]
        while len(curedges) != 0 or len(queue) != 0:
            # print('edges ', curedges)
            # print('queue ', queue)
            # print('curY ', curY)
            # Remove finished edges
            curedges = list(filter(lambda e: e.y2 != curY, curedges))
            # Add new edges
            while len(queue) != 0 and queue[0][0] == curY:
                (qY, edge) = heapq.heappop(queue)
                if edge != ():
                    curedges.append(edge)
            # Sort cur edges
            curedges = list(sorted(curedges, key=lambda e: e.x))
            for ind in range(0, len(curedges), 2):
                for x in range(curedges[ind].x, curedges[ind + 1].x):
                    # print(x, curY)
                    self.cells[curY][x] = value
                    if value[1] == Cell.ROT:
                        self.total_rot_cells += 1
            curY += 1

    # testing only
    def setBotPos(self, x, y):
        self.bots[0].pos = (x, y)

    # testing only
    def botPos(self):
        return self.bots[0].pos

    def cell(self, x, y):
        return self.cells[y][x]

    def visible(self, p):
        (x1, y1) = self.botPos()
        return self.visibleFrom(x1, y1, p)

    def visibleFrom(self, x1, y1, p):

        #print("visible " + str(p) + " from " + str(self.botPos()))
        def is_obstacle(x, y):
            (_, c) = self.cell(x, y)
            return c == Cell.OBSTACLE
        (x2, y2) = p
        dx = x2 - x1
        dy = y2 - y1
        if (abs(dx) == 1 or dx == 0) and (abs(dy) == 1 or dy == 0):
            # adjacent cell, just check it
            return not is_obstacle(*p)

        # straight line case
        if dx == 0:
            for y in range(min(y1, y2) + 1, max(y1, y2) + 1):
                if is_obstacle(x1, y): return False
            return True
        if dy == 0:
            for x in range(min(x1, x2) + 1, max(x1, x2) + 1):
                if is_obstacle(x, y1): return False
            return True

        # otherwise play lines
        # make dx/dy to be a step in direction to p
        if dx > 0: dx = 1
        else: dx = -1
        if dy > 0: dy = 1
        else: dy = -1

        line = ((x1 + 0.5, y1 + 0.5),
                (x2 + 0.5, y2 + 0.5))

        x = x1
        y = y1

        while x != x2 or y != y2:
            #print("cheking " + str(x) + " " + str(y))
            p1 = (x + dx, y)
            if cross_point(p1, line):
                if is_obstacle(*p1):
                    return False
                x = x + dx
            else:
                p2 = (x, y + dy)
                if cross_point(p2, line):
                    if is_obstacle(*p2):
                        return False
                    y = y + dy
                else:
                    # corner
                    p3 = (x + dx, y + dy)
                    if cross_point(p3, line):
                        if is_obstacle(*p3):
                            return False
                    x = x + dx
                    y = y + dy
        return True

    def paintCells(self, coords):
        for pos in coords:
            self.paintCell(*pos)


    def paintCell(self, x, y):
        num_painted = 0
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self.cell(x, y)
            if cell[1] == Cell.ROT and self.visible((x, y)):
                self.last_painted += 1
                self.total_rot_cells -= 1
                self.cells[y][x] = (cell[0], Cell.CLEAN)
                num_painted = 1
        return num_painted

    def tryPaintCellWith(self, bx, by, x, y, func):
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self.cell(x, y)
            if (cell[1] == Cell.ROT and self.visibleFrom(bx, by, (x, y))):
                self.last_painted = 0
                func(x, y)

    def nextActions(self, actions):
        for (bot, action, bot_ind) in zip(self.bots, actions, range(len(self.bots))):
            if action.validate(self, bot):
                bot.actions.append(action)
                self.last_painted = 0
                action.process(self, bot)
                bot.process(self)
                bot.tickTime()
                if self.save_log:
                    self.add_log(bot_ind, action)
                    bot.last_clean_num = 0
                    bot.last_booster = None
            else:
                #Encoder.encodeToFile("../fail.sol", [bot.actions])
                raise RuntimeError("Invalid command {} at {} step"
                                   .format(action, len(bot.actions)))
            self.tickNum += 1
        self.repaint()

    def nextAction(self, action):
        self.nextActions([action])

    def actions(self):
        return map(lambda x: x.actions, self.bots)

    def repaint(self):
        for bot in self.bots:
            bot.repaint(self)
            self.cells[bot.pos[1]][bot.pos[0]] = (None, Cell.CLEAN)

    def removeBooster(self, pos: tuple):
        self.cells[pos[1]][pos[0]] = (None, Cell.CLEAN)

    def show(self):
        print_cells(self.cells, self.width, self.height)

    def is_all_clean(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.cell(x, y)[1] == Cell.ROT:
                    return False
        return True
        #return self.total_rot_cells <= 0

def print_cells(cells, w, h):
    for y in reversed(range(h)):
        for x in range(w):
            (booster, cell) = cells[y][x]
            ch = '.'
            if cell is Cell.OBSTACLE:
                ch = '#'
            elif cell is Cell.CLEAN:
                ch = 'o'
            print(ch, end='')
        print()

