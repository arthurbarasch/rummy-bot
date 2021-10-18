import unittest
from builtins import int

from bot import RummyModel,RummySolver, RummyController, RummyView, runRummyGame


class RummyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.model = runRummyGame(solve=False)

    def tearDown(self) -> None:
        super().tearDown()

    # Model Tests
    def test_draw_tile(self):
        before = self.model.drawPile[:]
        self.model.drawTile(0,1)
        after = self.model.drawPile[:]
        for item in after:
            before.remove(item)
        test = len(before)==1 and before[0] in self.model.players[0]
        self.assertTrue(test)

    # Solver Tests
    # def test_make_runs(self):
    #     solver = RummySolver(self.model)
    #


if __name__ == '__main__':
    unittest.main()
