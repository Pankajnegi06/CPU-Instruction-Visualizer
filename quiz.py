"""quiz.py - lessons, quiz questions and practice challenges (Student 4)."""
from cpu import CPU
from instruction_cycle import InstructionCycle
from instruction_parser import ProgramError

LESSONS = {
    "CPU architecture": """
The **Control Unit (CU)** directs everything, the **ALU** calculates, and **registers** are tiny
fast storage inside the CPU. **RAM** is larger, slower memory that holds instructions and data.
**Input/Output** connects the computer to the outside world.""",
    "Fetch-Decode-Execute": """
- **FETCH** (blue): PC -> MAR, RAM -> MDR, MDR -> IR, then PC + 1.
- **DECODE** (orange): the CU splits IR into an opcode and operands.
- **EXECUTE** (green): the ALU, registers or RAM carry out the operation.

The cycle repeats for every instruction until `HLT`.""",
    "Registers": """
- **PC** - address of the next instruction
- **IR** - the instruction being executed
- **MAR** - address sent to RAM
- **MDR** - data read from / written to RAM
- **R1, R2** - general purpose
- **ACC** - accumulator: receives every ALU result""",
    "ALU": """
The ALU does **ADD, SUB, MUL, DIV** (arithmetic), **AND, OR, NOT** (bitwise logic) and
**CMP** (comparison: ACC becomes -1, 0 or 1).""",
    "Instruction set": """
`LOAD R1, 10` | `LOAD R1, [200]` | `STORE R1, 200` | `MOV R2, R1` |
`ADD / SUB / MUL / DIV / AND / OR / CMP R1, R2` | `NOT R1` | `JMP 104` | `HLT`.
Comments start with `;`""",
}

# Each question: text, options, index of the right option, explanation.
QUESTIONS = [
    ("Which register holds the address of the next instruction?",
     ["IR", "PC", "MAR", "ACC"], 1, "The Program Counter (PC) points to the next instruction."),
    ("What is the first micro-step of FETCH?",
     ["IR <- MDR", "PC <- PC + 1", "MAR <- PC", "ALU adds"], 2,
     "PC supplies the address, which is copied into MAR."),
    ("Which component decodes the instruction?",
     ["ALU", "RAM", "Control Unit", "MDR"], 2, "The Control Unit reads IR and decides what to do."),
    ("Which register holds data that was just read from memory?",
     ["MDR", "PC", "IR", "MAR"], 0, "MDR is the Memory Data Register."),
    ("Where does every ALU result go in this simulator?",
     ["PC", "ACC", "IR", "RAM"], 1, "ALU results are placed in the accumulator (ACC)."),
    ("What does CMP R1, R2 put in ACC when R1 < R2?",
     ["1", "0", "-1", "R2"], 2, "CMP gives -1 (less), 0 (equal) or 1 (greater)."),
    ("What does JMP 103 change?",
     ["R1", "ACC", "PC", "MDR"], 2, "JMP overwrites the PC, so the next fetch is from 103."),
    ("What happens on DIV R1, R2 when R2 is 0?",
     ["R1 becomes 0", "An error stops the CPU", "ACC = 1", "Nothing"], 1,
     "Dividing by zero is illegal, so the CPU stops with an error."),
]

# Each challenge: title, task, starter code, what must be true afterwards.
CHALLENGES = [
    ("Compute (7 + 3) * 4", "Store the result (40) at RAM address 150.",
     "LOAD R1, 7\n; your code here\nHLT", {"RAM": {150: 40}}),
    ("Divide and subtract", "Compute 100 / 5 - 8 so that R2 ends up as 12.",
     "LOAD R2, 100\n; your code here\nHLT", {"REG": {"R2": 12}}),
]


def score_quiz(answers):
    """answers = {question_number: chosen_option_number}. Returns the score."""
    return sum(1 for number, choice in answers.items() if QUESTIONS[number][2] == choice)


def check_challenge(challenge, program):
    """Run the learner's program. Returns (passed, message)."""
    expected = challenge[3]
    cycle = InstructionCycle(CPU())
    try:
        cycle.load(program)
    except ProgramError as error:
        return False, f"Program error: {error}"
    cycle.run_to_end()
    if cycle.cpu.error:
        return False, f"Runtime error: {cycle.cpu.error}"
    for name, want in expected.get("REG", {}).items():
        if cycle.cpu.regs[name] != want:
            return False, f"{name} is {cycle.cpu.regs[name]}, expected {want}"
    for address, want in expected.get("RAM", {}).items():
        if cycle.cpu.memory.cells[address] != want:
            return False, f"RAM[{address}] is {cycle.cpu.memory.cells[address]}, expected {want}"
    return True, "Correct!"
