import unittest

from state import State
from pathfinder import bfsFind, bfsFindExt


class BFSTest(unittest.TestCase):
    contour = [(0, 0), (0, 5), (5, 5), (5, 0)]
    obst1 = [(2, 2), (3, 2), (3, 4), (2, 4)]

    #    01234
    #    ..... 4
    #    ..#.. 3
    #    ..#.. 2
    #    ..... 1
    #    ..... 0

    def test1(self):
        state = State(self.contour, (0, 0), [self.obst1], [])
        path = bfsFind(state, (1, 1), lambda l, x, y: x == 2 and y == 4)
        self.assertEqual([(1, 1), (1, 2), (1, 3), (1, 4), (2, 4)], path)

    def test2(self):
        state = State(self.contour, (0, 0), [self.obst1], [])

        path = bfsFindExt(state, (1, 1), lambda l, x, y: x == 2 and y == 4)
        self.assertEqual([(1, 1), (1, 2), (1, 3), (1, 4), (2, 4)], path)
        
        path = bfsFindExt(state, (1, 3), lambda l, x, y: x == 3 and y == 3, wheels = 1, drill = 1)
        self.assertEqual([(1, 3), (3, 3)], path)

        path = bfsFindExt(state, (1, 3), lambda l, x, y: x == 3 and y == 3, wheels = 1, drill = 0)
        self.assertEqual([(1, 3), (1, 4), (2, 4), (3, 4), (3, 3)], path)


