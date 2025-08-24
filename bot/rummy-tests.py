import unittest

import multiset

from bot import runRummyGame, N, NUM_STARTING_TILES
from util import getChildren, MS
from view import *


class RummyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = runRummyGame(solve=False)
        self.model = self.controller.model

    def tearDown(self) -> None:
        super().tearDown()

    def test_runs_from_indexes(self):
        self.model.restart()
        solver = RummySolver(self.model)

        a = [0, 9, 3, 4]
        runs = solver.getRunsFromIndexes(a)
        print(runs)

    def test_scores(self):
        self.model.restart()
        self.model.addGroup([(1, 5), (2, 5), (3, 5)])
        solver = RummySolver(self.model)
        self.assertEqual(solver.maxScore(), 15)

        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 10), (3, 10), (4, 10),
                                              (1, 2), (1, 3), (1, 4)])
        solver = RummySolver(self.model)
        self.assertEqual(39, solver.maxScore())

        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 3), (1, 6)])
        solver = RummySolver(self.model)
        self.assertEqual(24, solver.maxScore())

    # Model Tests
    def test_draw_tile(self):
        self.model.restart()
        before = self.model.drawPile[:]
        self.model.drawTile(0, 1)
        after = self.model.drawPile[:]
        for item in after:
            before.remove(item)
        test = len(before) == 1 and before[0] in self.model.getCurrentPlayer()
        self.assertTrue(test)

    def test_add_run(self):
        self.model.restart()
        ret = self.model.addRun([(1, 1), (1, 2), (1, 3)])
        self.assertTrue(ret)
        self.assertEqual(1, len(self.model.board['runs']))

        ret = self.model.addRun([(1, 1), (1, 2), (1, 3)])
        ret = ret and self.model.addToRun((1, 4), 1)
        self.assertTrue(ret)
        self.assertEqual(2, len(self.model.board['runs']))
        self.assertEqual(7, len(self.model.getBoardTilePool()))

    def test_table_constraint(self):
        self.model.restart()
        self.model.addRun([(1, 11), (1, 12), (1, 13)])
        a = RummyModel(self.model)
        runs = np.zeros(shape=(k, m))

        self.assertTrue(a.checkTableConstraint(self.model, runs))
        a.addGroup([(1, 10), (2, 10), (3, 10)])
        self.assertTrue(a.checkTableConstraint(self.model, runs))
        a.board['runs'] = [[(1, 11), (1, 12)]]
        self.assertFalse(a.checkTableConstraint(self.model, runs))

        # Filtered tests
        self.model.restart()
        a.restart()
        self.model.addRun([(1, 11), (1, 12), (1, 13)])
        a.addRun([(1, 10), (1, 11), (1, 12)])
        self.assertTrue(a.checkTableConstraint(self.model, runs, filter_value=11))
        self.assertTrue(a.checkTableConstraint(self.model, runs, filter_value=12))
        self.assertFalse(a.checkTableConstraint(self.model, runs))
        self.assertFalse(a.checkTableConstraint(self.model, runs, filter_value=13))

    def test_total_tile_pool(self):
        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.getCurrentPlayer().append((1, 5))
        temp = self.model.getTotalTilePool(filter_value=10)
        self.assertEqual([(1, 10), (2, 10), (3, 10)], temp)
        temp = self.model.getTotalTilePool()
        self.assertEqual([(1, 5), (1, 10), (2, 10), (3, 10)], temp)

        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.addRun([(1, 11), (1, 12), (1, 13)])
        self.model.getCurrentPlayer().extend([(1, 1), (1, 2)])
        temp = self.model.getTotalTilePool()
        self.assertEqual(set([(1, 10), (2, 10), (3, 10), (1, 11), (1, 12), (1, 13), (1, 1), (1, 2)]), set(temp))

    def test_restart(self):
        self.model.restart()
        self.assertEqual(len(self.model.board["runs"]), 0)
        self.assertEqual(len(self.model.board["groups"]), 0)
        self.assertEqual(len(self.model.drawPile), n * k * m)
        for p in self.model.players:
            self.assertEqual(len(p), 0, "Player must have 0 tiles after 'restart()'")

    def test_start(self):
        self.model.restart()
        self.model.start()
        self.assertEqual(n, len(N))
        for player in self.model.players:
            self.assertEqual(NUM_STARTING_TILES, len(player))

    def test_rummy_params(self):
        self.assertEqual(n, 13)
        self.assertEqual(k, 4)
        self.assertEqual(m, 2)

    def test_validate_board(self):
        self.model.restart()
        self.model.addGroup([(1, 1), (2, 1), (3, 1)])
        self.model.initNewRun((1, 13))
        self.assertEqual(len(self.model.board["runs"][0]), 1)
        self.assertEqual(self.model.validateBoard(), False)
        self.assertEqual(self.model.getBoardScore(), 3)

        self.model.restart()
        self.model.initNewRun((1, 1))
        self.model.addToRun((1, 2), 0)
        self.model.addToRun((1, 3), 0)
        self.model.initNewRun((2, 1))
        self.assertEqual(self.model.board["runs"][0], [(1, 1), (1, 2), (1, 3)])
        self.assertEqual(self.model.validateBoard(filter_suit=2), False)
        self.assertEqual(self.model.getBoardScore(), 6)

    def test_get_children(self):
        children = getChildren(multiset.Multiset([0, 3]), 0)
        self.assertIn(MS([0, 0]), children)
        self.assertEqual(len(children), 1)

        children = getChildren(multiset.Multiset([0, 1]), 1)
        self.assertIn(MS([0, 2]), children)
        self.assertEqual(len(children), 1)

        children = getChildren(multiset.Multiset([3, 3]), 2)
        self.assertIn(MS([0, 0]), children)
        self.assertIn(MS([0, 3]), children)
        self.assertIn(MS([3, 3]), children)
        self.assertEqual(len(children), 3)
        return

    # Solver Tests
    def test_total_group_size(self):
        self.model.restart()
        self.model.addRun([(1, 10), (1, 11), (1, 12)])
        solver = RummySolver(self.model)
        hand = [(1, 1), (1, 1), (2, 1), (2, 1), (3, 1)]
        groupSize = solver.totalGroupSize(hand)
        self.assertEqual(3, groupSize)

        self.model.restart()
        self.model.addRun([(1, 1), (1, 2), (1, 3)])
        solver = RummySolver(self.model)
        hand = [(1, 1), (1, 1), (2, 1), (2, 1), (3, 1), (3, 1), (4, 1)]
        groupSize = solver.totalGroupSize(hand)
        self.assertEqual(7, groupSize)

        for _ in range(40):
            self.model.restart()
            score = self.model.addRandomHand(group=True)
            if score == 0:
                continue
            hand = self.model.getBoardTilePool()
            print('hand: {}'.format(hand))
            groupSize = solver.totalGroupSize(hand)
            self.assertGreater(groupSize, 0)

        groupSize = solver.totalGroupSize([(1, 1), (2, 1), (3, 1), (3, 1)])
        self.assertEqual(3, groupSize)

        groupSize = solver.totalGroupSize([(1, 1), (1, 1), (4, 1)])
        self.assertEqual(0, groupSize)

    def test_make_new_run(self):
        solver = RummySolver(self.model)
        new_runs, new_hands, run_scores = solver.makeRuns([(1, 1), (1, 1)],
                                                          [MS([0, 0]), MS([0, 0]), MS([0, 0]), MS([0, 0])], 1)

        self.assertIn([MS([0, 0]), MS([0, 0]), MS([0, 0]), MS([0, 0])], new_runs)
        self.assertIn([MS([0, 1]), MS([0, 0]), MS([0, 0]), MS([0, 0])], new_runs)
        self.assertIn([MS([1, 1]), MS([0, 0]), MS([0, 0]), MS([0, 0])], new_runs)
        self.assertEqual(len(new_runs), 3)
        print(new_hands)
        print(run_scores)

    def test_make_runs_1(self):
        self.model.restart()
        self.model.addRun([(2, 4), (2, 5), (2, 6)])
        self.model.getCurrentPlayer().extend([(3, 7)])
        solver = RummySolver(self.model)
        runs = [MS([0, 0]), MS([0, 0]), MS([0, 0]), MS([0, 0])]
        solution = RummyModel()

        hand = self.model.getTotalTilePool(filter_value=4)
        self.assertEqual(len(hand), 1)
        new_runs, new_hands, run_scores = solver.makeRuns(hand, runs, 4)
        self.assertEqual(len(new_runs), 2)
        self.assertEqual(run_scores, [0, 0])
        self.assertEqual(new_hands, [[], [(2, 4)]])

    def test_make_runs_2(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(2, 5), (2, 6), (2, 7), (2, 8), (2, 9)])
        solver = RummySolver(self.model)
        self.assertEqual(35, solver.maxScore())
        self.assertEqual(len(solver.solution.board["runs"]), 1)

    def test_make_runs_3(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 3), (1, 6)])
        solver = RummySolver(self.model)
        self.assertEqual(24, solver.maxScore())
        print(solver.solution)
        self.assertEqual(len(solver.solution.board["runs"]), 2)
        self.assertEqual(solver.solution.board["runs"][0], [(1, 1), (1, 2), (1, 3)])
        self.assertEqual(solver.solution.board["runs"][1], [(1, 3), (1, 4), (1, 5), (1, 6)])

    def test_make_runs_4(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 3)])
        solver = RummySolver(self.model)
        print(solver.solution)
        self.assertEqual(24, solver.maxScore())
        self.assertEqual(len(solver.solution.board["runs"]), 2)

    def test_make_groups(self):

        self.model.restart()
        self.model.addGroup([(1, 8), (2, 8), (3, 8)])
        self.model.getCurrentPlayer().extend([(4, 8), (1, 8), (2, 8)])
        solver = RummySolver(self.model)
        self.assertEqual(48, solver.maxScore())

        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        solver = RummySolver(self.model)
        self.assertEqual(30, solver.maxScore())

        # logging.warning(solver.solution.getCurrentPlayer())
        self.assertEqual(len(solver.solution.board['groups']), 1)
        self.assertEqual(set(solver.solution.board['groups'][0]), {(1, 10), (2, 10), (3, 10)})

    def test_make_groups_and_runs_2(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 11), (3, 11), (4, 11),
                                              (1, 10), (1, 11), (1, 12)])
        solver = RummySolver(self.model)
        self.assertEqual(66, solver.maxScore())
        self.assertEqual(solver.solution.board["runs"][0], [(1, 10), (1, 11), (1, 12)])
        self.assertEqual(set(solver.solution.board["groups"][0]), {(1, 11), (3, 11), (4, 11)})

    def test_make_groups_and_runs(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 3), (3, 3), (4, 3),
                                              (1, 1), (1, 2), (1, 3)])
        solver = RummySolver(self.model)
        self.assertEqual(15, solver.maxScore())
        self.assertEqual(solver.solution.board["runs"][0], [(1, 1), (1, 2), (1, 3)])
        self.assertEqual(set(solver.solution.board["groups"][0]), {(1, 3), (3, 3), (4, 3)})

        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 10), (3, 10), (4, 10),
                                              (1, 2), (1, 3), (1, 4)])
        solver = RummySolver(self.model)
        self.assertEqual(39, solver.maxScore())
        self.assertEqual(solver.solution.board["runs"][0], [(1, 2), (1, 3), (1, 4)])
        self.assertEqual(set(solver.solution.board["groups"][0]), {(1, 10), (3, 10), (4, 10)})

    def test_solve_random_hands(self):
        self.model.restart()
        score = 0
        for i in range(5):
            score += self.model.addRandomHand()
        solver = RummySolver(self.model)
        self.assertEqual(score, solver.maxScore())

        fails = []
        for i in range(30):
            self.model.restart()
            score = self.model.addRandomHand()
            self.assertEqual(score, self.model.getBoardScore())
            solver = RummySolver(self.model)
            if score != solver.maxScore():
                fails.append(str(self.model))

        self.assertEqual(fails, [])

    def test_13s(self):
        self.model.restart()
        self.model.addGroup([(1, 13), (2, 13), (3, 13)])
        solver = RummySolver(self.model)
        self.assertEqual(39, solver.maxScore())

        self.model.restart()
        self.model.initNewRun((1, 13))
        solver = RummySolver(self.model)
        self.assertLessEqual(solver.maxScore(), 0)

    def test_plot_graphs(self):
        plot_times_graph()

    # On a cloud compute or build pipeline, the algorithm is probably robust enough to handle a test
    # including all tiles in the game (if solution tracking is disabled).
    # However, my computer cannot handle it so I leave it disabled to be able to run local tests

    # def test_make_runs_all_tiles(self):
    #     self.model.restart()
    #     self.model.giveAllTilesToCurrentPlayer()
    #     solver = RummySolver(self.model)
    #     self.assertEqual(728, solver.maxScore())


if __name__ == '__main__':
    unittest.main()
