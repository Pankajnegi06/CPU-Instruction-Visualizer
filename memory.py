"""memory.py - simulated RAM (Student 4).

Each cell holds a number (data) or text (an instruction).
"""


class MemoryAccessError(Exception):
    """Raised when an address is outside RAM."""


class Memory:
    def __init__(self, size=256):
        self.size = size
        self.cells = [0] * size

    def check(self, address):
        if not isinstance(address, int) or not 0 <= address < self.size:
            raise MemoryAccessError(
                f"Invalid memory address {address} (valid: 0-{self.size - 1})")

    def read(self, address):
        self.check(address)
        return self.cells[address]

    def write(self, address, value):
        self.check(address)
        self.cells[address] = value

    def load_program(self, start, lines):
        """Place instruction text in consecutive cells starting at `start`."""
        self.check(start)
        self.check(start + len(lines) - 1)
        for offset, line in enumerate(lines):
            self.cells[start + offset] = line
