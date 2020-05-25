"""
    This modules contains the BoggleSolver, used to find all the words in a
    Boggle board.
"""

import re
from collections import defaultdict
from itertools import product
from pythonds.basic.stack import Stack

from src import wordtools


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
