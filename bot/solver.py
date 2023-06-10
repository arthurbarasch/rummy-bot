from functools import reduce

from bot.model import m, n, k, s, RummyModel, K, f_of_m
import math
import logging
import numpy as np

RUN_CONFIGS = [[0, 0], [0, 1], [0, 2], [0, 3], [1, 1], [1, 2], [1, 3], [2, 2], [2, 3], [3, 3]]

class RummySolver:

    def __init__(self, model: RummyModel):
        self.CONFIG = {'output_graph': True}
        self.model = model
        self.score = []  # Reduced from a 3D array of shape n*k*f(m) to a 2D array of shape n*(k*f(m))
        self.solutions = []


        self.counter = []
        for i in range(n):
            self.counter.append(0)
            self.score.append([])
            self.solutions.append(dict())
            for j in range(k*f_of_m):
                self.score[i].append(-math.inf)

        self.solution = None

        self.graph = ''


    def setModel(self, model: RummyModel):
        self.__init__(model)

    def displayCounter(self):
        for i, c in enumerate(self.counter):
            print(str(i+1) + '. ' + '*' * c)

    def exportGraphTree(self):
        print('Exporting graph...')
        # for i in range(n):
        #     arr = [ str(i+1)+'.'+k for k in list(self.score[i])]
        #     self.graph += '{rank=same; '+' '.join(arr)+'}\n'

        self.graph = 'digraph Rummy {\nrankdir="TB"\nnodesep=0.4;\nranksep=0.5;\n'+\
                     self.graph+\
                     '\n}'
        with open('output/graph.dot', 'w') as f:
            print(self.graph , file=f)

    def getIntermediateSolution(self,runsHash,value):
        multisets = self.getMultisetFromHash(runsHash)
        arr = []

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

        # Change formatting to HTML for .dot
        if len(arr) == 0:
            return '"[]"'

        dotStr = '<'
        colors = ['black', 'blue', 'orange', 'red']

        first = True
        for a in arr:
            if first:
                first = False
            else:
                dotStr += '-'

            firstTile = True
            for tile in a:
                if firstTile:
                    firstTile = False
                else:
                    dotStr += ','
                dotStr += '<FONT COLOR="{}">{}</FONT>'.format(colors[tile[0]-1], tile[1])

        dotStr += '>'

        return dotStr

    def addToGraphTree(self, dot):
        self.graph += dot

    def getDOTNode(self, value, oldRuns, newRuns):
        oldHash = self.getRunHash(oldRuns)
        newHash = self.getRunHash(newRuns)
        return '{0}.{1} -> {2}.{3}\n{2}.{3} [label={4}]\n'.format(value,oldHash,value+1,newHash, self.getIntermediateSolution(newHash,value))

    def maxScore(self, quarantine=False):
        if len(self.model.getTotalTilePool()) < 3:
            self.solution = RummyModel(self.model)
            return 0

        hand = self.model.getTotalTilePool() if not quarantine else self.model.getCurrentPlayer().getTilePool()
        print('Running MaxScore with tiles (quarantine={}):\n\t-{}'.format(quarantine,hand))

        score = self._maxScore(quarantine=quarantine)
        self.solution = RummyModel(self.model)
        self.displayCounter()

        self.traceSolution()
        self.exportGraphTree()
        return score

    def _maxScore(self, value=1, runs=np.zeros(shape=(k, m)), quarantine=False):
        # Base case
        if value > n:
            return 0

        runsIndex = self.getIndexFromRuns(runs)

        # Base case: memoization stored in 'score' array

        print('length array {} and index {}'.format(len(self.score[value - 1]),runsIndex))
        mem_score = self.score[value - 1][runsIndex]
        if mem_score > -math.inf:
            return mem_score

        # Recursion counter
        if value - 1 < len(self.counter):
            self.counter[value - 1] += 1

        # Get available tiles of tile value: 'value' in the union of board + player tiles
        # If player is still in quarantine, they may not use the board tiles yet to make points, so only use player tiles
        hand = self.model.getTotalTilePool(
            filter_value=value) if not quarantine else self.model.getCurrentPlayer().getTilePool(filter_value=value)

        # Make runs
        new_runs, new_hands, run_scores = self.makeRuns(hand, runs, value)

        if len(new_runs) == 0:
            return -math.inf

        for i in range(len(new_runs)):
            groupScores = self.totalGroupSize(new_hands[i])
            groupScores = groupScores * value

            # Check the table constraint with the previous model
            # if new_solution.checkTableConstraint(self.model, new_runs[i], filter_value=value):
            if True:
                if self.CONFIG['output_graph']:
                    dotNode = self.getDOTNode(value, runs, new_runs[i])
                    self.addToGraphTree(dotNode)

                score = self._maxScore(value + 1, new_runs[i])

                result = groupScores + run_scores[i] + score

                mem_score = self.score[value - 1][runsIndex]
                # If new-found result is bigger than the one being stored in the score array, save it
                if result > mem_score:
                    self.score[value - 1][runsIndex] = result
                    self.solutions[value - 1][str(runsIndex)] = self.getIndexFromRuns(new_runs[i])

            assert groupScores >= 0

        return self.score[value - 1][runsIndex]

    def makeRuns(self, hand, runs, value):
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': []}

        # For each suit, create or extend runs with available tiles
        self.makeNewRun(hand, runs, (1, value), ret)

        # Assertions about the length of the arrays returned
        assert sum(
            [len(ret['new_runs']), len(ret['new_hands']), len(ret['run_scores']) ]) / 3 == len(
            ret['new_runs'])
        assert len(ret['new_runs']) < (m + 2) ** 4
        return ret['new_runs'], ret['new_hands'], ret['run_scores']

    # Recursively iterate over possibilities of creating/extending runs of the given suit, value.
    def makeNewRun(self, hand, runs, searchTile, ret, run_scores=0):
        suit, value = searchTile
        if suit > k:
            ret['new_runs'].append(np.array(runs))
            ret['new_hands'].append(hand[:])
            ret['run_scores'].append(run_scores)
            return

        tilesAvailable = hand.count(searchTile)

        if tilesAvailable == 0:
            if (0 < runs[suit - 1][0] < 3) or (0 < runs[suit - 1][1] < 3):
                return

        # Cannot try both runs individually, if we only have one available tile and both runs are incomplete
        if tilesAvailable == 1 and (0 < runs[suit - 1][0] < 3) and (0 < runs[suit - 1][1] < 3):
            return

        if tilesAvailable == 2:
            new_runs = np.array(runs)
            new_score = 0
            new_hand = hand[:]
            for j in range(m):
                new_score += self.updateRun(new_runs, searchTile, j)
                new_hand.remove((suit, value))

            # Recursion over suits
            self.makeNewRun(new_hand, new_runs, (suit + 1, value), ret, run_scores + new_score)

        if tilesAvailable >= 1:
            # If the runs value of both m=1 and m=2 are equal, there is no need
            # to try both runs
            M = 1 if runs[suit - 1][0] == runs[suit - 1][1] else 2

            for i in range(M):
                new_runs = np.array(runs)

                #  Reset the other 'runs' value of this particular suit to 0
                new_runs[suit - 1][(i+1) % 2] = 0

                new_score = self.updateRun(new_runs, searchTile, i)
                new_hand = hand[:]
                new_hand.remove((suit, value))
                # Recursion over suits
                self.makeNewRun(new_hand, new_runs, (suit + 1, value), ret, run_scores + new_score)


        # An extra possibility of no tiles of this sort being used for runs
        new_runs = np.array(runs)
        new_runs[suit - 1][0] = 0
        new_runs[suit - 1][1] = 0
        self.makeNewRun(hand[:], new_runs, (suit + 1, value), ret, run_scores)


    # (Destructive method) Updates the runs array given input tile and value of m, and returns the score added
    # Also, keeps track of tiles used in the solution
    def updateRun(self, runs, tile, M):
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
            return (value - 2) + (value - 1) + value
        elif runVal >= 3:  # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
            return value

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self, hand):
        if len(hand) < 3:
            return 0

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

        score = l1 if l1 >= 3 else 0
        score += l2 if l2 >= 3 else 0
        return score


    @staticmethod
    def getIndexFromRuns(runs=np.zeros(shape=(k,m))):
        inds = np.zeros(k)
        for i in range(k):
            temp = sorted(runs[i])
            for j in range(f_of_m):
                if np.array_equal(temp, RUN_CONFIGS[j]):
                    inds[i] = j
                    break

        return inds

    @staticmethod
    def getRunsFromIndex(index):
        runs = np.zeros(shape=(k, m))


        for i in range(k):
            temp = index % i * f_of_m

        return


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
                multiset[j] = int(hash[(i*k)+j])

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
        i = np.argmax(self.score[0])

        return

