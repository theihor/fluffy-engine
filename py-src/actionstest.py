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
        state = State(self.contour, (0, 0), [], [])

        self.assertFalse(MoveDown().validate(state, state.bots[0]))
        self.assertFalse(MoveLeft().validate(state, state.bots[0]))
        self.assertTrue(MoveUp().validate(state, state.bots[0]))
        self.assertTrue(MoveRight().validate(state, state.bots[0]))

    def testValidateMovesCorner2(self):
        state = State(self.contour, (9, 9), [], [])

        self.assertTrue(MoveDown().validate(state, state.bots[0]))
        self.assertTrue(MoveLeft().validate(state, state.bots[0]))
        self.assertFalse(MoveUp().validate(state, state.bots[0]))
        self.assertFalse(MoveRight().validate(state, state.bots[0]))

    def testValidateMovesCenter(self):
        state = State(self.contour, (5, 5), [], [])

        self.assertTrue(MoveDown().validate(state, state.bots[0]))
        self.assertTrue(MoveLeft().validate(state, state.bots[0]))
        self.assertTrue(MoveUp().validate(state, state.bots[0]))
        self.assertTrue(MoveRight().validate(state, state.bots[0]))

    def testValidateWheels(self):
        state = State(self.contour, (5, 5), [], [])
        state.wheel_duration = 1

        self.assertTrue(MoveDown().validate(state, state.bots[0]))
        self.assertTrue(MoveLeft().validate(state, state.bots[0]))
        self.assertTrue(MoveUp().validate(state, state.bots[0]))
        self.assertTrue(MoveRight().validate(state, state.bots[0]))

    def testMovesCorner1(self):
        state = State(self.contour, (0, 0), [], [])
        state.nextAction(MoveUp())
        self.assertEqual((0, 1), state.botPos())
        state.nextAction(MoveRight())
        self.assertEqual((1, 1), state.botPos())
        state.nextAction(MoveDown())
        self.assertEqual((1, 0), state.botPos())
        state.nextAction(MoveLeft())
        self.assertEqual((0, 0), state.botPos())

    def testWheelsCenter(self):
        state = State(self.contour, (5, 5), [], [])
        state.bots[0].wheel_duration = 4

        state.nextAction(MoveUp())
        self.assertEqual((5, 7), state.botPos())
        self.assertEqual(3, state.bots[0].wheel_duration)
        state.nextAction(MoveLeft())
        self.assertEqual((3, 7), state.botPos())
        state.nextAction(MoveDown())
        self.assertEqual((3, 5), state.botPos())
        state.nextAction(MoveRight())
        self.assertEqual((5, 5), state.botPos())
        self.assertEqual(0, state.bots[0].wheel_duration)
        state.nextAction(MoveRight())
        self.assertEqual((6, 5), state.botPos())

    def testWheelsCorner(self):
        state = State(self.contour, (1, 1), [], [])
        state.bots[0].wheel_duration = 4

        state.nextAction(MoveLeft())
        self.assertEqual((0, 1), state.botPos())
        state.nextAction(MoveDown())
        self.assertEqual((0, 0), state.botPos())
        state.nextAction(MoveDown())
        self.assertEqual((0, 0), state.botPos())
        self.assertEqual(2, state.bots[0].wheel_duration)

    # https://icfpcontest2019.github.io/download/specification-v1.pdf
    # 2.2.1  Extension of the Manipulator
    def testValidateAttach(self):
        state = State(self.contour, (1, 1), [], [])
        state.boosters[Booster.MANIPULATOR] = 1

        self.assertTrue(AttachManipulator((1, 2)).validate(state, state.bots[0]))
        self.assertTrue(AttachManipulator((-1, 0)).validate(state, state.bots[0]))
        self.assertTrue(AttachManipulator((2, 1)).validate(state, state.bots[0]))
        self.assertFalse(AttachManipulator((3, 1)).validate(state, state.bots[0]))
        self.assertFalse(AttachManipulator((0, 0)).validate(state, state.bots[0]))
