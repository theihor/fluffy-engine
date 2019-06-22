import unittest
from decode import parse_task

from state import *


class ActionTest(unittest.TestCase):
    state = State.decode(parse_task("../examples/example-01.desc"))

    def testAdjacent(self):
        self.state.setBotPos(3, 2)

        self.assertFalse(self.state.visible((4, 3)))
        self.assertFalse(self.state.visible((4, 2)))
        self.assertTrue(self.state.visible((4, 1)))

    def testStraight(self):
        self.state.setBotPos(3, 2)

        self.assertFalse(self.state.visible((5, 2)))
        self.assertFalse(self.state.visible((6, 2)))
        self.assertFalse(self.state.visible((7, 2)))

        self.assertTrue(self.state.visible((2, 2)))
        self.assertTrue(self.state.visible((1, 2)))

        self.assertTrue(self.state.visible((3, 0)))

    def testLine(self):
        self.state.setBotPos(3, 2)

        self.assertTrue(self.state.visible((4, 0)))
        self.assertTrue(self.state.visible((1, 0)))
        self.assertTrue(self.state.visible((1, 4)))
        self.assertFalse(self.state.visible((6, 0)))
        self.assertFalse(self.state.visible((6, 5)))
        self.assertFalse(self.state.visible((5, 4)))
        self.assertFalse(self.state.visible((7, 7)))

    def testCorner(self):
        self.state.setBotPos(3, 5)

        self.assertFalse(self.state.visible((4, 7)))
        self.assertTrue(self.state.visible((4, 8)))
        self.assertTrue(self.state.visible((4, 9)))
