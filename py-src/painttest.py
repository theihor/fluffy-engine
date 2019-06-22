import unittest

from actions import *
from decode import parse_task


def getCellType(state, x, y):
    return state.cell(x, y)[1]


# TODO(test via map equality, not single cell checks)
class PaintTest(unittest.TestCase):
    contour = [
        (0, 0),
        (0, 10),
        (10, 10),
        (10, 0)
    ]
    obstacles = [
        [(2, 1), (2, 2), (3, 2), (3, 1)]
    ]

    def testDoNothing(self):
        state = State(self.contour, (1, 1), [], [])

        state.nextAction(DoNothing())

        self.assertEqual(Cell.CLEAN, getCellType(state, 1, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 2))

    def testDoMove(self):
        state = State(self.contour, (1, 1), [], [])

        state.nextAction(MoveRight())

        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 3, 2))

    def testDoMoveWheels(self):
        state = State(self.contour, (1, 1), [], [])
        state.wheel_duration = 1

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

    def testTurnRight(self):
        state = State(self.contour, (5, 5), [], [])

        state.nextAction(TurnRight())

        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 5))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 4))
        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 4))
        self.assertEqual(Cell.CLEAN, getCellType(state, 6, 4))

    def testTurnRight2(self):
        state = State(self.contour, (5, 5), [], [])

        state.nextAction(TurnRight())
        state.nextAction(TurnRight())

        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 5))
        # first action
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 4))
        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 4))
        self.assertEqual(Cell.CLEAN, getCellType(state, 6, 4))
        # second action
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 4))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 5))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 6))

    def testTurnLeft(self):
        state = State(self.contour, (5, 5), [], [])

        state.nextAction(TurnLeft())

        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 5))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 6))
        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 6))
        self.assertEqual(Cell.CLEAN, getCellType(state, 6, 6))

    def testTurnLeft2(self):
        state = State(self.contour, (5, 5), [], [])

        state.nextAction(TurnLeft())
        state.nextAction(TurnLeft())

        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 5))
        # first action
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 6))
        self.assertEqual(Cell.CLEAN, getCellType(state, 5, 6))
        self.assertEqual(Cell.CLEAN, getCellType(state, 6, 6))
        # second action
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 4))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 5))
        self.assertEqual(Cell.CLEAN, getCellType(state, 4, 6))

    def testInitial(self):
        state = State(self.contour, (1, 1), [], [])

        self.assertEqual(Cell.CLEAN, getCellType(state, 1, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 0))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 1))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 2))

    def testVisibility(self):
        state = State(self.contour, (1, 0), [], [])
        state.boosters[Booster.MANIPULATOR] = 1
        state.nextAction(AttachManipulator((1, 2)))

        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 2))

        state = State(self.contour, (1, 0), self.obstacles, [])
        state.boosters[Booster.MANIPULATOR] = 2
        state.nextAction(AttachManipulator((1, 2)))
        state.nextAction(AttachManipulator((1, 3)))

        self.assertEqual(Cell.ROT, getCellType(state, 2, 2))
        self.assertEqual(Cell.CLEAN, getCellType(state, 2, 3))

