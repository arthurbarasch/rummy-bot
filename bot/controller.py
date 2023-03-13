from bot.model import *
from bot.solver import RummySolver
import time
from threading import Timer

GAME_MODE = {'HUMAN vs. AI': 0, 'AI vs. AI': 1}
BOT_MOVE_DELAY = 0.7


class RummyController:
    def __init__(self, model: RummyModel,game_mode=GAME_MODE['HUMAN vs. AI']):
        assert isinstance(model, RummyModel)

        self.gameMode = game_mode
        self.model = model
        self.solver = RummySolver(self.model)
        self.botPlayer = NUM_PLAYERS - 1

    def init(self, model: RummyModel):
        self.model = model
        self.solver = RummySolver(self.model)

    def checkWinCondition(self):
        for i in range(NUM_PLAYERS):
            if len(self.model.players[i]) == 0:
                return i
        return False

    def start(self):
        self.model.start()

    def runSolver(self):
        return self.solver.maxScore()

    def nextPlayer(self):
        self.model.nextPlayer()
        if (self.gameMode == GAME_MODE['AI vs. AI'] or
           self.model.playerTurn == self.botPlayer) and not self.model.isGameOver():
            Timer(1.5 * BOT_MOVE_DELAY, self.makeMoveBot).start()

    def isValidMove(self, old, new):
        oldScore = old.getBoardScore()
        newScore = new.getBoardScore()
        return newScore != oldScore and newScore > 0 and (
                newScore-oldScore >= 30 or not self.model.players[self.botPlayer].quarantine) and old.getBoardAsArray() != new.getBoardAsArray()

    def makeMoveBot(self):
        self.solver = RummySolver(self.model)
        score = self.solver.maxScore(quarantine=self.model.players[self.botPlayer].quarantine)

        if self.isValidMove(self.model, self.solver.solution):
            print('RummyBot making moves on the board (best possible score is {})\n'.format(score))
            self.model = RummyModel(self.solver.solution)
            self.model.players[self.botPlayer].quarantine = False
            Timer(3.5 * BOT_MOVE_DELAY, self.nextPlayer).start()
        else:
            print('RummyBot draws a tile (best possible score is {})\n'.format(score))
            self.model.drawTile(self.model.playerTurn)
            Timer(2 * BOT_MOVE_DELAY, self.nextPlayer).start()


def runRummyGame(solve=True, game_mode=GAME_MODE['HUMAN vs. AI']):
    model = RummyModel()
    controller = RummyController(model, game_mode=game_mode)
    controller.model.start()
    # controller.model.getCurrentPlayer().extend([(1, 1), (1, 2), (1, 3), (1, 2), (1, 3), (1, 4)])

    if solve:
        # Insert example game states here
        print('Computing max score for current game state:')
        print(controller.model.getTotalTilePool())
        start = time.time()
        score, solution = controller.runSolver()
        print('Solution found in {} ms'.format((time.time() - start) * 1000))
        print('Maximum score for this state: {}'.format(score))
        print('Solution:')
        print(str(solution))
        print(controller.solver.score)

    return controller
