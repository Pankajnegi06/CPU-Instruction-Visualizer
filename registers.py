"""registers.py - the CPU registers (Student 1).

PC  Program Counter          address of the next instruction
IR  Instruction Register     the instruction being executed (text)
MAR Memory Address Register  address sent to RAM
MDR Memory Data Register     data going to / coming from RAM
R1, R2                       general purpose registers
ACC Accumulator              every ALU result is placed here
"""
REGISTER_NAMES = ["PC", "IR", "MAR", "MDR", "R1", "R2", "ACC"]
USER_REGISTERS = ["R1", "R2", "ACC"]  # the registers a program may use


def new_registers():
    """Return a fresh register set: all 0, except IR which is empty text."""
    registers = {name: 0 for name in REGISTER_NAMES}
    registers["IR"] = ""
    return registers
