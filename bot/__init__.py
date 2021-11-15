from bot.model import *
from bot.controller import *
from bot.view import *
from bot.detector import startLocalServer
import logging


def main():
    logging.basicConfig(filename='output/debug.log', level=logging.WARNING)
    startLocalServer()
    return 0

if __name__ == '__main__':
    main()