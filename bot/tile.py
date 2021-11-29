class RummyTile():
    def __init__(self,tile,belongsToPlayer=None):
        self.suit = tile[0]
        self.value = tile[1]
        self.belongsToPlayer = belongsToPlayer