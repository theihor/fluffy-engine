import unittest

from actions import *


class ActionTest(unittest.TestCase):
    contour = [
        (0, 0),
        (0, 10),
        (10, 10),
        (10, 0)
    ]

    def testValidateMovesCorner1(self):
        state = State(self.contour, (0, 0), None, None)

        self.assertFalse(MoveDown().validate(state))
        self.assertFalse(MoveLeft().validate(state))
        self.assertTrue(MoveUp().validate(state))
        self.assertTrue(MoveRight().validate(state))

    def testValidateMovesCorner2(self):
        state = State(self.contour, (9, 9), None, None)

        self.assertTrue(MoveDown().validate(state))
        self.assertTrue(MoveLeft().validate(state))
        self.assertFalse(MoveUp().validate(state))
        self.assertFalse(MoveRight().validate(state))

    def testValidateMovesCenter(self):
        state = State(self.contour, (5, 5), None, None)

        self.assertTrue(MoveDown().validate(state))
        self.assertTrue(MoveLeft().validate(state))
        self.assertTrue(MoveUp().validate(state))
        self.assertTrue(MoveRight().validate(state))

    def testValidateWheels(self):
        state = State(self.contour, (5, 5), None, None)
        state.wheel_duration = 1

        self.assertTrue(MoveDown().validate(state))
        self.assertTrue(MoveLeft().validate(state))
        self.assertTrue(MoveUp().validate(state))
        self.assertTrue(MoveRight().validate(state))

    def testMovesCorner1(self):
        state = State(self.contour, (0, 0), None, None)
        state.nextAction(MoveUp())
        self.assertEqual((0, 1), state.botPos())
        state.nextAction(MoveRight())
        self.assertEqual((1, 1), state.botPos())
        state.nextAction(MoveDown())
        self.assertEqual((1, 0), state.botPos())
        state.nextAction(MoveLeft())
        self.assertEqual((0, 0), state.botPos())

    def testWheelsCenter(self):
        state = State(self.contour, (5, 5), None, None)
        state.wheel_duration = 4

        state.nextAction(MoveUp())
        self.assertEqual((5, 7), state.botPos())
        self.assertEqual(3, state.wheel_duration)
        state.nextAction(MoveLeft())
        self.assertEqual((3, 7), state.botPos())
        state.nextAction(MoveDown())
        self.assertEqual((3, 5), state.botPos())
        state.nextAction(MoveRight())
        self.assertEqual((5, 5), state.botPos())
        self.assertEqual(0, state.wheel_duration)
        state.nextAction(MoveRight())
        self.assertEqual((6, 5), state.botPos())
