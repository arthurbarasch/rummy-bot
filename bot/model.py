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
K = list(range(1, k+1))  # Set of suits
N = list(range(1, n+1))  # Set of numbered values



class RummyModel:
    def __init__(self,model=None):
        assert model is None or model.isinstance(RummyModel)
        self.board = {'runs': [], 'groups': []} if not model else model.board
        self.players = [[] for i in range(NUM_PLAYERS)] if not model else model.players
        self.playerTurn = 0 if not model else model.playerTurn
        if not model:
            self.drawPile = []
            for suit in K:
                for val in N:
                    self.drawPile += [(suit,val)]

            # Copy the full tile set 'm' times
            temp = self.drawPile[:]
            for i in range(m - 1):
                self.drawPile.extend(temp)

            self.drawPile.extend([(0,0)] * j) # (0,0) is used to signify a joker
        else:
            self.drawPile = model.drawPile

    def giveAllTilesToCurrentPlayer(self):
        self.drawTile(self.playerTurn, k*n*m)

    def restart(self):
        self.__init__()

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
            if len(self.drawPile)>0:
                r = random.randrange(0, len(self.drawPile))
                tile = self.drawPile.pop(r)
                self.players[playerIndex].append(tile)

    def nextPlayer(self):
        self.playerTurn = (self.playerTurn + 1) % NUM_PLAYERS

    def getCurrentPlayer(self):
        if(self.playerTurn>=0 and self.playerTurn<len(self.players)):
            return self.players[self.playerTurn]

    # Return the tile pool which is defined to be the board + current player tiles
    # Params:
    # filter_value - if specified, return the tile pool filtered out on the given 'filter_value',
    #     so only return available tiles of that value, of any suit (useful for MaxScore)
    def getTotalTilePool(self, filter_value=None):
        temp = self.getCurrentPlayer()[:]
        for run in self.board.get('runs'):
            temp.extend(run)
        for group in self.board.get('groups'):
            temp.extend(group)
        if n:
            return sorted(list(filter(lambda tile: tile[1] == filter_value, temp)),key=lambda tile: tile[1])
        else:
            return sorted(temp,key=lambda tile: tile[1])

    def isGameOver(self):
        for p in self.players:
            if (len(p) == 0):
                return True
        return False

    def addRandomHand(self):
        hand = ''
        while hand == '' or not (self.addRun(hand) or self.addGroup(hand)):
            if random.random()>0.5:
                tile = random.choice(self.drawPile)
                length = random.randrange(3, 6)
                hand = [(tile[0], val) for val in range(tile[1], tile[1]+length)]
            else:
                tile = random.choice(self.drawPile)
                hand = [(suit, tile[1]) for suit in K]


    def addGroup(self, group):
        if len(group) < 3:
            return False
        temp = [tile[0] for tile in group]
        if len(temp) != len(set(temp)): # Ensure all tiles in group have unique colors
            return False
        temp = [tile[1] for tile in group]
        if len(set(temp)) != 1: # Ensure all tiles in group have same numbered value
            return False
        for g in group:
            if g not in self.drawPile:
                return False

        self.board['groups'].append(group)
        return True


    def addRun(self, run):
        assert len(run) >= 3
        suit = run[0][0]
        value = 0
        for tile in run:
            if tile not in self.drawPile:
                return False
            if suit != tile[0]:
                return False
            if value == 0:
                value = tile[1]
                continue
            if value != tile[1] - 1:
                print('ERROR: cannot add run because of tile '+tile)
                return False
            value = tile[1]

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
