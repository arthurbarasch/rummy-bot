from functools import reduce

from bot.model import m, n, k, s, RummyModel, K
import math
import logging
import numpy as np
from multiset import Multiset

import view


def MS(data):
    return Multiset(data)

RUN_CONFIGS = [MS([0, 0]), MS([0, 1]), MS([0, 2]), MS([0, 3]), MS([1, 1]), MS([1, 2]), MS([1, 3]), MS([2, 2]), MS([2, 3]), MS([3, 3])]

class RummySolver:

    def __init__(self, model: RummyModel):
        self.CONFIG = {'output_graph': True}
        self.model = model
        self.score = []
        self.counter = []
        for i in range(n+1):
            self.score.append(dict())
            self.counter.append(0)
        self.solution = None

        self.graph = ''

        self.otherSolutions = []

    def setModel(self, model: RummyModel):
        self.__init__(model)

    def displayRunsArray(self):
        print('Runs array')
        print(f'Value\tScore\tRuns\tSolution')
        for i in range(n):
            for key in self.score[i].keys():
                print(f'{i+1}\t\t{self.score[i][key][0]}\t\t{key}\t\t{self.score[i][key][1]}')
    def displayOtherSolutions(self):
        p = '#'*40
        print(p+'ALL SOLUTIONS'+p)
        for s in self.otherSolutions:
            print(s)
        print(p+p+p)

    def displayCounter(self):
        for i, c in enumerate(self.counter):
            print(str(i) + '. ' + '*' * c)


    def exportGraphTree(self):
        print('Exporting graph ')

        for i in range(n):
            arr = [ str(i+1)+'.'+k for k in list(self.score[i].keys())]
            self.graph += '{rank=same; '+' '.join(arr)+'}\n'

        self.graph = 'digraph Rummy {\nrankdir="TB"\nnodesep=0.4;\nranksep=0.5;\n'+\
                     self.graph+\
                     '\n}'
        with open('output/graph.dot', 'w') as f:
            print(self.graph , file=f)  # Python 3.x

    def getIntermediateSolution(self,solution:RummyModel,runsHash,value):
        arr = solution.getBoardAsArray()
        multisets = self.getMultisetFromHash(runsHash)

        # Add tiles in unfinished runs
        for i in range(k):
            n = multisets[i][1]
            while n>0:
                arr.append([(i+1,value)])
                n-=1

            n = multisets[i][2]
            while n>0:
                arr.append([(i+1,value-1),(i+1,value)])
                n-=1

        score = RummyModel.get_score_from_board_array(arr)
        return arr, score


    def addToGraphTree(self, value, oldRuns, newRuns, solution:RummyModel):
        newHash = self.getRunHash(newRuns)

        arr,score = self.getIntermediateSolution(solution,newHash,value)
        node = view.getDotNode(arr)

        self.graph += '{0}.{1} -> {2}.{3}\n{2}.{3} [label={4}]\n'.format(value,oldRuns,value+1,newHash, node)
        return score

    def maxScore(self, quarantine=False):
        if len(self.model.getTotalTilePool()) < 3:
            self.solution = RummyModel(self.model)
            return 0

        hand = self.model.getTotalTilePool() if not quarantine else self.model.getCurrentPlayer().getTilePool()
        print('Running MaxScore with tiles (quarantine={}):\n\t-{}'.format(quarantine,hand))

        score, solution,_ = self._maxScore(quarantine=quarantine)
        self.solution = RummyModel(self.model)
        self.solution.copySolution(solution)
        self.displayCounter()
        self.exportGraphTree()
        self.displayOtherSolutions()
        self.displayRunsArray()
        return score


    def _maxScore(self, value=1, runs=np.zeros(shape=(k, m)), solution=RummyModel(), quarantine=False):
        runHash = self.getRunHash(runs)
        solution = RummyModel(solution)

        # Base case
        if value > n:
            return 0, solution, runHash

        # Base case: memoization stored in 'score' array
        if runHash in self.score[value-1] and self.score[value-1][runHash][0] != -math.inf:
            # logging.warning('\n({}) return memoized val:{}\tsolution:{}'.format(value, self.score[value-1][runHash][0], list(
            #     map(lambda x: str(x[1]), self.score[value-1][runHash] ))))
            # if self.score[value-1][runHash][0] == 5:
            # print('\n({})!!! Score {} run hash-> {}\nSOLUTION:\n{}\n'.format(value, self.score[value-1][runHash][0],runHash,str(self.score[value-1][runHash][1])))

            return self.score[value-1][runHash]

        # Recursion counter
        if value < len(self.counter):
            self.counter[value] += 1

        # Get available tiles of tile value: 'value' in the union of board + player tiles
        # If player is still in quarantine, they may not use the board tiles yet to make points, so only use player tiles
        hand = self.model.getTotalTilePool(
            filter_value=value) if not quarantine else self.model.getCurrentPlayer().getTilePool(filter_value=value)

        # Make runs
        new_runs, new_hands, run_scores, solutions = self.makeRuns(hand, runs, value, solution)

        if len(new_runs) == 0:
            if runHash not in self.score[value-1]:
                self.score[value-1][runHash] = (-999, solution, runHash)
            return self.score[value-1][runHash]


        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value, new_hands[i], run_scores[i])

            groupScores, old_solution = self.totalGroupSize(new_hands[i], solutions[i])


            groupScores = groupScores * value
            logging.debug(
                '~~~~~~~~~~~~~* DEBUG STRING *~~~~~~~~~~~\n' + debugStr + ' \tgroupscores:{}\tsolution:\n{}\n'.format(
                    groupScores, old_solution))

            # Check the table constraint with the previous model
            if old_solution.checkTableConstraint(self.model, new_runs[i], filter_value=value):

                score, new_solution, old_runs_hash = self._maxScore(value + 1, new_runs[i], RummyModel(old_solution))

                if score is None:
                    continue

                if str(old_solution) == '[[(1, 1), (1, 2), (1, 3)], [(1, 3), (1, 4), (1, 5)]]':
                    print('FOUND SOLOLOLUTION')
                    print(score)
                    print(new_solution)

                result = groupScores + run_scores[i] + score

                if value == n:
                    self.otherSolutions.append((result, new_solution.getBoardAsArray()))

                if self.CONFIG['output_graph']:
                    self.addToGraphTree(value, runHash, new_runs[i], old_solution)

                # If new-found result is bigger than the one being stored in the score array, save it
                if runHash not in self.score[value-1] or result > self.score[value-1][runHash][0]:
                    # print(f'\nAt value {value} ----> {result} > {self.score[value-1][runHash][0]}\n')
                    self.score[value-1][runHash] = (result, new_solution, self.getRunHash(new_runs[i]))

                    if result == 18:
                        print('\n({})!!! Score {} run hash-> {}\nSOLUTION:\n{}\n'.format(value, self.score[value-1][runHash][0],runHash,str(self.score[value-1][runHash][1])))
                        # print(f'\n\nOLD VALUE -> {self.score[value-1][runHash][0]}\nNEW VALUE -> {result} \n')


            else:
                result = "-inf (doesn't satisfy table constraint) "
                if runHash not in self.score[value-1]:
                    self.score[value-1][runHash] = (-math.inf, solution, None)


            assert groupScores >= 0
            # Log the recursion
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores, result)


        return self.score[value-1][runHash]

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
                print('Found duplicate run')
                print(str(ret['new_runs'])+'\n')

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

        # First, the possibility of both tiles being used for runs
        if tilesAvailable == 2:
            new_runs = np.array(runs)
            new_solution = RummyModel(solution)
            new_score = 0
            new_hand = hand[:]
            for j in range(m):
                new_score += self.updateRun(new_runs, searchTile, j, new_solution)
                new_hand.remove((suit, value))

            # Recursion over suits
            self.makeNewRun(new_hand, new_runs, (suit + 1, value), new_solution, ret, run_scores + new_score)

        # Then, the possibility of one tile being used for runs (when we have 1 or 2 tiles available)
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

        # Finally, the possibility of no tiles of this sort being used for runs
        new_runs = np.array(runs)
        new_runs[suit - 1][0] = 0
        new_runs[suit - 1][1] = 0
        self.makeNewRun(hand[:], new_runs, (suit + 1, value), RummyModel(solution), ret, run_scores)


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

            if value == 5:
                print('AT VALUE 5 UPDATE RUNS'+str(solution))

            return (value - 2) + (value - 1) + value
        elif runVal >= 3:  # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value

            isLongest = runs[suit - 1, M] > runs[suit-1, (M+1) % m]
            assert solution.addToRun(tile, not isLongest)
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
            h += str(RUN_CONFIGS.index(MS(run[i])))

        # for i in range(k):
        #     multiset = {0: 0, 1: 0, 2: 0, 3: 0}
        #     for j in range(m):
        #         multiset[run[i][j]] += 1
        #
        #     for sVal in range(s+1):
        #         h += str(multiset[sVal])
        return h

    @staticmethod
    def getMultisetFromHash(run_hash):
        assert len(run_hash) == k
        print(run_hash)

        multisets = []
        for i in range(k):
            multiset = {0: 0, 1: 0, 2: 0, 3: 0}
            for it in RUN_CONFIGS[int(run_hash[i])]:
                multiset[it] += 1

            multisets.append(multiset)
        return multisets
    def unpackRunHashOnModel(self,run,lastRun, model,v):
        m0 = self.getMultisetFromHash(lastRun)
        m1 = self.getMultisetFromHash(run)

        for i in range(k):
            newRuns = m1[i][3] - m0[i][3]
            while newRuns > 0:
                model.addRun([(k+1,v-2),(k+1,v-1),(k+1,v)])
                newRuns -= 1

            if m0[i][3] == m1[i][3] and m0[i][3] > 0:
                model.addToRun((k+1,v))


    def traceSolution(self):
        solution = RummyModel()
        lastRun = '0'*k

        orderedRuns = []
        for val in range(n):
            maxScore = -math.inf
            maxRun = None
            for key in self.score[val].keys():
                if self.score[val][key][0] > maxScore:
                    maxScore = self.score[val][key][0]
                    maxRun = self.score[val][key][2]  # Max Run = The (old one, and new one)

            orderedRuns.append(maxRun)
            self.unpackRunHashOnModel(maxRun,lastRun,solution,val)
            lastRun = maxRun


        return solution, orderedRuns

