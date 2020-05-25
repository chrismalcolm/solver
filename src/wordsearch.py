"""
    The module contains the WordSearchSolver, used to solve a word search.
"""

from enum import Enum
from itertools import chain
import re

from src import wordtools


class Direction(Enum):
    """Compass directions."""
    ALL = 0
    NORTH = 1
    NORTH_EAST = 2
    EAST = 3
    SOUTH_EAST = 4
    SOUTH = 5
    SOUTH_WEST = 6
    WEST = 7
    NORTH_WEST = 8


class WordSearchSolver(wordtools.WordTree):
    """
        Class for solving a Word Search.

        Attributes:
        > grid (list) - 2d matrix representing letters and positions in a word
            search grid
        > width (int) - width of the word search grid
        > height (int) - height of the word search grid
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.grid = None
        self.width = 0
        self.height = 0
        self._upload_words(**kwargs)

    def _upload_words(self, filename=None, words=None):
        """
            Upload the hidden words from a text file. The hidden words will be
            seaarched for when solving. Words can be uploaded from a file and/or
            from a list.

            Parameters:
            > filename (str) - name of the text file
        """
        self.clear_words()
        hidden_words = list()
        if filename:
            with open(filename, "r") as file_text:
                text = file_text.read()
            hidden_words += re.findall(r"[\w']+", text.upper())
        if words:
            hidden_words += [word.upper() for word in words]
        for word in hidden_words:
            self.add_word(word)

    def solve(self, grid, directions=None):
        """
            Find the positions of all hidden words.

            Parameters:
            > grid (list) - 2d matrix of letters, representing the word search
                grid to be solved
            > directions (set) - compass directions to search for hidden words

            Returns:
            > solutions (list) - a list of tuples of the following form:
                (word, start_pos, end_pos)
                - word (str) : hidden word
                - start_pos (int, int) : x, y position of the start of the word
                - end_pos (int, int) : x, y position of the end of the word
        """
        self.width = len(grid[0])
        self.height = len(grid)
        self.grid = [
            [((col, row), grid[row][col].upper()) for col in range(self.width)]
            for row in range(self.height)
        ]

        directions = directions or {Direction.ALL}

        solutions = list()
        for grid_slice in self._generate_slices(directions):
            for solution in self._get_solutions(grid_slice):
                solutions.append(solution)

        return solutions

    def _generate_slices(self, directions):
        """
            Generator function used to extract word search grid slices.

            Parameters:
            > direction (Direction) - the direction to take the slices in

            Yields:
            > grid_slice (list) - a grid slice of the word search grid, in the
                given 'direction'
        """
        if Direction.ALL in directions:
            directions = {
                Direction.NORTH, Direction.NORTH_EAST,
                Direction.EAST, Direction.SOUTH_EAST,
                Direction.SOUTH, Direction.SOUTH_WEST,
                Direction.WEST, Direction.NORTH_WEST
            }

        yield_slice_funcs = {
            Direction.NORTH: self._yield_slices_north,
            Direction.NORTH_EAST: self._yield_slices_north_east,
            Direction.EAST: self._yield_slices_east,
            Direction.SOUTH_EAST: self._yield_slices_south_east,
            Direction.SOUTH: self._yield_slices_south,
            Direction.SOUTH_WEST: self._yield_slices_south_west,
            Direction.WEST: self._yield_slices_west,
            Direction.NORTH_WEST: self._yield_slices_north_west
        }

        generators = [
            func for direction, func in yield_slice_funcs.items()
            if direction in directions
        ]

        for grid_slice in chain(*generators):
            yield grid_slice

    def _yield_slices_north(self, grid_slice):
        """Yield grid slices in a north direction."""
        for col in range(self.width):
            grid_slice = list()
            for row in range(self.height - 1, -1, -1):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_north_east(self, grid_slice):
        """Yield grid slices in a north-east direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(max(0, 1-self.height+diag), min(self.width, diag+1)):
                grid_slice.append(self.grid[diag-col][col])
            yield grid_slice

    def _yield_slices_east(self, grid_slice):
        """Yield grid slices in an east direction."""
        for row in range(self.height):
            grid_slice = list()
            for col in range(self.width):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_south_east(self, grid_slice):
        """Yield grid slices in a south-east direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(max(0, 1-self.height+diag), min(self.width, diag+1)):
                grid_slice.append(self.grid[col-diag + self.height - 1][col])
            yield grid_slice

    def _yield_slices_south(self, grid_slice):
        """Yield grid slices in a south direction."""
        for col in range(self.width):
            grid_slice = list()
            for row in range(self.height):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_south_west(self, grid_slice):
        """Yield grid slices in a south-west direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(min(self.width, diag+1) - 1, max(0, 1-self.height+diag) - 1, -1):
                grid_slice.append(self.grid[diag-col][col])
            yield grid_slice

    def _yield_slices_west(self, grid_slice):
        """Yield grid slices in a west direction."""
        for row in range(self.height):
            grid_slice = list()
            for col in range(self.width-1, -1, -1):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_north_west(self, grid_slice):
        """Yield grid slices in a north-west direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(min(self.width, diag+1) - 1, max(0, 1-self.height+diag) - 1, -1):
                grid_slice.append(self.grid[col-diag + self.height - 1][col])
            yield grid_slice

    def _get_solutions(self, grid_slice):
        """
            Generator function for finding words in a word search grid slice.

            Parameters:
            > grid_slice (list) - a slice of the word search grid

            Yields:
            > word (str) - a word found in the grid slice
        """
        for pos, begin_entry in enumerate(grid_slice):
            if not self.root.get_child(begin_entry[1]):
                continue
            node = self.root.get_child(begin_entry[1])
            for end_entry in grid_slice[pos+1:]:
                node = node.get_child(end_entry[1])
                if not node:
                    break
                if node.my_word:
                    yield (node.my_word, begin_entry[0], end_entry[0])
