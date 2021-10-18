import unittest
from builtins import int
import numpy as np

from bot import RummyModel,RummySolver, RummyController, RummyView, runRummyGame, k, m


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

    # Solver Tests
    def test_make_runs(self):
        self.model.restart()
        self.model.addRun(['A1','A2', 'A3'])
        self.model.getCurrentPlayer().append('A4')
        solver = RummySolver(self.model)
        runs, tiles, scores = solver.makeRuns(np.zeros(shape=(k,m)),self.model.getTotalTilePool(),4)
        self.assertEqual(scores, 10)




if __name__ == '__main__':
    unittest.main()
