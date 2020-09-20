"""Test module for the hangman module."""

import unittest
from wordsolver import HangmanSolver


class HangmanTest(unittest.TestCase):
    """Class for testing the hangman module."""

    @classmethod
    def setUpClass(cls):
        """Define the solver."""
        cls.solver = HangmanSolver("test/dictionary.txt")

    def test_from_list(self):
        """Test words can be loaded from a list."""
        solver = HangmanSolver(["ROUND", "ROOTS", "SOUND", "ABOUT"])
        self.assertEqual({"ROUND"}, solver.solve("RO###", "S"))

    def test_from_set(self):
        """Test words can be loaded from a list."""
        solver = HangmanSolver({"ROUND", "ROOTS", "SOUND", "ABOUT"})
        self.assertEqual({"ABOUT"}, solver.solve("##O##", "R"))

    def test_basic(self):
        """Basic test."""
        self.assertEqual(
            {
                'ABOUT', 'ABCEE', 'ABLOW', 'ABUZZ', 'ABRIN', 'ABORT', 'ABORE',
                'ABUNE', 'ABOHM', 'ABLES', 'ABERS', 'ABHOR', 'ABETS', 'ABLER',
                'ABMHO', 'ABOVE', 'ABRIM', 'ABYSS', 'ABSEY', 'ABIES', 'ABYSM',
                'ABUTS', 'ABIDE', 'ABLED', 'ABLET', 'ABELE', 'ABOIL', 'ABOON',
                'ABRIS', 'ABODE', 'ABORD', 'ABYES', 'ABSIT', 'ABUSE'
            },
            self.solver.solve("AB###", "")
        )
        self.assertIn(
            ('E', 0.5),
            self.solver.guess_distribution("AB###", "")
        )

    def test_init_exceptions(self):
        """Test all exceptions that can be raised with init parameters."""
        self.assertRaises(TypeError, HangmanSolver, 1)

    def test_solve_exceptions(self):
        """Test all exceptions that can be raised with solve parameters."""
        self.assertRaises(TypeError, self.solver.solve, 1, "AOS")
        self.assertRaises(TypeError, self.solver.solve, [1, 2, 3], "AOS")
        self.assertRaises(ValueError, self.solver.solve, ["THE", "ERR"], "AOS")
        self.assertRaises(TypeError, self.solver.solve, "T###", 2)
        self.assertRaises(TypeError, self.solver.solve, "T###", [4, 5, 6])
        self.assertRaises(ValueError, self.solver.solve, "T###", ["RE", "DS"])

    def test_guess_exceptions(self):
        """Test all exceptions that can be raised with guess_distribution
        parameters."""
        self.assertRaises(TypeError, self.solver.guess_distribution, 1, "AOS")
        self.assertRaises(TypeError, self.solver.guess_distribution, [1, 2, 3], "AOS")
        self.assertRaises(ValueError, self.solver.guess_distribution, ["THE", "ERR"], "AOS")
        self.assertRaises(TypeError, self.solver.guess_distribution, "T###", 2)
        self.assertRaises(TypeError, self.solver.guess_distribution, "T###", [4, 5, 6])
        self.assertRaises(ValueError, self.solver.guess_distribution, "T###", ["RE", "DS"])
