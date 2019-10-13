"""
    This module contains useful functions to be used in the CLI.
"""

import os


def clear():
    """Clears the CLI interface."""
    os.system('cls' if os.name == 'nt' else 'clear')
