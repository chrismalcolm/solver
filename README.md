# solver
Python3 board game solvers, authored by Christopher Malcolm (chrismalcolm).

## Boggle
To play a game of Boggle in the CLI, in the solver repository, run the command:
```bash
python3 -m boggle_cli
```
It is also possible to use the `Solver` object to solve your own Boggle boards, via the example below:
```python
# python3 terminal
>>> from boggle import Solver
>>> s = Solver("Collins Scrabble Words (2015).txt")
>>> s.solve(
...     [["A","B"],
...      ["T","C"]]
... )
['ACT', 'BAT', 'BAC', 'TAB', 'CAB', 'CAT']
>>>
```
The board input of the `Solver.solve` method must be a 2d matrix, with all entries in caps.

## Scrabble
To play a game of Scrabble in the CLI, in the solver repository, run the command:
```bash
python3 -m scrabble_cli
```
It is also possible to use the `Solver` object to solve your own Scrabble boards, via the example below:
```python
# python3 terminal
>>> from scrabble import Solver
>>> from scrabble_data import EMPTY_STANDARD as EMPTY
>>> s = Solver("Collins Scrabble Words (2015).txt")
>>> s.solve(EMPTY, ["C", "A", "T"])
[('CAT', 7, 7, False, 10), ('CAT', 6, 7, False, 10), ('ACT', 7, 7, False, 10), ...
... ('AT', 7, 6, True, 4), ('TA', 7, 7, True, 4)]
>>>
```
The board input of the `Solver.solve` method must be a 2d matrix. Entries should be in caps for normal tiles, lower case for blanks. Empty spaces can be "", "\*" or `None`. The `EMPTY_STANDARD` imported from `scrabble_data` is a 15x15 matrix representing an empty board.
