from bot.view import RummyView
from bot.model import *
from bot.solver import RummySolver
from flask import request, app
import time
from threading import Timer


class RummyController:
    def __init__(self, model:RummyModel, view:RummyView):
        assert isinstance(model,RummyModel)
        assert isinstance(view,RummyView)
        self.model = model
        self.view = view
        self.solver = RummySolver(self.model)
        self.botPlayer = NUM_PLAYERS-1

    def setModel(self, model:RummyModel):
        self.__init__(model, self.view)


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
        return self.solver.maxScore()

    def nextPlayer(self):
        self.model.nextPlayer()
        if self.model.playerTurn == self.botPlayer:
            Timer(1.0, self.makeMoveBot).start()

    def makeMoveBot(self):
        self.solver.setModel(self.model)
        score, solution = self.solver.maxScore()
        if score>=30:
            self.model.copySolution(solution)
        else:
            self.model.drawTile(self.model.playerTurn)
        Timer(1.0, self.nextPlayer).start()

def runRummyGame(solve=True):
    model = RummyModel()
    view = RummyView()
    controller = RummyController(model, view)
    #model.start()
    model.addGroup([(1,13),(2,13),(3,13)],useDrawPile=True)
    model.addRun([(1,11),(1,12),(1,13)])
    if solve:
        # Insert example game states here
        print('Computing max score for current game state:')
        print(model.getTotalTilePool())
        start = time.time()
        score,solution = controller.runSolver()
        print('Solution found in {} ms'.format((time.time()-start)*1000 ))
        print('Maximum score for this state: {}'.format(score))
        print('Solution:')
        print(str(solution))
        print(controller.solver.score)

    return model, view, controller
