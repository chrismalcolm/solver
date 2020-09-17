"""
    This module provides classes making the process of checking word
    spelling more efficient.
"""

from collections import defaultdict


class WordNode():
    """
        Node object for the WordTree data structure.

        Attributes:
        > letter (str) - value of the node
        > children (list) - list of child node objects
        > my_word (str) - if this node completes a word, my_word is
            assigned to that word, else it equals ""
    """

    def __init__(self, letter=""):
        self.letter = letter
        self.children = []
        self.my_word = ""

    def add_child(self, letter):
        """Creates a new child WordNode object, assigning it with the
        given letter."""
        child = WordNode(letter)
        self.children.append(child)
        return child

    def get_child(self, letter):
        """Returns the child WordNode with the given letter, if it
        exists."""
        for child in self.children:
            if child.letter == letter:
                return child
        return None

    def delete(self):
        """Deletes this WordNode object and all descendant child
        nodes."""
        for child in self.children:
            child.delete()
        del self


class WordTree():
    """
        Tree data structure object, used as an efficient method for
        checking word spelling. All words added form a path from the
        root node, with each node representing a letter of that word.

        Attributes:
        > root (WordNode) - root of the tree
        > word_set (set) - set of words added
    """

    def __init__(self):
        self.root = WordNode()
        self.word_set = set()

    def add_word(self, word):
        """Adds a word into the tree data structure."""
        current = self.root
        for letter in word:
            child = current.get_child(letter)
            if not child:
                child = current.add_child(letter)
            current = child
        current.my_word = word
        self.word_set.add(word)

    def clear_words(self):
        """Clears the all words from the tree data structure."""
        for child in self.root.children:
            child.delete()
        self.word_set = set()


class WordHash():
    """
        Hash table object, used as an efficient method for looking up
        words with particular letters in given positions. Reverse hash
        lookups can be used to return the set of all words with a given
        length and a particular letter at a given index. Words may
        belong to more that one set.

        Attributes:
        > hash_table (dict) - keys are hashes, values are sets of the
            words with that hash
    """

    def __init__(self):
        self.hash_table = defaultdict(set)

    def add_word(self, word):
        """Add the word to hash_table."""
        length = len(word)
        for position, letter in enumerate(word):
            hash_value = self._hasher(length, letter, position)
            self.hash_table[hash_value].add(word)

    def lookup(self, length, letter, position):
        """Returns the set of added words with the given length and with
        the given letter in the given position."""
        hash_value = self._hasher(length, letter, position)
        return self.hash_table[hash_value]

    def clear_words(self):
        """Clears the all words from the hash table."""
        self.hash_table = defaultdict(set)

    @staticmethod
    def _hasher(length, letter, position):
        """Returns a hash combining the given arguments."""
        return str(length) + letter + str(position)
