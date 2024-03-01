from matplotlib import pyplot as plt
import numpy as np
from solver import RUN_CONFIGS
from model import k,n,m, COLORS


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
