from functools import reduce

from bot.model import m, n, k, s, RummyModel, f_of_m, K
import math
import logging
import numpy as np
import matplotlib.pyplot as plt
import multiset
import collections
from util import MS, getChildren

RUN_CONFIGS = [MS([0, 0]), MS([0, 1]), MS([0, 2]), MS([0, 3]), MS([1, 1]), MS([1, 2]), MS([1, 3]), MS([2, 2]), MS([2, 3]), MS([3, 3])]


class RummySolver:

    def __init__(self, model: RummyModel):
        self.CONFIG = {'output_graph': True}
        self.model = model
        self.score = np.full((n,k,f_of_m), -math.inf)
        self.solutions = []

        self.counter = []
        for i in range(n):
            self.counter.append(0)
            self.solutions.append(dict())

        self.solution = None

        self.graph = ''


    def setModel(self, model: RummyModel):
        self.__init__(model)

    def displayCounter(self):
        for i, c in enumerate(self.counter):
            print(str(i+1) + '. ' + '*' * c)

    def exportScoreHeatmap(self):
        print('Exporting heatmap...')

        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

        fig, axs = plt.subplots(3, 5)
        for currValue in range(n):
            arr = self.score[currValue]
            ax = axs[currValue % 3, currValue//3]

            im = ax.imshow(arr)
            ax.set_title('Score array at value = '+str(currValue+1))

            ax.set_ylabel('Suit')
            ax.set_xlabel('Runs lengths')

            ax.set_yticks(np.arange(4), labels=['Black','Blue','Yellow','Red'])
            ax.set_xticks(np.arange(len(RUN_CONFIGS)), labels=RUN_CONFIGS)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")

            for i in range(k):
                for j in range(f_of_m):
                    text = ax.text(j, i, arr[i, j],
                                   ha="center", va="center", color="black")
        cbar = fig.colorbar(im,ax=axs[0,0])
        cbar.ax.set_ylabel("Score", rotation=-90, va="bottom")

        plt.show()
        plt.savefig('output/score.png')
        print('Exported heatmap.')

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
        multisets = self.getRunsFromIndexes(runsHash)
        arr = []

        # Add tiles in unfinished runs
        for i in range(k):
            n = multisets[i].get(1,0)
            while n>0:
                arr.append([(i+1,value)])
                n-=1

            n = multisets[i].get(2,0)
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
        print('Max Score found: '+str(score))
        print(self.solutions)

        self.displayCounter()
        self.solution = self.traceSolution()

        if self.CONFIG['output_graph']:
            # self.exportScoreHeatmap()
            self.exportGraphTree()

        print(self.solution.getBoardAsArray())

        # if score != self.solution.getBoardScore():
        #     for tile in self.solution.getCurrentPlayer().tiles:
        #         if self.solution.addToRun(tile):
        #             self.solution.getCurrentPlayer().remove(tile)
        #             print('ADDED A MISSING TILE')

        assert self.solution.isValid()
        # assert score == self.solution.getBoardScore()
        return score

    def _maxScore(self, value=1, runs=[MS([0,0])]*k, quarantine=False):
        # Base case
        if value > n:
            return 0

        runHash = self.getRunHash(runs)

        # Base case: memoization stored in 'score' array

        # print('length array {} and index {}'.format(len(self.score[value - 1]),runsIndex))
        mem_score = self.getScoreFromRuns(value, runs)
        if mem_score > -math.inf:
            # print(f'Returning memorized score[{value},{self.getRunHash(runs)}]')
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
            if runHash not in self.solutions[value - 1]:
                self.solutions[value - 1][runHash] = '0'*k
            return 0
            # self.setScoreFromRuns(0,value,runs)
            # runsHash = self.getRunHash(runs)
            # self.solutions[value-1][runsHash] = runsHash
            # return self.getScoreFromRuns(value, runs)



        for i in range(len(new_runs)):
            groupScores = self.totalGroupSize(new_hands[i]) * value

            # Check the table constraint with the previous model
            # if new_solution.checkTableConstraint(self.model, new_runs[i], filter_value=value):

            if self.CONFIG['output_graph']:
                dotNode = self.getDOTNode(value, runs, new_runs[i])
                self.addToGraphTree(dotNode)

            score = self._maxScore(value + 1, new_runs[i])

            result = groupScores + run_scores[i] + score

            mem_score = self.getScoreFromRuns(value, runs)
            # If new-found result is bigger than the one being stored in the score array, save it
            if result > mem_score:
                self.setScoreFromRuns(result, value, runs)
                self.solutions[value-1][runHash] = self.getRunHash(new_runs[i])
                # self.solutions[value - 1][str(hash(str(runs)))] = self.getIndexFromRuns(new_runs[i])

            assert groupScores >= 0

        return self.getScoreFromRuns(value, runs)

    def makeRuns(self, hand, runs, value):
        possible_runs = self._makeRuns(hand, runs, value)

        ret = {'new_runs':[],'new_hands':[],'run_scores':[]}

        for next_runs in possible_runs:
            if len(next_runs) != k:
                continue
                # return [],[],[]

            run_score = 0
            new_hand = hand[:]
            for i in range(k):
                suit = i + 1
                tilesUsed = int(max(sum(list(next_runs[i])) - sum(list(runs[i])), 0))

                num_new_runs, num_only_tiles = self.getNumNewRunsAndTiles(runs[i],next_runs[i])

                run_score += ((value - 2) + (value - 1) + value)*num_new_runs
                run_score += value*num_only_tiles

                for j in range(tilesUsed):
                    new_hand.remove((suit,value))

            ret['new_runs'].append(next_runs)
            ret['new_hands'].append(new_hand)
            ret['run_scores'].append(run_score)

        return ret['new_runs'],ret['new_hands'],ret['run_scores']

    def _makeRuns(self, hand, runs, value, suit=1):

        if suit > k:
            return []

        searchTile = (suit,value)
        tilesAvailable = hand.count(searchTile)

        ms = runs[suit-1]

        possible_runs = self._makeRuns(hand,runs,value,suit+1)

        children = getChildren(ms, tilesAvailable)

        if len(children) == 0:
            final = []
            if len(possible_runs) == 0:
                return []

            for run in possible_runs:
                d = collections.deque(run[:])
                # d.appendleft(MS([0,0]))
                final.append(list(d))
            return final

        if len(possible_runs) == 0:
            assert 0 not in children
            return [[c] for c in children]

        final = []

        for runs in possible_runs:
            for child in children:
                assert len(list(child)) == m

                # assert len(runs) == k-suit
                d = collections.deque(runs[:])
                d.appendleft(child)
                # l = runs[:]
                # l.append(child)
                final.append(list(d))
                # print(f'RUN {run} \nCHILD {child} \nFINAL {final}')


        return final


    def getNumNewRunsAndTiles(self,prevRun, nextRun):
        p2 = prevRun.get(2,0)
        p3 = prevRun.get(3,0)
        n3 = nextRun.get(3,0)

        num_new_runs = max(0, min(p2, 1) * (n3 - p3))
        num_only_tiles = p3 if 0 < p3 <= n3 else 0

        return num_new_runs, num_only_tiles

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

    def setScoreFromRun(self,score,value,suit,run):
        for j in range(f_of_m):
            if run == RUN_CONFIGS[j]:
                self.score[value-1][suit-1][j] = int(score)
                break

    def setScoreFromRuns(self, score, value, runs):
        for i in range(k):
            run = runs[i]

            for j in range(f_of_m):
                if run == RUN_CONFIGS[j]:
                    prevScore = self.score[value-1][i][j]
                    self.score[value-1][i][j] = max(prevScore, int(score))
                    break

    def getScoreFromRuns(self, value, runs):
        scores = np.zeros(k)
        for i in range(k):
            run = runs[i]
            for j in range(f_of_m):
                if run == RUN_CONFIGS[j]:
                    scores[i] = self.score[value-1][i][j]
                    break

        temp = scores[0]
        for s in scores:
            if s != temp:
                # print(f'{value} {scores}')
                # assert False
                return -math.inf
                # return 0

        return temp

    @staticmethod
    def getRunsFromIndexes(indexes=np.zeros(k)):
        runs = []

        for i in range(k):
            runs.append(RUN_CONFIGS[int(indexes[i])])

        assert len(runs) == k
        return runs

    @staticmethod
    def getRunHash(runs):
        h = ''

        for i in range(k):
            h += str(RUN_CONFIGS.index(runs[i]))

        assert len(h) == k
        return h

    def addGroupsToSolution(self,hand, solution):
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


        if len(g1) >= 3:
            solution.addGroup(g1)
        if len(g2) >= 3:
            solution.addGroup(g2)

        return solution


    def traceSolution(self):
        solution = RummyModel()
        prevRuns = [MS([0,0]),MS([0,0]),MS([0,0]),MS([0,0])]
        print('Tracing solution...')
        for i in range(n):
            print(i)
            value = i+1

            hand = self.model.getTotalTilePool(filter_value=value)

            prevHash = self.getRunHash(prevRuns)
            if prevHash not in self.solutions[i]:
                logging.error('Could not find the solution. Hash nr '+prevHash)
                continue

            if len(self.solutions[i]) == 0 or prevHash not in self.solutions[i]:
                self.addGroupsToSolution(hand, solution)
                continue


            nextHash = self.solutions[i][prevHash]

            nextRuns = self.getRunsFromIndexes(nextHash)

            for j in range(k):
                num_new_runs, num_new_tiles = self.getNumNewRunsAndTiles(prevRuns[j],nextRuns[j])

                if value == 6:
                    print('NUM NEW TILES')
                    print(prevRuns[j])
                    print(nextRuns[j])
                    print(num_new_tiles)

                while num_new_runs>0:
                    suit = j+1
                    hand.remove((suit,value))
                    solution.addRun([(suit,value-2),(suit,value-1),(suit,value)])
                    num_new_runs -= 1

                while num_new_tiles>0:
                    suit = j+1
                    hand.remove((suit,value))
                    solution.addToRun((suit,value))
                    num_new_tiles -= 1

            solution = self.addGroupsToSolution(hand,solution)


            prevRuns = nextRuns[:]

        final = RummyModel(self.model)
        final.copySolution(solution)
        return final



    def getMultisetFromHash(self, hash):
        multisets = []
        for i in range(k):
            multisets.append(RUN_CONFIGS[int(hash[i])])
        return multisets
