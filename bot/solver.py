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
        return self.maxScore()[0]

    def maxScore(self, value=1, runs=np.zeros(shape=(k, m)), solution=RummyModel()):
        if value > n:
            return 0, solution, ''
        runHash = self.getRunHash(runs)
        if runHash in self.score[value-1]:
            logging.warning('return memoized val:{}\tscore lengths:{}'.format(self.score[value-1][runHash][0], list(map(lambda x: len(x), self.score)) ))
            return self.score[value-1][runHash]

        logging.warning('SOLUTION:\n'+ str(solution))

        hand = self.model.getTotalTilePool(filter_value=value)
        new_runs,new_hands, run_scores,solutions = self.makeRuns(hand, runs, value, solution)
        assert sum([len(new_runs),len(new_hands),len(run_scores),len(solutions)])/4 == len(new_runs)
        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value,new_hands[i],run_scores[i])
            groupScores = self.totalGroupSize(new_hands[i],solutions[i]) * value
            if not solutions[i].checkTableConstraint(self.model.getBoardTilePool()):
                continue

            score, solutions[i], nextRunHash = self.maxScore(value + 1, new_runs[i], solutions[i])
            result = groupScores + run_scores[i] + score
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores,result)
            logging.warning(debugStr)
            if runHash not in self.score[value-1] or result > self.score[value-1][runHash][0]:
                self.score[value-1][runHash] = (result,solutions[i],nextRunHash)

        if runHash in self.score[value - 1]:
            return self.score[value-1][runHash][0], self.score[value-1][runHash][1], runHash
        else:
            return 0, solution, ''

    def makeRuns(self,hand, runs, value,solution:RummyModel):
        currTiles = hand[:]
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions":[]}
        for suit in K:
            for M in range(m):
                searchTile = (suit, value)
                if searchTile in currTiles:
                    runVal = runs[suit-1,M]
                    newRun = np.array(runs)
                    if value == 13 and runVal == 2:
                        logging.warning('\n*runs* = {}\t\n\n'.format(newRun))

                    if runVal < 2:  # If current length of run 0 or 1, increase length by one
                        newRun[suit-1, M]+=1
                        ret['run_scores'].append(0)
                        newSolution = RummyModel(solution)
                        ret['solutions'].append(newSolution)
                    elif runVal == 2: # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
                        newRun[suit-1, M]+=1
                        assert newRun[suit-1, M] == 3
                        ret['run_scores'].append((value-2)+(value-1)+value)
                        newSolution = RummyModel(solution)
                        newSolution.addRun([(suit, value-2),(suit, value-1),(suit, value)])
                        ret['solutions'].append(newSolution)
                    elif runVal >=3: # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
                        ret['run_scores'].append(value)
                        newSolution = RummyModel(solution)
                        newSolution.addToRuns([(suit, value)])
                        ret['solutions'].append(newSolution)
                    currTiles.remove(searchTile)
                    ret['new_runs'].append(newRun)
                    ret['new_hands'].append(currTiles[:]) #TODO: remove tile used from hand
                else:
                    newRun = np.array(runs)
                    newRun[suit-1,M] = 0
                    ret['new_runs'].append(newRun)
                    ret['new_hands'].append(hand[:])
                    ret['run_scores'].append(0)
                    newSolution = RummyModel(solution)
                    newSolution.validateBoard(filter_suit=suit)
                    ret['solutions'].append(newSolution)
        hand = list(filter(lambda tile: tile[1] != value , hand))
        return ret['new_runs'], ret['new_hands'], ret['run_scores'], ret['solutions']

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self,hand,solutions):
        temp = hand[:]
        noDuplicates = list(set(hand))
        l1 = len(noDuplicates)
        if l1 >= 3:
            solutions.addGroup(noDuplicates)
            for tile in noDuplicates:
                hand.remove(tile)

        for item in noDuplicates:
            temp.remove(item)
        l2 = len(temp)
        if l2 >= 3:
            solutions.addGroup(hand)
            hand = []
        return (l1 if l1 >= 3 else 0) + (l2 if l2 >= 3 else 0) #TODO Check this line

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
