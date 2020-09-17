"""
    This module contains the ScrabbleSolver, used to find all the possible
    words that can be played on a Scrabble board.
"""

import re
from string import ascii_lowercase, ascii_uppercase
from collections import defaultdict
import numpy as np

from wordsolver import wordtools


VALUE_STANDARD = {
    "A" : 1, "B" : 3, "C" : 3, "D" : 2, "E" : 1, "F" : 4, "G" : 2, "H" : 4,
    "I" : 1, "J" : 8, "K" : 5, "L" : 1, "M" : 3, "N" : 1, "O" : 1, "P" : 3,
    "Q" : 10, "R" : 1, "S" : 1, "T" : 1, "U" : 1, "V" : 4, "W" : 4, "X" : 8,
    "Y" : 4, "Z" : 10
}

PREMIUM_STANDARD = [
    ["T", "*", "*", "d", "*", "*", "*", "T", "*", "*", "*", "d", "*", "*", "T"],
    ["*", "D", "*", "*", "*", "t", "*", "*", "*", "t", "*", "*", "*", "D", "*"],
    ["*", "*", "D", "*", "*", "*", "d", "*", "d", "*", "*", "*", "D", "*", "*"],
    ["d", "*", "*", "D", "*", "*", "*", "d", "*", "*", "*", "D", "*", "*", "d"],
    ["*", "*", "*", "*", "D", "*", "*", "*", "*", "*", "D", "*", "*", "*", "*"],
    ["*", "t", "*", "*", "*", "t", "*", "*", "*", "t", "*", "*", "*", "t", "*"],
    ["*", "*", "d", "*", "*", "*", "d", "*", "d", "*", "*", "*", "d", "*", "*"],
    ["T", "*", "*", "d", "*", "*", "*", "D", "*", "*", "*", "d", "*", "*", "T"],
    ["*", "*", "d", "*", "*", "*", "d", "*", "d", "*", "*", "*", "d", "*", "*"],
    ["*", "t", "*", "*", "*", "t", "*", "*", "*", "t", "*", "*", "*", "t", "*"],
    ["*", "*", "*", "*", "D", "*", "*", "*", "*", "*", "D", "*", "*", "*", "*"],
    ["d", "*", "*", "D", "*", "*", "*", "d", "*", "*", "*", "D", "*", "*", "d"],
    ["*", "*", "D", "*", "*", "*", "d", "*", "d", "*", "*", "*", "D", "*", "*"],
    ["*", "D", "*", "*", "*", "t", "*", "*", "*", "t", "*", "*", "*", "D", "*"],
    ["T", "*", "*", "d", "*", "*", "*", "T", "*", "*", "*", "d", "*", "*", "T"]
]

EMPTY_STANDARD = [
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
    ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"]
]


class ScrabbleSolver(wordtools.WordHash):
    """
        Class for solving a Scrabble board.

        Attributes:
        > board (np.array) - 2d matrix representing a Scrabble board,
            entries in caps for normal tiles, lower case for blanks,
            empty spaces can be "", "*" or None
        > minor (np.array) - 2d matrix of scores obtained from minor
            words
        > rack (str) - letters in the rack, '#' for blanks
        > values (dict) - keys are possible tiles, values are the values
        > premium (list) - 2d matrix representing the premium squares on
            the Scrabble board; '*' : no bonus, 'd' double letter,
            't' : triple letter, 'D' double word, 'T' : triple word
        > words_of_length (dict) - keys are word lengths, values are all
            words added with that length
    """

    def __init__(self, collection):
        super().__init__()
        self.board = None
        self.minor = None
        self.rack = ""
        self.values = VALUE_STANDARD
        self.premium = PREMIUM_STANDARD
        self.words_of_length = defaultdict(set)
        self._setup(collection)

    def _setup(self, collection):
        """Upload the Dictionary words from a text file 'filename'. When
        solving, the words from this text file will be used for spell
        checking."""
        self.clear_words()
        for word in self._validate_collection(collection):
            if not word.isalpha():
                continue
            self.add_word(word)
            self.words_of_length[len(word)].add(word)

    def solve(self, board, rack):
        """
            Solves the given Scrabble board, using the tiles in 'rack'.

            Parameters:
            > board (list) - 2d matrix representing a Scrabble board, all
                letter tiles in upper case, blanks all lower case, empty
                spaces can be "", "*" or None
            > rack (list) - letters of the tiles on the rack, blanks are
                represented by a "#"

            Returns:
            > solutions (list) - list of solutions, each solution is of
                the form (word, x, y, orientation, score)

            IMPORTANT NOTE:
            The algorithm used will not use blanks in place of tiles it
            already has. Blanks will only be to make a word if it has to
        """
        matrix = self._validate_board(board)
        rack = self._validate_rack(rack)
        solutions = set()

        # Gather horizontal word solutions
        for word, x, y, score in self._horizontal_solve(matrix, rack):
            solutions.add((word, x, y, False, score))

        # Gather vertical word solutions
        for word, y, x, score in self._horizontal_solve(matrix.transpose(), rack):
            solutions.add((word, x, y, True, score))

        return sorted(solutions, key=lambda x: x[-1], reverse=True)

    def get_score(self, board, rack, attempt):
        """
            Returns the points earned from placing attempt on the given
            board with the given rack.

            Parameters:
            > board (list) - 2d matrix representing a Scrabble board, all
                letter tiles in upper case, blanks all lower case, empty
                spaces can be "", "*" or None
            > rack (list) - letters of the tiles on the rack, blanks are
                represented by a "#"
            > attempt (tuple) - information of the attempt of the form:
                (word, x, y, orientation)
        """
        board = self._validate_board(board)
        rack = self._validate_rack(rack)
        (word, x, y, orientation) = self._validate_attempt(attempt)

        if not orientation:
            self._prepare(np.array(board), rack)
        else:
            self._prepare(np.array(board).transpose(), rack)
            x, y = y, x

        placements, adjacent = [], False
        for n in range(len(word)):
            tile = self._get_tile(x+n, y)
            if tile.isalpha():
                adjacent = True
            elif not tile:
                break
            elif tile == "*":
                if len(placements) == len(self.rack):
                    break
                placements.append(n)
                if not adjacent:
                    adjacent = self._is_vertically_adjacent(x+n, y)
        else:
            if not adjacent:
                return -1
            for (_, score) in self._yield_solutions([word], x, y, placements):
                return score
        return -1

    def _horizontal_solve(self, board, rack):
        """
            Generator function which yields horizontal word solutions,
            for the given Scrabble board, using the tiles in 'rack'.

            Parameters:
            > board (list) - 2d matrix representing a Scrabble board, all
                letter tiles in upper case, blanks all lower case
            > rack (str) - letters of the tiles on the rack, blanks are
                represented by a "#"

            Yields:
            > (word, x, y, score)
                word (str) : the whole main word created
                x (int) : the x coordinate of the beginning of the word
                y (int) : the y coordinate of the beginning of the word
                score (int) : the points gained by creating the word
        """
        self._prepare(board, rack)
        for x, y in np.ndindex(self.board.shape):
            for word, score in self._horizontal_solutions(x, y):
                yield (word, x, y, score)

    def _horizontal_solutions(self, x, y):
        """
            Yields the possible words and scores given from placing a
            word in beginningin the position x, y.

            Parameters
            > x (int) - x position of the words
            > y (int) - y position of the words

            Yields:
            > (word, score) - word: str, score: int
        """

        # Not interested in positions with a preceding tile to the left
        if self._get_tile(x-1, y).isalpha():
            return

        # placements : list of indices of tiles placed since the first
        # requirements : letter, position pairs, words must have to fit
        # adjacent : is the current tile stream adjacent to placed tiles
        placements, requirements, adjacent = [], [], False

        # Streams tiles horizontally from (x, y), yielding all solutions
        for n in range(self.board.shape[0]):
            tile = self._get_tile(x+n, y)
            if tile.isalpha():
                requirements.append((tile, n))
            elif requirements or adjacent:
                words = self._find_words(n, requirements)
                for word, score in self._yield_solutions(
                        words, x, y, placements
                    ):
                    yield (word, score)
            if not tile:
                break
            elif tile == "*":
                if len(placements) == len(self.rack):
                    break
                placements.append(n)
                if not adjacent:
                    adjacent = self._is_vertically_adjacent(x+n, y)

    def _yield_solutions(self, words, x, y, placements):
        """
            Yields the words and scores given from placing the word in
            words in the given x, y position, given that new tiles are
            being placed with indices in placements.

            Parameters
            > words (iterable) - possible words to be checked
            > x (int) - x position of the words
            > y (int) - y position of the words
            > placements (lst) - indices of tiles placed to make the
                words

            Yields
            > (word, score) - word: str, score: int
        """
        for word in words:
            rack_tiles = self._get_rack_tiles(self.rack, word, placements)
            if not rack_tiles:
                continue
            score = 0
            placed = [(rack_tiles[n], pos) for n, pos in enumerate(placements)]
            for let, pos in placed:
                if not let in self.minor[y][x + pos]:
                    break
                if let.islower():
                    word = word[:pos] + let + word[pos+1:]
                score += self.minor[y][x + pos][let]
            else:
                bingo = (len(placements) == 7)
                score += self._evaluate_major_score(word, x, y, bingo)
                yield (word, score)

    def _get_minor_scores(self):
        """Returns the points gained from any vertical words. The return
        value is a 2d matrix representing positions on self.board. The
        entries are dicts, keys are possible tiles which can be placed
        and that position, values are the points earned."""
        minor_scores = np.full(self.board.shape, dict())
        for x, y in np.ndindex(self.board.shape):
            minor_scores[x][y] = {}
        minor_shape = (self.board.shape[0], self.board.shape[1] + 1)
        allow_all = dict.fromkeys(ascii_lowercase + ascii_uppercase, 0)

        # Iterate though positions vertically
        letters, pos = [], ()
        for x, y in np.ndindex(minor_shape):
            tile = self._get_tile(x, y)
            if not tile.isalpha() and pos:
                ind = letters.index("*")
                if letters == ["*"]:
                    minor_scores[pos[1]][pos[0]] = allow_all
                else:
                    for part in self._generate_minor_score(
                            letters, pos[0], pos[1], ind
                    ):
                        minor_scores[pos[1]][pos[0]].update(part)
                if tile == "*":
                    letters = letters[ind+1:]
            if not tile:
                letters, pos = [], ()
            else:
                letters.append(tile.upper())
            if tile == "*":
                pos = (x, y)

        return minor_scores

    def _generate_minor_score(self, letters, x, y, ind):
        """Yields key-value pairs of letters and the scores given by
        placing the tile at position x, y, having index ind in the word.
        """
        letter_mult = {"d" : 2, "t" : 3}.get(self.premium[y][x], 1)
        base_value = sum([self.values.get(letter, 0) for letter in letters])
        base_mult = {"D" : 2, "T" : 3}.get(self.premium[y][x], 1)

        # Get all words
        requirements = [
            (let, pos) for pos, let in enumerate(letters) if let != "*"
        ]
        words = self._find_words(len(letters), requirements)

        # Yield a solution for each word
        for letter in {word[ind] for word in words}:
            letter_value = self.values.get(letter, 0)
            yield {
                letter : base_mult * (base_value + letter_mult * letter_value),
                letter.lower() : base_mult * base_value
            }

    def _prepare(self, board, rack):
        """Prepares for calculating scores."""
        self.board = board
        self.minor = self._get_minor_scores()
        self.rack = "".join(rack)

    def _find_words(self, length, requirements):
        """Returns the set of all words of length 'length', meeting the
        criteria set in the list 'requirements'. For every tuple
        ("?", n) in 'requirements', the word must contain the letter "?"
        at index 'n'. If 'requirements' is empty, all words of length
        'length' are returned."""
        if not requirements:
            return self.words_of_length[length]
        set_list = [self.lookup(length, let, pos) for let, pos in requirements]
        return set.intersection(*set_list)

    def _is_vertically_adjacent(self, x, y):
        """Returns whether the given (x, y) position on self.board in
        on the centre of the board or has a tile above or below it."""
        if x == (self.board.shape[1]-1)/2 and y == (self.board.shape[0]-1)/2:
            return True
        return self._get_tile(x, y-1).isalpha() or self._get_tile(x, y+1).isalpha()

    def _evaluate_major_score(self, word, x, y, bingo):
        """"Returns the points gained for spelling the given word
        horizontally at position (x, y). Points gained from minor words
        are not added."""
        value_total, word_mult = 0, 1
        bingo_bonus = 50 if bingo else 0
        for n, letter in enumerate(word):
            letter_mult = 1
            if self._get_tile(x+n, y) == "*":
                letter_mult = {"d" : 2, "t" : 3}.get(self.premium[y][x+n], 1)
                word_mult *= {"D" : 2, "T" : 3}.get(self.premium[y][x+n], 1)
            value_total += self.values.get(letter, 0) * letter_mult
        return value_total * word_mult + bingo_bonus

    def _get_tile(self, x, y):
        """Returns the letter of the tile on the board at position
        (x, y). If the position is free, '*' is returned. If (x, y)
        does not exist on the board, "" is returned."""
        if not (0 <= x < self.board.shape[1] and 0 <= y < self.board.shape[0]):
            return ""
        tile = self.board[y][x]
        if tile in ["", "*", None]:
            return "*"
        return tile

    @staticmethod
    def _get_rack_tiles(rack, word, placements):
        """Returns the word tiles used to place the word."""
        placed_tiles = [word[pos] for pos in placements]
        rack_tiles = ""
        for letter in placed_tiles:
            if letter in rack:
                rack = rack.replace(letter, "", 1)
                rack_tiles += letter
            elif "#" in rack:
                rack = rack.replace("#", "", 1)
                rack_tiles += letter.lower()
            else:
                return ""
        return rack_tiles

    @staticmethod
    def _validate_collection(collection):
        """Validate the collection parameter. Returns the words extracted."""

        # Return collection if it is already a list/set
        if isinstance(collection, (list, set)):
            return [word.upper() for word in collection]

        # Opens file and return lists of words in the file
        if isinstance(collection, str):
            with open(collection, "r") as file_text:
                text = file_text.read()
            return re.findall(r"[\w']+", text.upper())

        # Else an incorrect type has been received
        raise TypeError(
            "invalid value for 'collection' parameter. "
            "Expected list, set or str, received '%s'." % type(collection).__name__
        )

    @staticmethod
    def _validate_board(board):
        """Validate the board parameter. Returns the board matrix."""

        # Check board is a list
        if not isinstance(board, list):
            raise TypeError(
                "invalid value for 'board' parameter. "
                "Expected list, received '%s'." % type(board).__name__
            )

        # Check board is a list of length 15
        rows = len(board)
        if rows != 15:
            raise ValueError(
                "invalid value for 'board' parameter. "
                "Expected 15 rows, received %i.." % rows
            )

        # Check board is a list of lists
        element_lengths = set()
        for index, element in enumerate(board):
            if not isinstance(element, list):
                raise TypeError(
                    "invalid value for 'board' parameter at index %i. "
                    "Expected list, received '%s'." % (index, type(element).__name__)
                )
            element_lengths.add(len(element))

        # Check all lists are the same size
        if element_lengths != {15}:
            raise ValueError(
                "invalid value for 'board' parameter. "
                "Not all rows are 15 tiles long."
            )

        # Check each element in the lists are strings
        for index, element in enumerate(board):
            for tile in element:
                if not isinstance(tile, str):
                    raise TypeError(
                        "invalid value for 'board' parameter at index %i. "
                        "Not all elements are str, found '%s'" % (index, type(tile).__name__)
                    )
            board[index] = [
                (tile if tile.isalpha() else "*")
                for tile in element
            ]

        # Check that each element of board is a single character
        for index, element in enumerate(board):
            for letter in element:
                if len(letter) != 1:
                    raise ValueError(
                        "invalid value for 'board' parameter at index %i. "
                        "Cannot convert '%s' into a letter." % (index, letter)
                    )

        return np.array(board)

    @staticmethod
    def _validate_rack(rack):
        """Validate the rack parameter. Returns the rack."""

        # Check that rack is either a list, set or string
        if isinstance(rack, list):
            return rack
        if isinstance(rack, set):
            return list(rack)
        if isinstance(rack, str):
            return rack.split()
        raise TypeError(
            "invalid value for 'rack' parameter. "
            "Expected list, set or str, received '%s'." % type(rack).__name__
        )

    @staticmethod
    def _validate_attempt(attempt):
        """Validate the attempt parameter. Returns the attempt."""

        # Check the tuple count
        try:
            (word, x, y, orientation) = attempt
        except ValueError as exc:
            raise exc

        # Check word is an alphabetically string
        if not isinstance(word, str):
            raise ValueError(
                "invalid value for 'attempt' parameter. "
                "The word value is not an alphabetical string."
            )
        if not word.isalpha():
            raise ValueError(
                "invalid value for 'attempt' parameter. "
                "The word value is not an alphabetical string."
            )

        # Check the x value
        if not isinstance(x, int):
            raise ValueError(
                "invalid value for 'attempt' parameter. "
                "The x value is not an int."
            )

        # Check the y value
        if not isinstance(y, int):
            raise ValueError(
                "invalid value for 'attempt' parameter. "
                "The y value is not an int."
            )

        # Check the y value
        if not isinstance(orientation, bool):
            raise ValueError(
                "invalid value for 'attempt' parameter. "
                "The orientation value is not a bool."
            )

        return attempt
