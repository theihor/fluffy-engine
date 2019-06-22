import unittest

from actions import *
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

    def testAttachWheels(self):
        state = State(self.contour, (1, 1), [], [(Booster.WHEEL, (1, 2))])
        state.nextAction(MoveUp())
        state.nextAction(AttachWheels())

        self.assertEqual(WHEELS_DURATION, state.bots[0].wheel_duration)
        self.assertEqual(0, state.boosters[Booster.WHEEL])

    def testAttachDrill(self):
        state = State(self.contour, (1, 1), [], [(Booster.DRILL, (1, 2))])
        state.nextAction(MoveUp())
        state.nextAction(AttachDrill())

        self.assertEqual(DRILL_DURATION, state.bots[0].drill_duration)
        self.assertEqual(0, state.boosters[Booster.DRILL])

    def testTimings(self):
        state = State(self.contour, (1, 1), [], [(Booster.DRILL, (1, 2))])
        bot = state.bots[0]
        bot.wheel_duration = 20
        state.nextAction(MoveUp())
        state.nextAction(AttachDrill())

        self.assertEqual(DRILL_DURATION, bot.drill_duration)
        self.assertEqual(0, state.boosters[Booster.DRILL])
        self.assertEqual(18, bot.wheel_duration)
