"""instruction_parser.py - assembly text -> Instruction (Student 2).

Examples (not case-sensitive, ';' starts a comment):
    LOAD R1, 10        put 10 in R1            LOAD R1, [200]   read RAM[200]
    STORE R1, 200      write R1 to RAM[200]    MOV R2, R1
    ADD R1, R2         also SUB MUL DIV AND OR CMP (second operand: register or number)
    NOT R1             JMP 104                 HLT
"""
from dataclasses import dataclass

from alu import ALU_OPCODES
from registers import USER_REGISTERS


class ParseError(Exception):
    """One instruction is invalid."""


class ProgramError(Exception):
    """The program has errors. `errors` is a list of (line_number, message)."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"line {n}: {m}" for n, m in errors))


@dataclass
class Instruction:
    opcode: str
    operands: list  # tidy text such as "R1", "10" or "[200]"

    @property
    def text(self):
        return " ".join([self.opcode, ", ".join(self.operands)]).strip()


# What each opcode expects for its operands.
RULES = {"LOAD": ["register", "number or [address]"], "STORE": ["register", "number"],
         "MOV": ["register", "register or number"], "NOT": ["register"],
         "JMP": ["number"], "HLT": []}
for _op in ALU_OPCODES:
    RULES.setdefault(_op, ["register", "register or number"])


def to_number(token):
    try:
        return str(int(token, 0))  # accepts 10, 0xA, 0b1010
    except ValueError:
        raise ParseError(f"'{token}' is not a number or register (use R1, R2, ACC)")


def check_operand(token, rule):
    """Validate one operand against its rule and return it in tidy form."""
    token = token.strip().upper()
    if token == "":
        raise ParseError("empty operand (stray comma?)")
    if token in USER_REGISTERS:
        if rule == "number" or rule == "number or [address]":
            raise ParseError(f"register {token} is not allowed here")
        return token
    if rule == "register":
        raise ParseError(f"'{token}' is not a register (use R1, R2 or ACC)")
    if rule == "number or [address]" and token.startswith("[") and token.endswith("]"):
        return "[" + to_number(token[1:-1].strip()) + "]"
    return to_number(token)


def parse_line(line):
    """Parse one line. Returns None for blank or comment-only lines."""
    line = line.split(";")[0].strip()
    if line == "":
        return None
    parts = line.split(None, 1)
    opcode = parts[0].upper()
    if opcode not in RULES:
        raise ParseError(f"Unknown instruction '{parts[0]}'")
    rules = RULES[opcode]
    text = parts[1] if len(parts) > 1 else ""
    tokens = text.split(",") if text.strip() else []
    if len(tokens) != len(rules):
        raise ParseError(f"{opcode} needs {len(rules)} operand(s) but got {len(tokens)}")
    return Instruction(opcode, [check_operand(t, r) for t, r in zip(tokens, rules)])


def parse_program(text):
    """Parse a whole program. Raises ProgramError listing every bad line."""
    instructions, errors = [], []
    for number, line in enumerate(text.splitlines(), start=1):
        try:
            instruction = parse_line(line)
            if instruction:
                instructions.append(instruction)
        except ParseError as error:
            errors.append((number, str(error)))
    if not errors and not instructions:
        errors.append((1, "The program is empty"))
    if errors:
        raise ProgramError(errors)
    return instructions
