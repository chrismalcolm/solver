"""
    This modules contains the BoggleSolver, used to find all the words in a
    Boggle board.
"""

import re

from collections import defaultdict
from itertools import product
from pythonds.basic.stack import Stack

from wordsolver import wordtools


class BoggleSolver(wordtools.WordTree):
    """
        Class for solving a Boggle board.

        Attributes:
        > word_paths (dict) - keys are the Dictionary words used for
            solving. The value for each word is a list of all possible
            board paths to attain that word. A board path is a list
            of board co-ordinates (x, y). The values of words that
            are not attainable on the board are empty lists.
        > substitutions (dict) - mapping for swapping sub-strings in
            words for a single character substitution.
            e.g. substitute = {"QU" : "Q"}. Needs to be all in caps.
    """

    SUBSTITUTIONS = {"QU": "Q"}

    def __init__(self, collection, min_length=3):
        super().__init__()
        self._setup(collection, min_length)
        self.word_paths = defaultdict(list)

    def _setup(self, collection, min_length):
        """
            Upload the Dictionary words from 'collection'. When solving,
            the words file will be used for finding words.

            Parameters:
            > collection (list/set/str) - can either be a list/set of strings
                or the filename of list of words
            > min_length (int) - the minimum length of words uploaded
        """
        self._validate_min_length(min_length)
        self.clear_words()
        for word in self._validate_collection(collection):
            if (not word.isalpha() or len(word) < min_length):
                continue
            substituted = self._apply_substitute(word.upper(), reverse=False)
            self.add_word(substituted)

    def solve(self, board, with_positions=False):
        """
            Iterates through all starting positions on the board, adding
            all possible words starting at that position.

            Parameters:
            > board (list) - 2d matrix representing a Boggle board, all
                entries in caps
            > with_positions (bool) - whether positions of the letters forming
                the words should be added to the solution

            Returns:
            > (list) - all words on the board, beginning with the longest
                word(s)
        """
        board = self._validate_board(board, with_positions)
        self.word_paths = defaultdict(list)
        for row, col in product(range(len(board)), range(len(board[0]))):
            self._iteration(board, row, col)
        if with_positions:
            return sorted(self.word_paths.items(), key=lambda x: -len(x[0]))
        return sorted(self.word_paths.keys(), key=len, reverse=True)

    def _apply_substitute(self, word, reverse=True):
        """If reverse is True, replace any single character
        substitutions in word with the sub-string substitution, found in
        self.SUBSTITUTIONS. If reverse is False, replace any sub-strings
        in word with the single character substitution."""
        for item in self.SUBSTITUTIONS.items():
            word = word.replace(item[reverse], item[not reverse])
        return word

    def _iteration(self, board, row, col):
        """
            Main iterative process. This method adds all possible board
            paths to self.word_paths, starting at position (row, col).
            The iterative process works as follows:
            1) starts with the path [(row, col)]
            2) checks all possible additions from the end of the path
            3) if an addition forms a word, the path is appended to the
            corresponding list in self.word_paths
            4) repeat from 2) until all possiblities from that branch
            have been exhausted
        """
        first_node = self.root.get_child(board[row][col])
        if not first_node:
            return
        stack = Stack()
        stack.push((first_node, [(row, col)]))
        while not stack.isEmpty():
            current = stack.pop()
            for (adj_row, adj_col) in self._get_adjacent(board, current[1]):
                adj_node = current[0].get_child(board[adj_row][adj_col])
                adj_path = current[1] + [(adj_row, adj_col)]
                if not adj_node:
                    continue
                if adj_node.my_word:
                    true_word = self._apply_substitute(adj_node.my_word)
                    self.word_paths[true_word].append(adj_path)
                stack.push((adj_node, adj_path))

    @staticmethod
    def _get_adjacent(board, path):
        """
            This method finds all possible candidate co-ordinates for
            additions to a path.

            Parameters:
            > board (list) - 2d matrix representing a Boogle Board
            > path (list) - board path

            Returns:
            > (list) - all board co-ordinates (x, y) which are adjacent
                to the last co-ordinate in path and are also not in path
        """
        adjacent = []
        row_range = max(0, path[-1][0]-1), min(len(board), path[-1][0]+2)
        col_range = max(0, path[-1][1]-1), min(len(board[0]), path[-1][1]+2)
        for adj_row, adj_col in product(range(*row_range), range(*col_range)):
            if (adj_row, adj_col) not in path:
                adjacent.append((adj_row, adj_col))
        return adjacent

    @staticmethod
    def _validate_collection(collection):
        """Validate the collection parameter. Returns the words extracted."""

        # Return collection if it is already a list/set
        if isinstance(collection, (list, set)):
            return collection

        # Opens file and return lists of words in the file
        if isinstance(collection, str):
            with open(collection, "r") as file_text:
                text = file_text.read()
            return re.findall(r"[\w']+", text)

        # Else an incorrect type has been received
        raise TypeError(
            "invalid value for 'collection' parameter. "
            "Expected list, set or str, received '%s'." % type(collection).__name__
        )

    @staticmethod
    def _validate_min_length(min_length):
        """Validate the min_length parameter."""

        # Check that value is an int
        if not isinstance(min_length, int):
            raise TypeError(
                "invalid value for 'min_length' parameter. "
                "Expected int, received '%s'." % type(min_length).__name__
            )

        # Check that value is in the correct range
        if min_length < 0:
            raise ValueError(
                "invalid value for 'min_length' parameter. "
                "Value needs to be non-negative"
            )

    def _validate_board(self, board, with_positions):
        """Validate the board parameter. Returns the board."""

        # Check board is a list
        if not isinstance(board, list):
            raise TypeError(
                "invalid value for 'board' parameter. "
                "Expected list, received '%s'." % type(board).__name__
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
        if len(element_lengths) > 1:
            raise ValueError(
                "invalid value for 'board' parameter. "
                "Not all rows are the same size."
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
                self._apply_substitute(tile.upper(), reverse=False)
                for tile in element
            ]

        # Check that each element of board is a single letter
        for index, element in enumerate(board):
            for letter in element:
                if len(letter) != 1:
                    raise ValueError(
                        "invalid value for 'board' parameter at index %i. "
                        "Cannot convert '%s' into a letter." % (index, letter)
                    )

        # Check the with_positions paramter
        if not isinstance(with_positions, bool):
            raise TypeError(
                "invalid value for 'with_positions' parameter. "
                "Expected bool, received '%s'." % type(board).__name__
            )

        return board
