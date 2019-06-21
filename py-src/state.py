from constants import Booster, Cell
from bot import Bot
from math import ceil, floor
from collections import namedtuple
import heapq


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
    ((x1, y1), (x2, y2)) = line
    (ix, iy) = point

    cross_points = []

    for dx in range(2):
        for dy in range(2):
            line2 = ((ix, iy), (ix + dx, iy + dy))
            p = line_intersection(line, line2)
            if p: cross_points.append(p)
    return cross_points



class State(object):
    def __init__(self, contour, botPos: tuple, obstacles, boosters):
        self.actions = []
        self.bot = Bot(botPos)
        self.wheel_duration = 0
        self.drill_duration = 0
        # map [booster -> amount]
        self.boosters = {
            Booster.DRILL: 0,
            Booster.WHEEL: 0,
            Booster.MANIPULATOR: 0
        }
        self.createCells(contour)
        for obstacle in obstacles:
            if len(obstacle) > 0:
                self.fillContour(obstacle, (None, Cell.OBSTACLE))

    def decode(d):
        return State(d['map'], d['start'], d['obstacles'], d['boosters'])

    def createCells(self, contour):
        self.width = max(contour, key=lambda pos: pos[0])[0]
        self.height = max(contour, key=lambda pos: pos[1])[1]
        self.cells = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append((None, Cell.OBSTACLE))
            self.cells.append(row)
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
            curY += 1

    def setBotPos(self, x, y):
        self.bot.pos = (x, y)

    def botPos(self):
        return self.bot.pos

    def cell(self, x, y):
        return self.cells[y][x]

    def visible(self, p):
        (x1, y1) = self.botPos
        (x2, y2) = p
        if x1 < x2:
            start_x = x1
            end_x = x2
        else:
            start_x = x2
            end_x = x1
        def y(x):
            return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
        x = start_x + 1
        while x < end_x:
            ix = ceil(x)
            y = y(ix)
            iy = floor(y)
            if self.cell(ix, iy)[1] == Cell.OBSTACLE:
                return False



    def paintCell(self, x, y):
        cell = self.cell(x, y)
        if cell[1] != Cell.OBSTACLE:
            # TODO(visibility handling)
            self.cells[y][x] = (cell[0], Cell.CLEAN)

    def nextAction(self, action):
        if action.validate(self):
            self.actions += [action]
            action.process(self)
            self.tickTime()

    def repaint(self):
        self.bot.process(self)

    def tickTime(self):
        self.repaint()
        if self.wheel_duration > 0:
            self.wheel_duration -= 1
        if self.drill_duration > 0:
            self.drill_duration -= 1

    def show(self):
        for y in reversed(range(self.height)):
            for x in range(self.width):
                (booster, cell) = self.cells[y][x]
                ch = '.'
                if cell is Cell.OBSTACLE:
                    ch = '#'
                elif cell is Cell.CLEAN:
                    ch = 'o'
                print(ch, end='')
            print()
