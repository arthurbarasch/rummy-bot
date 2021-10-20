from bot.view import RummyView
from bot.model import *
from bot.solver import RummySolver
from flask import request, app
import time


class RummyController:
    def __init__(self, model, view):
        assert isinstance(model,RummyModel)
        assert isinstance(view,RummyView)
        self.model = model
        self.view = view
        self.solver = RummySolver(self.model)

    def promptAction(self):
        action = ''
        while action != 'A' and action != 'B':
            action = input('\nPlayer {}, choose an action:\n-------------------\n\nA. Draw tile\nB. Make moves\n'.format(self.model.playerTurn))
            action = action[0].capitalize()

        if(action == 'A'):
            self.model.drawTile(self.model.playerTurn)

        if(action == 'B'):
            while action != 's':
                action = input('')

        self.model.nextPlayer()

    def runSolver(self):
        self.solver.setModel(self.model)
        self.solver.maxScore()


def runRummyGame(solve=True):
    model = RummyModel()
    view = RummyView()
    controller = RummyController(model, view)
    model.start()

    if solve:
        # Insert example game states here
        model.addRun([(1,10), (1,11), (1,12), (1,13)])
        model.addRun([(4,11),(4,12),(4,13),(4,14)])

        print('Computing max score for current game state:')
        print(model.getTotalTilePool())
        start = time.time()
        solver = RummySolver(model)
        score = solver.maxScore()
        print('Solution found in {} ms'.format((time.time()-start)*1000 ))
        print('Maximum score for this state: {}'.format(score))
        print('Solution: (length {})'.format(len(solver.getSolution())))
        print(str(solver.getSolution()))
    return model
