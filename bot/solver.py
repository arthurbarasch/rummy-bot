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

        #Assert the arrays have equal length
        assert sum([len(new_runs),len(new_hands),len(run_scores),len(solutions)])/4 == len(new_runs)
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

        # Create or extend runs with available tiles
        for searchTile in hand:
            suit, value = searchTile
            runVal = runs[suit-1,M]
            newRun = np.array(runs)
            newSolution = RummyModel(solution)
            if runVal == 0:
                newRun[suit-1, M]+=1
                ret['run_scores'].append(0)
                newSolution.initNewRun(searchTile)
            elif runVal == 1:  # If current length of run 0 or 1, increase length by one
                newRun[suit-1, M]+=1
                ret['run_scores'].append(0)
                newSolution.addToRuns([searchTile])
            elif runVal == 2: # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
                newRun[suit-1, M]+=1
                assert newRun[suit-1, M] == 3
                ret['run_scores'].append((value-2)+(value-1)+value)
                newSolution.addToRuns([searchTile])
            elif runVal >=3: # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
                ret['run_scores'].append(value)
                newSolution.addToRuns([searchTile])
            ret['solutions'].append(newSolution)
            ret['new_runs'].append(newRun)
            newHand = hand[:]
            newHand.remove(searchTile)
            ret['new_hands'].append(newHand)

        newRun = np.array(runs)
        ret['new_runs'].append(newRun)
        ret['new_hands'].append(hand[:])
        ret['run_scores'].append(0)
        newSolution = RummyModel(solution)
        ret['solutions'].append(newSolution)
        return ret['new_runs'], ret['new_hands'], ret['run_scores'], ret['solutions']

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self,hand,solution):
        noDuplicates = list(set(hand))
        l1 = len(noDuplicates)
        if l1 >= 3:
            solution.addGroup(noDuplicates)
        for item in noDuplicates:
            hand.remove(item)

        l2 = len(hand)
        if l2 >= 3:
            solution.addGroup(hand)
            hand = []
        return (l1 if l1 >= 3 else 0) + (l2 if l2 >= 3 else 0)

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
