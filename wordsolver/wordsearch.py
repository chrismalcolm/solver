"""
    The module contains the WordSearchSolver, used to solve a word search.
"""

from enum import Enum
from itertools import chain
import re

from wordsolver import wordtools


class Direction(Enum):
    """Compass directions."""
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

    DIRECTIONS = {
        "N": Direction.NORTH,
        "NE": Direction.NORTH_EAST,
        "E": Direction.EAST,
        "SE": Direction.SOUTH_EAST,
        "S": Direction.SOUTH,
        "SW": Direction.SOUTH_WEST,
        "W": Direction.WEST,
        "NW": Direction.NORTH_WEST
    }

    def __init__(self, collection):
        super().__init__()
        self.grid = None
        self.width = 0
        self.height = 0
        self._yield_slice_funcs = dict()
        self._setup(collection)

    def _setup(self, collection):
        """
            Upload the hidden words from a text file. The hidden words will be
            seaarched for when solving. Words can be uploaded from a file and/or
            from a list.

            Parameters:
            > filename (str) - name of the text file
        """
        self.clear_words()
        for word in self._validate_collection(collection):
            self.add_word(word.upper())

        self._yield_slice_funcs = {
            Direction.NORTH: self._yield_slices_north,
            Direction.NORTH_EAST: self._yield_slices_north_east,
            Direction.EAST: self._yield_slices_east,
            Direction.SOUTH_EAST: self._yield_slices_south_east,
            Direction.SOUTH: self._yield_slices_south,
            Direction.SOUTH_WEST: self._yield_slices_south_west,
            Direction.WEST: self._yield_slices_west,
            Direction.NORTH_WEST: self._yield_slices_north_west
        }

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
        directions = directions or {"ALL"}

        grid = self._validate_grid(grid)
        directions = self._validate_directions(directions)

        self.width = len(grid[0])
        self.height = len(grid)
        self.grid = [
            [((col, row), grid[row][col].upper()) for col in range(self.width)]
            for row in range(self.height)
        ]

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
        generators = [
            func() for direction, func in self._yield_slice_funcs.items()
            if direction in directions
        ]

        for grid_slice in chain(*generators):
            yield grid_slice

    def _yield_slices_north(self):
        """Yield grid slices in a north direction."""
        for col in range(self.width):
            grid_slice = list()
            for row in range(self.height - 1, -1, -1):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_north_east(self):
        """Yield grid slices in a north-east direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(max(0, 1-self.height+diag), min(self.width, diag+1)):
                grid_slice.append(self.grid[diag-col][col])
            yield grid_slice

    def _yield_slices_east(self):
        """Yield grid slices in an east direction."""
        for row in range(self.height):
            grid_slice = list()
            for col in range(self.width):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_south_east(self):
        """Yield grid slices in a south-east direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(max(0, 1-self.height+diag), min(self.width, diag+1)):
                grid_slice.append(self.grid[col-diag + self.height - 1][col])
            yield grid_slice

    def _yield_slices_south(self):
        """Yield grid slices in a south direction."""
        for col in range(self.width):
            grid_slice = list()
            for row in range(self.height):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_south_west(self):
        """Yield grid slices in a south-west direction."""
        for diag in range(self.width + self.height - 1):
            grid_slice = list()
            for col in range(min(self.width, diag+1) - 1, max(0, 1-self.height+diag) - 1, -1):
                grid_slice.append(self.grid[diag-col][col])
            yield grid_slice

    def _yield_slices_west(self):
        """Yield grid slices in a west direction."""
        for row in range(self.height):
            grid_slice = list()
            for col in range(self.width-1, -1, -1):
                grid_slice.append(self.grid[row][col])
            yield grid_slice

    def _yield_slices_north_west(self):
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
    def _validate_grid(grid):
        """Validate the grid parameter. Returns the grid."""

        # Check grid is a list
        if not isinstance(grid, list):
            raise TypeError(
                "invalid value for 'grid' parameter. "
                "Expected list, received '%s'." % type(grid).__name__
            )

        # Check grid is a list of lists
        element_lengths = set()
        for index, element in enumerate(grid):
            if not isinstance(element, list):
                raise TypeError(
                    "invalid value for 'grid' parameter at index %i. "
                    "Expected list, received '%s'." % (index, type(element).__name__)
                )
            element_lengths.add(len(element))

        # Check all lists are the same size
        if len(element_lengths) > 1:
            raise ValueError(
                "invalid value for 'grid' parameter. "
                "Not all rows are the same size."
            )

        # Check each element in the lists are strings
        for index, element in enumerate(grid):
            for tile in element:
                if not isinstance(tile, str):
                    raise TypeError(
                        "invalid value for 'grid' parameter at index %i. "
                        "Not all elements are str, found '%s'" % (index, type(tile).__name__)
                    )
            grid[index] = [tile.upper() for tile in element]

        # Check that each element of grid is a single letter
        for index, element in enumerate(grid):
            for letter in element:
                if len(letter) != 1:
                    raise ValueError(
                        "invalid value for 'grid' parameter at index %i. "
                        "Cannot convert '%s' into a letter." % (index, letter)
                    )
        return grid

    def _validate_directions(self, directions):
        """Validate the directions parameter. Returns the directions."""

        # Check directions is a list or set
        if not isinstance(directions, (list, set)):
            raise TypeError(
                "invalid value for 'directions' parameter. "
                "Expected list or set , received '%s'." % type(directions).__name__
            )

        # Check each element in the directions are strings
        for index, element in enumerate(directions):
            if not isinstance(element, str):
                raise TypeError(
                    "invalid value for 'directions' parameter at index %i. "
                    "Not all elements are str, found '%s'" % (index, type(element).__name__)
                )

        # Check that directions are all valid compass directions or all
        directions = {dir.upper() for dir in directions}

        if not directions.issubset(self.DIRECTIONS.keys() | {"ALL"}):
            raise ValueError(
                "invalid value for 'directions' parameter. "
                "Permitted directions are N, NW, W, SW, S, SE, E, NE or ALL."
            )

        if "ALL" in directions:
            return self.DIRECTIONS.values()

        return {self.DIRECTIONS[direction] for direction in directions}
