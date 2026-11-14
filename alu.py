"""alu.py - the Arithmetic Logic Unit (Student 2).

The ALU only calculates: numbers in, number out. It knows nothing about
registers or memory.
"""


class ALUError(Exception):
    """Raised for illegal operations such as division by zero."""


OPERATIONS = {
    "ADD": lambda a, b: a + b,
    "SUB": lambda a, b: a - b,
    "MUL": lambda a, b: a * b,
    "AND": lambda a, b: a & b,
    "OR": lambda a, b: a | b,
    "CMP": lambda a, b: (a > b) - (a < b),  # -1 if a<b, 0 if equal, 1 if a>b
}
SYMBOLS = {"ADD": "+", "SUB": "-", "MUL": "*", "DIV": "/", "AND": "&", "OR": "|"}
ALU_OPCODES = list(OPERATIONS) + ["DIV", "NOT"]


def calculate(op, a, b=None):
    """Return the result of `a op b` (NOT only uses a)."""
    if op == "NOT":
        return ~a
    if op == "DIV":
        if b == 0:
            raise ALUError("Division by zero")
        return int(a / b)  # whole-number division, rounds toward zero
    return OPERATIONS[op](a, b)


def describe(op, a, b, result):
    """One-line explanation of an ALU operation, for the UI."""
    if op == "NOT":
        return f"NOT {a} = {result}"
    if op == "CMP":
        return f"CMP {a} with {b}: ACC = {result} (-1 less, 0 equal, 1 greater)"
    return f"{a} {SYMBOLS[op]} {b} = {result}"
