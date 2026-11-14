# Project Guide

## 1. How the instruction cycle works
Six micro-steps per instruction (one click of *Next Step* = one micro-step):

| # | Stage | Micro-op | Components lit |
|---|---|---|---|
| 1 | FETCH | `MAR <- PC` | PC, MAR |
| 2 | FETCH | `MDR <- M[MAR]` | MAR, RAM, MDR |
| 3 | FETCH | `IR <- MDR` | MDR, IR |
| 4 | FETCH | `PC <- PC + 1` | PC |
| 5 | DECODE | CU parses IR into opcode + operands | IR, CU |
| 6 | EXECUTE | ALU / register / RAM operation; result shown | CU, ALU, regs, RAM |

**Interaction:** PC gives the address → MAR → RAM puts the content in MDR → copied to IR →
PC advances. The CU decodes IR. For ALU instructions the result goes to **ACC** and to the
destination register (`CMP` only sets ACC and the Z/N flags). `LOAD R,[a]` and `STORE` use
MAR (address) and MDR (data). `JMP` overwrites PC. `HLT` stops the cycle. Nothing is
hard-coded: the diagram is built from the real CPU state after every step.

## 2. Module interfaces (so four people can work in parallel)
```python
# S2  alu.py                calculate(op, a, b=None) -> int          (raises ALUError)
# S2  instruction_parser.py parse_line(text) -> Instruction | None   (raises ParseError)
#                           parse_program(text) -> [Instruction]      (raises ProgramError)
# S4  memory.py             Memory.read(addr) / write(addr, value)    (raises MemoryAccessError)
# S1  registers.py          new_registers() -> {"PC": 0, "IR": "", ...}
# S1+S2 cpu.py              CPU.load_program(text) / reset() / execute(instruction)
# S1  instruction_cycle.py  InstructionCycle(cpu): load(text) step() reset() step_back()
#                           .last .history .last_alu .cpu
# S3  visualizer.py         build_cpu_dot(active, stage, regs), timeline_figure(history), alu_figure(alu)
```
`StepRecord` fields: `number, instr_no, stage, micro, instruction, description, active, changes, address, alu, error`.
The UI (S3) only uses `InstructionCycle`; S3 can begin with a stub that returns made-up `StepRecord`s.

## 3. Development phases
| Phase | Work | Files | Owner | Check |
|---|---|---|---|---|
| 1 | Architecture + instruction set (this guide) | docs | all | team review |
| 2 | Components | `registers, memory, alu, instruction_parser, cpu` | S1,S2,S4 | `python -m unittest tests.test_alu tests.test_parser_memory` |
| 3 | Cycle engine + executor | `instruction_cycle` (+ `cpu.execute`) | S1,S2 | `python -m unittest tests.test_cycle` |
| 4 | Dashboard | `app, visualizer` | S3 | `streamlit run app.py` |
| 5 | Animation, history, learning | `app, quiz, sample_programs` | S3,S4 | try all samples + quiz |
| 6 | Integration testing | `tests/` | all | all tests green, demo run-through |

## 4. Team contributions
- **Student 1** – `cpu.py` (structure), `registers.py`, `instruction_cycle.py`: component models, F-D-E logic, PC/IR handling, undo/reset.
- **Student 2** – `alu.py`, `instruction_parser.py`, `CPU.execute()` in `cpu.py`: operations, parsing, error messages, execution.
- **Student 3** – `app.py`, `visualizer.py`, `.streamlit/config.toml`: dashboard, diagram, controls, auto-play, styling.
- **Student 4** – `memory.py`, `quiz.py`, `sample_programs.py`, `tests/`, docs: RAM, history display, learning content, testing.
Git workflow: one branch per student (`s1-cpu`, `s2-alu`, …), pull requests reviewed by a teammate, merge to `main`.

## 5. Test cases and expected output
| Program | Expected |
|---|---|
| Sample 1 (10 + 5, store) | R1=15, ACC=15, RAM[200]=15 |
| Sample 2 (20−4, ×3, ÷4) | R1=12 |
| Sample 3 (12 AND 10, OR 1, NOT 10) | R1=9, R2=−11 |
| Sample 4 (store/load 42) | RAM[150]=42, R2=42 |
| Sample 5 (CMP 7,9) | ACC=−1, R1 unchanged |
| Sample 6 (JMP) | R1=2 (`LOAD R1, 99` skipped) |
| Sample 7 (DIV by 0) | error "Division by zero", CPU halts |
| Sample 8 (STORE 999) | error "Invalid memory address 999 …" |
| `ADD R1` / `FOO` / `LOAD R3, 1` | parse errors with line numbers, nothing loaded |
| Step ×14 then Previous ×14 | state identical to the start |
| Reset after run | PC=100, registers 0, RAM[200]=0, history empty |

## 6. Presentation outline (10–12 min)
1. Problem: why computer architecture is hard to picture (1 min)
2. CPU components and registers (2)
3. Fetch–Decode–Execute with the six micro-steps (2)
4. Live demo: sample 1, then the division-by-zero error (3)
5. Software design: modules, interfaces, UI/logic separation (2)
6. Testing and quiz module (1)
7. Teamwork, challenges, future work, Q&A (2)

## 7. Future improvements
Input/output instructions (IN/OUT) · conditional jumps (JZ/JNZ) and loops · CALL/RET and a stack · pipeline visualization ·
separate data/instruction memory · binary/hex views and real opcodes · more registers ·
breakpoints · save/share programs via URL · interrupts and I/O devices · cache simulation ·
progress tracking in the quiz · UI tests (Streamlit `AppTest`) and CI via GitHub Actions.
