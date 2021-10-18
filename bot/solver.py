from bot.model import m, n, k, RummyModel
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
        new_runs, tiles_used, run_scores = self.makeRuns(hand, runs, value)
        maxMove = tiles_used
        for i in range(len(new_runs)):
            #groupScores = self.totalGroupSize(hand) * value

            result = 0 + run_scores + self.maxScore(value + 1, new_runs[i])
            if runHash in self.score[value-1]:
                temp = self.score[value-1][runHash]
                if(result>temp):
                    maxMove = tiles_used

                self.score[value-1][runHash] = max(result, temp)

            else:
                self.score[value-1][runHash] = result

        if(value >= len(self.moves)):
            self.moves.append(maxMove)
        else:
            self.moves[value - 1] = maxMove
        return self.score[value-1][runHash]

    def makeRuns(self,hand, runs, value):
        currTiles = list(filter(lambda tile: tile != 'joker' and int(tile[1:]) == value , hand)) # Filter out only tiles with current value
        newRuns = []
        tilesUsed = []
        runs = runs[:]
        runScores = 0
        for K in range(k):
            for M in range(m):
                # Suits in alphabetic order, starting with capital "A" (ascii value 65)
                searchTile = chr(65+K) + str(value)
                if searchTile in currTiles:
                    runVal = runs[K,M]
                    newRun = runs[:]
                    if runVal < 2:  # If current length of run 0 or 1, increase length by one
                        newRun[K, M]+=1
                    elif runVal == 2: # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
                        newRun[K, M]+=1
                        runScores += (value-2)+(value-1)+value
                    elif runVal >=3: # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
                        runScores += value
                    currTiles.remove(searchTile)
                    newRuns.append(newRun)
                    tilesUsed.append(searchTile)
                else:
                    runs[K,M] = 0
                    newRuns.append(runs[:])
        hand = list(filter(lambda tile: tile == 'joker' or int(tile[1:]) != value , hand))
        return newRuns, tilesUsed, runScores

    def totalGroupSize(self,hand):
        return 0

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
