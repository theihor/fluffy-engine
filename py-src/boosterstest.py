import unittest

from actions import MoveUp
from constants import Booster, Cell
from state import State


class BoosterTest(unittest.TestCase):
    contour = [
        (0, 0),
        (0, 10),
        (10, 10),
        (10, 0)
    ]

    def testCreate(self):
        state = State(self.contour, (1, 1), [], [(Booster.WHEEL, (2, 2))])

        self.assertEqual((Booster.WHEEL, Cell.CLEAN), state.cell(2, 2))

    def testCollect(self):
        state = State(self.contour, (1, 1), [], [(Booster.WHEEL, (1, 2))])
        self.assertEqual(0, state.boosters[Booster.WHEEL])
        state.nextAction(MoveUp())

        self.assertEqual((None, Cell.CLEAN), state.cell(1, 2))
        self.assertEqual(1, state.boosters[Booster.WHEEL])
