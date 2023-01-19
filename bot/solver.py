from bot.model import m, n, k, RummyModel, K
import math
import logging
import numpy as np


class RummySolver:
    def __init__(self, model: RummyModel):
        self.model = model
        self.score = []
        self.counter = []
        for i in range(n):
            self.score.append(dict())
            self.counter.append(0)
        self.solution = None

    def setModel(self, model: RummyModel):
        self.__init__(model)

    def displayCounter(self):
        for i, c in enumerate(self.counter):
            print(str(i+1) + '. ' + '*' * c)

    def traceSolution(self, runHash):
        solutions = []
        while runHash != '':
            for i in range(n):
                if runHash in self.score[i]:
                    solutions.append(self.score[i][runHash][1])
                    runHash = self.score[i][runHash][2]
                    continue
        return solutions

    def maxScore(self, quarantine=False):
        score, solution = self._maxScore(quarantine=quarantine)
        self.solution = solution
        self.displayCounter()
        return score

    def _maxScore(self, value=1, runs=np.zeros(shape=(k, m)), solution=RummyModel(), quarantine=False):
        # Recursion counter
        if value -1 < len(self.counter):
            self.counter[value - 1] += 1

        # Base case
        if value > n:
            return 0, solution
        runHash = self.getRunHash(runs)
        # Base case: memoization stored in 'score' array
        if runHash in self.score[value - 1] and self.score[value - 1][runHash][0] > -math.inf:
            logging.warning('\nreturn memoized val:{}\tscore lengths:{}'.format(self.score[value - 1][runHash][0], list(
                map(lambda x: len(x), self.score))))
            return self.score[value - 1][runHash]

        logging.warning('\nSOLUTION:\n' + str(solution))

        # Get available tiles of tile value: 'value' in the union of board + player tiles
        # If player is still in quarantine, they may not use the board tiles yet to make points, so only use player tiles
        hand = self.model.getTotalTilePool(
            filter_value=value) if not quarantine else self.model.getCurrentPlayer().getTilePool(filter_value=value)

        # Make runs
        new_runs, new_hands, run_scores, solutions = self.makeRuns(hand, runs, value, solution)

        if len(new_runs) == 0:
            # if runHash not in self.score[value-1]:
            #     self.score[value - 1][runHash] = (-math.inf, solution)

            return 0, solution


        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value, new_hands[i], run_scores[i])
            new_solution = solutions[i]

            if(run_scores[i]>0):
                logging.warning(run_scores[i])

            groupScores, new_solution = self.totalGroupSize(new_hands[i], new_solution)
            groupScores = groupScores * value
            logging.debug(
                '~~~~~~~~~~~~~* DEBUG STRING *~~~~~~~~~~~\n' + debugStr + ' \tgroupscores:{}\tsolution:\n{}\n'.format(
                    groupScores, new_solution))
            assert groupScores <= new_solution.getBoardScore()

            # Check the table constraint with the previous model
            if solution.checkTableConstraint(self.model, value):
                score, new_solution = self._maxScore(value + 1, new_runs[i], new_solution)
                result = groupScores + run_scores[i] + score
                if runHash not in self.score[value - 1] or result > self.score[value - 1][runHash][0]:
                    self.score[value - 1][runHash] = (result, new_solution)
            else:
                result = "-inf (doesn't satisfy table constraint) "
                if runHash not in self.score[value - 1]:
                    self.score[value - 1][runHash] = (-math.inf, new_solution)

            # Log the recursion
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores, result)
            logging.warning(debugStr)

        return self.score[value - 1][runHash]

    def makeRuns(self, hand, runs, value, solution: RummyModel):
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}
        # # Finish runs that cannot be continued (due to lack of tiles)
        # for suit in K:
        #     for M in range(m):
        #         searchTile = (suit, value)
        #         if not searchTile in hand and runs[suit - 1, M] > 0:
        #             runs[suit - 1, M] = 0
        #             solution.validateBoard(filter_suit=suit)

        # makeNewRun - recursive function
        # For each suit, create or extend runs with available tiles
        self.makeNewRun(hand, np.array(runs), (1, value), RummyModel(solution), ret)

        # Assertions about the length of the arrays returned
        assert sum(
            [len(ret['new_runs']), len(ret['new_hands']), len(ret['run_scores']), len(ret['solutions'])]) / 4 == len(
            ret['new_runs'])
        assert len(ret['new_runs']) < (m + 2) ** 4
        return ret['new_runs'], ret['new_hands'], ret['run_scores'], ret['solutions']

    def makeNewRun(self, hand, runs, searchTile, solution, ret, run_scores=0):
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
            if (runs[suit-1][0]>0 and  runs[suit-1][0]<3) or (runs[suit-1][1]>0 and runs[suit-1][1]<3):
                ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}
                return

            runs[suit - 1][0] = 0
            runs[suit - 1][1] = 0
            self.makeNewRun(hand, runs, (suit + 1, value), solution, ret, run_scores)
            return


        # Iterate over possibilities of creating/extending runs of the given suit, value.
        # (m+1) because we must try tiles in each run individually, and also in both runs at once.
        for M in range(m + 1):
            new_run = np.array(runs)

            if M + 1 > m and m >= 2:
                # Break if there are no (m=2) tiles
                if tilesAvailable != m:
                    break
                else:
                    new_score = 0
                    new_hand = hand[:]
                    logging.warning("TRYING BOTH AT SAME TIME")
                    for i in range(m):
                        new_score += self.updateRun(new_run, searchTile, i, solution)
                        logging.warning('NEW SCORE({}):{}'.format(i,new_score))
                        new_hand.remove((suit, value))

                    # Recursion over suits
                    self.makeNewRun(new_hand, new_run, (suit + 1, value), solution, ret, run_scores + new_score)
            else:
                # If the runs value of both m=1 and m=2 are equal, there is no need
                # to try both runs
                if runs[suit - 1, 0] == runs[suit - 1, 1] and M == 1:
                    continue

                new_score = self.updateRun(new_run, searchTile, M, solution)
                new_hand = hand[:]
                new_hand.remove((suit, value))
                # Recursion over suits
                self.makeNewRun(new_hand, new_run, (suit + 1, value), solution, ret, run_scores + new_score)

        # An extra possibility of no tiles of this sort being used for runs
        self.makeNewRun(hand, new_run, (suit + 1, value), solution, ret, run_scores)


    # def extendBranch(self, ret, add):
    #     ret['new_runs'].extend(add['new_runs'])
    #     ret['new_hands'].extend(add['new_hands'])
    #     ret['run_scores'].extend(add['run_scores'])
    #     ret['solutions'].extend(add['solutions'])
    #     return ret

    # (Destructive method) Updates the runs array with the given tile, and returns the score added
    # Also, keeps track of tiles used in the solution
    def updateRun(self, runs, tile, M, solution: RummyModel):
        suit, value = tile
        runVal = runs[suit - 1, M]

        if runVal == 0:
            if value + 3 >= n:
                # No need to start a new run if we know we can't finish it
                return 0

            logging.warning('STEP 1')
            runs[suit - 1, M] += 1
            return 0
        elif runVal == 1:  # If current length of run 0 or 1, increase length by one
            logging.warning('STEP 2')
            runs[suit - 1, M] += 1
            return 0
        elif runVal == 2:  # If current length of run 2, increase length by one and make it a valid run (summing the score so far)
            logging.warning('STEP 3')
            runs[suit - 1, M] += 1

            r = [(suit, value-2), (suit, value-1), tile]
            solution.addRun(r)
            logging.warning('Added new run -> '+str(r))
            assert len(solution.board['runs']) > 0
            return (value - 2) + (value - 1) + value
        elif runVal >= 3:  # If current length of run 3 (which can also mean more than 3), increase the score by the current tile value
            assert solution.addToRuns([tile])
            return value

    # Return the total group size that can be formed from the given 'hand'
    def totalGroupSize(self, hand, solution: RummyModel):
        if len(hand) < 3:
            return 0, solution

        # TODO: Generalize over 'm'
        g1 = list(set(hand))
        g2 = hand
        for tile in g1:
            g2.remove(tile)

        #Special case for when a group has length 4 and the other length 2
        if len(g1) == 4 and len(g2) ==2:
            for t in g1:
                if t not in g2:
                    g1.remove(t)
                    g2.append(t)
                    break

        groups = [g1, g2]
        l1 = len(groups[0])
        l2 = len(groups[1])


        if l1 >= 3:
            lengroups = len(solution.board['groups'])
            solution.addGroup(groups[0])
            if lengroups + 1 != len(solution.board['groups']):
                logging.error('ERROR: on /solver.py/totalGroupSize > tried adding {} as a group'.format(groups[0]))
                return 0, solution

        if l2 >= 3:
            solution.addGroup(groups[1])
        return ((l1 if l1 >= 3 else 0) + (l2 if l2 >= 3 else 0)), solution

    @staticmethod
    def getRunHash(run):

        return str(hash(str(run)))
