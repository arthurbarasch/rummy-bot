from matplotlib import pyplot as plt

from bot import RummySolver


def plot_runs_graph(ordered_runs):


    run_hash = ordered_runs[0]
    ms = RummySolver.getMultisetFromHash(run_hash)

    plt.show()