import unittest
from builtins import int
import json
import  logging
import numpy as np

from bot import RummyModel, RummySolver, RummyController, runRummyGame, k, K, m, n, N, NUM_PLAYERS


class RummyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        logging.basicConfig(filename='output/tests.log', filemode='w', level=logging.DEBUG)
        self.controller = runRummyGame(solve=False)
        self.model = self.controller.model

    def tearDown(self) -> None:
        super().tearDown()

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
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.start()
        self.model.restart()
        self.assertEquals(len(self.model.board["runs"]), 0)
        self.assertEquals(len(self.model.board["groups"]), 0)
        self.assertEquals(len(self.model.drawPile), n*k*m)
        for p in self.model.players:
            self.assertEquals(len(p),0, "Player must have 0 tiles after 'restart()'")

    def test_start(self):
        self.model.restart()
        self.model.start()
        self.assertEqual(n, len(N))
        for player in self.model.players:
            self.assertEqual(14, len(player))

    def test_rummy_params(self):
        self.assertEqual(n, 13)
        self.assertEqual(k, 4)
        self.assertEqual(m, 2)

    def test_validate_board(self):
        self.model.restart()
        self.model.addGroup([(1,1),(2,1),(3,1)])
        self.model.initNewRun((1,13))
        self.assertEqual(len(self.model.board["runs"][0]), 1)
        self.assertEqual(self.model.validateBoard(), False)
        self.assertEqual(self.model.getBoardScore(), 3)

        self.model.restart()
        self.model.initNewRun((1,1))
        self.model.addToRuns([(1,2),(1,3)])
        self.model.initNewRun((1,1))
        self.assertEquals(self.model.board["runs"][0], [(1,1),(1,2),(1,3)])
        self.assertEqual(self.model.validateBoard(filter_suit=1), False)
        self.assertEqual(self.model.getBoardScore(), 6)
        self.assertEquals(self.model.board["runs"][0], [(1,1),(1,2),(1,3)])

    def test_encode_decode(self):
        self.model.restart()
        self.model.addGroup([(1,1),(2,1),(3,1)])
        self.model.addRun([(4,1),(4,2),(4,3)])
        encoding = json.loads(self.model.encodeJSON())
        self.assertEqual(encoding['board']['runs'][0], [[4,1],[4,2],[4,3]])
        self.model.initNewRun((1,13))

        encoding = json.dumps({'board':[(1,12), (1,13)], 'players':[]})
        self.assertFalse(self.model.decodeJSON(encoding))


    # Solver Tests
    def test_total_group_size(self):
        self.model.restart()
        self.model.addRun([(1,1),(1,2),(1,3)])
        solver = RummySolver(self.model)
        groupSize,solution = solver.totalGroupSize([(1,1),(1,1),(2,1),(2,1),(3,1)],self.model)
        self.assertEqual(3, groupSize)
        self.assertEquals(len(solution.board["groups"]),1)
        self.assertEqual(set(solution.board["groups"][0]),set([(1,1),(2,1),(3,1)]))
        self.assertEquals(len(solution.board["runs"]),1)

        groupSize,solution = solver.totalGroupSize([(1,1),(2,1),(3,1),(3,1)],RummyModel())
        self.assertEqual(3, groupSize)
        self.assertEqual(set(solution.board["groups"][0]),set([(1,1),(2,1),(3,1)]))

        groupSize,solution = solver.totalGroupSize([(1,1),(1,1),(4,1)],RummyModel())
        self.assertEqual(0, groupSize)
        self.assertEquals(len(solution.board["groups"]),0)

    def test_make_runs(self):
        self.model.restart()
        self.model.addRun([(1, 1), (1, 2), (1, 3)])
        self.model.addRun([(1, 2), (1, 3),(1,4)])
        self.model.getCurrentPlayer().append((1, 1))
        solver = RummySolver(self.model)
        self.assertEqual(16, solver.maxScore())


        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 12), (1, 13), (2,8),(2,9)])
        solver = RummySolver(self.model)
        self.assertEqual(0, solver.maxScore())

        self.model.restart()
        self.model.addRun([(2, 2), (2, 3), (2, 4)])
        self.model.addRun([(2, 4), (2, 5), (2, 6)])
        self.model.getCurrentPlayer().extend([(2, 2)])
        solver = RummySolver(self.model)
        runs = np.zeros(shape=(k, m))
        solution = RummyModel()
        new_runs,new_hands, run_scores,solutions = solver.makeRuns(self.model.getTotalTilePool(filter_value=4),runs, 4, solution)
        self.assertEqual(len(new_runs), 4)
        self.assertEqual(new_hands.count([(2,4)]), 2)
        self.assertEqual(new_hands.count([]), 1)
        self.assertEqual(new_hands.count([(2,4),(2,4)]), 1)
        self.assertEqual(run_scores,[0,0,0,0])
        self.assertEqual(len(solutions[1].board["runs"]),1)
        self.assertEqual(len(solutions[3].board["runs"]),2)



    def test_make_groups(self):
        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        self.model.getCurrentPlayer().append((3, 10))
        solver = RummySolver(self.model)
        self.assertEqual(30, solver.maxScore())
        self.assertEqual(len(solver.solution.board['groups']), 1)
        self.assertEqual(set(solver.solution.board['groups'][0]), {(1, 10), (2, 10), (3, 10)} )
        self.assertEqual(len(solver.solution.getCurrentPlayer()), 1)

    def test_make_groups_and_runs(self):
        self.model.restart()
        self.model.addGroup([(1, 3), (3, 3), (4, 3)])
        self.model.addRun([(1, 2), (1, 3),(1,4)])
        self.model.getCurrentPlayer().append((1,1))

        solver = RummySolver(self.model)
        self.assertEqual(19, solver.maxScore())
        self.assertEqual([(1,1),(1, 2), (1, 3),(1,4)],solver.solution.board["runs"][0])
        self.assertEqual(set([(1, 3), (3, 3), (4, 3)]), set(solver.solution.board["groups"][0]))

    def test_add_random_hand(self):
        self.model.restart()
        score = self.model.addRandomHand()
        solver = RummySolver(self.model)
        self.assertEqual(score, solver.maxScore())

    def test_13s(self):
        self.model.restart()
        self.model.addGroup([(1, 13), (2, 13), (3, 13)])
        solver = RummySolver(self.model)
        self.assertEqual(39, solver.maxScore())

        self.model.restart()
        self.model.initNewRun((1, 13))
        solver = RummySolver(self.model)
        self.assertEqual(0, solver.maxScore())

    def test_generate_graphs(self):
        self.model.restart()
        score = self.model.addRandomHand()
        solver = RummySolver(self.model,test_mode=True)
        solver.displayRunsArray(solver.runs)
        self.assertEqual(True,True)

    # def test_make_runs_all_tiles(self):
    #     self.model.restart()
    #     for suit in K:
    #         run = []
    #         for value in N:
    #             run.append((suit,value))
    #         self.model.addRun(run)
    #     self.model.addRun(run)
    #     solver = RummySolver(self.model)
    #     self.assertEqual(728, solver.maxScore())

if __name__ == '__main__':
    unittest.main()
