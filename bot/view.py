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

    states_opt = []
    times_opt = []

    padding = 3

    sample_range = range(padding,52,3)
    repetitions = 50

    for i in sample_range:
        states.append([])
        times.append([])
        states_opt.append([])
        times_opt.append([])
        scores.append([])

        for x in range(repetitions):
            print(f'Input size = {i}\nRepetition number = {x}\n')
            model = RummyModel()
            tiles = random.choices(model.drawPile, k=i)
            model.getCurrentPlayer().extend(tiles)

            solver = RummySolver(model,track_solution=False)
            score = 0

            try:
                start_time = time.time()
                score = solver.maxScore()
            except AssertionError as e:
                print("AssertionError")
            finally:
                duration = time.time()-start_time
                states[-1].append(sum(solver.counter))
                times[-1].append(duration)
                scores[-1].append(max(score,0))


            solver = RummySolver(model,track_solution=True)
            try:
                start_time = time.time()
                score = solver.maxScore()
            except AssertionError as e:
                print("AssertionError")
                # print(e)
            finally:
                duration = time.time()-start_time
                states_opt[-1].append(sum(solver.counter))
                times_opt[-1].append(duration)


    avg_states = [np.mean(s) for s in states]
    avg_states_opt = [np.mean(s) for s in states_opt]
    print("Plotting graphs...")
    print(avg_states)
    print(avg_states_opt)


    # plt.plot(avg_states,label='Score only')
    plt.plot(avg_states_opt)
    plt.legend(loc="upper left")
    plt.title(f"Search tree nodes given input size")
    plt.xlabel("Input size (number of tiles)")
    plt.ylabel("Number of nodes calculated")
    plt.xticks(range(len(states)),list(sample_range))
    plt.show()

    avg_times = [np.mean(t) for t in times]
    avg_times_opt = [np.mean(t) for t in times_opt]
    print(avg_times)
    print(avg_times_opt)

    scatter_x = [[s]*repetitions for s in list(sample_range)]
    scatter_x = np.array(scatter_x).flatten()
    print("Scatter x")
    print(scatter_x)

    plt.plot(sample_range,avg_times_opt,label='Solution tracking')
    plt.plot(sample_range,avg_times,label='Score only')
    plt.scatter(scatter_x,times)
    plt.legend(loc="upper left")
    plt.title(f"Execution duration")
    plt.xlabel("Input size (number of tiles)")
    plt.ylabel("Duration (in ms)")
    plt.xticks(sample_range,list(sample_range))
    plt.show()


    avg_scores = [np.mean(s) for s in scores]

    plt.plot(avg_scores)
    plt.title(f"Average score achieved")
    plt.xlabel("Input size (number of tiles)")
    plt.ylabel("Score")
    plt.xticks(range(len(avg_scores)),list(sample_range))
    plt.show()

