"""Test module for the scrabble module."""

import unittest
from src import scrabble


class ScrabbleTest(unittest.TestCase):
    """Class for testing the scrabble module."""

    @classmethod
    def setUpClass(cls):
        """Define the solver."""
        cls.solver = scrabble.ScrabbleSolver("test/dictionary.txt")
        cls.board = [
            ["T", "E", "S", "T", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "B", "O", "A", "R", "D", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "O", "*", "P", "*", "O", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "N", "*", "*", "*", "I", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "Y", "*", "*", "*", "N", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "G", "R", "E", "E", "T", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "R", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "C", "A", "T", "c", "H", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "O", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "P", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"],
            ["*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*", "*"]
        ]

    def test_from_list(self):
        """Test words can be loaded from a list."""
        solver = scrabble.ScrabbleSolver(["CAT", "DOG"])
        solutions = solver.solve(scrabble.EMPTY_STANDARD, ["C", "A", "T", "D", "O", "G"])
        self.assertEqual(12, len(solutions))

    def test_from_set(self):
        """Test words can be loaded from a set."""
        solver = scrabble.ScrabbleSolver({"ABC", "DEF"})
        solutions = solver.solve(scrabble.EMPTY_STANDARD, ["A", "B", "C", "D", "E", "F"])
        self.assertEqual(12, len(solutions))

    def test_blanks(self):
        """Test words can be found without blanks."""
        solutions = self.solver.solve(self.board, ["#", "#", "T"])
        self.assertIn(('Too', 11, 7, True, 16), solutions)
        self.assertEqual(3293, len(solutions))

    def test_no_blanks(self):
        """Test words can be found with blanks."""
        solutions = self.solver.solve(self.board, ["I", "N", "G"])
        self.assertIn(('TAPING', 3, 0, True, 18), solutions)
        self.assertEqual(55, len(solutions))

    def test_get_score(self):
        """Test the get_score function."""
        self.assertEqual(
            18,
            self.solver.get_score(self.board, ["I", "N", "G"], ('TAPING', 3, 0, True))
        )
        self.assertEqual(
            16,
            self.solver.get_score(self.board, ["#", "#", "T"], ('Too', 11, 7, True))
        )
        self.assertEqual(
            -1,
            self.solver.get_score(self.board, ["#", "#", "T"], ('TOOT', 11, 7, True))
        )

    def test_init_exceptions(self):
        """Test all exceptions that can be raised with init parameters."""
        self.assertRaises(TypeError, scrabble.ScrabbleSolver, 1)

    def test_solve_exceptions(self):
        """Test all exceptions that can be raised with solve parameters."""
        self.assertRaises(TypeError, self.solver.solve, 1, ["A", "B", "C"])
        self.assertRaises(ValueError, self.solver.solve, [1], ["A", "B", "C"])
        self.assertRaises(ValueError, self.solver.solve, [[1]], ["A", "B", "C"])
        self.assertRaises(
            ValueError,
            self.solver.solve,
            [
                ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
            ],
            ["A", "B", "C"]
        )

    def test_get_score_exceptions(self):
        """Test all exceptions that can be raised with get_score paramters."""
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            (1, 2, 3)
        )
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            (1, 2, 3, 4, 5)
        )
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            ([], 2, 3, True)
        )
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            ("ABC", [], 3, True)
        )
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            ("ABC", 5, [], True)
        )
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            ("ABC", 5, 3, [])
        )
        self.assertRaises(
            ValueError,
            self.solver.get_score,
            self.board,
            ["#", "#", "T"],
            ("123", 5, 3, True)
        )
