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

    def __init__(self, model: RummyModel, track_solution=True):
        self.CONFIG = {'output_graph': True}
        self.model = model
        self.score = np.full((n,k,f_of_m), -math.inf)
        self.solutions = []
        self.track_solution = track_solution

        self.counter = []
        for i in range(n):
            self.counter.append(0)
            self.solutions.append(dict())

        self.solution = None

        self.graph = ''


    def setModel(self, model: RummyModel):
        self.__init__(model)

    # Displays the recursion counter in the logs (output/debug.log)
    def displayCounter(self):
        for i, c in enumerate(self.counter):
            logging.debug(str(i+1) + '. ' + '*' * c)


    # Export the score array as a heatmap (output/score.png)
    def exportScoreHeatmap(self):
        logging.debug('Exporting heatmap...')

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
        logging.debug('Exported heatmap.')

    # Export the recursion graph as a .dot file (output/graph.dot)
    # note that the solution tracing is not perfect as explained in the research paper,
    # so the graph is not 100% accurate with solution tracing
    def exportGraphTree(self):
        logging.debug('Exporting graph...')
        self.graph = 'digraph Rummy {\nrankdir="TB"\nnodesep=0.4;\nranksep=0.5;\n'+\
                     self.graph+\
                     '\n}'
        with open('output/graph.dot', 'w') as f:
            print(self.graph , file=f)


    # Get a string representation of the intermediate solution at a specific (runs,value) combination,
    # since some runs may be unfinished (1 or 2 tiles only)
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

    # Add a .dot string to the graph tree
    def addToGraphTree(self, dot):
        self.graph += dot

    # Get a .dot representation of the transition from (runs,value) to (newRuns,value+1)
    def getDOTNode(self, value, oldRuns, newRuns):
        oldHash = self.getRunHash(oldRuns)
        newHash = self.getRunHash(newRuns)
        return '{0}.{1} -> {2}.{3}\n{2}.{3} [label={4}]\n'.format(value,oldHash,value+1,newHash, self.getIntermediateSolution(newHash,value))


    # Post-processing function to check whether the algorithm
    # miscalculated the correct solution for runs, and correct them.
    #
    # MaxScore does compute the correct score for all runs, however it cannot keep track accurately
    # of the tiles used due to the "run length" logic used in the design of the algorithm.
    # Once a run becomes valid (3 tiles) the run length does not increase so a run with more than 3 tiles
    # is ONLY distinguished by the score, therefore when tracing the solution, longer runs might be cut short
    # even though their score was calculated correctly.
    #
    # This is a mitigation for the solution tracking problem described on the paper under "Future Work"
    def checkRuns(self,solution:RummyModel):
        playerTiles = solution.getCurrentPlayer().tiles

        for run in solution.board["runs"]:
            suit,val = run[0]
            tile = (suit,val-1)
            if tile in playerTiles:
                run.insert(0,tile)
                playerTiles.remove(tile)
                print("Fixed run")

            suit,val = run[-1]
            tile = (suit,val+1)
            if tile in playerTiles:
                run.append(tile)
                playerTiles.remove(tile)
                print("Fixed run")

    def maxScore(self, quarantine=False):
        if len(self.model.getTotalTilePool()) < 3:
            self.solution = RummyModel(self.model)
            return 0

        hand = self.model.getTotalTilePool() if not quarantine else self.model.getCurrentPlayer().getTilePool()
        print('Running MaxScore with tiles (quarantine={}):\n\t-{}'.format(quarantine,hand))

        score = self._maxScore(quarantine=quarantine)
        logging.debug('Max Score found: '+str(score))
        logging.debug(self.solutions)

        self.displayCounter()

        if self.track_solution:
            self.solution = self.traceSolution()
            logging.debug(self.solution.getBoardAsArray())
            self.checkRuns(self.solution)

        if self.CONFIG['output_graph']:
            # self.exportScoreHeatmap()
            self.exportGraphTree()



        assert not self.track_solution or self.solution.isValid()
        return score

    def _maxScore(self, value=1, runs=[MS([0,0])]*k, quarantine=False):
        # Base case
        if value > n:
            return 0

        runHash = self.getRunHash(runs)

        # Base case: memoization stored in 'score' array
        mem_score = self.getScoreFromRuns(value, runs)
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
            if self.track_solution and runHash not in self.solutions[value - 1]:
                self.solutions[value - 1][runHash] = '0'*k
            return 0


        for i in range(len(new_runs)):
            groupScores = self.totalGroupSize(new_hands[i]) * value

            if self.CONFIG['output_graph']:
                dotNode = self.getDOTNode(value, runs, new_runs[i])
                self.addToGraphTree(dotNode)

            score = self._maxScore(value + 1, new_runs[i])

            result = groupScores + run_scores[i] + score

            mem_score = self.getScoreFromRuns(value, runs)
            # If new-found result is bigger than the one being stored in the score array, save it
            if result > mem_score:
                self.setScoreFromRuns(result, value, runs)
                if self.track_solution:
                    self.solutions[value-1][runHash] = self.getRunHash(new_runs[i])

            assert groupScores >= 0

        return self.getScoreFromRuns(value, runs)

    # Wrapper function to _makeRuns - Compute all possible runs from the given
    # 'hand' and 'runs' configuration (considering only tiles of value 'value')
    def makeRuns(self, hand, runs, value):
        possible_runs = self._makeRuns(hand, runs, value)

        ret = {'new_runs':[],'new_hands':[],'run_scores':[]}

        for next_runs in possible_runs:
            if len(next_runs) != k:
                continue

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


    # Recursive function to make all possible runs from the given 'hand' and 'runs' configuration
    # Returns a list of all possible 'runs' configurations that can be made
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
                final.append(list(d))
            return final

        if len(possible_runs) == 0:
            assert 0 not in children
            return [[c] for c in children]

        final = []

        for runs in possible_runs:
            for child in children:
                assert len(list(child)) == m
                d = collections.deque(runs[:])
                d.appendleft(child)
                final.append(list(d))

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

    # Set the score for a specific (value,suit,run) combination
    def setScoreFromRun(self,score,value,suit,run):
        for j in range(f_of_m):
            if run == RUN_CONFIGS[j]:
                self.score[value-1][suit-1][j] = int(score)
                break

    # Set the score for a specific (value,runs) combination
    def setScoreFromRuns(self, score, value, runs):
        for i in range(k):
            run = runs[i]

            for j in range(f_of_m):
                if run == RUN_CONFIGS[j]:
                    prevScore = self.score[value-1][i][j]
                    self.score[value-1][i][j] = max(prevScore, int(score))
                    break

    # Get the score for a specific (value,runs) combination     
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
                return -math.inf
            
        return temp


    # Convert a list of RUN_CONFIG indexes to a 'runs' array
    @staticmethod
    def getRunsFromIndexes(indexes=np.zeros(k)):
        runs = []

        for i in range(k):
            runs.append(RUN_CONFIGS[int(indexes[i])])

        assert len(runs) == k
        return runs

    # Convert a list of runs to a hash, comprised of the RUN_CONFIGS indexes for each suit appended together as a string
    @staticmethod
    def getRunHash(runs):
        h = ''
        for i in range(k):
            h += str(RUN_CONFIGS.index(runs[i]))

        assert len(h) == k
        return h

    # Add the groups that can be formed from 'hand' to the given 'solution'
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

      
        # Add groups to solution if they have length >= 3
        if len(g1) >= 3:
            solution.addGroup(g1)
        if len(g2) >= 3:
            solution.addGroup(g2)

        return solution


    # Trace the solution from the 'solutions' array
    def traceSolution(self):
        solution = RummyModel()
        prevRuns = [MS([0,0]),MS([0,0]),MS([0,0]),MS([0,0])]
        logging.debug('Tracing solution...')
        for i in range(n):
            logging.debug(i)
            value = i+1

            hand = self.model.getTotalTilePool(filter_value=value)

            prevHash = self.getRunHash(prevRuns)
            if prevHash not in self.solutions[i]:
                if prevHash != '0000':
                    logging.error('Could not find the solution. Hash nr '+prevHash)
                continue

            if len(self.solutions[i]) == 0 or prevHash not in self.solutions[i]:
                self.addGroupsToSolution(hand, solution)
                continue


            nextHash = self.solutions[i][prevHash]

            nextRuns = self.getRunsFromIndexes(nextHash)

            for j in range(k):
                num_new_runs, num_new_tiles = self.getNumNewRunsAndTiles(prevRuns[j],nextRuns[j])

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
