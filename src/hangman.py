"""
    This module contains the HangmanSolver, used to list the remaining letters
    in a game of Hangman, in order of chance of being correct.
"""

from collections import defaultdict
import re

from src import wordtools

class HangmanSolver(wordtools.WordHash):
    """
        Class for solving a game of Hangman.

        This is not fully implemented yet.

        Attributes:
        > words_of_length (dict) - keys are word lengths, values are all
            words added with that length
    """

    def __init__(self, filename):
        super().__init__()
        self.words_of_length = defaultdict(set)
        self._upload_words(filename)

    def _upload_words(self, filename):
        """Upload the Dictionary words from a text file 'filename'. When
        solving, the words from this text file will be used for spell
        checking."""
        self.clear_words()
        with open(filename, "r") as file_text:
            text = file_text.read()
        words = re.findall(r"[\w']+", text.upper())
        for word in words:
            self.add_word(word)
            self.words_of_length[len(word)].add(word)
