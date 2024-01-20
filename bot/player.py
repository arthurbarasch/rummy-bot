import logging


class RummyPlayer(list):
    def __init__(self, player=None, playerNr=0):
        self.playerNr = playerNr if player is None else player.playerNr
        self.tiles = [] if player is None else player.tiles[:]
        self.quarantine = True if player is None else player.quarantine
        self.human = True if player is None else player.human
        return

    def getTilePool(self, filter_value=None):
        return list(filter(lambda t: t[1] == filter_value, self.tiles)) if filter_value else self.tiles

    def sortTiles(self):
        self.tiles = sorted(self.tiles, key=lambda tile: tile[1])

    def setTiles(self,tiles):
        self.tiles = tiles

    def extend(self,tile):
        self.tiles.extend(tile)

    def append(self,tile):
        self.tiles.append(tile)

    def remove(self,tile):
        self.tiles.remove(tile)

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
        if len(self.tiles) <= key:
            return None
        return self.tiles[key]

    def __len__(self):
        return len(self.tiles)

    def __str__(self):
        return str(self.tiles)