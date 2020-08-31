# Word Game Solver
Python3 Word game solvers.

Authored by Christopher Malcolm (chrismalcolm).

Supports the following word games:
* Boggle
* Scrabble
* Hangman
* Wordsearch

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

```python
>>> from src import boggle
>>> solver = boggle.BoggleSolver("test/dictionary.txt")
>>> solver.solve([
...     ["A", "C", "T"],
...     ["N", "O", "I"]
... ])
['ACTION', 'ACTON', 'CION', 'CITO', 'COIT', 'NAOI', 'OTIC', 'ICON', 'ACT', 'CIT', 'COT', 'CON', 'CAN', 'TIC', 'TOC', 'TON', 'NOT', 'OCA', 'ION']
>>>
```

### Scrabble

```python
>>> from src import scrabble
>>> solver = scrabble.ScrabbleSolver("test/dictionary.txt")
>>> solver.solve(scrabble.EMPTY_STANDARD, ["Z", "O", "D", "I", "A", "C", "S"])
[('ZODIACS', 3, 7, False, 108), ('ZODIACS', 7, 3, True, 108), ('ZODIACS', 6, 7, False, 94), ... , ('OS', 7, 6, True, 4), ('OI', 6, 7, False, 4), ('OI', 7, 6, True, 4)]
>>> solver.get_score(scrabble.EMPTY_STANDARD, ["A", "#", "E"], ("ARE", 7, 7, False))
4
>>>
```

### Hangman

```python
>>> from src import hangman
>>> solver = hangman.HangmanSolver("test/dictionary.txt")
>>> solver.solve("UN###", "ABET")
{'UNRIG', 'UNCOY', 'UNHIP', 'UNFIX', 'UNGOD', 'UNDOS', 'UNLID', 'UNZIP', 'UNRID', 'UNDID', 'UNCOS', 'UNRIP', 'UNSOD', 'UNMIX', 'UNIFY', 'UNKID'}
>>> solver.guess_distrubtion("UN###", "ABET")
[('I', 0.6875), ('D', 0.4375), ('O', 0.3125), ('P', 0.1875), ('S', 0.1875), ('R', 0.1875), ('F', 0.125), ('Y', 0.125), ('G', 0.125), ('X', 0.125), ('C', 0.125), ('Z', 0.0625), ('M', 0.0625), ('L', 0.0625), ('K', 0.0625), ('H', 0.0625), ('J', 0), ('V', 0), ('Q', 0), ('W', 0)]
>>>
```

### Wordsearch

```python
>>> from src import wordsearch
>>> solver = wordsearch.WordSearchSolver("test/dictionary.txt")
>>> solver.solve([
...     ["C", "O", "A", "T"],
...     ["R", "E", "C", "O"],
...     ["A", "R", "T", "E"],
...     ["M", "E", "S", "S"]
... ])
[('MA', (0, 3), (0, 2)), ('MAR', (0, 3), (0, 1)), ('MARC', (0, 3), (0, 0)), ('AR', (0, 2), (0, 1)), ('ARC', (0, 2), (0, 0)), ('ER', (1, 3), (1, 2)), ('ERE', (1, 3), (1, 1)), ('RE', (1, 2), (1, 1)), ('REO', (1, 2), (1, 0)), ('ST', (2, 3), (2, 2)), ('AE', (0, 2), (1, 1)), ('EA', (1, 1), (2, 0)), ('ET', (1, 3), (2, 2)), ('TO', (2, 2), (3, 1)), ('COAT', (0, 0), (3, 0)), ('OAT', (1, 0), (3, 0)), ('AT', (2, 0), (3, 0)), ('RE', (0, 1), (1, 1)), ('REC', (0, 1), (2, 1)), ('ECO', (1, 1), (3, 1)), ('AR', (0, 2), (1, 2)), ('ART', (0, 2), (2, 2)), ('TE', (2, 2), (3, 2)), ('ME', (0, 3), (1, 3)), ('MES', (0, 3), (2, 3)), ('MESS', (0, 3), (3, 3)), ('ES', (1, 3), (2, 3)), ('ESS', (1, 3), (3, 3)), ('AE', (0, 2), (1, 3)), ('ET', (1, 1), (2, 2)), ('CRAM', (0, 0), (0, 3)), ('RAM', (0, 1), (0, 3)), ('AM', (0, 2), (0, 3)), ('OE', (1, 0), (1, 1)), ('ER', (1, 1), (1, 2)), ('ERE', (1, 1), (1, 3)), ('RE', (1, 2), (1, 3)), ('ACT', (2, 0), (2, 2)), ('ACTS', (2, 0), (2, 3)), ('TO', (3, 0), (3, 1)), ('TOE', (3, 0), (3, 2)), ('TOES', (3, 0), (3, 3)), ('OE', (3, 1), (3, 2)), ('OES', (3, 1), (3, 3)), ('ES', (3, 2), (3, 3)), ('OR', (1, 0), (0, 1)), ('AE', (2, 0), (1, 1)), ('EA', (1, 1), (0, 2)), ('TE', (2, 2), (1, 3)), ('ES', (3, 2), (2, 3)), ('TA', (3, 0), (2, 0)), ('TAO', (3, 0), (1, 0)), ('ER', (1, 1), (0, 1)), ('ET', (3, 2), (2, 2)), ('EM', (1, 3), (0, 3)), ('EA', (1, 3), (0, 2)), ('ST', (3, 3), (2, 2)), ('TE', (2, 2), (1, 1)), ('TEC', (2, 2), (0, 0)), ('ECO', (3, 2), (1, 0))]
>>>
```

## CLI

To play a game of Boggle in the CLI, use the command `python3 -m cli.boggle_cli`.

To play a game of Scrabble in the CLI, use the command `python3 -m cli.scrabble_cli`.

Hangman TBC.

Wordsearch TBC.
