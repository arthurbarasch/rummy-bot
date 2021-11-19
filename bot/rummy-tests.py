import unittest
from builtins import int
import numpy as np

from bot import RummyModel, RummySolver, RummyController, RummyView, runRummyGame, k, K, m, n, N, NUM_PLAYERS


class RummyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.model = runRummyGame(solve=False)

    def tearDown(self) -> None:
        super().tearDown()

    # Model Tests
    def test_draw_tile(self):
        before = self.model.drawPile[:]
        self.model.drawTile(0, 1)
        after = self.model.drawPile[:]
        for item in after:
            before.remove(item)
        test = len(before) == 1 and before[0] in self.model.players[0]
        self.assertTrue(test)

    def test_table_constraint(self):
        self.model.restart()
        self.model.addGroup([(1, 13), (2, 13), (3, 13)])
        a = RummyModel(self.model)
        self.assertTrue(a.checkTableConstraint(self.model))
        a.addGroup([(1, 12), (2, 12), (3, 12)])
        self.assertTrue(a.checkTableConstraint(self.model))
        a.restart()
        self.assertFalse(a.checkTableConstraint(self.model))

        #Filtered tests
        self.model.restart()
        self.model.addRun([(1, 11), (1, 12), (1, 13)])
        a.restart()
        a.addRun([(1,10),(1, 11), (1, 12)])
        self.assertTrue(a.checkTableConstraint(self.model,filter_value=11))
        self.assertTrue(a.checkTableConstraint(self.model,filter_value=12))
        self.assertFalse(a.checkTableConstraint(self.model))

    def test_total_tile_pool(self):
        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.getCurrentPlayer().append((1, 5))
        temp = self.model.getTotalTilePool(filter_value=10)
        self.assertEquals([(1, 10), (2, 10), (3, 10)], temp)
        temp = self.model.getTotalTilePool()
        self.assertEquals([(1, 5), (1, 10), (2, 10), (3, 10)], temp)

    def test_restart(self):
        self.model.restart()
        self.assertEquals(len(self.model.board["runs"]), 0)
        self.assertEquals(len(self.model.board["groups"]), 0)
        self.assertEquals(len(self.model.drawPile), n*k*m)
        for p in self.model.players:
            self.assertEquals(len(p),0, "Player must have 0 tiles after 'restart()'")

    def test_start(self):
        self.model.start()
        self.assertEqual(n, len(N))
        for player in self.model.players:
            self.assertEqual(14, len(player))

    def test_rummy_params(self):
        self.assertEqual(n, 13)
        self.assertEqual(k, 4)
        self.assertEqual(m, 2)

    # Solver Tests
    def test_make_runs(self):
        self.model.restart()
        self.model.addRun([(1, 1), (1, 2), (1, 3)])
        self.model.getCurrentPlayer().append((1, 4))
        solver = RummySolver(self.model)
        self.assertEqual(10, solver._maxScore())

        self.model.restart()
        self.model.addRun([(2, 4), (2, 5), (2, 6)])
        self.model.getCurrentPlayer().append((3, 7))
        solver = RummySolver(self.model)
        self.assertEqual(15, solver._maxScore())

    def test_make_groups(self):
        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.getCurrentPlayer().append((4, 10))
        solver = RummySolver(self.model)
        self.assertEqual(40, solver._maxScore())

    def test_make_groups_and_runs(self):
        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.addGroup([(2, 3), (3, 3), (4, 3)])
        self.model.addRun([(1, 1), (1, 2), (1, 3)])
        solver = RummySolver(self.model)
        self.assertEqual(45, solver._maxScore())

    def test_add_random_hand(self):
        self.model.restart()
        score = self.model.addRandomHand()
        solver = RummySolver(self.model)
        self.assertEqual(score, solver._maxScore())

    def test_13s(self):
        self.model.restart()
        self.model.addGroup([(1, 13), (2, 13), (3, 13)])
        solver = RummySolver(self.model)
        self.assertEqual(39, solver._maxScore())


    # def test_make_runs_all_tiles(self):
    #     self.model.restart()
    #     self.model.giveAllTilesToCurrentPlayer()
    #     solver = RummySolver(self.model)
    #     self.assertEqual(728, solver._maxScore())

if __name__ == '__main__':
    unittest.main()
