from enum import Enum, auto
from math import ceil, floor


class Cell(Enum):
    ROT = auto()
    CLEAN = auto()
    OBSTACLE = auto()


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
    def __init__(self, contour, botPos, obstacles, boosters):
        pass

    def createCells(self, contour):
        self.width = max(contour, key=lambda pos: pos[0])
        self.height = max(contour, key=lambda pos: pos[1])
        self.cells = [[(None, Cell.ROT)] * self.width] * self.height
        self.addObstacles(contour)
        for y in range(self.height):
            lastX = self.fillRow(y, 0, 1)
            if lastX < self.width:
                self.fillRow(y, self.width - 1, -1)

    def addObstacles(self, obstacles):
        for (x, y) in obstacles:
            self.cells[y][x] = (None, Cell.OBSTACLE)

    def fillRow(self, y, x, dx):
        row = self.cells[y]
        while row[x][1] != Cell.OBSTACLE and x < self.width:
            row[x] = (None, Cell.OBSTACLE)
            x += dx
        return x

    def setBotPos(self, x, y):
        self.botPos = (x, y)

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







