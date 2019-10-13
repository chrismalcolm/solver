"""
    This module provides the necessary components for playing a game of
    Boggle.
"""

import random
import re

from collections import defaultdict
from itertools import product
from pythonds.basic.stack import Stack
import numpy as np

import wordtools


class Solver(wordtools.WordTree):
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

    def __init__(self, filename, substitutions=None, min_length=3):
        super().__init__()
        self.word_paths = defaultdict(list)
        self.substitutions = substitutions if substitutions else {"QU": "Q"}
        self._upload_words(filename, min_length)

    def solve(self, board):
        """
            Iterates through all starting positions on the board, adding
            all possible words starting at that position.

            Parameters:
            > board (lst) - 2d matrix representing a Boggle board, all
                entries in caps

            Returns:
            > (lst) - all words on the board, beginning with the longest
                word(s)
        """
        self.word_paths = defaultdict(list)
        for row, col in product(range(len(board)), range(len(board[0]))):
            self._iteration(board, row, col)
        return sorted(self.word_paths.keys(), key=len, reverse=True)

    def _upload_words(self, filename, min_length):
        """
            Upload the Dictionary words from a text file. When solving,
            the words from this text file will be used for spell
            checking.

            Parameters:
            > filename (str) - name of the text file
            > min_length (int) - the minimum length of words uploaded
        """
        self.clear_words()
        with open(filename, "r") as file_text:
            text = file_text.read()
        words = re.findall(r"[\w']+", text.upper())
        for word in words:
            if len(word) < min_length:
                continue
            substituted = self._apply_substitute(word, reverse=False)
            self.add_word(substituted)

    def _apply_substitute(self, word, reverse=True):
        """If reverse is True, replace any single character
        substitutions in word with the sub-string substitution, found in
        self.substitutions. If reverse is False, replace any sub-strings
        in word with the single character substitution."""
        for item in self.substitutions.items():
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
            > board (lst) - 2d matrix representing a Boogle Board
            > path (lst) - board path

            Returns:
            > (lst) - all board co-ordinates (x, y) which are adjacent
                to the last co-ordinate in path and are also not in path
        """
        adjacent = []
        row_range = max(0, path[-1][0]-1), min(len(board), path[-1][0]+2)
        col_range = max(0, path[-1][1]-1), min(len(board[0]), path[-1][1]+2)
        for adj_row, adj_col in product(range(*row_range), range(*col_range)):
            if (adj_row, adj_col) not in path:
                adjacent.append((adj_row, adj_col))
        return adjacent


class Tray():
    """
        Class for storing information about a Boggle tray.

        Attributes:
        > width (int) - the number of columns of the tray
        > height (int) - the number of rows of the tray
        > cubes (lst) - list of uppercase strings, each string
            representing the letters of a cube's faces, first letter is
            the top face
        > board (lst) - 2d matrix representing a Boggle board, all
            entries in caps
        > substitutions (dict) - mapping for swapping sub-strings in
            words for single character representations.
            e.g. substitute = {"Q" : "QU"}. Needs to be all in caps.
    """

    def __init__(self, width, height, cubes, substitutions=None):
        self.width = width
        self.height = height
        self.cubes = cubes.split(',')
        self.board = np.full((height, width), "")
        self.substitutions = substitutions if substitutions else {"QU": "Q"}

    def __repr__(self):
        rep = ""
        gap = " " * max([1] + [len(v) for v in self.substitutions.values()])
        for row in self.board:
            rep += gap.join(list(row) + ["\n"])
        for substitute, sub_string in self.substitutions.items():
            rep = rep.replace(substitute + gap[1:], sub_string.capitalize())
        return rep

    def shake(self):
        """
            Shakes the tray so all cubes are in randomly chosen
            positions with one of their six sides facing up.

            Returns:
            > (lst) - 2d matrix of the top faces of the cubes after
                Boggle board has been shaken
        """
        random.shuffle(self.cubes)
        for num, cube in enumerate(self.cubes):
            self.board[num // self.height][num % self.width] = (
                random.sample(cube, 1)[0]
            )
        return self.board


class Player():
    """
        Class for representing a player in a Boggle game.

        Attributes:
        > name (str) - player's name
        > scheme (dict) - keys are word length, values are points given
        > score (int) - the player's current score
        > solutions (set) - words tha tcan be found on the board
        > words (dict) - list of valid words added by the player
    """

    def __init__(self, name, scheme):
        self.name = name
        self.scheme = scheme
        self.score = 0
        self.solutions = set()
        self.words = dict()

    def __repr__(self):
        words = ", ".join(self.words.keys())
        return "%s:\n\nScore: %i\nWords found: %s" % (
            self.name, self.score, words
        )

    def add_word(self, word):
        """Adds a word and its score to self.words if valid."""
        if not word in self.solutions:
            return "%s is not a valid word on the board." % word
        if word in self.words:
            return "%s is already in the list of found words." % word
        points = self.scheme[len(word)]
        if points == 0:
            return "%s does not score any points." % word
        self.words[word] = points
        self.score += points
        return "%s scored %i points." % (word, points)

    def update_solutions(self, solutions):
        """Update self.solutions for the current board."""
        self.solutions = solutions

    def summary(self):
        """Provides a summary on the game."""
        summary_string = (
            "%s found %i/%i words.\nThose words and their scores "
            "are:\n%s.\n%s's total score was %i"
        )
        return summary_string % (
            self.name, len(self.words), len(self.solutions),
            str(self.words), self.name, self.score
        )
