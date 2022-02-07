from bot.model import m, n, k, RummyModel, K
import math
import logging
import numpy as np

class RummySolver:
    def __init__(self, model: RummyModel):
        self.model = model
        self.score = []
        for i in range(n):
            self.score.append(dict())
        self.solution = None

    def setModel(self, model: RummyModel):
        self.__init__(model)

    def traceSolution(self, runHash):
        solutions = []
        while runHash != '':
            for i in range(n):
                if runHash in self.score[i]:
                    solutions.append(self.score[i][runHash][1])
                    runHash = self.score[i][runHash][2]
                    continue
        return solutions

    def _maxScore(self):
        score, solution = self.maxScore()
        self.solution = solution
        return score

    def maxScore(self, value=1, runs=np.zeros(shape=(k, m)), solution=RummyModel()):
        # Base case
        if value > n:
            solution.validateBoard()
            return 0, solution
        runHash = self.getRunHash(runs)
        # Base case: memoization stored in 'score' array
        if runHash in self.score[value-1]:
            logging.warning('\nreturn memoized val:{}\tscore lengths:{}'.format(self.score[value-1][runHash][0], list(map(lambda x: len(x), self.score)) ))
            return self.score[value-1][runHash]

        logging.warning('\nSOLUTION:\n'+ str(solution))

        # Get available tiles of tile value: 'value'
        hand = self.model.getTotalTilePool(filter_value=value)
        # Make runs
        new_runs,new_hands, run_scores,solutions = self.makeRuns(hand, runs, value, solution)

        #Assertions about the length of the arrays
        assert sum([len(new_runs),len(new_hands),len(run_scores),len(solutions)])/4 == len(new_runs)
        assert len(new_runs) < (m+2) ** 4

        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value,new_hands[i],run_scores[i])
            groupScores = self.totalGroupSize(new_hands[i],solutions[i]) * value
            if solutions[i].checkTableConstraint(self.model, value):
                score, solutions[i] = self.maxScore(value + 1, new_runs[i], solutions[i])
                result = groupScores + run_scores[i] + score
            else:
                result = 0
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores,result)
            logging.warning(debugStr)
            if runHash not in self.score[value-1] or result > self.score[value-1][runHash][0]:
                self.score[value-1][runHash] = (result,solutions[i])
        return self.score[value-1][runHash]


    def makeRuns(self,hand, runs, value,solution:RummyModel):
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions":[]}
        # Finish runs that cannot be continued (due to lack of tiles)
        for suit in K:
            for M in range(m):
                searchTile = (suit, value)
                if not searchTile in hand and runs[suit-1, M] > 0:
                    runs[suit - 1, M] = 0
                    solution.validateBoard(filter_suit=suit)

        # makeNewRun - recursive function
        # For each suit, create or extend runs with available tiles
        self.makeNewRun(hand,np.array(runs),(1, value),RummyModel(solution),ret)
        assert len(ret['new_runs']) > 0
        return ret['new_runs'],ret['new_hands'],ret['run_scores'],ret['solutions']

    def makeNewRun(self,hand,runs,searchTile,solution,ret,run_scores=0):
        suit, value = searchTile
        if suit > k:
            ret['new_runs'].append(np.array(runs))
            ret['new_hands'].append(hand[:])
            ret['run_scores'].append(run_scores)
            ret['solutions'].append(RummyModel(solution))
            return

        # TODO: Check for performance
        tilesAvailable = hand.count(searchTile)

        if tilesAvailable == 0:
            logging.warning("SKIP")
            self.makeNewRun(hand, runs,(suit + 1, value), solution, ret,run_scores)
            return

        # Iterate over possibilites of creating/extending runs of the given suit, value.
        # (m+1) because we must try tiles in each run individually, and also in both runs at once.
        for M in range(m+1):
            if M+1>m and m>=2:
                if tilesAvailable != m:
                    continue
                else:
                    new_score = 0
                    for i in range(m):
                        new_score += self.updateRun(runs,searchTile,i,solution)
                    newHand = hand[:]
                    newHand.remove((suit,value))
                    newHand.remove((suit,value))
                    # Recursion over suits
                    self.makeNewRun(newHand,runs,(suit+1, value),solution,ret,run_scores+new_score)
            else:
                new_score = self.updateRun(runs,searchTile,M,solution)
                newHand = hand[:]
                newHand.remove((suit,value))
                # Recursion over suits
                self.makeNewRun(newHand,runs,(suit+1, value),solution,ret,run_scores+new_score)

        # An extra possibility of no tiles of this sort being used for runs
        self.makeNewRun(hand, runs, (suit + 1, value), solution, ret, run_scores)
        return


    # (Destructive method) Updates the runs array with the given tile, and returns the score added
    # Also, keeps track of tiles used in the solution
    def updateRun(self,runs,tile,M,solution):
        suit, value = tile
        runVal = runs[suit - 1, M]
        if runVal == 0:
            runs[suit - 1, M] += 1
            solution.initNewRun(tile)
            return 0
        elif runVal == 1:  # If current length of run 0 or 1, increase length by one
            runs[suit - 1, M] += 1
            solution.addToRuns([tile])
            return 0
        elif runVal == 2:  # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
            runs[suit - 1, M] += 1
            assert runs[suit - 1, M] == 3
            solution.addToRuns([tile])
            return (value - 2) + (value - 1) + value
        elif runVal >= 3:  # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
            solution.addToRuns([tile])
            return value

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self,hand,solution):
        noDuplicates = list(set(hand))
        l1 = len(noDuplicates)
        if l1 >= 3:
            solution.addGroup(noDuplicates)
        for item in noDuplicates:
            hand.remove(item)

        l2 = len(hand)
        print('L1 is {} and l2 is {}'.format(l1, l2))
        if l2 >= 3:
            solution.addGroup(hand)
            hand = []
        return (l1 if l1 >= 3 else 0) + (l2 if l2 >= 3 else 0)

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
