import unittest

from state import State
from pathfinder import bfsFind


class BFSTest(unittest.TestCase):
    contour = [(0, 0), (0, 5), (5, 5), (5, 0)]
    obst1 = [(2, 2), (3, 2), (3, 4), (2, 4)]

    #    .....
    #    ..#..
    #    ..#..
    #    .....
    #    .....

    def test1(self):
        state = State(self.contour, (0, 0), [self.obst1], [])
        path = bfsFind(state, (1, 1), lambda x, y: x == 2 and y == 4)
        self.assertEqual([(1, 1), (1, 2), (1, 3), (1, 4), (2, 4)], path)
