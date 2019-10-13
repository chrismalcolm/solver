"""
    Basic CLI for playing a game of Scrabble.
"""

from scrabble import Solver, Board, Bag, Player

import solver_cli


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
    solver_cli.clear()
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
    solver_cli.clear()
    SOLVER = Solver("Collins Scrabble Words (2015).txt")
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
        solver_cli.clear()
        print("Calculating solutions...")
        PLAYER = PLAYERS[COUNTER]
        SOLUTIONS = SOLVER.solve(BOARD.tiles, PLAYER.rack)

        # Show the current player the game stats
        solver_cli.clear()
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
        solver_cli.clear()
        PLAYER.replenish_tiles()
        print_turn(PLAYERS, COUNTER, BOARD, BAG)
        print(PLAYER)
        if WORD:
            print("%s has been successfully placed scoring %i!" % (WORD, SCORE))
        input("\nPress enter to end your turn\n")
        COUNTER = (COUNTER + 1) % TOTAL

    # Summarise the game
    solver_cli.clear()
    PLAYERS.sort(key=lambda x: -x.score)
    WINNER = PLAYERS[0]
    print("The winner is %s with a score of %i\n" % (WINNER.name, WINNER.score))
    print("Final standings: ")
    for PLAYER in PLAYERS:
        print('\n' + PLAYER.summary())
    print('\n' + BOARD)
    print("\nThank you for playing!")
