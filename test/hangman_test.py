"""Test module for the hangman module."""

import unittest
from src import hangman


class HangmanTest(unittest.TestCase):
    """Class for testing the hangman module."""

    @classmethod
    def setUpClass(cls):
        """Define the solver."""
        cls.solver = hangman.HangmanSolver("test/dictionary.txt")

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
            self.solver.guess_distrubtion("AB###", "")
        )
