import board
import unittest

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = board.Board()

    def test_get_index(self):
        self.assertTrue(self.board.get_index(0, 0) == 0)
        self.assertTrue(self.board.get_index(0, 6) == 6)
        self.assertTrue(self.board.get_index(1, 0) == 7)
        self.assertTrue(self.board.get_index(1, 6) == 13)

    def test_play(self):
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 0)
        self.board.play(self.board.red, self.board.columns - 1)
        self.assertTrue(self.board.get_piece(self.board.rows - 1, 0) == self.board.red)
        self.assertTrue(self.board.get_piece(self.board.rows - 2, 0) == self.board.black)
        self.assertTrue(self.board.get_piece(self.board.rows - 1, self.board.columns - 1) == self.board.red)

    def test_get_column(self):
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 1)
        self.board.play(self.board.red, 1)
        self.assertTrue([x[1] for x in self.board._get_column(0)] == [None, None, None, None, None, self.board.red])
        self.assertTrue([x[1] for x in self.board._get_column(1)] == [None, None, None, None, self.board.red, self.board.black])

    def test_get_row(self):
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 1)
        self.board.play(self.board.red, 1)
        self.assertTrue([x[1] for x in self.board._get_row(5)] == [self.board.red, self.board.black, None, None, None, None, None ])
        self.assertTrue([x[1] for x in self.board._get_row(4)] == [None, self.board.red, None, None, None, None, None])

    def test_get_left_diagonal(self):
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 0)
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 1)
        self.board.play(self.board.red, 1)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.red, 2)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.red, 3)
        self.assertTrue([x[1] for x in self.board._get_left_diagonal(3)] == [None, None, None, self.board.red])
        self.assertTrue([x[1] for x in self.board._get_left_diagonal(4)] == [None, None, None, None, self.board.black])
        self.assertTrue([x[1] for x in self.board._get_left_diagonal(5)] == [None, None, None, self.board.black, self.board.red, self.board.red])
        self.assertTrue([x[1] for x in self.board._get_left_diagonal(6)] == [None, None, None, None, self.board.red, self.board.black])
        self.assertTrue([x[1] for x in self.board._get_left_diagonal(-1)] == [None, None, None, None, self.board.black])

    def test_get_right_diagonal(self):
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 0)
        self.board.play(self.board.red, 0)

        self.board.play(self.board.black, 1)
        self.board.play(self.board.red, 1)

        self.board.play(self.board.black, 2)
        self.board.play(self.board.red, 2)
        self.board.play(self.board.black, 2)

        self.board.play(self.board.red, 3)
        self.board.play(self.board.black, 6)
        self.board.play(self.board.red, 5)
        self.board.play(self.board.black, 4)

        self.assertTrue([x[1] for x in self.board._get_right_diagonal(1)] == [None, None, None, None, None, self.board.black])
        self.assertTrue([x[1] for x in self.board._get_right_diagonal(0)] == [None, None, None, None, None, self.board.red])
        self.assertTrue([x[1] for x in self.board._get_right_diagonal(-1)] == [None, None, self.board.black, None, self.board.black])

    def test_find_winner_vertical(self):
        self.board.play(self.board.black, 2)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.black, 2)

        win = self.board.find_winner()
        self.assertTrue(win == None)

        self.board.play(self.board.black, 2)
        win = self.board.find_winner()
        self.assertTrue(win[0] == self.board.black)
        self.assertTrue(win[1] == [16, 23, 30, 37])

    def test_find_winner_horizontal(self):
        self.board.play(self.board.black, 1)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.black, 3)

        win = self.board.find_winner()
        self.assertTrue(win == None)

        self.board.play(self.board.black, 4)
        win = self.board.find_winner()
        self.assertTrue(win[0] == self.board.black)
        self.assertTrue(win[1] == [36, 37, 38, 39])

    def test_find_winner_left_diagonal(self):
        self.board.play(self.board.black, 0)
        self.board.play(self.board.red, 1)
        self.board.play(self.board.black, 1)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.red, 2)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.red, 3)
        self.board.play(self.board.black, 3)
        self.board.play(self.board.red, 3)

        win = self.board.find_winner()
        self.assertTrue(win == None)

        self.board.play(self.board.black, 3)
        win = self.board.find_winner()
        self.assertTrue(win[0] == self.board.black)
        self.assertTrue(win[1] == [17, 23,29, 35])

    def test_find_winner_right_diagonal(self):
        self.board.play(self.board.black, 3)
        self.board.play(self.board.red, 2)
        self.board.play(self.board.black, 2)
        self.board.play(self.board.black, 1)
        self.board.play(self.board.red, 1)
        self.board.play(self.board.black, 1)
        self.board.play(self.board.red, 0)
        self.board.play(self.board.black, 0)
        self.board.play(self.board.red, 0)

        win = self.board.find_winner()
        self.assertTrue(win == None)

        self.board.play(self.board.black, 0)
        win = self.board.find_winner()
        self.assertFalse(win == None)
        self.assertTrue(win[0] == self.board.black)
        self.assertTrue(win[1] == [14, 22, 30, 38])

if __name__ == "__main__":
    unittest.main()
