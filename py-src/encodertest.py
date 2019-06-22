import os
import unittest

from encoder import Encoder
from actions import *


class EncoderTest(unittest.TestCase):
    actions = [
        MoveUp(),
        AttachManipulator((3, 4)),
        MoveUp(),
        DoNothing(),
        AttachManipulator((1, 2)),
        TurnLeft()
    ]
    filename = "prob-001.sol"
    task_no = 1

    def testEncodeFileExists(self):
        Encoder.encodeToFile(self.filename, self.actions)
        self.addCleanup(lambda: os.remove(self.filename))

        self.assertTrue(os.path.isfile(self.filename))

    def testEncodeValue(self):
        Encoder.encodeToFile(self.filename, self.actions)
        self.addCleanup(lambda: os.remove(self.filename))
        file = open(self.filename)
        result = file.readline()
        file.close()

        self.assertEqual("WB(3,4)WZB(1,2)Q", result)
