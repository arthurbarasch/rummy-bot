from bot.model import m, n, k, RummyModel, K
import math
import numpy as np

class RummySolver:
    def __init__(self, model: RummyModel):
        self.model = model
        self.score = [dict()] * n
        self.moves = []

    def setModel(self, model: RummyModel):
        self.model = model

    def getSolution(self):
        return self.moves


    def maxScore(self, value=1, runs=np.zeros(shape=(k, m))):
        if value > n:
            return 0
        runHash = self.getRunHash(runs)
        if runHash in self.score[value-1]:

            return self.score[value-1][runHash]

        hand = self.model.getTotalTilePool()
        new_runs, run_scores = self.makeRuns(hand, runs, value)
        if(value > len(self.moves)):
            self.moves.append((-1,-1))
        for i in range(len(new_runs)):
            #groupScores = self.totalGroupSize(hand) * value
            result = 0 + run_scores + self.maxScore(value + 1, new_runs[i])
            if runHash in self.score[value-1]:
                temp = self.score[value-1][runHash]
                self.score[value-1][runHash] = max(result, temp)
            else:
                self.score[value-1][runHash] = result

            # For storing the solution
            if result > self.moves[value-1][0]:
                self.moves[-1] = (result, self.getRunHash(new_runs[i]))
        return self.score[value-1][runHash]

    def makeRuns(self,hand, runs, value):
        currTiles = list(filter(lambda tile: tile[0] != 0  and tile[1] == value , hand)) # Filter out only tiles with current value
        newRuns = []
        runScores = 0
        for suit in K:
            for M in range(m):
                # Suits in alphabetic order, starting with capital "A" (ascii value 65)
                searchTile = (suit, value)
                if searchTile in currTiles:
                    runVal = runs[suit-1,M]
                    newRun = runs[:]
                    if runVal < 2:  # If current length of run 0 or 1, increase length by one
                        newRun[suit-1, M]+=1
                    elif runVal == 2: # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
                        newRun[suit-1, M]+=1
                        runScores += (value-2)+(value-1)+value
                    elif runVal >=3: # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
                        runScores += value
                    currTiles.remove(searchTile)
                    newRuns.append(newRun)
                else:
                    newRun = runs[:]
                    newRun[suit-1,M] = 0
                    newRuns.append(newRun)
        hand = list(filter(lambda tile: tile == 'joker' or tile[1] != value , hand))
        return newRuns, runScores

    def totalGroupSize(self,hand):
        return 0

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
