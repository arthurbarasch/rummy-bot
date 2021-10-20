import unittest
from builtins import int
import numpy as np

from bot import RummyModel,RummySolver, RummyController, RummyView, runRummyGame, k,K,m,n,N,NUM_PLAYERS


class RummyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.model = runRummyGame(solve=False)

    def tearDown(self) -> None:
        super().tearDown()

    # Model Tests
    def test_draw_tile(self):
        before = self.model.drawPile[:]
        self.model.drawTile(0,1)
        after = self.model.drawPile[:]
        for item in after:
            before.remove(item)
        test = len(before)==1 and before[0] in self.model.players[0]
        self.assertTrue(test)

    def test_start(self):
        self.model.start()
        self.assertEqual(n, len(N))
        for i in self.model.players:
            self.assertEqual(n,len(self.model.players[i]))

    def test_rummy_params(self):
        self.assertEqual(n, 13)
        self.assertEqual(k, 4)
        self.assertEqual(m, 2)

    # Solver Tests
    def test_make_runs(self):
        self.model.restart()
        self.model.addRun([(1,1),(1,2), (1,3)])
        self.model.getCurrentPlayer().append((1,4))
        solver = RummySolver(self.model)
        self.assertEqual(10, solver.maxScore())




if __name__ == '__main__':
    unittest.main()
