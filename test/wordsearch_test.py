"""Test module for the wordsearch module."""

import unittest
from src import wordsearch


class WordSearchTest(unittest.TestCase):
    """Class for testing the wordsearch module."""

    @classmethod
    def setUpClass(cls):
        """Define the solver."""
        cls.solver = wordsearch.WordSearchSolver("test/dictionary.txt")

    def test_sample(self):
        """Basic test."""
        sols = {
            ('ER', (1, 2), (1, 1)),
            ('AE', (2, 2), (2, 1)),
            ('ET', (2, 1), (2, 0))
        }
        solutions = self.solver.solve(
            [
                ["A", "C", "T"],
                ["C", "R", "E"],
                ["T", "E", "A"]
            ],
            directions=["N"]
        )
        for sol in sols:
            self.assertIn(sol, solutions)

        # All directions
        sols = {
            ('ER', (1, 2), (1, 1)), ('AE', (2, 2), (2, 1)),
            ('ET', (2, 1), (2, 0)), ('EE', (1, 2), (2, 1)),
            ('ACT', (0, 0), (2, 0)), ('RE', (1, 1), (2, 1)),
            ('TE', (0, 2), (1, 2)), ('TEA', (0, 2), (2, 2)),
            ('EA', (1, 2), (2, 2)), ('AR', (0, 0), (1, 1)),
            ('ACT', (0, 0), (0, 2)), ('RE', (1, 1), (1, 2)),
            ('TE', (2, 0), (2, 1)), ('TEA', (2, 0), (2, 2)),
            ('EA', (2, 1), (2, 2)), ('EE', (2, 1), (1, 2)),
            ('ER', (2, 1), (1, 1)), ('AE', (2, 2), (1, 2)),
            ('ET', (1, 2), (0, 2)), ('AR', (2, 2), (1, 1))
        }
        solutions = self.solver.solve(
            [
                ["A", "C", "T"],
                ["C", "R", "E"],
                ["T", "E", "A"]
            ]
        )
        for sol in sols:
            self.assertIn(sol, solutions)
