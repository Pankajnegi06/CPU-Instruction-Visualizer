import unittest

from tests.helpers import run, state
from cpu import CPU
from instruction_cycle import InstructionCycle
from instruction_parser import ProgramError
from quiz import CHALLENGES, QUESTIONS, check_challenge, score_quiz
from sample_programs import SAMPLE_PROGRAMS


class TestInstructions(unittest.TestCase):
    def test_all_samples_run(self):
        for program in SAMPLE_PROGRAMS.values():
            run(program)

    def test_add_and_store(self):
        cycle = run(SAMPLE_PROGRAMS["1. Add two numbers"])
        self.assertEqual((cycle.cpu.regs["R1"], cycle.cpu.regs["ACC"]), (15, 15))
        self.assertEqual(cycle.cpu.memory.cells[200], 15)

    def test_every_opcode(self):
        cases = {
            "LOAD R1, 9\nHLT": ("R1", 9),
            "MOV R2, 4\nHLT": ("R2", 4),
            "LOAD R1, 9\nMOV R2, R1\nHLT": ("R2", 9),
            "LOAD R1, 6\nSUB R1, 2\nHLT": ("R1", 4),
            "LOAD R1, 6\nMUL R1, 2\nHLT": ("R1", 12),
            "LOAD R1, 7\nDIV R1, 2\nHLT": ("R1", 3),
            "LOAD R1, 6\nAND R1, 3\nHLT": ("R1", 2),
            "LOAD R1, 6\nOR R1, 1\nHLT": ("R1", 7),
            "LOAD R1, 0\nNOT R1\nHLT": ("R1", -1),
            "LOAD R1, 1\nCMP R1, 5\nHLT": ("ACC", -1),
            "LOAD R1, 1\nJMP 103\nLOAD R1, 99\nHLT": ("R1", 1),
            "LOAD R1, 5\nSTORE R1, 50\nLOAD R2, [50]\nHLT": ("R2", 5),
        }
        for program, (register, expected) in cases.items():
            cycle = run(program)
            self.assertIsNone(cycle.cpu.error, program)
            self.assertEqual(cycle.cpu.regs[register], expected, program)

    def test_cmp_keeps_register(self):
        self.assertEqual(run("LOAD R1, 1\nCMP R1, 5\nHLT").cpu.regs["R1"], 1)

    def test_runtime_errors(self):
        self.assertEqual(run("LOAD R1, 1\nDIV R1, 0\nHLT").cpu.error, "Division by zero")
        self.assertIn("Invalid memory", run("STORE R1, 999\nHLT").cpu.error)
        self.assertIn("Invalid memory", run("LOAD R1, [300]\nHLT").cpu.error)
        self.assertIn("Invalid memory", run("JMP 5000\nHLT").cpu.error)
        self.assertIn("Unknown instruction", run("LOAD R1, 1").cpu.error)  # no HLT

    def test_infinite_loop_is_stopped(self):
        cycle = InstructionCycle(CPU())
        cycle.load("JMP 100")
        cycle.run_to_end(max_steps=60)
        self.assertIn("infinite loop", cycle.cpu.error)


class TestCycle(unittest.TestCase):
    def test_six_micro_steps(self):
        cycle = InstructionCycle(CPU())
        cycle.load("LOAD R1, 10\nHLT")
        regs = cycle.cpu.regs
        cycle.step()
        self.assertEqual((regs["MAR"], cycle.last.stage), (100, "FETCH"))
        cycle.step()
        self.assertEqual(regs["MDR"], "LOAD R1, 10")
        cycle.step()
        self.assertEqual(regs["IR"], "LOAD R1, 10")
        cycle.step()
        self.assertEqual(regs["PC"], 101)
        cycle.step()
        self.assertEqual(cycle.last.stage, "DECODE")
        cycle.step()
        self.assertEqual((cycle.last.stage, regs["R1"]), ("EXECUTE", 10))
        self.assertEqual(len(cycle.history), 6)

    def test_step_back_restores_exact_state(self):
        cycle = InstructionCycle(CPU())
        cycle.load(SAMPLE_PROGRAMS["1. Add two numbers"])
        states = [state(cycle)]
        for _ in range(14):
            cycle.step()
            states.append(state(cycle))
        for expected in reversed(states[:-1]):
            self.assertTrue(cycle.step_back())
            self.assertEqual(state(cycle), expected)
        self.assertFalse(cycle.step_back())

    def test_step_back_after_error(self):
        cycle = run("LOAD R1, 1\nDIV R1, 0\nHLT")
        cycle.step_back()
        self.assertFalse(cycle.cpu.halted)
        self.assertIsNone(cycle.cpu.error)

    def test_reset_restores_original_state(self):
        cycle = run(SAMPLE_PROGRAMS["1. Add two numbers"])
        cycle.reset()
        regs = cycle.cpu.regs
        self.assertEqual((regs["PC"], regs["R1"], regs["ACC"], regs["IR"]), (100, 0, 0, ""))
        self.assertEqual(cycle.cpu.memory.cells[200], 0)
        self.assertEqual(cycle.cpu.memory.cells[100], "LOAD R1, 10")
        self.assertEqual(cycle.history, [])

    def test_step_after_halt(self):
        self.assertIsNone(run("HLT").step())

    def test_bad_program_rejected(self):
        with self.assertRaises(ProgramError):
            InstructionCycle(CPU()).load("ADD R1")

    def test_history_records_changes(self):
        cycle = run("LOAD R1, 5\nSTORE R1, 50\nHLT")
        stores = [r for r in cycle.history if "RAM[50]" in r.changes]
        self.assertEqual(stores[0].changes["RAM[50]"], (0, 5))


class TestQuiz(unittest.TestCase):
    def test_scoring(self):
        perfect = {n: q[2] for n, q in enumerate(QUESTIONS)}
        self.assertEqual(score_quiz(perfect), len(QUESTIONS))
        self.assertEqual(score_quiz({}), 0)

    def test_challenges(self):
        solution = "LOAD R1, 7\nADD R1, 3\nMUL R1, 4\nSTORE R1, 150\nHLT"
        self.assertTrue(check_challenge(CHALLENGES[0], solution)[0])
        self.assertFalse(check_challenge(CHALLENGES[0], CHALLENGES[0][2])[0])
        self.assertFalse(check_challenge(CHALLENGES[1], "BAD")[0])


if __name__ == "__main__":
    unittest.main()
