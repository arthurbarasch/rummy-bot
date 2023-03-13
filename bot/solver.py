from functools import reduce

from bot.model import m, n, k, s, RummyModel, K
import math
import logging
import numpy as np


class RummySolver:
    def __init__(self, model: RummyModel):
        self.model = model
        self.score = []
        self.counter = []
        for i in range(n):
            self.score.append(dict())
            self.counter.append(0)
        self.solution = None

        self.otherSolutions = []

    def setModel(self, model: RummyModel):
        self.__init__(model)

    def displayCounter(self):
        for i, c in enumerate(self.counter):
            print(str(i+1) + '. ' + '*' * c)
    def maxScore(self, quarantine=False):
        if len(self.model.getTotalTilePool()) < 3:
            self.solution = RummyModel(self.model)
            return 0

        hand = self.model.getTotalTilePool() if not quarantine else self.model.getCurrentPlayer().getTilePool()
        print('Running MaxScore with tiles (quarantine={}):\n\t-{}'.format(quarantine,hand))

        score, solution = self._maxScore(quarantine=quarantine)
        self.solution = RummyModel(self.model)
        self.solution.copySolution(solution)
        self.displayCounter()
        return score

    def _maxScore(self, value=1, runs=np.zeros(shape=(k, m)), solution=RummyModel(), quarantine=False):
        # Base case
        if value > n:
            return 0, solution

        runHash = self.getRunHash(runs)

        # Base case: memoization stored in 'score' array
        if runHash in self.score[value - 1] and self.score[value - 1][runHash][0] > -math.inf:
            # logging.warning('\n({}) return memoized val:{}\tsolution:{}'.format(value, self.score[value - 1][runHash][0], list(
            #     map(lambda x: str(x[1]), self.score[value - 1][runHash] ))))
            # if self.score[value - 1][runHash][0] == 5:
            print('\n({})!!! Score {} run hash-> {}\nSOLUTION:\n{}\n'.format(value, self.score[value - 1][runHash][0],runHash,str(self.score[value - 1][runHash][1])))

            return self.score[value - 1][runHash]

        # Recursion counter
        if value - 1 < len(self.counter):
            self.counter[value - 1] += 1

        # Get available tiles of tile value: 'value' in the union of board + player tiles
        # If player is still in quarantine, they may not use the board tiles yet to make points, so only use player tiles
        hand = self.model.getTotalTilePool(
            filter_value=value) if not quarantine else self.model.getCurrentPlayer().getTilePool(filter_value=value)

        # Make runs
        new_runs, new_hands, run_scores, solutions = self.makeRuns(hand, runs, value, solution)

        if len(new_runs) == 0:
            if runHash not in self.score[value-1]:
                self.score[value - 1][runHash] = (-math.inf, solution)
            return -math.inf, solution


        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value, new_hands[i], run_scores[i])

            groupScores, new_solution = self.totalGroupSize(new_hands[i], solutions[i])

            groupScores = groupScores * value
            logging.debug(
                '~~~~~~~~~~~~~* DEBUG STRING *~~~~~~~~~~~\n' + debugStr + ' \tgroupscores:{}\tsolution:\n{}\n'.format(
                    groupScores, new_solution))
            # assert groupScores <= new_solution.getBoardScore()

            # Check the table constraint with the previous model
            if new_solution.checkTableConstraint(self.model, new_runs[i], filter_value=value):

                score, new_solution = self._maxScore(value + 1, new_runs[i], new_solution)

                result = groupScores + run_scores[i] + score

                if value == n:
                    self.otherSolutions.append((result, new_solution.getBoardAsArray()))

                # If new-found result is bigger than the one being stored in the score array, save it
                if runHash not in self.score[value - 1] or result >= self.score[value - 1][runHash][0]:
                    self.score[value - 1][runHash] = (result, RummyModel(new_solution))
            else:
                result = "-inf (doesn't satisfy table constraint) "
                if runHash not in self.score[value - 1]:
                    self.score[value - 1][runHash] = (-math.inf, RummyModel(new_solution))


            assert groupScores >= 0
            # Log the recursion
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores, result)


        return self.score[value - 1][runHash]

    def makeRuns(self, hand, runs, value, solution: RummyModel):
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}

        # For each suit, create or extend runs with available tiles
        self.makeNewRun(hand, np.array(runs), (1, value), RummyModel(solution), ret)

        # Assertions about the length of the arrays returned
        assert sum(
            [len(ret['new_runs']), len(ret['new_hands']), len(ret['run_scores']), len(ret['solutions'])]) / 4 == len(
            ret['new_runs'])
        assert len(ret['new_runs']) < (m + 2) ** 4
        return ret['new_runs'], ret['new_hands'], ret['run_scores'], ret['solutions']

    # Recursively iterate over possibilities of creating/extending runs of the given suit, value.
    def makeNewRun(self, hand, runs, searchTile, solution, ret, run_scores=0):
        suit, value = searchTile
        if suit > k:
            if str(runs) in [str(r) for r in ret['new_runs']]:
                print('Found duplicate run+\n'+str(runs))

            ret['new_runs'].append(np.array(runs))
            ret['new_hands'].append(hand[:])
            ret['run_scores'].append(run_scores)
            ret['solutions'].append(RummyModel(solution))
            return

        tilesAvailable = hand.count(searchTile)

        if tilesAvailable == 0:
            if (0 < runs[suit - 1][0] < 3) or (0 < runs[suit - 1][1] < 3):
                ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}
                return

            runs[suit - 1][0] = 0
            runs[suit - 1][1] = 0
            self.makeNewRun(hand, runs, (suit + 1, value), solution, ret, run_scores)
            return

        # Cannot try both runs individually, if we only have one available tile and both runs are incomplete
        if tilesAvailable == 1 and (0 < runs[suit - 1][0] < 3) and (0 < runs[suit - 1][1] < 3):
            ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}
            return

        if tilesAvailable == 2:
            new_runs = np.array(runs)
            new_solution = RummyModel(solution)
            new_score = 0
            new_hand = hand[:]
            for j in range(m):
                new_score += self.updateRun(new_runs, searchTile, j, new_solution)
                new_hand.remove((suit, value))

            print('FOUND U {}: \n{}'.format(str(new_solution),new_runs[suit - 1]))
            # Recursion over suits
            self.makeNewRun(new_hand, new_runs, (suit + 1, value), new_solution, ret, run_scores + new_score)

            # sol = ['\n\t-runVal ' + str(ret['run_scores'][i])+'\t'+ str(ret['solutions'][i]) for i in range(len(ret['run_scores']))]
            # print('SOLUTIONS\n\t-RUNS={}'.format(str(runs[0]))+reduce(lambda x,y: x+y,sol,''))
            # print('Value {} and ret is:\n{}'.format(value, ret))


        if tilesAvailable >= 1:
            # If the runs value of both m=1 and m=2 are equal, there is no need
            # to try both runs
            M = 1 if runs[suit - 1][0] == runs[suit - 1][1] else 2

            for i in range(M):
                new_runs = np.array(runs)

                #  Reset the other 'runs' value of this particular suit to 0
                new_runs[suit - 1][(i+1) % 2] = 0

                new_solution = RummyModel(solution)
                new_score = self.updateRun(new_runs, searchTile, i, new_solution)
                new_hand = hand[:]
                new_hand.remove((suit, value))
                # Recursion over suits
                self.makeNewRun(new_hand, new_runs, (suit + 1, value), new_solution, ret, run_scores + new_score)

        # An extra possibility of no tiles of this sort being used for runs
        runs[suit - 1][0] = 0
        runs[suit - 1][1] = 0
        self.makeNewRun(hand, runs, (suit + 1, value), RummyModel(solution), ret, run_scores)

    # (Destructive method) Updates the runs array given input tile and value of m, and returns the score added
    # Also, keeps track of tiles used in the solution
    def updateRun(self, runs, tile, M, solution: RummyModel):
        suit, value = tile
        runVal = runs[suit - 1, M]

        if runVal == 0:
            if value + 2 > n:
                # No need to start a new run if we know we can't finish it
                return 0
            runs[suit - 1, M] += 1
            return 0
        elif runVal == 1:  # If current length of run 0 or 1, increase length by one
            runs[suit - 1, M] += 1
            return 0
        elif runVal == 2:  # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
            runs[suit - 1, M] += 1

            r = [(suit, value-2), (suit, value-1), tile]
            assert solution.addRun(r)
            return (value - 2) + (value - 1) + value
        elif runVal >= 3:  # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value

            isLongest = runs[suit - 1, M] > runs[suit-1, (M+1) % 2]
            assert solution.addToRun(tile, isLongest)
            return value

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self, hand, solution: RummyModel):
        if len(hand) < 3:
            return 0, solution

        # TODO: Generalize over 'm'
        g1 = list(set(hand))
        g2 = hand[:]
        for tile in g1:
            g2.remove(tile)

        # Special case for when a group has length 4 and the other length 2
        if len(g1) == 4 and len(g2) == 2:
            for t in g1:
                if t not in g2:
                    g1.remove(t)
                    g2.append(t)
                    break

        l1 = len(g1)
        l2 = len(g2)

        if l1 >= 3:
            lengroups = len(solution.board['groups'])
            assert solution.addGroup(g1)
            if lengroups + 1 != len(solution.board['groups']):
                logging.error('ERROR: on /solver.py/totalGroupSize > tried adding {} as a group'.format(g1))
                return 0, solution

        if l2 >= 3:
            assert solution.addGroup(g2)

        score = l1 if l1 >= 3 else 0
        score += l2 if l2 >= 3 else 0
        return score, solution

    @staticmethod
    def getRunHash(run):
        h = ''

        for i in range(k):
            multiset = {0: 0, 1: 0, 2: 0, 3: 0}
            for j in range(m):
                multiset[run[i][j]] += 1

            for sVal in range(s+1):
                h += str(multiset[sVal])
        return h

    def getMultisetFromHash(self, hash):
        multisets = []
        for i in range(k):
            multiset = {0: 0, 1: 0, 2: 0, 3: 0}
            for j in range(s+1):
                multiset[j] = hash[(i*k)+j]

            multisets.append(multiset)
        return multisets
    def unpackRunHashOnModel(self,run,lastRun, model,v):
        tiles = self.model.getTotalTilePool(filter_value=v)

        m0 = self.getMultisetFromHash(lastRun)
        m1 = self.getMultisetFromHash(run)

        for i in range(k):
            newRuns = m1[i][3] - m0[i][3]
            while newRuns > 0:
                model.addRun([(k,v-2),(k,v-1),(k,v)])
                newRuns -= 1


    def traceSolution(self):
        solution = RummyModel()
        lastRun = np.zeros(shape=(k, m))
        for val in range(n):
            maxScore = -math.inf
            maxRun = None
            for key in self.score[val].keys():
                if self.score[val][key][0] > maxScore:
                    maxRun = key
                    maxScore = self.score[val][key]


            self.unpackRunHashOnModel(maxRun,lastRun,solution,val)


        return solution

