from enum import Enum, auto
from bot import Bot


class Cell(Enum):
    ROT = auto()
    CLEAN = auto()
    OBSTACLE = auto()


class Booster(Enum):
    WHEEL = auto()
    DRILL = auto()
    MANIPULATOR = auto()


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

    def createCells(self, contour):
        self.width = max(contour, key=lambda pos: pos[0])[0]
        self.height = max(contour, key=lambda pos: pos[1])[1]
        self.cells = [[(None, Cell.ROT)] * self.width] * self.height

        # temporary disabled for test purposes

        # self.addObstacles(contour)
        # for y in range(self.height):
        #     lastX = self.fillRow(y, 0, 1)
        #     if lastX < self.width:
        #         self.fillRow(y, self.width - 1, -1)

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
        self.bot.pos = (x, y)

    def botPos(self):
        return self.bot.pos

    def cell(self, x, y):
        return self.cells[y][x]

    def nextAction(self, action):
        if action.validate(self):
            self.actions += [action]
            action.process(self)
            self.tickTime()

    def tickTime(self):
        if self.wheel_duration > 0:
            self.wheel_duration -= 1
        if self.drill_duration > 0:
            self.drill_duration -= 1
