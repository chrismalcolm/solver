"""
    Basic CLI for playing a game of Boggle.
"""

# pylint: disable=too-few-public-methods

from collections import defaultdict
import random
import numpy as np

from src.boggle import BoggleSolver
from . import utilities as utils


CUBES_STANDARD = (
    "RIFOBX,IFEHEY,DENOWS,UTOKND,HMSRAO,LUPETS,ACITOA,YLGKUE,"
    "QBMJOA,EHISPN,VETIGN,BALIYT,EZAVND,RALESC,UWILRG,PACEMD"
)

SCHEME_STANDARD = {0:0, 1:0, 2:0, 3:1, 4:1, 5:2, 6:3, 7:5, 8:11}


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
        return self.board.tolist()


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


if __name__ == "__main__":

    # Introduction
    utils.clear()
    print("Welcome to Boggle!\n\n")
    HELP = (
        "Enter words that you see on the tray.\n"
        "Letters to form the words must be adjacent (including diagonally)."
        "Once you have entered your words, "
        "enter 'end turn' to end your turn.\n\n"
    )
    print(HELP)
    input("Press enter to continue...")

    # Initialise any game conditions
    SCHEME = defaultdict(lambda: 11)
    SCHEME.update(SCHEME_STANDARD)

    # Initialise game conditions
    utils.clear()
    SOLVER = BoggleSolver("Collins Scrabble Words (2015).txt")
    TRAY = Tray(4, 4, CUBES_STANDARD)

    # Get number of players
    TOTAL = 0
    while TOTAL == 0:
        INPUT = input("Please input the number of players: ")
        if INPUT.isdigit():
            TOTAL = int(INPUT)

    # Get names of the players
    PLAYERS = list()
    for NUM in range(int(TOTAL)):
        NAME = input("Please input the name of player %i: " % (NUM+1))
        PLAYERS.append(Player(NAME, SCHEME))

    # Shake the tray and get solutions
    print("Shaking the tray and computing solutions...")
    SOLUTIONS = SOLVER.solve(TRAY.shake())

    # Main game loop
    for PLAYER in PLAYERS:
        PLAYER.update_solutions(SOLUTIONS)
        REPORT = ""
        while True:
            utils.clear()
            print(str(PLAYER) + '\n\n' + str(TRAY))
            WORD = input(REPORT + "Please enter a word: ").upper()
            if WORD == "END TURN":
                break
            REPORT = PLAYER.add_word(WORD) + '\n'

    # Summary
    PLAYERS.sort(key=lambda x: -x.score)
    WINNER = PLAYERS[0]
    utils.clear()
    print("The winner is %s with a score of %i\n" % (WINNER.name, WINNER.score))
    print("Final standings: ")
    for PLAYER in PLAYERS:
        print('\n' + PLAYER.summary())
    print(
        "\n%s\nAll possible words:\n%s\n\n"
        "Thank you for playing!\n" % (str(TRAY), ", ".join(SOLUTIONS))
    )
