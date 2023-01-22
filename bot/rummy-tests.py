import logging
import unittest
from builtins import int
import json
import numpy as np

from bot import RummyModel, RummySolver, RummyController, RummyView, runRummyGame, k, K, m, n, N, NUM_PLAYERS


class RummyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = runRummyGame(solve=False)
        self.model = self.controller.model

    def tearDown(self) -> None:
        super().tearDown()

    # Model Tests
    def test_copy_models(self):
        self.model.restart()
        self.model.addGroup([(1,5),(2,5),(3,5)])
        copy = RummyModel(self.model)
        self.assertEqual(copy.board['groups'][0],[(1,5),(2,5),(3,5)])

        copy.getCurrentPlayer().append((1,1))
        self.assertIn((1,1),copy.getCurrentPlayer())
        self.assertNotIn((1,1),self.model.getCurrentPlayer())


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
        ret = ret and self.model.addToRun((1,4), 1)
        self.assertTrue(ret)
        self.assertEqual(2, len(self.model.board['runs']))
        self.assertEqual(7, len(self.model.getBoardTilePool()))

    def test_table_constraint(self):
        self.model.restart()
        self.model.addRun([(1, 11), (1, 12), (1, 13)])
        a = RummyModel(self.model)
        self.assertTrue(a.checkTableConstraint(self.model))
        a.addGroup([(1, 10), (2, 10), (3, 10)])
        self.assertTrue(a.checkTableConstraint(self.model))
        a.board['runs'] = [[(1, 11), (1, 12)]]
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

        self.model.restart()
        self.model.addGroup([(1, 10), (2, 10), (3, 10)])
        temp = self.model.getTotalTilePool()
        self.assertEquals([(1, 10), (2, 10), (3, 10)], temp)

    def test_restart(self):
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
        self.model.addToRun((1,2),0)
        self.model.addToRun((1,3),0)
        self.model.initNewRun((2,1))
        self.assertEquals(self.model.board["runs"][0], [(1,1),(1,2),(1,3)])
        self.assertEqual(self.model.validateBoard(filter_suit=2), False)
        self.assertEqual(self.model.getBoardScore(), 6)

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
        self.model.addRun([(1,10),(1,11),(1,12)])
        solver = RummySolver(self.model)
        hand = [(1,1),(1,1),(2,1),(2,1),(3,1)]
        groupSize,solution = solver.totalGroupSize(hand,self.model)
        self.assertEqual(3, groupSize)
        self.assertEquals(len(solution.board["groups"]),1)
        self.assertEqual(set(solution.board["groups"][0]),set([(1,1),(2,1),(3,1)]))
        self.assertEquals(len(solution.board["runs"]),1)


        self.model.restart()
        self.model.addRun([(1,1),(1,2),(1,3)])
        solver = RummySolver(self.model)
        hand = [(1,1),(1,1),(2,1),(2,1),(3,1),(3,1),(4,1)]
        groupSize,solution = solver.totalGroupSize(hand,self.model)
        self.assertEqual(7, groupSize)
        self.assertEquals(len(solution.board["groups"]),2)

        for _ in range(40):
            self.model.restart()
            score = self.model.addRandomHand(group=True)
            hand = self.model.getBoardTilePool()
            groupOfTile = hand[0][1]
            print('hand: {}'.format(hand))
            groupSize,solution = solver.totalGroupSize(hand,RummyModel())
            print(solution.board['groups'])
            self.assertEqual(groupSize*groupOfTile, solution.getBoardScore())
            self.assertGreater(groupSize,0)


        groupSize,solution = solver.totalGroupSize([(1,1),(2,1),(3,1),(3,1)],RummyModel())
        self.assertEqual(3, groupSize)
        self.assertEqual(set(solution.board["groups"][0]),set([(1,1),(2,1),(3,1)]))

        groupSize,solution = solver.totalGroupSize([(1,1),(1,1),(4,1)],RummyModel())
        self.assertEqual(0, groupSize)
        self.assertEqual(len(solution.board["groups"]),0)

    def test_make_new_run(self):
        self.model.restart()
        self.model.addRun([(2, 4), (2, 5), (2, 6)])
        solver = RummySolver(self.model)
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}
        tile = (2,4)
        solver.makeNewRun([tile],np.zeros(shape=(k, m)),tile,RummyModel(),ret)
        self.assertEqual(len(ret['new_runs']), 2)


        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}

        runs = np.zeros(shape=(k, m))
        runs[2-1][0] = 2
        runs[2-1][1] = 2
        solver.makeNewRun([(2, 6),(2, 6)],runs,(2,6),RummyModel(),ret)
        self.assertEqual(len(ret['run_scores']),3)
        self.assertEqual(ret['run_scores'],[15,30,0])
        self.assertEqual(len(ret['new_runs']), 3)
        self.assertEqual(ret['new_runs'][0][2-1][0],3)
        self.assertEqual(ret['new_runs'][0][2-1][1],2)
        self.assertEqual(ret['new_runs'][1][2-1][0],3)
        self.assertEqual(ret['new_runs'][1][2-1][1],3)

    def test_make_runs_1(self):
        self.model.restart()
        self.model.addRun([(2, 4), (2, 5), (2, 6)])
        self.model.getCurrentPlayer().extend([(3, 7)])
        solver = RummySolver(self.model)
        runs = np.zeros(shape=(k, m))
        solution = RummyModel()
        new_runs,new_hands, run_scores,solutions = solver.makeRuns(self.model.getTotalTilePool(filter_value=4),runs, 4, solution)
        self.assertEqual(len(new_runs), 2)
        self.assertEqual(new_hands, [[],[(2,4)]] )
        self.assertEqual(run_scores,[0,0])

    def test_make_runs_2(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 2), (1, 3),(1, 4),(1,5),(1,6)])
        solver = RummySolver(self.model)
        self.assertEqual(20, solver.maxScore())
        self.assertEqual(len(solver.solution.board["runs"]),1)

    def test_make_runs_3(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 2), (1, 3), (1, 4), (1, 5), (1, 2), (1, 3), (1, 4)])
        solver = RummySolver(self.model)
        self.assertEqual(23, solver.maxScore())
        logging.error(solver.solution)
        self.assertEqual(len(solver.solution.board["runs"]), 2)


    def test_make_groups(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 10), (2, 10), (3, 10),(3, 10)])
        solver = RummySolver(self.model)
        self.assertEqual(30, solver.maxScore())

        logging.warning(solver.solution.getCurrentPlayer())
        self.assertEqual(len(solver.solution.board['groups']),1)
        self.assertEqual(set(solver.solution.board['groups'][0]), set([(1, 10), (2, 10), (3, 10)]))
        self.assertEqual(len(solver.solution.getCurrentPlayer()), 1)

    def test_make_groups_and_runs(self):
        self.model.restart()
        self.model.getCurrentPlayer().extend([(1, 3), (3, 3), (4, 3),
                                              (1, 1), (1, 2), (1, 3)])
        solver = RummySolver(self.model)
        self.assertEqual(15, solver.maxScore())
        self.assertEqual(solver.solution.board["runs"][0], [(1, 1), (1, 2), (1, 3)])
        self.assertEqual(set(solver.solution.board["groups"][0]), set([(1, 3), (3, 3), (4, 3)]))

    def test_solve_random_hand(self):
        fails = []
        for i in range(20):
            self.model.restart()
            score = self.model.addRandomHand()
            solver = RummySolver(self.model)
            if score != solver.maxScore():
                fails.append(str(self.model))

        self.assertEqual(fails,[])



    def test_13s(self):
        self.model.restart()
        self.model.addGroup([(1, 13), (2, 13), (3, 13)])
        solver = RummySolver(self.model)
        self.assertEqual(39, solver.maxScore())

        self.model.restart()
        self.model.initNewRun((1, 13))
        solver = RummySolver(self.model)
        self.assertLessEqual(solver.maxScore(), 0)

    # def test_make_runs_all_tiles(self):
    #     self.model.restart()
    #     self.model.giveAllTilesToCurrentPlayer()
    #     solver = RummySolver(self.model)
    #     self.assertEqual(728, solver.maxScore())

if __name__ == '__main__':
    unittest.main()
