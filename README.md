# Word Game Solver
Python3 Word game solvers.

Authored by Christopher Malcolm (chrismalcolm).

Supports the following word games:
* Boggle
* Scrabble
* Hangman
* Words earch

## Installation

```bash
$ pip install wordsolver
```

## Usage

Each word game has a dedicated solver class. This class can be used to provide solutions for it's word game. To solve, firstly the words used for solving have to be added to the solver instance. The words can either be added via a list, set or filename. If loading from a filename, the file should contain each word separated by commas, spaces or newline characters. Examples of each are given below.

```python
# Load words from list
solver = Solver(["CAT", "DOG"])

# Load words from set
solver = Solver({"RED", "BLUE"})

# Load words from the file "dictionary.txt"
solver = Solver("dictionary.txt")
```

Once the solver has been initialised, it is read to solve via the `solve` method. A short description for each word game solver is given below.

### Boggle

For solving Boggle, the `BoggleSolver` class is used. The `solve` method accepts a first arguments as a 2d list representing a board. All letters must be upper case, aside from "Qu" which is also accepted. The letter "Q" will always be substituted for a "Qu". Any size of board dimensions are supported. Solutions are returned as a list of upper case strings.

The `solve` method also has an optional positional argument `with_positions`. If this is set to True, the positions of the solutions are returned, each solution represented as a tuple.

```python
>>> from wordsolver import BoggleSolver
>>> boggle_solver = BoggleSolver("dictionary.txt")
>>> boggle_solver.solve([
...     ["A", "C", "T"],
...     ["N", "O", "I"]
... ])
['ACTION', 'ACTON', 'CION', 'CITO', 'COIT', 'NAOI', 'OTIC', 'ICON', 'ACT', 'CIT', 'COT', 'CON', 'CAN', 'TIC', 'TOC', 'TON', 'NOT', 'OCA', 'ION']
>>>
>>> boggle_solver.solve([
...     ["Qu", "E", "N", "T"],
...     ["E", "X", "D", "L"],
...     ["J", "K", "L", "M"]
... ])
['QUEEN', 'EXED', 'DEEK', 'DENT', 'JEED', 'KEEN', 'EEK', 'END', 'NEE', 'NED', 'EEN', 'XED', 'DEN', 'DEE', 'DEX', 'JEE', 'KEX']
>>>
>>> boggle_solver.solve([
...     ["C", "A", "T"]
... ], with_positions=True)
[('CAT', [[(0, 0), (0, 1), (0, 2)]])]
>>>
```

### Scrabble

For solving Scrabble, the `ScrabbleSolver` class is used. The `solve` method accepts two arguments. The first is a 15x15 2d list representing a Scrabble board. Upper case letters should be used for normal tiles, lower case letters should be used for blanks and the wildcard character "\*" should be used for vacant spaces. The `EMPTY_STANDARD` variable is also provided as a shorthand for representing an empty 15x15 board. The second argument is the rack which should be a list of rack tiles, capital letters for tiles and "#" for blanks. Placements of the solutions are returned as tuple of 4 variables: a string of the word placed in upper case, the x and y coordinates and a boolean value, True for horizontal, False for vertical.

A `get_score` method is also provided for checking the score given for a word placement. This method accepts the same arguments as the previous method, alongside the additional placement argument. The placement should be a tuple of 4 variables: a string of the word placed in upper case, the x and y coordinates and a boolean value, True for horizontal, False for vertical. The score is returned.

```python
>>> from wordsolver import ScrabbleSolver, EMPTY_STANDARD
>>> scrabble_solver = ScrabbleSolver("dictionary.txt")
>>> scrabble_solver.solve(EMPTY_STANDARD, ["Z", "O", "D", "I", "A", "C", "S"])
[('ZODIACS', 3, 7, False, 108), ('ZODIACS', 7, 3, True, 108), ('ZODIACS', 6, 7, False, 94), ... , ('OI', 6, 7, False, 4), ('OI', 7, 6, True, 4)]
>>>
>>> scrabble_solver.get_score(EMPTY_STANDARD, ["A", "#", "E"], ("ARE", 7, 7, False))
4
>>>
>>> test_board = [
...     ["T", "E", "S", "T", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "B", "O", "A", "R", "D", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "O", "*", "P", "*", "O", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "N", "*", "*", "*", "I", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "Y", "*", "*", "*", "N", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "G", "R", "E", "E", "T", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "R", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "C", "A", "T", "c", "H", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "O", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "P", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
...     ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"]
... ]
>>> scrabble_solver.solve(test_board, ["X","I", "N", "G"])
[('XI', 4, 3, True, 31), ('NIX', 8, 4, False, 24), ('TAPING', 3, 0, True, 18), ('OX', 5, 2, False, 17), ... , ('IN', 5, 3, False, 2)]
>>>
```

### Hangman

For solving Hangman, the `HangmanSolver` class is used. The `solve` method accepts two arguments, both are strings. The first argument is the current attempt of the word, with "#" to represent any missing letters. The second argument is a string containing each letter that was a guess but incorrect. Note that the solver automatically assumes that all the letters in the current attempt will not reappear in the final word. A list of possible solutions is returned as a list.

The `guess_distribution` method can be used to get the probabilities of each of the letters being in the solution. A list of tuple pairs in returned, with each letter and their probability.

```python
>>> from wordsolver import HangmanSolver
>>> hangman_solver = HangmanSolver("dictionary.txt")
>>> hangman_solver.solve("UN###", "ABET")
{'UNRIG', 'UNCOY', 'UNHIP', 'UNFIX', 'UNGOD', 'UNDOS', 'UNLID', 'UNZIP', 'UNRID', 'UNDID', 'UNCOS', 'UNRIP', 'UNSOD', 'UNMIX', 'UNIFY', 'UNKID'}
>>> hangman_solver.guess_distrubtion("UN###", "ABET")
[('I', 0.6875), ('D', 0.4375), ('O', 0.3125), ('P', 0.1875), ('S', 0.1875), ... , ('H', 0.0625), ('J', 0), ('V', 0), ('Q', 0), ('W', 0)]
>>>
```

### Word search

For solving a word search, the `WordSearchSolver` class is used. The `solve` method accepts a 2d list representing the word search as its first argument. Any size dimensions are supported. Returns each solution as a tuple, with the word as the first variable, its start x, y coordinates as the second and final x, y coordinates as its last.

The directions to check for words can also be specified via the optional positional argument `directions`. This should be a list containing any combination of the following compass directions ("N", "NE", "E", "SE", "S", "SW", "W", "NW"). Only words reading in the compass directions added will be in the solutions. Without this argument, default behaviour is to check all directions.

```python
>>> import wordsolver import WordSearchSolver
>>> wordsearch_solver = WordSearchSolver("dictionary.txt")
>>> wordsearch_solver.solve([
...     ["C", "O", "A", "T"],
...     ["R", "E", "C", "O"],
...     ["A", "R", "T", "E"],
...     ["M", "E", "S", "S"]
... ])
[('MA', (0, 3), (0, 2)), ('MAR', (0, 3), (0, 1)), ('MARC', (0, 3), (0, 0)), ... , ('ECO', (3, 2), (1, 0))]
>>>
>>> wordsearch_solver.solve([
...     ["C", "O", "A", "T"],
...     ["R", "E", "C", "O"],
...     ["A", "R", "T", "E"],
...     ["M", "E", "S", "S"]
... ], directions=["E", "W"])
[('COAT', (0, 0), (3, 0)), ('OAT', (1, 0), (3, 0)), ('AT', (2, 0), (3, 0)), ('RE', (0, 1), (1, 1)), ... , ('EM', (1, 3), (0, 3))]
```
