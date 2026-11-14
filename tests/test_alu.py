import unittest

from tests.helpers import run  # noqa: F401  (sets up the import path)
from alu import ALUError, calculate


class TestALU(unittest.TestCase):
    def test_operations(self):
        cases = [("ADD", 7, 5, 12), ("SUB", 7, 5, 2), ("MUL", 7, 5, 35), ("DIV", 7, 2, 3),
                 ("DIV", -7, 2, -3), ("AND", 12, 10, 8), ("OR", 12, 10, 14),
                 ("CMP", 3, 9, -1), ("CMP", 9, 9, 0), ("CMP", 9, 3, 1)]
        for op, a, b, expected in cases:
            self.assertEqual(calculate(op, a, b), expected, (op, a, b))

    def test_not(self):
        self.assertEqual(calculate("NOT", 0), -1)

    def test_division_by_zero(self):
        with self.assertRaises(ALUError):
            calculate("DIV", 1, 0)


if __name__ == "__main__":
    unittest.main()
