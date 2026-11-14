"""instruction_cycle.py - the Fetch-Decode-Execute engine (Student 1).

Each call to step() performs ONE of these six micro-steps:

  FETCH    1. MAR <- PC       the PC supplies the address
           2. MDR <- RAM[MAR] RAM returns the instruction
           3. IR  <- MDR      the instruction is stored in IR
           4. PC  <- PC + 1   PC now points to the next instruction
  DECODE   5. the Control Unit splits IR into opcode + operands
  EXECUTE  6. the CPU does the work (ALU / registers / RAM)
"""
import copy
from dataclasses import dataclass

from alu import ALUError
from instruction_parser import ParseError, parse_line
from memory import MemoryAccessError

STAGE_COLORS = {"FETCH": "#3b82f6", "DECODE": "#f59e0b", "EXECUTE": "#22c55e"}
PHASES = [("FETCH", "MAR <- PC"), ("FETCH", "MDR <- RAM[MAR]"), ("FETCH", "IR <- MDR"),
          ("FETCH", "PC <- PC + 1"), ("DECODE", "Decode IR"), ("EXECUTE", "Execute")]


@dataclass
class StepRecord:
    """Everything the UI needs to know about one micro-step."""
    number: int
    instr_no: int
    stage: str
    micro: str
    instruction: str = ""
    description: str = ""
    active: set = None  # components to highlight
    changes: dict = None  # {"PC": (100, 101)}
    address: int = None  # RAM address used, if any
    alu: tuple = None  # (op, a, b, result) if the ALU was used
    error: str = None


class InstructionCycle:
    def __init__(self, cpu):
        self.cpu = cpu
        self.reset()

    def load(self, text):
        """Load assembly text (raises ProgramError if invalid) and start over."""
        self.cpu.load_program(text)
        self.reset()

    def reset(self):
        self.cpu.reset()
        self.phase = 0  # which of the six micro-steps comes next
        self.instr_no = 1  # which instruction we are on
        self.decoded = None  # result of the DECODE step
        self.history = []  # one StepRecord per micro-step
        self.undo_stack = []  # snapshots used by step_back()

    @property
    def last(self):
        return self.history[-1] if self.history else None

    @property
    def last_alu(self):
        """The most recent ALU operation (op, a, b, result) or None."""
        for record in reversed(self.history):
            if record.alu:
                return record.alu
        return None

    def step(self):
        """Run one micro-step and return its StepRecord (None if halted)."""
        cpu = self.cpu
        if cpu.halted:
            return None
        self.undo_stack.append((copy.deepcopy(cpu.__dict__), self.phase,
                                self.instr_no, self.decoded))
        regs_before, memory_before = dict(cpu.regs), list(cpu.memory.cells)

        stage, micro = PHASES[self.phase]
        record = StepRecord(len(self.history) + 1, self.instr_no, stage, micro)
        try:
            self.run_phase(record)
        except (ParseError, ALUError, MemoryAccessError) as error:
            cpu.halted, cpu.error = True, str(error)
            record.description, record.error = f"ERROR: {error}", str(error)
            record.active = {"CU"}

        # Record what changed, so the history table can show it.
        record.changes = {name: (regs_before[name], value)
                          for name, value in cpu.regs.items() if value != regs_before[name]}
        for address, value in enumerate(cpu.memory.cells):
            if value != memory_before[address]:
                record.changes[f"RAM[{address}]"] = (memory_before[address], value)
        if self.phase >= 2:
            record.instruction = cpu.regs["IR"]

        self.history.append(record)
        if self.phase == 5:
            self.instr_no += 1
        self.phase = (self.phase + 1) % len(PHASES)
        return record

    def run_phase(self, record):
        """Do the work of the current micro-step and describe it in `record`."""
        regs, memory = self.cpu.regs, self.cpu.memory
        if self.phase == 0:  # FETCH 1
            regs["MAR"] = regs["PC"]
            record.description = f"PC holds {regs['PC']}, so MAR <- {regs['PC']}"
            record.active, record.address = {"PC", "MAR"}, regs["MAR"]
        elif self.phase == 1:  # FETCH 2
            regs["MDR"] = memory.read(regs["MAR"])
            record.description = f"RAM[{regs['MAR']}] = '{regs['MDR']}' is copied to MDR"
            record.active, record.address = {"MAR", "RAM", "MDR"}, regs["MAR"]
        elif self.phase == 2:  # FETCH 3
            regs["IR"] = str(regs["MDR"])
            record.description = f"IR now holds '{regs['IR']}'"
            record.active = {"MDR", "IR"}
        elif self.phase == 3:  # FETCH 4
            regs["PC"] += 1
            record.description = f"PC incremented to {regs['PC']}"
            record.active = {"PC"}
        elif self.phase == 4:  # DECODE
            self.decoded = parse_line(regs["IR"])
            if self.decoded is None:
                raise ParseError("IR is empty")
            operands = ", ".join(self.decoded.operands) or "none"
            record.description = f"Opcode {self.decoded.opcode}, operands: {operands}"
            record.active = {"IR", "CU"}
        else:  # EXECUTE
            result = self.cpu.execute(self.decoded)
            record.description, record.active = result.description, result.active
            record.address, record.alu = result.address, result.alu

    def step_back(self):
        """Undo the last micro-step. Returns False if there is nothing to undo."""
        if not self.undo_stack:
            return False
        cpu_state, self.phase, self.instr_no, self.decoded = self.undo_stack.pop()
        self.cpu.__dict__.update(cpu_state)
        self.history.pop()
        return True

    def run_to_end(self, max_steps=10000):
        """Run until HLT or an error (used by tests and challenges)."""
        steps = 0
        while not self.cpu.halted and steps < max_steps:
            self.step()
            steps += 1
        if not self.cpu.halted:
            self.cpu.halted = True
            self.cpu.error = f"Stopped after {max_steps} steps (infinite loop?)"
