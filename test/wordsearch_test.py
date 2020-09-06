"""Test module for the wordsearch module."""

import unittest
from src import wordsearch


class WordSearchTest(unittest.TestCase):
    """Class for testing the wordsearch module."""

    @classmethod
    def setUpClass(cls):
        """Define the solver."""
        cls.solver = wordsearch.WordSearchSolver("test/dictionary.txt")
        cls.grid = [
            ["C", "A", "R", "O", "L"],
            ["O", "R", "E", "E", "A"],
            ["R", "O", "A", "S", "T"],
            ["E", "P", "L", "T", "T"],
            ["S", "L", "A", "T", "E"],
        ]

    def test_from_list(self):
        """Test words can be loaded from a list."""
        solver = wordsearch.WordSearchSolver(["LEAPS", "CORES"])
        correct = [
            ('CORES', (0, 0), (0, 4)),
            ('LEAPS', (4, 0), (0, 4))
        ]
        solutions = solver.solve(self.grid)
        self.assertEqual(len(correct), len(solutions))
        for solution in solutions:
            self.assertIn(solution, correct)

    def test_from_set(self):
        """Test words can be loaded from a set."""
        solver = wordsearch.WordSearchSolver({"CAROL", "CRATE"})
        correct = [
            ('CAROL', (0, 0), (4, 0)),
            ('CRATE', (0, 0), (4, 4))
        ]
        solutions = solver.solve([
            ["C", "A", "R", "O", "L"],
            ["O", "R", "E", "E", "A"],
            ["R", "O", "A", "S", "T"],
            ["E", "P", "L", "T", "T"],
            ["S", "L", "A", "T", "E"],
        ])
        self.assertEqual(len(correct), len(solutions))
        for solution in solutions:
            self.assertIn(solution, correct)

    def test_basic(self):
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

    def test_init_exceptions(self):
        """Test all exceptions that can be raised with init parameters."""
        self.assertRaises(TypeError, wordsearch.WordSearchSolver, 1)

    def test_solve_exceptions(self):
        """Test all exceptions that can be raised with solve parameters."""
        self.assertRaises(TypeError, self.solver.solve, 1)
        self.assertRaises(TypeError, self.solver.solve, [1])
        self.assertRaises(ValueError, self.solver.solve, [["A"], ["B", "C"]])
        self.assertRaises(TypeError, self.solver.solve, [[1, 2], [3, 4]])
        self.assertRaises(ValueError, self.solver.solve, [["AB", "C"], ["D", "E"]])
        self.assertRaises(TypeError, self.solver.solve, self.grid, 2)
        self.assertRaises(TypeError, self.solver.solve, self.grid, {3, 4, 5})
        self.assertRaises(ValueError, self.solver.solve, self.grid, {"A", "N", "C"})
