import logging


class RummyPlayer(dict):
    def __init__(self, playerNr,human=None, tiles=None):
        self.playerNr = playerNr
        self.tiles = [] if tiles is None else tiles[:]
        self.quarantine = True
        self.human = True if human else human
        return

    def append(self,tile):
        self.tiles.append(tile)

    def clearTiles(self):
        self.tiles = []

    def decodeJSON(self,player):
        logging.warning('Player {} before decode: {}'.format(self.playerNr,self.tiles))
        self.clearTiles()
        for tile in player:
            # Frontend returns tiles as lists instead of tuple, make conversion
            self.append((tile[0], tile[1]))
        logging.info('Player {} after decode: {}'.format(self.playerNr,self.tiles))

    def __contains__(self, item):
        return item in self.tiles

    def __getitem__(self, key):
        return self.tiles[key]

    def __len__(self):
        return len(self.tiles)

    def __str__(self):
        return str(self.tiles)