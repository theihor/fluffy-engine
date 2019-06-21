from enum import Enum, auto


class Cell(Enum):
    ROT = auto()
    CLEAN = auto()
    OBSTACLE = auto()


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
