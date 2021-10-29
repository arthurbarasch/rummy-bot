from bot.model import m, n, k, RummyModel, K
import math
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
            print('return memoized val:{}\tscore lengths:{}'.format(self.score[value-1][runHash][0], list(map(lambda x: len(x), self.score)) ))
            return self.score[value-1][runHash]

        hand = self.model.getTotalTilePool(filter_value=value)
        new_runs,new_hands, run_scores,solutions = self.makeRuns(hand, runs, value, solution)
        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value,new_hands[i],run_scores[i])
            groupScores = self.totalGroupSize(new_hands[i],solutions[i]) * value
            score, solutions[i], nextRunHash = self.maxScore(value + 1, new_runs[i], solutions[i])
            print(str(solutions[i]))
            result = groupScores + run_scores[i] + score
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores,result)
            print(debugStr)
            if runHash not in self.score[value-1] or result > self.score[value-1][runHash][0]:
                self.score[value-1][runHash] = (result,solutions[i],nextRunHash)

        return self.score[value-1][runHash][0], self.score[value-1][runHash][1], runHash

    def makeRuns(self,hand, runs, value,solution:RummyModel):
        currTiles = hand[:]
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions":[]}
        for suit in K:
            for M in range(m):
                searchTile = (suit, value)
                if searchTile in currTiles:
                    runVal = runs[suit-1,M]
                    newRun = runs[:]
                    if runVal==0:
                        newSolution = RummyModel(solution)
                        newSolution.initNewRun(searchTile)
                        ret['solutions'].append(newSolution)
                    else:
                        newSolution = RummyModel(solution)
                        newSolution.addToRuns([searchTile])
                        ret['solutions'].append(newSolution)

                    if runVal < 2:  # If current length of run 0 or 1, increase length by one
                        newRun[suit-1, M]+=1
                        ret['run_scores'].append(0)
                    elif runVal == 2: # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
                        newRun[suit-1, M]+=1
                        ret['run_scores'].append((value-2)+(value-1)+value)
                    elif runVal >=3: # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
                        ret['run_scores'].append(value)
                    currTiles.remove(searchTile)
                    ret['new_runs'].append(newRun)
                    newHand = currTiles[:]
                    ret['new_hands'].append(newHand)
                else:
                    newRun = runs[:]
                    newRun[suit-1,M] = 0
                    ret['new_runs'].append(newRun)
                    ret['new_hands'].append(hand[:])
                    ret['run_scores'].append(0)
                    ret['solutions'].append(RummyModel(solution))
        hand = list(filter(lambda tile: tile[1] != value , hand))
        return ret['new_runs'], ret['new_hands'], ret['run_scores'], ret['solutions']

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self,hand,solutions):
        noDuplicates = set(hand)
        for item in noDuplicates:
            hand.remove(item)

        l1 = len(noDuplicates)
        l2 = len(hand)
        if l1 >= 3:
            solutions.addGroup(list(noDuplicates))
        return (l1 if l1>=3 else 0) + (l2-l1 if l2>=3 else 0) #TODO Check this line

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
