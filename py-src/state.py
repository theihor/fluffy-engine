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
    """Check whether the cell on point is crossed by line"""
    ((x1, y1), (x2, y2)) = line
    (ix, iy) = point

    cross_points = []

    for dx in range(2):
        for dy in range(2):
            line2 = ((ix, iy), (ix + dx, iy + dy))
            p = line_intersection(line, line2)
            if p: cross_points.append(p)

    if cross_points and cross_points[0] != cross_points[1]:
        #print(str(point) + " crossed! " + str(cross_points))
        return True
    else:
        #print(str(point) + " not crossed!")
        return False


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
            curY += 1

    def setBotPos(self, x, y):
        self.bot.pos = (x, y)

    def botPos(self):
        return self.bot.pos

    def cell(self, x, y):
        return self.cells[y][x]

    def visible(self, p):
        def is_obstacle(x, y):
            (_, c) = self.cell(x, y)
            return c == Cell.OBSTACLE
        (x1, y1) = self.botPos()
        (x2, y2) = p
        dx = x2 - x1
        dy = y2 - y1
        if (abs(dx) == 1 or dx == 0) and (abs(dy) == 1 or dy == 0):
            # adjacent cell, just check it
            return not is_obstacle(*p)

        # straight line case
        if dx == 0:
            for y in range(y1 + 1, y2 + 1):
                if is_obstacle(x1, y): return False
            return True
        if dy == 0:
            for x in range(x1 + 1, x2 + 1):
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

        while x != x2 and y != y2:
         #   print("cheking " + str(x) + " " + str(y))
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
                else: raise Exception("This should never happen")
        return True


    def paintCell(self, x, y):
        if (x >= 0 and x < self.width and y >= 0 and y < self.height):
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
