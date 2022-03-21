from bot.model import *
from bot.controller import *
from bot.detector import startLocalServer
import logging
import sys


def main(argv):
    logging.basicConfig(filename='output/debug.log', filemode='w', level=logging.ERROR)
    if '--graphs' in argv:
        RummySolver(RummyModel(), test_mode=True).outputGraphs()
    else:
        startLocalServer()

    return 0

if __name__ == '__main__':
    main(sys.argv)