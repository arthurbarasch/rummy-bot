import random
import numpy as np
import json
import logging
from bot.player import RummyPlayer

# Variables

NUM_PLAYERS = 2
m = 2  # Number of copies of the full tile set (without jokers)
j = 0  # Number of jokers
n = 13 # Number of different numbered values of tiles
k = 4  # Number of different suits

# Sets
K = list(range(1, k+1))  # Set of suits
N = list(range(1, n+1))  # Set of numbered values


class RummyModel:
    def __init__(self,model=None):
        assert model is None or isinstance(model,RummyModel)
        self.board = {'runs': [], 'groups': []} if not model else {'runs': model.board["runs"][:], 'groups': model.board["groups"][:]}
        self.players = [RummyPlayer(i) for i in range(NUM_PLAYERS)] if not model else model.players[:]
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

            #self.drawPile.extend([(0,0)] * j) # (0,0) is used to signify a joker
        else:
            self.drawPile = model.drawPile[:]

    def __repr__(self) -> str:
        return super().__repr__()

    def copySolution(self, model):
        previous = RummyModel(self)
        self.board = model.board
        tiles = self.compareModels(previous)
        logging.warning("Copying solution from board score {} to board score {} ({} player tiles used this round)".format(previous.getBoardScore(), self.getBoardScore(),len(tiles)))
        self.players[self.playerTurn] = tiles

    # Compares current model with input model to determine tiles not present on the intersections of board sets.
    # Return the updated player tiles
    def compareModels(self, model):
        tiles = self.getBoardTilePool()
        for tile in model.getBoardTilePool():
            if tile in tiles:
                tiles.remove(tile)

        player = model.getCurrentPlayer()
        for t in tiles:
            if t in player:
                player.remove(t)
        return player

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

    def getBoardScore(self):
        score = 0
        for group in self.board["runs"] + self.board["groups"]:
            score += sum(map(lambda tile: tile[1], group))
        return score

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

    def getBoardTilePool(self,filter_value=None):
        temp = []
        for run in self.board.get('runs'):
            temp.extend(run)
        for group in self.board.get('groups'):
            temp.extend(group)
        return temp if filter_value is None else list(filter(lambda t: t[1] == filter_value, temp))

    # Return the tile pool which is defined to be the board + current player tiles
    # Params:
    # filter_value - if specified, return the tile pool filtered out on the given 'filter_value',
    #     so only return available tiles of that value, of any suit (useful for MaxScore)
    def getTotalTilePool(self, filter_value=None):
        temp = self.getBoardTilePool()
        temp.extend(self.getCurrentPlayer()[:])
        if filter_value is not None:
            return list(filter(lambda tile: tile[1] == filter_value, temp))
        else:
            return sorted(temp,key=lambda tile: tile[1])


    # Check to see if current model satisfies the table constraint (defined by 'board' parameter)
    # i.e. check wether all tiles that were present in 'previous' board, are also present in current board
    # Params:
    # value - if specified, only check table constraint for tiles of that value
    def checkTableConstraint(self, previousModel, filter_value=None):
        temp = previousModel.getBoardTilePool(filter_value=filter_value)
        for tile in self.getBoardTilePool(filter_value):
            if tile in temp:
                temp.remove(tile)
        return len(temp) == 0


    def isGameOver(self):
        for p in self.players:
            if (len(p) == 0):
                return True
        return False

    # Add a random group or run to the board (given available tiles on the draw pile)
    # return the number of points in the hand added
    def addRandomHand(self):
        hand = None
        while (hand is None) or not (self.addRun(hand) or self.addGroup(hand)):
            if random.random()>0.5:
                tile = random.choice(self.drawPile)
                length = random.randrange(3, 6)
                hand = [(tile[0], val) for val in range(tile[1], tile[1]+length)]
            else:
                tile = random.choice(self.drawPile)
                hand = [(suit, tile[1]) for suit in K]
        score = 0
        for tile in hand:
            score+=tile[1]
        return score


    def addGroup(self, group, useDrawPile=False, usePlayerStand=False):
        if len(group) < 3:
            return False
        temp = [tile[0] for tile in group]
        if len(temp) != len(set(temp)): # Ensure all tiles in group have unique colors
            return False
        temp = [tile[1] for tile in group]
        if len(set(temp)) != 1: # Ensure all tiles in group have same numbered value
            return False

        if useDrawPile:
            for tile in group:
                if tile not in self.drawPile:
                    return False

        if usePlayerStand:
            player = self.getCurrentPlayer()
            for tile in group:
                if tile not in player:
                    logging.error('Attempted to add a tile to the board that the player does not have: {}'.format(tile))
                    return False
                else:
                    player.remove(tile)


        self.board['groups'].append(group)
        return True


    def addRun(self, run):
        if len(run) < 3:
            return False
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
                logging.error('Cannot add run because of tile '+str(tile))
                return False
            value = tile[1]

        self.board["runs"].append(run)
        return True

    def initNewRun(self,tile):
        self.board["runs"].append([tile])

    # Adds the input list of tiles to any runs available
    def addToRuns(self, tiles):
        assert len(tiles)>0
        for run in self.board['runs']:
            if run[-1][1] + 1 == tiles[0][1] and run[-1][0] == tiles[0][0]:
                for tile in tiles:
                    if run[-1][1] + 1 == tile[1] and run[-1][0] == tile[0]:
                        run.append(tile)
                    else:
                        logging.error('Cannot insert tile {} in {}'.format(tile, self.board['runs']))
                        assert False


    # Checks to see if all groups and runs on the board are valid
    # Remove invalid hands
    def validateBoard(self,filter_suit=None):
        prev = RummyModel(self)
        self.board["runs"] = []
        self.board["groups"] = []
        valid = True
        for run in prev.board["runs"]:
            if filter_suit and run[0][0] != filter_suit:
                self.board["runs"].append(run)
                continue
            if not self.addRun(run):
                valid = False
        for group in prev.board["groups"]:
            if not self.addGroup(group):
                valid = False
        return valid

    # Encode current state
    def encodeJSON(self):
        return json.dumps({
            'board':self.board,
            'players':[p.tiles for p in self.players],
            'playerTurn':self.playerTurn
        })

    def decodeJSON(self, data):
        self.board["runs"] = []
        self.board["groups"] = []
        data = json.loads(data)
        print(data)
        set = []
        last = len(data["board"])
        if last >= 0 and data["board"][last-1] != '':
            data["board"].append('')

        for tile in data['board']:
            # Empty string '' represents a break between sets in the frontend
            if tile != '':
                # Frontend returns tiles as lists instead of tuple, make conversion
                set.append((tile[0], tile[1]))
            elif not self.addRun(set) and not self.addGroup(set):
                # Try adding the set to the model as a run or group
                # If neither is valid, return False (board invalid)
                return False
            else:
                set = []

        for i, tiles in enumerate(data['players']):
            # Frontend returns tiles as lists instead of tuple, make conversion
            self.players[i].clearTiles()
            self.players[i].extend(tiles)

        assert len(self.players) == NUM_PLAYERS
        return True

    def __str__(self):
        str = 'Board: {}\nDraw pile({}): {}\nPlayers({},{}):{}'
        return str.format(self.board, len(self.drawPile),self.drawPile, len(self.players[0]),len(self.players[1]), self.players)
