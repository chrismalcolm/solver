"""
    Basic CLI for playing a game of Scrabble.
"""

# pylint: disable=invalid-name

from enum import Enum
from itertools import product
import random
from string import ascii_uppercase
import numpy as np

from src import scrabble
from src.scrabble import ScrabbleSolver, PREMIUM_STANDARD
from . import utilities as utils


TILES_STANDARD = [
    'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'C', 'C', 'D', 'D',
    'D', 'D', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'F',
    'F', 'G', 'G', 'G', 'H', 'H', 'I', 'I', 'I', 'I', 'I', 'I', 'I', 'I', 'I',
    'J', 'K', 'L', 'L', 'L', 'L', 'M', 'M', 'N', 'N', 'N', 'N', 'N', 'N', 'O',
    'O', 'O', 'O', 'O', 'O', 'O', 'O', 'P', 'P', 'Q', 'R', 'R', 'R', 'R', 'R',
    'R', 'S', 'S', 'S', 'S', 'T', 'T', 'T', 'T', 'T', 'T', 'U', 'U', 'U', 'U',
    'V', 'V', 'W', 'W', 'X', 'Y', 'Y', 'Z', '#', '#'
]


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
        #rows[rows == None] = '\033[92m' + "*" + '\033[95m'
        for row, col in np.ndindex(rows.shape):
            tile = rows[row, col] or "*"
            if row == (rows.shape[1]-1)/2 and col == (rows.shape[0]-1)/2:
                colour = '\33[103m\33[30m'
            else:
                colour = {
                    "d": '\33[46m\33[30m',
                    "t": '\33[44m\33[30m',
                    "D": '\33[43m\33[30m',
                    "T": '\33[41m\33[30m'
                }.get(PREMIUM_STANDARD[row][col], '\33[40m')
            rows[row, col] = colour + tile + '\33[40m' + '\33[0m'
        header = list(ascii_uppercase)[:self.width]
        main = [f'\n{n+1:>2} ' + " ".join(row) for n, row in enumerate(rows)]
        return "   " + " ".join(header) + "".join(main)

    def get_tiles(self):
        """Returns the tiles as a list of lists."""
        matrix = list()
        for row in self.tiles:
            new_row = list()
            for element in row:
                new_row.append(element if element else "*")
            matrix.append(new_row)
        return matrix

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
        > solver (ScrabbleSolver) - instance of ScrabbleSolver used for calculating
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
        points = self.solver.get_score(self.board.get_tiles(), self.rack, attempt)
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


def parse_command(solutions, instructions):
    """Parse a command (commands referenced in HELP)."""
    if not solutions:
        print("No placements are possible!")
        return ("", 0, 0, 0)
    placement = input("Please enter ypur placement: ")
    if placement in ["/H", "/HELP"]:
        print(instructions)
        return None
    if placement in ["/S", "/SKIP"]:
        return ("", 0, 0, 0)
    if placement in ["/B", "/BEST"]:
        return solutions[0][0:4]
    attempt = parse_placement(placement)
    if attempt:
        return attempt
    print("Command was invalid")
    return None

def parse_placement(input_string):
    """Parse the input when getting the placement for a new word on
    the board."""
    split_string = input_string.split()
    letters = "ABCDEFGHIJKLMNO"
    if len(split_string) == 3:
        if not (
                len(split_string[1]) >= 2 and split_string[1][0] in letters and
                split_string[1][1:].isdigit() and split_string[2] in ["0", "1"]
        ):
            return None
        word = split_string[0]
        col = letters.index(split_string[1][0])
        row = int(split_string[1][1:]) - 1
        orientation = bool(int(split_string[2]))
        return (word, col, row, orientation)
    return None

def print_turn(players, turn, board, bag):
    """Prints relevant info at the beginning of the player's turn."""
    print("%s's turn\n" % players[turn].name)
    print("Current Standings:\n\nTiles left in bag %i" % len(bag.tiles))
    for player in players:
        summary = "%s - Score %i, Tiles %i"
        print(summary % (player.name, player.score, len(player.rack)))
    print('\n' + str(board))


if __name__ == "__main__":

    # Introduction
    utils.clear()
    print("Welcome to Scrabble!\n\n")
    HELP = (
        "To place a word on the word, type in the full word, the "
        "coordinates and the orientation:\n\n"
        "> word - the full word you want to form on the board, including "
        "letters of tiles currently on the board. Normal tiles in caps, "
        "blank tiles in lower case\n"
        "> coordinate - the starting coordinate of the word\n"
        "> orientation - 0 : horizontal, 1: vertical\n\n"
        "Examples:\n"
        "READY H8 0 - spells 'READY' horizontally, starting at H8\n"
        "TRUNCATE C4 1 - spells 'TRUNCATE' vertically, starting at C4\n"
        "FREnZY B11 1- spells 'FRENZY' vertically at B11, with a blank n\n\n"
        "Enter '/SKIP' or '/S' to skip your turn.\n"
        "Enter '/BEST' or '/B' to enter the highest scoring word\n"
        "Enter '/HELP' or '/H' to show the help\n\n"
    )
    print(HELP)
    input("Press enter to continue...")

    # Initialise game conditions
    utils.clear()
    SOLVER = ScrabbleSolver("Collins Scrabble Words (2015).txt")
    BOARD = Board(15, 15)
    BAG = Bag()

    # Get number of players
    TOTAL = 0
    while TOTAL == 0:
        INPUT = input("Please input the number of players: ")
        if INPUT.isdigit():
            TOTAL = int(INPUT)

    # Get names of the players
    PLAYERS = list()
    for NUM in range(TOTAL):
        NAME = input("Please input the name of player %i: " % (NUM+1))
        PLAYERS.append(Player(NAME, SOLVER, BOARD, BAG))

    # Main game loop
    COUNTER = 0
    SKIPPED = 0
    while BAG.tiles or SKIPPED < TOTAL:

        # Calculate the solutions given the current player's rack
        utils.clear()
        print("Calculating solutions...")
        PLAYER = PLAYERS[COUNTER]
        SOLUTIONS = SOLVER.solve(BOARD.get_tiles(), PLAYER.rack)

        # Show the current player the game stats
        utils.clear()
        print_turn(PLAYERS, COUNTER, BOARD, BAG)
        input("\nPress enter to see your tiles\n")
        print(PLAYER)

        # Turn loop
        while True:
            REPLY = parse_command(SOLUTIONS, HELP)
            if not REPLY:
                continue
            WORD, X, Y, ORIENTATION = REPLY
            if not WORD:
                PLAYER.reset_tiles()
                SKIPPED += 1
                break
            SCORE = PLAYER.add_word(*REPLY)
            if SCORE >= 0:
                SKIPPED = 0
                break
            print("Placement was invalid!")

        # Summarise the players turn
        utils.clear()
        PLAYER.replenish_tiles()
        print_turn(PLAYERS, COUNTER, BOARD, BAG)
        print(PLAYER)
        if WORD:
            print("%s has been successfully placed scoring %i!" % (WORD, SCORE))
        input("\nPress enter to end your turn\n")
        COUNTER = (COUNTER + 1) % TOTAL

    # Summarise the game
    utils.clear()
    PLAYERS.sort(key=lambda x: -x.score)
    WINNER = PLAYERS[0]
    print("The winner is %s with a score of %i\n" % (WINNER.name, WINNER.score))
    print("Final standings: ")
    for PLAYER in PLAYERS:
        print('\n' + PLAYER.summary())
    print('\n' + str(BOARD))
    print("\nThank you for playing!")
