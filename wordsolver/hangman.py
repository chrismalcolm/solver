"""
    This module contains the HangmanSolver, used to list the remaining letters
    in a game of Hangman, in order of chance of being correct.
"""

from collections import defaultdict
import re
from string import ascii_uppercase
from itertools import product
from wordsolver import wordtools


class HangmanSolver(wordtools.WordHash):
    """
        Class for solving a game of Hangman.

        Attempt to guess the solution.

        Attributes:
        > _candidates (set) - list of words that satify the criteria
        > _length (int) - length of the solution
        > _correct (dict) - mapping of correct letters
        > _incorrect (iterable) - letters which are not in the word
        > _words_of_length (dict) - keys are word lengths, values are all words
            added with that length
    """

    def __init__(self, filename):
        super().__init__()
        self.candidates = set()
        self.length = 0
        self.correct = defaultdict(set)
        self.incorrect = defaultdict(set)
        self.attempt = ""
        self.words_of_length = defaultdict(set)
        self._upload_words(filename)

    def _upload_words(self, collection):
        """Upload the Dictionary words from a text file 'filename'. When
        solving, the words from this text file will be used for spell
        checking."""
        self.clear_words()
        for word in self._validate_collection(collection):
            if not word.isalpha():
                continue
            self.add_word(word)
            self.words_of_length[len(word)].add(word)

    def solve(self, attempt, incorrect):
        """
            Returns a set of all words which fit the criteria.

            Parameters:
            > attempt (iterable) - the current guess of the solution. All
                unknown letters must be filled in with an non-alphabetical
                character.
            > incorrect (iterable) - letters which are not in the word

            Returns:
            > (set) - all words which fit the criteria
        """
        attempt, incorrect = self._validate_parameters(attempt, incorrect)
        self._reduce_candidates(attempt, incorrect)
        return self.candidates

    def guess_distribution(self, attempt, wrong):
        """
            Returns the probability for each letter to be in the word.

            Parameters:
            > attempt (iterable) - the current guess of the solution. All
                unknown letters must be filled in with an non-alphabetical
                character.
            > wrong (iterable) - letters which are not in the word

            Returns:
            > (list) - each element is in the form (letter, probability)
        """
        attempt, wrong = self._validate_parameters(attempt, wrong)
        self._reduce_candidates(attempt, wrong)

        tally = dict.fromkeys(set(ascii_uppercase) - self.incorrect.keys(), 0)

        for candidate in self.candidates:
            for letter in set(candidate) & tally.keys():
                tally[letter] += 1/len(self.candidates)

        return sorted(tally.items(), key=lambda x: -x[1])

    def _reduce_candidates(self, attempt, wrong):
        """
            Filters out all candidates in self.candidates which do not reach
            the specification.

            Parameters:
            > attempt (iterable) - current guess
            > wrong (iterable) - wrong letters
        """
        self.length = len(attempt)
        self.candidates = self.words_of_length[self.length]

        self.correct.clear()
        self.incorrect.clear()

        for pos, let in enumerate(attempt):
            if not let in ascii_uppercase:
                continue
            self.correct[let].add(pos)
            self.incorrect[let] |= (set(range(self.length)) - {pos})

        for pos, let in product(range(self.length), wrong):
            if not let in ascii_uppercase:
                continue
            self.incorrect[let].add(pos)

        self._filter_correct_letters(self.correct)
        self._filter_incorrect_letters(self.incorrect)

    def _filter_correct_letters(self, requirements):
        """
            Filters out all candidates in self.candidates which do not reach
            the specification.

            The specification is that for each (letter, positions) pair in
            'requirements', a candidate must have the letter at all the indicies
            in positions.

            Parameters:
            > requirements (dict) - mapping letters (str) and positions (list)
        """
        self.candidates = self.candidates.intersection(
            *[
                self.lookup(self.length, let, pos)
                for let, pos in self._yield_requirements(requirements)
            ]
        )

    def _filter_incorrect_letters(self, requirements):
        """
            Filters out all candidates in self.candidates which do not reach
            the specification.

            The specification is that for each (letter, positions) pair in
            'requirements', a candidate must not have the letter in any of the
            indicies in positions.

            Parameters:
            > requirements (dict) - mapping letters (str) and positions (list)
        """
        self.candidates = self.candidates.difference(
            *[
                self.lookup(self.length, let, pos)
                for let, pos in self._yield_requirements(requirements)
            ]
        )

    @staticmethod
    def _yield_requirements(requirements):
        """Yields the letter and positions in requirements."""
        for letter, positions in requirements.items():
            for position in positions:
                yield (letter, position)

    @staticmethod
    def _validate_collection(collection):
        """Validate the collection parameter. Returns the words extracted."""

        # Return collection if it is already a list/set
        if isinstance(collection, (list, set)):
            return [word.upper() for word in collection]

        # Opens file and return lists of words in the file
        if isinstance(collection, str):
            with open(collection, "r") as file_text:
                text = file_text.read()
            return re.findall(r"[\w']+", text.upper())

        # Else an incorrect type has been received
        raise TypeError(
            "invalid value for 'collection' parameter. "
            "Expected list, set or str, received '%s'." % type(collection).__name__
        )

    @staticmethod
    def _validate_parameters(attempt, wrong):

        # Check that attempt is a list or str
        if isinstance(attempt, str):
            attempt = list(attempt)
        elif not isinstance(attempt, list):
            raise TypeError(
                "invalid value for 'attempt' parameter. "
                "Expected list, set or str received '%s'." % type(attempt).__name__
            )

        # Check that attempt elements are strings
        element_lengths = set()
        for index, element in enumerate(attempt):
            if not isinstance(element, str):
                raise TypeError(
                    "invalid value for 'attempt' parameter at index %i. "
                    "Expected str, received '%s'." % (index, type(element).__name__)
                )
            attempt[index] = element.upper()
            element_lengths.add(len(element))

        # Check each element of attempt is a single character
        if element_lengths != {1}:
            raise ValueError(
                "invalid value for 'attempt' parameter. "
                "Not all strings are characters."
            )

        # Check that wrong is a list set or str
        if isinstance(wrong, (list, str)):
            wrong = set(wrong)
        elif not isinstance(wrong, set):
            raise TypeError(
                "invalid value for 'wrong' parameter. "
                "Expected list, set or str received '%s'." % type(attempt).__name__
            )

        # Check that wrong is a set of strings
        element_lengths = set()
        for index, element in enumerate(wrong):
            if not isinstance(element, str) or not element.isalpha():
                raise TypeError(
                    "invalid value for 'wrong' parameter at index %i. "
                    "Expected alphabet character, received '%s'." % (index, type(element).__name__)
                )
            element_lengths.add(len(element))
        wrong = {letter.upper() for letter in wrong}

        # Check each element of wrong is a single character (if non-empty)
        if wrong and element_lengths != {1}:
            raise ValueError(
                "invalid value for 'wrong' parameter. "
                "Not all strings are characters."
            )

        return attempt, wrong
