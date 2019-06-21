import unittest

from actions import *


def getCellType(state, x, y):
    return state.cell(x, y)[1]


class PaintTest(unittest.TestCase):
    contour = [
        (0, 0),
        (0, 10),
        (10, 10),
        (10, 0)
    ]

    def testDoNothing(self):
        state = State(self.contour, (1, 1), [], [])
        self.assertEqual(Cell.ROT, getCellType(state, 1, 1))

        state.nextAction(DoNothing())

        self.assertEqual(Cell.CLEAN, getCellType(state, 1, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 2))

    def testDoMove(self):
        state = State(self.contour, (1, 1), [], [])
        self.assertEqual(Cell.ROT, getCellType(state, 1, 1))

        state.nextAction(MoveRight())

        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 2))

    def testDoMoveWheels(self):
        state = State(self.contour, (1, 1), [], [])
        state.wheel_duration = 1
        self.assertEqual(Cell.ROT, getCellType(state, 1, 1))

        state.nextAction(MoveRight())

        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 2))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 2))

    def testAttach(self):
        state = State(self.contour, (1, 1), [], [])
        state.boosters[Booster.MANIPULATOR] = 1
        self.assertEqual(Cell.ROT, getCellType(state, 1, 3))

        state.nextAction(AttachManipulator((1, 2)))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 3))
