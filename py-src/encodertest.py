import os
import unittest

from encoder import Encoder
from actions import *


class EncoderTest(unittest.TestCase):
    contour = [
        (0, 0),
        (0, 10),
        (10, 10),
        (10, 0)
    ]
    obstacles = [
        [(2, 1), (2, 2), (3, 2), (3, 1)]
    ]
    state = State(contour, (1, 1), [], [])
    state.boosters[Booster.MANIPULATOR] = 2
    state.nextAction(MoveUp())
    state.nextAction(AttachManipulator((2, 1)))
    state.nextAction(MoveUp())
    state.nextAction(DoNothing())
    state.nextAction(AttachManipulator((3, 1)))
    state.nextAction(TurnLeft())
    filename = "prob-001.sol"
    task_no = 1

    def testEncodeFileExists(self):
        Encoder.encodeToFile(self.filename, self.state)
        new_filename = self.filename + "." + str(self.state.tickNum)
        self.addCleanup(lambda: os.remove(new_filename))

        self.assertTrue(os.path.isfile(new_filename))

    def testEncodeValue(self):
        Encoder.encodeToFile(self.filename, self.state)
        new_filename = self.filename + "." + str(self.state.tickNum)
        self.addCleanup(lambda: os.remove(new_filename))
        file = open(new_filename)
        result = file.readline()
        file.close()

        self.assertEqual("WB(2,1)WZB(3,1)Q", result)
