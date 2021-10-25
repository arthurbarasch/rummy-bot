from bot.model import m, n, k, RummyModel, K
import math
import numpy as np

class RummySolver:
    def __init__(self, model: RummyModel):
        self.model = model
        self.score = []
        for i in range(n):
            self.score.append(dict())

        self.moves = [(-1,-1)] * n

    def setModel(self, model: RummyModel):
        self.__init__(model)


    def getSolution(self):
        temp = []
        for i, move in enumerate(self.moves):
            print(move)
            if len(move[1])>0:
                temp.append(self.score[i][move[1]])
        return temp


    def maxScore(self, value=1, runs=np.zeros(shape=(k, m))):
        if value > n:
            return 0
        runHash = self.getRunHash(runs)
        if runHash in self.score[value-1]:
            print('return memoized val:{}\tscore lengths:{}'.format(self.score[value-1][runHash], list(map(lambda x: len(x), self.score)) ))
            return self.score[value-1][runHash]

        hand = self.model.getTotalTilePool(filter_value=value)
        new_runs,new_hands, run_scores = self.makeRuns(hand, runs, value)
        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value,new_hands[i],run_scores[i])
            groupScores = self.totalGroupSize(new_hands[i]) * value
            result = groupScores + run_scores[i] + self.maxScore(value + 1, new_runs[i])
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores,result)
            print(debugStr)
            if runHash in self.score[value-1]:
                self.score[value-1][runHash] = max(result, self.score[value-1][runHash])
            else:
                self.score[value-1][runHash] = result

            # For storing the solution
            if result > self.moves[value-1][0]:
                self.moves[value-1] = (result, runHash)
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
                    newHand = currTiles[:]
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
        noDuplicates = set(hand)
        for item in noDuplicates:
            hand.remove(item)

        l1 = len(noDuplicates)
        l2 = len(hand)
        return (l1 if l1>=3 else 0) + (l2 if l2>=3 else 0)

    @staticmethod
    def getRunHash(run):
        return str(hash(str(run)))
