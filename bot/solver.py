from bot.model import m, n, k, RummyModel, K, SUIT_COLORS, N
import math
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time
import seaborn as sn
import pandas as pd
import imageio

class RummySolver:
    def __init__(self, model: RummyModel, test_mode = False):
        self.setModel(model)
        self.test_mode = test_mode

    def setModel(self, model: RummyModel):
        self.model = model
        self.counters = {'recursions':np.zeros(n), 'memoization_prunes': np.zeros(n),'tb_constraint_prunes': np.zeros(n),'best_runs':[]}
        self.score = []
        for i in range(n):
            self.score.append(dict())
        self.solution = None

    # Collects data over multiple runs of MaxScore with different parameters.
    # Output's graph's of collected data to /output/fig.png
    def outputGraphs(self):
        assert False # Ensure assertions are disabled for optimizing running MaxScore
        n_repetitions = 40 # Number of repetitions per run. Results are averaged accross repetitions
        x_range = np.arange(10,50,5)
        recursions = []
        scores = []
        exec_times = []
        for i, handSize in enumerate(x_range):
            recursion, score, exec_time = np.zeros(n_repetitions),np.zeros(n_repetitions),np.zeros(n_repetitions)
            for rep in range(n_repetitions):
                model = RummyModel()
                model.drawTile(0,handSize)
                self.setModel(model)
                start = time.time()
                score[rep] = self.maxScore(quarantine=False)
                exec_time[rep] = time.time()-start
                recursion[rep] = sum(self.counters.get('recursions'))
                progress = math.floor(((n_repetitions*i)+rep)/(len(x_range)*n_repetitions)*100)
                print('{}% {} {}/{} (took {:.3f} s)'.format(progress,'*'*progress, (n_repetitions*i)+rep, len(x_range)*n_repetitions, exec_time[rep]))
            recursions.append(np.median(recursion))
            exec_times.append(exec_time)
            scores.append(np.median(score))

        fig, axs = plt.subplots(3,1,figsize=(18, 22))
        ax = axs[0]
        ax.set_title('RummySolver efficiency')
        y_range = scores
        ax.plot(x_range,y_range)
        ax.plot(x_range,[30]*len(x_range), '--', color='red', label="Quarantine threshold")
        ax.legend()
        ax.set_xlabel('Hand size')
        ax.set_ylabel('Score')

        ax = axs[1]
        ax.set_title('RummySolver states')
        y_range = recursions
        ax.plot(x_range,y_range,color='orange')
        ax.set_xlabel('Hand size')
        ax.set_ylabel('# of states generated')

        ax = axs[2]
        ax.set_title('RummySolver performance')
        y_range = exec_times
        plt.boxplot(y_range,showfliers=False)
        plt.xticks(np.arange(len(x_range)),x_range) #TODO fix x ticks
        ax.set_xlabel('Hand size')
        ax.set_ylabel('Execution time (s)')
        plt.rcParams.update({
            "font.family": "serif",  # use serif/main font for text elements
            "text.usetex": True,  # use inline math for ticks
            "pgf.rcfonts": False,  # don't setup fonts from rc parameters
            "pgf.preamble": "\n".join([
                r"\usepackage{url}",  # load additional packages
                r"\usepackage{unicode-math}",  # unicode math setup
                r"\setmainfont{DejaVu Serif}",  # serif font via preamble
            ])
        })
        plt.savefig('output/fig.pdf') # Use pgf backend for outputting graphs styled for LaTex https://matplotlib.org/stable/tutorials/text/pgf.html

    def displayRunsArray(self):
        for i in range(n):
            maxRun = max(self.score[i].items(),key=(lambda x:x[1]))[1][1]

            print(maxRun)
            df = pd.DataFrame(maxRun,K,list(range(m)))
            df.style.background_gradient(cmap='Blues')
            figure = sn.heatmap(df, annot=True, cmap='coolwarm',linecolor='white',linewidths=1).get_figure()
            figure.savefig('output/runs'+i+'.png', dpi=400)

        with imageio.get_writer('runs.gif', mode='I') as writer:
            for filename in ['output/runs'+i+'.png' for i in range(n)]:
                image = imageio.imread(filename)
                writer.append_data(image)

    def displayCounters(self):
        print('#+#+#+#+#+#+#+#+#+#+# RECURSION COUNTERS #+#+#+#+#+#+#+#+#+#+#')
        print('Total number of recursive calls to MaxScore: {}'.format(sum(self.counters.get('recursions'))))
        print('Total number of branches pruned due to memoization: {}'.format(sum(self.counters.get('memoization_prunes'))))
        print('Total number of branches pruned due to table constraint not satisfied: {}\n\n'.format(sum(self.counters.get('tb_constraint_prunes'))))
        # print('Final score array:\n{}'.format(str(self.score)))
        print('Solution:\n{}'.format(self.solution.getBoardTilePool()))
        # for i, s in enumerate(self.score):
        #     for item in s:
        #         print('{}. (runHash={}) {}'.format(i,item, s[item][1].getBoardTilePool()))

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
        self.solution = RummyModel(self.model)
        self.solution.copySolution(solution)
        # if not self.test_mode:
        #     self.displayCounters()
        return score

    def _maxScore(self, value=1, runs=np.zeros(shape=(k, m)), solution=RummyModel(), quarantine=False):
        # Recursion counter
        if (value-1) < len(self.counters):
            self.counters['recursions'][value - 1] += 1

        # Base case
        if value > n:
            solution.validateBoard()
            return 0, solution
        runHash = self.getRunHash(runs)
        # Base case: memoization stored in 'score' array
        if runHash in self.score[value - 1]:
            logging.warning('\nreturn memoized val:{}\tscore lengths:{}'.format(self.score[value - 1][runHash][0], list(
                map(lambda x: len(x), self.score))))

            self.counters['memoization_prunes'][value - 1] += 1
            return self.score[value - 1][runHash]

        logging.warning('\nSOLUTION:\n' + str(solution))

        # Get available tiles of tile value: 'value' in the union of board + player tiles
        # If player is still in quarantine, they may not use the board tiles yet to make points, so only use player tiles
        hand = self.model.getTotalTilePool(
            filter_value=value) if not quarantine else self.model.getCurrentPlayer().getTilePool(filter_value=value)
        logging.warning('HAND->{}\n'.format(hand))
        # Make runs
        new_runs, new_hands, run_scores, solutions = self.makeRuns(hand, runs, value, solution)
        if(len(new_runs)==0):
            return 0, solution
        for i in range(len(new_runs)):
            debugStr = '({})\tnew_hands:{}\trun_score[i]:{}'.format(value, new_hands[i], run_scores[i])
            groupScores, solutions[i] = self.totalGroupSize(new_hands[i], solutions[i])
            # found = ''
            # if groupScores == 3:
            #     found = 'IN VALUE {} FOUND GROUP:\n{}\n'.format(value,solutions[i])
            groupScores = groupScores * value
            logging.debug(
                '~~~~~~~~~~~~~* DEBUG STRING *~~~~~~~~~~~\n' + debugStr + ' \tgroupscores:{}\tsolution:\n{}\n'.format(
                    groupScores, solutions[i]))
            assert groupScores <= solutions[i].getBoardScore()

            # Check the table constraint with the previous model, unless player is in quarantine
            if quarantine or solutions[i].checkTableConstraint(self.model, value):
                score, solutions[i] = self._maxScore(value + 1, new_runs[i], solutions[i],quarantine)
                result = groupScores + run_scores[i] + score
                if runHash not in self.score[value - 1] or result >= self.score[value - 1][runHash][0]:
                    self.runs = new_runs[i]
                    self.score[value - 1][runHash] = (result, RummyModel(solutions[i]))
            else:
                self.counters['tb_constraint_prunes'][value - 1] += 1
                result = "0 (doesn't satisfy table constraint) "

            # Log the recursion
            debugStr += '\tgroupScores:{}\tresult: {}'.format(groupScores, result)
            if(value == 1):
                logging.debug(debugStr)
        return self.score[value-1][runHash]

    def makeRuns(self, hand, runs, value, solution: RummyModel):
        ret = {'new_runs': [], 'new_hands': [], 'run_scores': [], "solutions": []}

        # makeNewRun - recursive function
        # For each suit, create or extend runs with available tiles
        self.makeNewRun(hand, np.array(runs), (1, value), RummyModel(solution), ret)

        # Assertions about the length of the arrays returned
        assert len(ret['new_runs']) >= 0
        assert sum(
            [len(ret['new_runs']), len(ret['new_hands']), len(ret['run_scores']), len(ret['solutions'])]) / 4 == len(
            ret['new_runs'])
        # assert len(ret['new_runs']) < (m + 2) ** 4
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
            if runs[suit-1][0]>0 or runs[suit-1][1]>0 :
                return
            self.makeNewRun(hand, runs, (suit + 1, value), solution, ret, run_scores)
            return

        # A possibility of no tiles of this sort being used for runs
        self.makeNewRun(hand[:], np.array(runs), (suit + 1, value), RummyModel(solution), ret, run_scores)

        # Iterate over possibilities of creating/extending runs of the given suit, value.
        # We must try tiles in each run individually
        for M in range(m):
            if tilesAvailable == 1 and M == m-1 and runs[suit-1][0] > runs[suit-1][1]:
                continue
            new_runs = np.array(runs)
            new_solution = RummyModel(solution)
            new_score = self.updateRun(new_runs, searchTile, M, new_solution)
            new_hand = hand[:]
            new_hand.remove((suit, value))
            # Recursion over suits
            self.makeNewRun(new_hand, new_runs, (suit + 1, value), new_solution, ret, run_scores + new_score)

        # Add a search branch where both tiles are played in runs (if available)
        if tilesAvailable == m:
            new_runs = np.array(runs)
            new_score = 0
            new_solution = RummyModel(solution)
            for i in range(m):
                new_score += self.updateRun(new_runs, searchTile, i, new_solution)
            new_hand = hand[:]
            new_hand.remove(searchTile)
            new_hand.remove(searchTile)
            # Recursion over suits
            self.makeNewRun(new_hand, new_runs, (suit + 1, value), new_solution, ret, run_scores + new_score)
        return

    # (Destructive method) Updates the runs array with the given tile, and returns the score added
    # Also, keeps track of tiles used in the solution
    def updateRun(self, runs, tile, M, solution: RummyModel):
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
    def totalGroupSize(self, hand, solution: RummyModel):
        if len(hand) < 3:
            return 0, solution

        groups = [[], []]
        for tile in hand:
            if isinstance(tile, list):
                tile = (tile[0], tile[1])
            if tile in groups[0]:
                groups[1].append(tile)
            else:
                groups[0].append(tile)

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
