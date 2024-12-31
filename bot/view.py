from matplotlib import pyplot as plt
import numpy as np
from solver import RUN_CONFIGS, RummySolver
import random
from model import k, n, m, COLORS, RummyModel

import time

def getDotNode(arr):
    # Change formatting to HTML for .dot
    if len(arr) == 0:
        return '"[]"'

    dotStr = '<'
    colors = ['black', 'blue', 'orange', 'red']

    first = True
    for a in arr:
        if first:
            first = False
        else:
            dotStr += '-'

        firstTile = True
        for tile in a:
            if firstTile:
                firstTile = False
            else:
                dotStr += ','
            dotStr += '<FONT COLOR="{}">{}</FONT>'.format(colors[tile[0] - 1], tile[1])

    dotStr += '>'

    return dotStr

def plot_runs_graph(ordered_runs):

    for i, run_hash in enumerate(ordered_runs):

        data = np.zeros(k)
        for j in range(k):
            data[j] = run_hash[j]

        bar_colors = ['black', 'blue', 'yellow', 'red']
        plt.bar(COLORS,data, color=bar_colors)
        plt.title(f"Runs lengths at value {i+1}")
        plt.yticks(range(10),[list(r) for r in RUN_CONFIGS])

        plt.show()


def plot_times_graph():

    states = []
    times = []
    scores = []

    padding = 12

    sample_range = range(padding,53,2)
    repetitions = 100

    for i in sample_range:
        states.append([])
        times.append([])
        scores.append([])
        for x in range(repetitions):
            model = RummyModel()
            tiles = random.choices(model.drawPile,k=i)
            model.getCurrentPlayer().extend(tiles)

            solver = RummySolver(model)

            try:
                start_time = time.time()
                score = solver.maxScore()
                duration = time.time()-start_time
            except AssertionError:
                print("AssertionError")
                continue
            else:
                states[-1].append(sum(solver.counter))
                times[-1].append(duration)
                scores[-1].append(max(score,0))

    plt.boxplot(states,showfliers=False)
    plt.title(f"Search tree nodes given input size")
    plt.xlabel("Input size (number of tiles)")
    plt.ylabel("Number of nodes calculated")
    plt.xticks(range(len(states)),list(sample_range))
    plt.show()

    avg_times = [np.mean(t) for t in times]
    plt.plot(avg_times)
    plt.title(f"Execution duration")
    plt.xlabel("Input size (number of tiles)")
    plt.ylabel("Duration (in ms)")
    plt.xticks(range(len(avg_times)),list(sample_range))
    plt.show()


    avg_scores = [np.mean(s) for s in scores]

    plt.boxplot(avg_scores,showfliers=False)
    plt.title(f"Average score achieved")
    plt.xlabel("Input size (number of tiles)")
    plt.ylabel("Score")
    plt.xticks(range(len(avg_scores)),list(sample_range))
    plt.show()


