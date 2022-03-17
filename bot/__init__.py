from bot.model import *
from bot.controller import *
from bot.detector import startLocalServer
import logging


def main():
    logging.basicConfig(filename='output/debug.log', filemode='w', level=logging.CRITICAL +1)
    startLocalServer()
    # RummySolver(RummyModel(), test_mode=True).outputGraphs()
    return 0

if __name__ == '__main__':
    main()