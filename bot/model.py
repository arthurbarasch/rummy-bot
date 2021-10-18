import random
import numpy as np
import json

# Variables
NUM_PLAYERS = 2
m = 2  # Number of copies of the full tile set (without jokers)
j = 2  # Number of jokers
n = 13 # Number of different numbered values of tiles
k = 4  # Number of different suits

# Sets
K = [chr(i) for i in range(65, 65+k)]  # Set of suits
N = list(range(1, n+1))  # Set of numbered values



class RummyModel:
    def __init__(self):
        self.board = {'runs': [], 'groups': []}
        self.players = [[] for i in range(NUM_PLAYERS)]
        self.drawPile = []
        self.playerTurn = 0
        for suit in K:
            for val in N:
                self.drawPile += [suit + str(val)]

        temp = self.drawPile[:]
        for i in range(m - 1):
            self.drawPile.extend(temp)

        self.drawPile.extend(['joker'] * j)

    def start(self):
        assert NUM_PLAYERS > 0
        assert n == len(N)
        assert k == len(K)

        # Distribute 14 random tiles to each player
        for i in range(NUM_PLAYERS):
            self.drawTile(i, 14)

    # Params:
    # playerIndex - Player who is drawing the tile
    # n - number of tiles to draw
    def drawTile(self, playerIndex, n=1):
        for i in range(n):
            r = random.randrange(1, len(self.drawPile))
            tile = self.drawPile.pop(r)
            self.players[playerIndex].append(tile)

    def nextPlayer(self):
        self.playerTurn = (self.playerTurn + 1) % NUM_PLAYERS

    def getCurrentPlayer(self):
        if(self.playerTurn>=0 and self.playerTurn<len(self.players)):
            return self.players[self.playerTurn]

    #Return the tile pool which is defined to be the board + current player tiles
    def getTotalTilePool(self):
        temp = self.getCurrentPlayer()[:]
        for run in self.board.get('runs'):
            temp.extend(run)
        for group in self.board.get('groups'):
            temp.extend(group)
        temp.sort()
        return temp

    def isGameOver(self):
        for p in self.players:
            if (len(p) == 0):
                return True
        return False

    def addGroup(self, group):
        assert len(group) >= 3
        temp = [tile[0] for tile in group]
        assert len(temp) == len(set(temp)) # Ensure all tiles in group have unique colors
        temp = [tile[1:] for tile in group]
        assert len(set(temp)) == 1 # Ensure all tiles in group have same numbered value
        self.board['groups'].append(group)
        return True


    def addRun(self, run):
        assert len(run) >= 3
        suit = run[0][0]
        value = 0
        for tile in run:
            if suit != tile[0]:
                return False
            if value == 0:
                value = int(tile[1:])
                continue
            if value != int(tile[1:]) - 1:
                print('ERROR: cannot add run because of tile '+tile)
                return False
            value = int(tile[1:])

        self.board["runs"].append(run)
        return True

    def encodeJSON(self):
        return json.dumps({
            'board':self.board,
            'players':self.players,
            'playerTurn':self.playerTurn
        })




    def __str__(self):
        str = 'Board: {}\nDraw pile: {}\nPlayers:{}'
        return str.format(self.board, self.drawPile, self.players)
