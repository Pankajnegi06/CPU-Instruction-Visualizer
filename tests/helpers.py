import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cpu import CPU
from instruction_cycle import InstructionCycle


def run(program):
    """Load a program, run it to the end and return the InstructionCycle."""
    cycle = InstructionCycle(CPU())
    cycle.load(program)
    cycle.run_to_end()
    return cycle


def state(cycle):
    """A comparable snapshot of the CPU."""
    cpu = cycle.cpu
    return dict(cpu.regs), list(cpu.memory.cells), cpu.halted, cpu.error
