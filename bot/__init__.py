from bot.model import *
from bot.controller import *
from bot.app import startLocalServer
import logging


def main():
    logging.basicConfig(filename='output/debug.log', filemode='w', level=logging.ERROR)
    startLocalServer()
    return 0

if __name__ == '__main__':
    main()