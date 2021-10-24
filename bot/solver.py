from bot.model import m, n, k, RummyModel, K
import math
import numpy as np

class RummySolver:
    def __init__(self, model: RummyModel):
        self.model = model
        self.score = [dict()] * n
        self.moves = []

    def setModel(self, model: RummyModel):
        self.__init__(model)

    def getSolution(self):
        return self.moves


    def maxScore(self, value=1, runs=np.zeros(shape=(k, m))):
        if value > n:
            return 0
        runHash = self.getRunHash(runs)
        if runHash in self.score[value-1]:
            return self.score[value-1][runHash]

        hand = self.model.getTotalTilePool(filter_value=value)
        new_runs,new_hands, run_scores = self.makeRuns(hand, runs, value)
        if(value-1 >= len(self.moves)):
            self.moves.append((-1,-1))
        for i in range(len(new_runs)):
            groupScores = self.totalGroupSize(new_hands[i]) * value
            result = groupScores + run_scores[i] + self.maxScore(value + 1, new_runs[i])
            if runHash in self.score[value-1]:
                self.score[value-1][runHash] = max(result, self.score[value-1][runHash])
            else:
                self.score[value-1][runHash] = result

            # For storing the solution
            if result > self.moves[value-1][0]:
                self.moves[-1] = (result, self.getRunHash(new_runs[i]))
        return self.score[value-1][runHash]

    def makeRuns(self,hand, runs, value):
        currTiles = hand[:]
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': []}
        for suit in K:
            for M in range(m):
                searchTile = (suit, value)
                if searchTile in currTiles:
                    runVal = runs[suit-1,M]
                    newRun = runs[:]
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
                    newHand = hand[:]
                    newHand.remove(searchTile)
                    ret['new_hands'].append(newHand)
                else:
                    newRun = runs[:]
                    newRun[suit-1,M] = 0
                    ret['new_runs'].append(newRun)
                    ret['new_hands'].append(hand[:])
                    ret['run_scores'].append(0)
        hand = list(filter(lambda tile: tile[1] != value , hand))
        return ret['new_runs'], ret['new_hands'], ret['run_scores']

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self,hand):
        val = len(set(hand))
        return val if val >= 3 else 0

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
