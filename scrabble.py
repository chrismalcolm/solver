"""
    This module contains all the required objects to play a game of
    Scrabble.
"""

import random
import re
from string import ascii_lowercase, ascii_uppercase

from collections import defaultdict
import numpy as np

from scrabble_data import TILES_STANDARD, VALUE_STANDARD, PREMIUM_STANDARD
import wordtools


class Solver(wordtools.WordHash):
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

    def __init__(self, filename, values=None, premium=None):
        super().__init__()
        self.board = None
        self.minor = None
        self.rack = ""
        self.values = values if values else VALUE_STANDARD
        self.premium = premium if premium else PREMIUM_STANDARD
        self.words_of_length = defaultdict(set)
        self._upload_words(filename)

    def _upload_words(self, filename):
        """Upload the Dictionary words from a text file 'filename'. When
        solving, the words from this text file will be used for spell
        checking."""
        self.clear_words()
        with open(filename, "r") as file_text:
            text = file_text.read()
        words = re.findall(r"[\w']+", text.upper())
        for word in words:
            self.add_word(word)
            self.words_of_length[len(word)].add(word)

    def solve(self, board, rack):
        """
            Solves the given Scrabble board, using the tiles in 'rack'.

            Parameters:
            > board (lst) - 2d matrix representing a Scrabble board, all
                letter tiles in upper case, blanks all lower case, empty
                spaces can be "", "*" or None
            > rack (lst) - letters of the tiles on the rack, blanks are
                represented by a "#"

            Returns:
            > solutions (lst) - list of solutions, each solution is of
                the form (word, x, y, orientation, score)

            IMPORTANT NOTE:
            The algorithm used will not use blanks in place of tiles it
            already has. Blanks will only be to make a word if it has to
        """
        matrix = np.array(board)
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
            > board (lst) - 2d matrix representing a Scrabble board, all
                letter tiles in upper case, blanks all lower case, empty
                spaces can be "", "*" or None
            > rack (lst) - letters of the tiles on the rack, blanks are
                represented by a "#"
            > attempt (tuple) - information of the attempt of the form:
                (word, x, y, orientation)
        """
        (word, x, y, orientation) = attempt

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
            > board (lst) - 2d matrix representing a Scrabble board, all
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


class Board():
    """
        Class for storing information about a Scrabble board.

        Attributes:
        > width (int) - the width of the board
        > height (int) - the height of the board
        > tiles (np.array) - 2d matrix representing a Scrabble board,
            entries in caps for normal tiles, lower case for blanks
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = np.full((height, width), None)

    def __repr__(self):
        rows = self.tiles.copy()
        rows[rows == None] = "*"
        header = list(ascii_uppercase)[:self.width]
        main = [f'\n{n+1:>2} ' + " ".join(row) for n, row in enumerate(rows)]
        return "   " + " ".join(header) + "".join(main)

    def set_word(self, word, x, y, orientation):
        """Places the given word on the board, originating at position
        (x, y) with orientation 0 if horizontal, 1 if vertical."""
        placed = []
        for letter in word:
            if self._set_tile(x, y, letter):
                placed.append(letter)
            x, y = x + (not orientation), y + (orientation)
        return placed

    def clear_board(self):
        """Remove all tiles on the board."""
        self.tiles = np.full((self.height, self.width), None)

    def _set_tile(self, x, y, letter):
        """Places the tile of the given letter at position (x, y)."""
        if x in range(self.width) and y in range(self.height):
            pre_tile = self.tiles[y, x]
            self.tiles[y, x] = letter
            return pre_tile == None
        return False


class Bag():
    """
        Class for representing a bag of tiles in a game of Scrabble.

        Attributes:
        > tiles (lst) - list of starting tiles in the bag. All letter
            tiles are in caps, blanks are "#"
    """

    def __init__(self, tiles=None):
        self.tiles = tiles if tiles else TILES_STANDARD
        self.shake()

    def shake(self):
        """Randomise the order of the tiles in the bag."""
        random.shuffle(self.tiles)

    def add_tiles(self, tiles):
        """Adds the list given tiles to the bag."""
        self.tiles += tiles

    def remove_tiles(self, amount):
        """Returns a list of 'amount' number of removed tiles. If there
        are not enough tiles, the remained of the tiles are returned."""
        return [self._pop_tile() for _ in range(min(len(self.tiles), amount))]

    def _pop_tile(self):
        """Removes a tile from the top of the bag, if it exists."""
        if self.tiles:
            return self.tiles.pop()
        return None


class Player():
    """
        Class for representing a player in a Scrabble game.

        Attributes:
        > name (str) - player's name
        > solver (Solver) - instance of Solver used for calculating
            scores
        > board (Board) - instance of Board for placing tiles
        > bag (Bag) - instance of  Bag used for collecting tiles
        > score (int) - the player's current score
        > rack (lst) - list representing tiles in the rack
        > words (dict) - data on words added
    """

    def __init__(self, name, solver, board, bag):
        self.name = name
        self.solver = solver
        self.board = board
        self.bag = bag
        self.score = 0
        self.rack = []
        self.words = {}
        self.replenish_tiles()

    def __repr__(self):
        return "Score: %i\nRack: %s" % (self.score, self.rack)

    def replenish_tiles(self):
        """Attempt to fill the rack up to 7 tiles."""
        self.rack += self.bag.remove_tiles(7 - len(self.rack))

    def reset_tiles(self):
        """Reset the tiles currently in the rack."""
        self.bag.add_tiles(self.rack)
        self.bag.shake()
        self.rack = self.bag.remove_tiles(7)

    def add_word(self, word, x, y, orientation):
        """Attempt to add the given word to the board. Returns the score
        if successful, else returns -1."""
        attempt = (word, x, y, orientation)
        points = self.solver.get_score(self.board.tiles, self.rack, attempt)
        if points <= 0:
            return -1
        set_tiles = self.board.set_word(word, x, y, orientation)
        placed = [let if let.isupper() else "#" for let in set_tiles]
        for let in placed:
            del self.rack[self.rack.index(let)]
        self.score += points
        self.words.update({word: points})
        return points

    def summary(self):
        """Provides a summary on the player's stats in the game."""
        summary_string = "%s found the following words:\n%s\nFinal score: %i"
        return summary_string % (self.name, str(self.words), self.score)
