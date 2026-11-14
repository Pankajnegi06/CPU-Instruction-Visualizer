"""cpu.py - the CPU: registers + RAM + the EXECUTE logic (Student 1 and 2).

The cycle (fetch/decode/execute step by step) lives in instruction_cycle.py.
This file knows how to carry out ONE decoded instruction.
"""
from collections import namedtuple

import alu
from instruction_parser import parse_program
from memory import Memory
from registers import USER_REGISTERS, new_registers

START_ADDRESS = 100

# What an executed instruction reports back to the UI.
Result = namedtuple("Result", "description active address alu", defaults=(None, None))


def registers_in(*operands):
    """The operands that are registers, e.g. ("R1", "10") -> {"R1"}."""
    return {operand for operand in operands if operand in USER_REGISTERS}


class CPU:
    def __init__(self, memory_size=256):
        self.regs = new_registers()
        self.memory = Memory(memory_size)
        self.halted = False
        self.error = None
        self.start = START_ADDRESS
        self.program = []  # instruction text, kept so reset() can reload it

    def load_program(self, text):
        """Check the program (raises ProgramError) and put it in RAM."""
        self.program = [i.text for i in parse_program(text)]
        self.reset()

    def reset(self):
        """Back to the original state: program in RAM, registers cleared."""
        self.regs = new_registers()
        self.regs["PC"] = self.start
        self.memory = Memory(self.memory.size)
        self.memory.load_program(self.start, self.program)
        self.halted = False
        self.error = None

    def number(self, operand):
        """Value of a register operand (R1) or a number operand (10)."""
        return self.regs[operand] if operand in USER_REGISTERS else int(operand)

    def execute(self, instruction):
        """Carry out one instruction and return a Result."""
        op, args, regs = instruction.opcode, instruction.operands, self.regs

        if op == "HLT":
            self.halted = True
            return Result("HLT: the CPU stops", {"CU"})

        if op == "JMP":
            target = int(args[0])
            self.memory.check(target)
            regs["PC"] = target
            return Result(f"JMP: PC <- {target}", {"CU", "PC"})

        if op == "LOAD":
            dest, source = args
            if source.startswith("["):  # read from RAM using MAR and MDR
                address = int(source[1:-1])
                regs["MAR"] = address
                regs["MDR"] = self.memory.read(address)
                regs[dest] = regs["MDR"]
                return Result(f"{dest} <- RAM[{address}] = {regs[dest]}",
                              {"CU", "MAR", "RAM", "MDR", dest}, address)
            regs[dest] = int(source)
            return Result(f"{dest} <- {source}", {"CU", dest})

        if op == "STORE":
            source, address = args[0], int(args[1])
            self.memory.check(address)
            regs["MAR"] = address
            regs["MDR"] = regs[source]
            self.memory.write(regs["MAR"], regs["MDR"])
            return Result(f"RAM[{address}] <- {source} = {regs[source]}",
                          {"CU", source, "MAR", "MDR", "RAM"}, address)

        if op == "MOV":
            dest = args[0]
            regs[dest] = self.number(args[1])
            return Result(f"{dest} <- {regs[dest]}", {"CU"} | registers_in(*args))

        # All other instructions use the ALU: ADD SUB MUL DIV AND OR CMP NOT
        dest = args[0]
        a = regs[dest]
        b = self.number(args[1]) if len(args) > 1 else None
        result = alu.calculate(op, a, b)
        regs["ACC"] = result  # the ALU output always goes to ACC...
        if op != "CMP":
            regs[dest] = result  # ...and to the destination register (not for CMP)
        active = {"CU", "ALU", "ACC"} | registers_in(*args)
        return Result(alu.describe(op, a, b, result), active, None, (op, a, b, result))
