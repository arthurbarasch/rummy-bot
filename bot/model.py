import copy
import random
import numpy as np
import json
import logging
from bot.player import RummyPlayer
from flask import jsonify
from functools import reduce

# Variables

NUM_STARTING_TILES = 14
NUM_PLAYERS = 2
m = 2  # Number of copies of the full tile set (without jokers)
f_of_m = 10  # In this case for m=2, f(m) = 10
j = 0  # Number of jokers
n = 13  # Number of different numbered values of tiles
k = 4  # Number of different suits
s = 3  # Minimal set size

# Sets
K = list(range(1, k+1))  # Set of suits
N = list(range(1, n+1))  # Set of numbered values


class RummyModel:
    def __init__(self,model=None):
        assert model is None or isinstance(model,RummyModel)
        self.board = {'runs': [], 'groups': []} if not model else self.getBoardCopy(model.board)

        self.playerTurn = 0 if not model else model.playerTurn
        if not model:
            self.generateDrawPile()
            self.players = [RummyPlayer(playerNr=i) for i in range(NUM_PLAYERS)]
        else:
            self.drawPile = model.drawPile[:]
            self.copyPlayers(model.players)

    @staticmethod
    def getBoardCopy(board):
        temp = {'runs': [], 'groups': []}
        for run in board['runs']:
            temp['runs'].append(run[:])
        for group in board['groups']:
            temp['groups'].append(group[:])
        return temp

    def start(self):
        assert NUM_PLAYERS > 0
        assert n == len(N)
        assert k == len(K)

        # Distribute 14 random tiles to each player
        for i in range(NUM_PLAYERS):
            self.drawTile(i, NUM_STARTING_TILES)
    def copyPlayers(self,players):
        self.players = []
        for p in players:
            self.players.append(RummyPlayer(p))

    def __repr__(self) -> str:
        return super().__repr__()

    def generateDrawPile(self):
        self.drawPile = []
        for suit in K:
            for val in N:
                self.drawPile += [(suit, val)]

        # Copy the full tile set 'm' times
        temp = self.drawPile[:]
        for i in range(m - 1):
            self.drawPile.extend(temp)

        # self.drawPile.extend([(0,0)] * j) # (0,0) is used to signify a joker

    def copySolution(self, model):
        previous = RummyModel(self)
        self.board = model.board
        tiles = self.compareModels(previous)

        logging.warning("Copying solution from board score {} to board score {} ({} player tiles used this round)".format(previous.getBoardScore(), self.getBoardScore(),len(tiles)))
        self.players[self.playerTurn] = tiles
        self.correctDrawPile()
        assert self.getBoardScore() == model.getBoardScore()

    # Makes sure that the draw pile has the correct tiles after a player makes a move.
    def correctDrawPile(self):
        self.generateDrawPile()
        for tile in self.getTilesInGame():
            if tile not in self.drawPile:
                logging.error('ERROR: while trying to correctBoard in /model.py/copySolution: tile {} is present more than {} times on the board'.format(tile, m))
            else:
                self.drawPile.remove(tile)


    # Compares current model with input (previous) model to determine tiles not present on the intersections of board sets.
    # Return the updated player tiles
    def compareModels(self, prev):
        tiles = self.getBoardTilePool()
        for tile in prev.getBoardTilePool():
            if tile in tiles:
                tiles.remove(tile)

        player = prev.getCurrentPlayer()
        for t in tiles:
            if t in player:
                player.remove(t)
        return player

    def giveAllTilesToCurrentPlayer(self):
        self.drawTile(self.playerTurn, k*n*m)

    def restart(self):
        self.__init__()

    def getBoardScore(self):
        score = 0
        for group in self.board["runs"] + self.board["groups"]:
            score += sum(map(lambda tile: tile[1], group))
        return score

    # Params:
    # playerIndex - Player who is drawing the tile
    # n - number of tiles to draw
    def drawTile(self, playerIndex, numTiles=1):
        for i in range(numTiles):
            if len(self.drawPile) > 0:
                r = random.randrange(0, len(self.drawPile))
                tile = self.drawPile.pop(r)
                self.players[playerIndex].append(tile)
        self.players[playerIndex].sortTiles()

    def nextPlayer(self):
        self.playerTurn = (self.playerTurn + 1) % NUM_PLAYERS

    def getCurrentPlayer(self):
        if 0 <= self.playerTurn < len(self.players):
             return self.players[self.playerTurn]

    def getBoardAsArray(self):
        arr = [r[:] for r in self.board['runs']]

        arr.extend([g[:] for g in self.board['groups']])
        return arr

    def getBoardTilePool(self, filter_value=None):
        temp = []
        for run in self.board.get('runs'):
            temp.extend(run)
        for group in self.board.get('groups'):
            temp.extend(group)
        return temp if filter_value is None else list(filter(lambda t: t[1] == filter_value, temp))

    # Return the total playable tile pool which is defined to be the board + current player tiles
    # Params:
    # filter_value - if specified, return the tile pool filtered out on the given 'filter_value',
    #     so only return available tiles of that value, of any suit (useful for MaxScore)
    def getTotalTilePool(self, filter_value=None):
        temp = self.getBoardTilePool()
        temp.extend(self.getCurrentPlayer().tiles[:])
        if filter_value is not None:
            return list(filter(lambda tile: tile[1] == filter_value, temp))
        else:
            return sorted(temp, key=lambda tile: tile[1])

    # Return the tile pool which is defined to be the board + all player tiles
    # a.k.a all tiles except draw pile
    def getTilesInGame(self):
        temp = self.getBoardTilePool()
        for p in self.players:
            temp.extend(p.tiles)
        return temp

    # Check to see if current model and 'runs' array satisfy the table constraint (defined by 'board' parameter)
    # i.e. check whether all tiles that were present in 'previous' board, are also present in current board,
    # or in unfinished runs
    # Params:
    # value - if specified, only check table constraint for tiles of that value
    def checkTableConstraint(self, previousModel, runs, filter_value=None):
        temp = previousModel.getBoardTilePool(filter_value=filter_value)

        # Tiles present on the board (in groups or runs)
        for t in self.getBoardTilePool(filter_value=filter_value):
            if t in temp:
                temp.remove(t)

        # # Tiles present on unfinished runs
        for t in temp:
            suit, value = t
            if runs[suit-1][0] == 0 and runs[suit-1][0] == 0:
                return False

        return True

    def isGameOver(self):
        if self.drawPile == 0:
            return True
        for p in self.players:
            if len(p) == 0:
                return True
        return False

    # Add a random group or run to the board (given available tiles on the draw pile)
    # return the number of points in the hand added
    def addRandomHand(self, group=None, useDrawPile=True):
        hand = None
        counter = 0
        while (hand is None) or not (self.addRun(hand) or self.addGroup(hand)):
            counter+=1
            if counter>100:
                return 0

            if random.random() > 0.5 and not group:
                tile = random.choice(self.drawPile)
                length = random.randrange(3, 5)
                if tile[1]+length > n:
                    continue
                hand = [(tile[0], val) for val in range(tile[1], min(tile[1]+length, n))]
            else:
                tile = random.choice(self.drawPile)
                hand = [(suit, tile[1]) for suit in K]

            if useDrawPile and reduce(lambda a,b:a and b ,[tile in self.drawPile for tile in hand]):
                hand = None

        score = 0
        for tile in hand:
            score += tile[1]
        return score

    def addGroup(self, group, useDrawPile=False, usePlayerStand=False):
        if len(group) < 3:
            return False
        temp = [tile[0] for tile in group]
        if len(temp) != len(set(temp)):  # Ensure all tiles in group have unique colors
            return False
        temp = [tile[1] for tile in group]
        if len(set(temp)) != 1:  # Ensure all tiles in group have same numbered value
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

    def addRun(self, run, useDrawPile=False):
        if len(run) < 3:
            return False
        suit = run[0][0]
        value = 0
        for tile in run:
            if useDrawPile and tile not in self.drawPile:
                return False
            if suit != tile[0]:
                return False
            if value == 0:
                value = tile[1]
                continue
            if value + 1 != tile[1] or tile[1]>n:
                logging.error('Cannot add run because of tile '+str(tile))
                return False
            value = tile[1]

        self.board["runs"].append(run)
        return True

    def initNewRun(self, tile):
        self.board["runs"].append([tile])

    # Adds the input tile to an available run available
    # If two available runs for such tile, use the input value 'isLongest' to establish which run
    # to add the tile to (the longest or shortest run)
    def addToRun(self, tile, isLongest=True):
        run1 = None
        run2 = None

        for run in self.board['runs']:
            if run[-1][0] != tile[0]:
                continue

            if run[-1][1]+1 == tile[1]:
                if run1 is None:
                    run1 = run
                else:
                    run2 = run

        if run1 is not None and run2 is None:
            run1.append(tile)
            return True

        if run1 is not None and run2 is not None:
            if len(run1) >= len(run2):
                if isLongest:
                    run1.append(tile)
                else:
                    run2.append(tile)
            else:
                if isLongest:
                    run2.append(tile)
                else:
                    run1.append(tile)
            return True

        msg = 'ERROR: /model.py/addToRuns: Cannot insert tile {} in {}'.format(tile, self.board['runs'])
        logging.error(msg)
        print(msg)
        return False


        # for run in self.board['runs']:
        #     if run[-1][1] + 1 == tiles[0][1] and run[-1][0] == tiles[0][0]:
        #         for tile in tiles:
        #             if run[-1][1] + 1 == tile[1] and run[-1][0] == tile[0]:
        #                 run.append(tile)
        #                 tilesToAdd -= 1
        #             else:
        #                 logging.error('Cannot insert tile {} in {}'.format(tile, self.board['runs']))
        #                 assert False
        #
        # if tilesToAdd != 0:
        #     logging.warning('RummyModel.addToRuns: Cannot insert tiles on runs. Tiles left -> {}'.format(tilesToAdd))
        # return tilesToAdd == 0

    def isValid(self):
        count = np.zeros((k,n))
        for run in self.board["runs"]:
            for suit,value in run:
                count[suit-1,value-1]+=1

                if count[suit-1,value-1] > m:
                    logging.error(f'ERROR: Board is not valid. Found more than {m} occurrences of tile {(suit,value)}')
                    return False

        return True


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
            elif not self.addRun(run):
                valid = False
        for group in prev.board["groups"]:
            if not self.addGroup(group):
                valid = False
        return valid

    # Encode current state
    def encodeJSON(self, app):
        with app.app_context():
            return jsonify(
                    board=self.board,
                    players=[p.tiles for p in self.players],
                    playerTurn=self.playerTurn,
                    drawPileSize=len(self.drawPile)
            )

    def decodeJSON(self, data, app):
        with app.app_context():
            self.board["runs"] = []
            self.board["groups"] = []
            data = json.loads(data)
            logging.info('*======*\nClient data received: data')
            last = len(data["board"])
            if last >= 0 and data["board"][last-1] != '':
                data["board"].append('')

            # Flag for removing double spaces between groups
            newSet = True
            hand = []
            for tile in data['board']:
                # Empty string '' represents a break between sets in the frontend
                if tile != '':
                    # Frontend returns tiles as lists instead of tuple, make conversion
                    hand.append((tile[0], tile[1]))
                    newSet = False
                elif newSet:
                    # Double space between sets returned from the frontend. Simply discard
                    continue
                elif self.addRun(hand) or self.addGroup(hand):
                    # Try adding the set to the model as a run or group
                    hand = []
                    newSet = True
                else:
                    # If neither is valid, return False (board invalid)
                    errMsg = 'ERROR: on decodeJSON:\n | Trying to add set: '+str(hand)+'\n | Not a valid group or run\n'
                    logging.error(errMsg)
                    print(errMsg)
                    return False

            for i, tiles in enumerate(data['players']):
                self.players[i].clearTiles()
                for tile in tiles:
                    if not tile:
                        continue;
                    # Frontend returns tiles as lists instead of tuple, make conversion
                    self.players[i].append((tile[0], tile[1]))

            assert len(self.players) == NUM_PLAYERS
            return True

    def __str__(self):
        SIMPLIFIED = True

        if SIMPLIFIED:
            hands = self.board['runs'][:]
            hands.extend(self.board['groups'])
            return hands.__str__()

        str = 'Board: {}\nDraw pile({})\nPlayers({},{}):{}'
        return str.format(self.board, len(self.drawPile), len(self.players[0]),len(self.players[1]), self.players)
