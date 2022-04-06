from bot.model import *
from bot.solver import RummySolver
import time
from threading import Timer

GAME_MODE = {'HUMAN vs. AI': 0,'AI vs. AI': 1}
DELAY = 0.3

class RummyController:
    def __init__(self, model:RummyModel, gameMode = 'HUMAN vs. AI'):
        self.setModel(model,gameMode)

    def setModel(self, model:RummyModel, gameMode = 'HUMAN vs. AI'):
        assert isinstance(model,RummyModel)
        self.model = model
        self.solver = RummySolver(self.model)
        self.botPlayer = NUM_PLAYERS-1
        self.gameMode = GAME_MODE[gameMode]
        self.model.players[self.botPlayer].human = False


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
        if self.model.isGameOver():
            return True
        self.model.nextPlayer()
        if (self.gameMode == GAME_MODE['AI vs. AI'] or self.model.playerTurn == self.botPlayer):
            Timer(1.5*DELAY, self.makeMoveBot).start()

    def makeMoveBot(self):
        prev_score = self.model.getBoardScore()
        self.solver.setModel(self.model)
        score = self.solver.maxScore(quarantine=False)

        if (score > prev_score) and (not self.model.players[self.model.playerTurn].quarantine or score >= 30+prev_score):
            self.model.players[self.model.playerTurn].quarantine = False
            print('RummyBot making moves on the board (prev score {} new score {})\n'.format(prev_score, score))
            self.model = RummyModel(self.solver.solution)
            Timer(3.5*DELAY, self.nextPlayer).start()
        else:
            print('RummyBot making move: Drawing tile\n')
            self.model.drawTile(self.model.playerTurn)
            Timer(2*DELAY, self.nextPlayer).start()

def runRummyGame(solve=False, gameMode="HUMAN vs. AI"):
    model = RummyModel()
    controller = RummyController(model,gameMode)
    controller.model.start()
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
