"""Test module for the boggle module."""

import unittest
from src import boggle


class BoggleTest(unittest.TestCase):
    """Class for testing the boggle module."""

    @classmethod
    def setUpClass(cls):
        """Define the solver."""
        cls.solver = boggle.BoggleSolver("test/dictionary.txt")

    def test_from_list(self):
        """Test words can be loaded from a list."""
        solver = boggle.BoggleSolver(["CAT", "DOG"])
        self.assertEqual(
            {"CAT", "DOG"},
            set(solver.solve([
                ["C", "A", "T"],
                ["D", "O", "G"]
            ]))
        )

    def test_from_set(self):
        """Test words can be loaded from a set."""
        solver = boggle.BoggleSolver({"BLUE", "CYAN"})
        self.assertEqual(
            {"BLUE", "CYAN"},
            set(solver.solve([
                ["C", "B"],
                ["Y", "L"],
                ["A", "U"],
                ["N", "E"]
            ]))
        )

    def test_horizontal_solutions(self):
        """Test that the solver can pick up horizontal solutions."""
        self.assertIn(
            "ONE",
            self.solver.solve([
                ["X", "X", "X"],
                ["O", "N", "E"],
                ["X", "X", "X"]
            ])
        )
        self.assertIn(
            "CAR",
            self.solver.solve([
                ["X", "X", "X"],
                ["R", "A", "C"],
                ["X", "X", "X"]
            ])
        )

    def test_vertical_solutions(self):
        """Test that the solver can pick up vertical solutions."""
        self.assertIn(
            "TWO",
            self.solver.solve([
                ["X", "T", "X"],
                ["X", "W", "X"],
                ["X", "O", "X"]
            ])
        )
        self.assertIn(
            "BED",
            self.solver.solve([
                ["X", "D", "X"],
                ["X", "E", "X"],
                ["X", "B", "X"]
            ])
        )

    def test_diagonal_solutions(self):
        """Test that the solver can pick up diagonal solutions."""
        self.assertIn(
            "RED",
            self.solver.solve([
                ["R", "X", "X"],
                ["X", "E", "X"],
                ["X", "X", "D"]
            ])
        )
        self.assertIn(
            "OUR",
            self.solver.solve([
                ["R", "X", "X"],
                ["X", "U", "X"],
                ["X", "X", "O"]
            ])
        )
        self.assertIn(
            "POT",
            self.solver.solve([
                ["X", "X", "P"],
                ["X", "O", "X"],
                ["T", "X", "X"]
            ])
        )
        self.assertIn(
            "LAY",
            self.solver.solve([
                ["X", "X", "Y"],
                ["X", "A", "X"],
                ["L", "X", "X"]
            ])
        )

    def test_random_pattern_solutions(self):
        """Test that the solver can pick up a random pattern solutions."""
        self.assertIn(
            "TRAUMATIZATIONS",
            self.solver.solve([
                ["T", "R", "A"],
                ["A", "M", "U"],
                ["T", "I", "Z"],
                ["I", "T", "A"],
                ["O", "N", "S"]
            ])
        )
        self.assertIn(
            "FEATURES",
            self.solver.solve([
                ["F", "E", "A", "U"],
                ["S", "E", "R", "T"]
            ])
        )
        self.assertEqual(
            {
                'TAED', 'TEAD', 'DATE', 'EAT', 'ETA',
                'TAE', 'TAD', 'TED', 'TEA', 'DAE', 'ATE'
            },
            set(self.solver.solve([
                ["E", "T"],
                ["D", "A"]
            ]))
        )

    def test_with_position_option(self):
        """Test that the with_positions works."""
        self.assertEqual(
            {'TEST', 'TETS', 'SETT', 'STET', 'TET', 'TES', 'SET', 'EST'},
            set(self.solver.solve([
                ["T", "T"],
                ["S", "E"]
            ], with_positions=False))
        )
        elements = [
            ('TEST', [[(0, 0), (1, 1), (1, 0), (0, 1)], [(0, 1), (1, 1), (1, 0), (0, 0)]]),
            ('TETS', [[(0, 0), (1, 1), (0, 1), (1, 0)], [(0, 1), (1, 1), (0, 0), (1, 0)]]),
            ('SETT', [[(1, 0), (1, 1), (0, 1), (0, 0)], [(1, 0), (1, 1), (0, 0), (0, 1)]]),
            ('STET', [[(1, 0), (0, 1), (1, 1), (0, 0)], [(1, 0), (0, 0), (1, 1), (0, 1)]]),
            ('TET', [[(0, 0), (1, 1), (0, 1)], [(0, 1), (1, 1), (0, 0)]]),
            ('TES', [[(0, 0), (1, 1), (1, 0)], [(0, 1), (1, 1), (1, 0)]]),
            ('SET', [[(1, 0), (1, 1), (0, 0)], [(1, 0), (1, 1), (0, 1)]]),
            ('EST', [[(1, 1), (1, 0), (0, 0)], [(1, 1), (1, 0), (0, 1)]])
        ]
        solutions = self.solver.solve(
            [
                ["T", "T"],
                ["S", "E"]
            ],
            with_positions=True
        )
        for element in elements:
            self.assertIn(element, solutions)

    def test_multiple_positions(self):
        """Test solutions which form at multiple positions."""
        solutions = self.solver.solve(
            [
                ["B", "A", "N"],
                ["A", "N", "A"],
                ["N", "A", "N"]
            ],
            with_positions=True
        )
        solution = [sol for sol in solutions if sol[0] == "BANANA"]
        self.assertEqual(1, len(solution))
        positions = [
            [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2)],
            [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (0, 1)],
            [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (1, 2)],
            [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (1, 2)],
            [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2), (2, 1)],
            [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2), (0, 1)],
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 2), (1, 2)],
            [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2), (1, 2)],
            [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0), (1, 0)],
            [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 1)],
            [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0), (2, 1)],
            [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1)],
            [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0)],
            [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (2, 1)]
        ]
        solution_positions = solution[0][1]
        self.assertEqual(len(positions), len(solution_positions))
        for pos in positions:
            self.assertIn(pos, solution_positions)

    def test_q_equals_qu(self):
        """Test that a board tile with 'Q' is equivalent to 'Qu'."""
        self.assertEqual(
            self.solver.solve([["Qu", "E", "E", "N"]]),
            self.solver.solve([["Q", "E", "E", "N"]])
        )

    def test_init_exceptions(self):
        """Test all exceptions that can be raised with init parameters."""
        self.assertRaises(TypeError, boggle.BoggleSolver, 1)
        self.assertRaises(TypeError, boggle.BoggleSolver, {"TIN"}, "3")
        self.assertRaises(ValueError, boggle.BoggleSolver, {"CAN"}, -1)

    def test_solve_exceptions(self):
        """Test all exceptions that can be raised with solve parameters."""
        self.assertRaises(TypeError, self.solver.solve, 1)
        self.assertRaises(TypeError, self.solver.solve, [1])
        self.assertRaises(TypeError, self.solver.solve, [[1]])
        self.assertRaises(ValueError, self.solver.solve, [["A", "B"], ["C"]])
        self.assertRaises(TypeError, self.solver.solve, [["A", "B"], ["C", 1]])
        self.assertRaises(ValueError, self.solver.solve, [["AA", "B"], ["C", "D"]])
        self.assertRaises(TypeError, self.solver.solve, [["A", "B"]], 1)
