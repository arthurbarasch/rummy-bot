import json

class RummyView:
    def RummyView(self):
        self.boardViewJson = '' #string holding JSON information to display board in HTML
        self.players = '' #string holding JSON information to display player tiles in HTML
        return

    def displayBoardTiles(self, board):
        self.boardViewJson = json.dumps(board)
