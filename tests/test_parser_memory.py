import unittest

from tests.helpers import run  # noqa: F401
from instruction_parser import ParseError, ProgramError, parse_line, parse_program
from memory import Memory, MemoryAccessError


class TestParser(unittest.TestCase):
    def test_valid_lines(self):
        self.assertEqual(parse_line("load r1, 10").text, "LOAD R1, 10")
        self.assertEqual(parse_line("LOAD R1, [200]").text, "LOAD R1, [200]")
        self.assertEqual(parse_line("STORE R1, 200 ; comment").text, "STORE R1, 200")
        self.assertEqual(parse_line("MOV R1, 0x10").operands, ["R1", "16"])
        self.assertEqual(parse_line("HLT").text, "HLT")
        self.assertIsNone(parse_line("  ; only a comment"))

    def test_invalid_lines(self):
        for bad in ["FOO R1", "ADD R1", "ADD R1, R2, R3", "LOAD 5, R1", "LOAD R3, 1",
                    "ADD R1,", "HLT R1", "STORE R1, abc", "LOAD R1, R2", "JMP R1"]:
            with self.assertRaises(ParseError, msg=bad):
                parse_line(bad)

    def test_program_lists_every_bad_line(self):
        with self.assertRaises(ProgramError) as context:
            parse_program("LOAD R1, 1\nBAD\nADD R1\n")
        self.assertEqual([n for n, _ in context.exception.errors], [2, 3])

    def test_empty_program(self):
        with self.assertRaises(ProgramError):
            parse_program("; nothing here")


class TestMemory(unittest.TestCase):
    def test_read_write(self):
        memory = Memory(16)
        memory.write(3, 99)
        self.assertEqual(memory.read(3), 99)

    def test_invalid_address(self):
        memory = Memory(16)
        for address in (-1, 16, 1000):
            with self.assertRaises(MemoryAccessError):
                memory.read(address)
            with self.assertRaises(MemoryAccessError):
                memory.write(address, 1)

    def test_program_too_big(self):
        with self.assertRaises(MemoryAccessError):
            Memory(4).load_program(2, ["HLT"] * 5)


if __name__ == "__main__":
    unittest.main()
