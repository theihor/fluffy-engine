import os
import unittest

from encoder import Encoder
from actions import *


class EncoderTest(unittest.TestCase):
    actions = [
        SimpleAction("W"),
        AttachManipulatorAction(3, 4),
        SimpleAction("W"),
        SimpleAction("Z"),
        AttachManipulatorAction(1, 2),
        SimpleAction("Q")
    ]
    filename = "prob-001.sol"
    task_no = 1

    def testEncodeFileExists(self):
        Encoder.encode(self.task_no, self.actions)
        self.addCleanup(lambda: os.remove(self.filename))

        self.assertTrue(os.path.isfile(self.filename))

    def testEncodeValue(self):
        Encoder.encode(self.task_no, self.actions)
        self.addCleanup(lambda: os.remove(self.filename))
        file = open(self.filename)
        result = file.readline()
        file.close()

        self.assertEqual("WB(3,4)WZB(1,2)Q", result)
