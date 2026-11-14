# 🖥️ CPU Instruction Cycle Visualizer

An interactive Streamlit app that shows how a CPU runs instructions through the
**Fetch → Decode → Execute** cycle, one micro-step at a time. PBL project for a team of four.

## Install & run
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                   # opens http://localhost:8501
python -m unittest discover -s tests -t .              # run all tests (pytest also works)
```
Python 3.10+ recommended. Graphviz diagrams render in the browser, no system install needed.

## Using the app
Pick a sample (or type assembly) → **Start** loads it and runs the first step → **Next Step /
Previous** move one micro-step → **Auto Play / Pause** animate (speed in the sidebar) →
**Reset** restores the original CPU state. Active components glow in the stage colour
(🔵 Fetch, 🟠 Decode, 🟢 Execute); the RAM row being accessed is highlighted.

## Project structure
| File | Purpose | Owner |
|---|---|---|
| `app.py` | Streamlit dashboard: controls, layout, tabs | S3 |
| `visualizer.py` | Graphviz CPU diagram, Plotly timeline/register chart, Matplotlib ALU chart | S3 |
| `cpu.py` | `CPU` class: registers + RAM + executes one instruction | S1 + S2 |
| `registers.py` | Register names and a function that creates them | S1 |
| `instruction_cycle.py` | Fetch-Decode-Execute engine: 6 micro-steps, history, undo | S1 |
| `alu.py` | ADD SUB MUL DIV AND OR NOT CMP + division-by-zero error | S2 |
| `instruction_parser.py` | Assembly text -> `Instruction`, error checking | S2 |
| `memory.py` | `Memory` (RAM) with address checking | S4 |
| `quiz.py` | Lessons, 10-question quiz, 3 practice challenges | S4 |
| `sample_programs.py` | 8 demo programs (incl. 2 error demos) | S4 |
| `tests/` | 25 unit tests | S4 |
| `docs/PROJECT_GUIDE.md` | Cycle explanation, interfaces, phases, team plan, tests, slides, future work | all |

## Instruction set
`LOAD R1, 10` · `LOAD R1, [200]` · `STORE R1, 200` · `MOV R2, R1|5` ·
`ADD/SUB/MUL/DIV/AND/OR/CMP Rd, Rs|n` · `NOT Rd` · `JMP addr` · `HLT`.
Registers: `R1 R2 ACC`. Programs load at address 100; RAM has 256 cells. `;` starts a comment.
