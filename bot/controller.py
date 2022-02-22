from bot.view import RummyView
from bot.model import *
from bot.solver import RummySolver
from flask import request, app
import time
from threading import Timer

GAME_MODE = {'HUMAN vs. AI': 0,'AI vs. AI': 1}
DELAY = 0.5

class RummyController:
    def __init__(self, model:RummyModel, view:RummyView):
        assert isinstance(model,RummyModel)
        assert isinstance(view,RummyView)

        self.view = view
        self.init(model)


    def init(self, model:RummyModel):
        self.model = model
        self.solver = RummySolver(self.model)
        self.botPlayer = NUM_PLAYERS-1
        self.gameMode = GAME_MODE['HUMAN vs. AI']
        if self.gameMode == GAME_MODE['AI vs. AI']:
            self.nextPlayer()

    def start(self):
        self.model.start()


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
        if (self.gameMode == GAME_MODE['AI vs. AI'] or self.model.playerTurn == self.botPlayer) and not self.model.isGameOver():
            Timer(1.5*DELAY, self.makeMoveBot).start()

    def makeMoveBot(self):
        prev_score = self.model.getBoardScore()
        self.solver = RummySolver(self.model)
        score = self.solver.maxScore(quarantine=self.model.players[self.botPlayer].quarantine)
        if score != self.model.getBoardScore() and (score >= 30+prev_score or not self.model.players[self.botPlayer].quarantine):
            print('RummyBot making moves on the board\n')
            self.model.copySolution(self.solver.solution)
            Timer(3.5*DELAY, self.nextPlayer).start()
        else:
            print('RummyBot making move: Drawing tile\n')
            self.model.drawTile(self.model.playerTurn)
            Timer(2*DELAY, self.nextPlayer).start()

def runRummyGame(solve=True):
    model = RummyModel()
    view = RummyView()
    controller = RummyController(model, view)
    controller.model.start()
    #controller.model.players[controller.botPlayer].extend([(1,9),(1,10),(1,11)])
    #controller.model.getCurrentPlayer().extend([(1,1),(2,1),(3,1)])
    if solve:
        # Insert example game states here
        print('Computing max score for current game state:')
        print(controller.model.getTotalTilePool())
        start = time.time()
        score,solution = controller.runSolver()
        print('Solution found in {} ms'.format((time.time()-start)*1000 ))
        print('Maximum score for this state: {}'.format(score))
        print('Solution:')
        print(str(solution))
        print(controller.solver.score)

    return controller
