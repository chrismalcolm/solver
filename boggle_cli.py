"""
    Basic CLI for playing a game of Boggle.
"""

from collections import defaultdict

from boggle_data import CUBES_STANDARD, SCHEME_STANDARD
from boggle import Solver, Tray, Player
import solver_cli


if __name__ == "__main__":

    # Introduction
    solver_cli.clear()
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
    solver_cli.clear()
    SOLVER = Solver("Collins Scrabble Words (2015).txt")
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
            solver_cli.clear()
            print(str(PLAYER) + '\n\n' + str(TRAY))
            WORD = input(REPORT + "Please enter a word: ").upper()
            if WORD == "END TURN":
                break
            REPORT = PLAYER.add_word(WORD) + '\n'

    # Summary
    PLAYERS.sort(key=lambda x: -x.score)
    WINNER = PLAYERS[0]
    solver_cli.clear()
    print("The winner is %s with a score of %i\n" % (WINNER.name, WINNER.score))
    print("Final standings: ")
    for PLAYER in PLAYERS:
        print('\n' + PLAYER.summary())
    print(
        "\n%s\nAll possible words:\n%s\n\n"
        "Thank you for playing!\n" % (str(TRAY), ", ".join(SOLUTIONS))
    )
