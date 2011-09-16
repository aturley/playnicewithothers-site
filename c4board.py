class Board (object):
    def __init__(self):
        self.rows = 6
        self.columns = 7
        self.min_side = min(self.rows, self.columns)
        self.board_size = self.rows * self.columns
        # The board is row-dominant.
        #    0  1  2  3  4  5  6
        #   --------------------
        # 0| 0  1  2  3  4  5  6
        # 1| 7  8  9 10 11 12 13
        # 2|14 15 16 17 18 19 20
        # 3|21 22 23 24 25 26 27
        # 4|28 29 30 31 32 33 34
        # 5|35 36 37 38 39 40 41
        self.board_array = [None for item in xrange(self.rows * self.columns)]
        self.red = object()
        self.black = object()
        self.colors = [self.red, self.black]

    def db_store_game_state(self, db):
        db.rows = self.rows
        db.columns = self.columns
        board_map = {self.red: "r", self.black : "b", None : "_"}
        db.board_array = [board_map[x] for x in self.board_array]

    def db_load_game_state(self, db):
        self.rows = db.rows
        self.columns = db.columns
        board_map = {"r" : self.red, "b" : self.black, "_" : None}
        self.board_array = [board_map[x] for x in db.board_array]

    def __str__(self):
        s = "\n"
        glyphs = {self.red : "r", self.black: "b", None: " "}
        for i in xrange(len(self.board_array)):
            if i % self.columns == 0:
                s = "%s%d | "%(s, i / self.columns)
            s = "%s%s"%(s, glyphs[self.board_array[i]])
            if (i + 1) % self.columns == 0:
                s = "%s\n"%(s)
        return s

    def play(self, color, column):
        """Place a piece of the given color in the given column."""
        row = self._get_empty_row(column)
        if row:
            self.board_array[self.get_index(row, column)] = color

    def test_play(self, column):
        """Return true if a piece can be played in a column."""
        return self._get_empty_row(column) != None

    def get_piece(self, row, column):
        """Return the object at the given row and column."""
        return self.board_array[self.get_index(row, column)]

    def get_index(self, row, column):
        """Return the list index based on the row and column."""
        return row * self.columns + column

    def get_column_from_index(self, index):
        """Return the column based on the index."""
        return index % self.columns

    def get_row_from_index(self, index):
        """Return the row based on the index."""
        return index / self.rows

    def _get_column(self, column):
        """Return the given column (index, piece) pairs."""
        return zip(range(column, len(self.board_array), self.columns), self.board_array[column::self.columns])

    def _get_row(self, row):
        """Return the given row (index, piece) pairs."""
        return zip(range(row * self.columns, row * self.columns + self.columns), self.board_array[row * self.columns:row * self.columns + self.columns])

    def _get_left_diagonal(self, diagonal):
        """Return the given left diagonal (index, piece) pairs."""
        #    0  1  2  3  4  5  6
        #   --------------------
        # 0| 0  1  2  3  4  5  6
        # 1| 1  2  3  4  5  6 -1
        # 2| 2  3  4  5  6 -1 -2
        # 3| 3  4  5  6 -1 -2 -3
        # 4| 4  5  6 -1 -2 -3 -4
        # 5| 5  6 -1 -2 -3 -4 -5
        #
        if (diagonal >= 0):
            start = diagonal
            length = min(diagonal + 1, self.rows, self.columns)
        else:
            start = (-diagonal + 1) * self.columns - 1
            length = min(min(self.rows, self.columns) + diagonal, self.rows, self.columns)
        return zip(range(start, len(self.board_array), self.columns - 1), self.board_array[start::self.columns - 1])[:length]

    def _get_right_diagonal(self, diagonal):
        """Return the given right diagonal (index, piece) pairs."""
        #    0  1  2  3  4  5  6
        #   --------------------
        # 0| 0  1  2  3  4  5  6
        # 1| -1 0  1  2  3  4  5
        # 2| -2 -1 0  1  2  3  4
        # 3| -3 -2 -1 0  1  2  3
        # 4| -4 -3 -2 -1 0  1  2
        # 5| -5 -4 -3 -2 -1 0  1
        #
        if (diagonal >= 0):
            start = diagonal
            length = min(self.columns - diagonal, self.rows)
        else:
            start = -diagonal * self.columns
            length = min(self.columns - (-diagonal), self.rows)
        return zip(range(start, len(self.board_array), self.columns + 1), self.board_array[start::self.columns + 1])[:length]

    def _get_empty_row(self, column):
        """Return the first empty row, or None if the row column is full."""
        empty_rows = [x[0] for x in enumerate(self._get_column(column)) if x[1][1] == None]
        if (len(empty_rows) == 0):
            return None
        return empty_rows[-1]

    def find_winner(self):
        """Return the winning color and positions, or None if there is no winner."""
        for checker in [self._check_vertical_winner, self._check_horizontal_winner, self._check_left_diagonal_winner, self._check_right_diagonal_winner]:
            win = checker()
            if win:
                return win
        return None

    def _check_winner(self, group):
        """Return the color and positions of the winner, or None if there is no winner. group is a list of (index, color) pairs."""
        # This is a monstrosity, but it works.
        # win = reduce(lambda x, y: ({True: (x[0], x[1] + [y[0]]), False: (y[1], [y[0]])}[x[0] == y[1] or len(x[1]) >= 4]), group, (None, []))
        # if win[0] == None or len(win[1]) < 4:
        #     return None
        win = (None, [])
        for x in group:
            if x[1] == win[0]:
                win = (win[0], win[1] + [x[0]])
            else:
                win = (x[1], [x[0]])
            if (len(win[1]) == 4) and (win[0] != None):
                return win
                
        return None

    def _check_vertical_winner(self):
        """Return the color and positions of the vertical winner, or None if there is no winner."""
        for column in xrange(self.columns):
            win = self._check_winner(self._get_column(column))
            if win:
                return win
        return None

    def _check_horizontal_winner(self):
        """Return the color and positions of the horizontal winner, or None if there is no winner."""
        for row in xrange(self.rows):
            win = self._check_winner(self._get_row(row))
            if win:
                return win
        return None

    def _check_left_diagonal_winner(self):
        """Return the color and positions of the left-diagonal winner, or None if there is no winner."""
        for diagonal in xrange(-self.rows, self.columns):
            win = self._check_winner(self._get_left_diagonal(diagonal))
            if win:
                return win
        return None

    def _check_right_diagonal_winner(self):
        """Return the color and positions of the right-diagonal winner, or None if there is no winner."""
        for diagonal in xrange(-self.rows, self.columns):
            win = self._check_winner(self._get_right_diagonal(diagonal))
            if win:
                return win
        return None

    
