"""app.py - Streamlit dashboard (Student 3).   Run with:  streamlit run app.py

The page only SHOWS the CPU state. All CPU logic lives in cpu.py and
instruction_cycle.py.
"""
import time

import pandas as pd
import streamlit as st

from cpu import CPU
from instruction_cycle import STAGE_COLORS, InstructionCycle
from instruction_parser import ProgramError
from quiz import CHALLENGES, LESSONS, QUESTIONS, check_challenge, score_quiz
from sample_programs import DEFAULT_SAMPLE, SAMPLE_PROGRAMS
from visualizer import alu_figure, build_cpu_dot, timeline_figure

st.set_page_config(page_title="CPU Instruction Cycle Visualizer", page_icon="🖥️", layout="wide")

# ---- keep the CPU between button clicks (Streamlit reruns this file each time) ----
if "cycle" not in st.session_state:
    st.session_state.cycle = InstructionCycle(CPU())
    st.session_state.cycle.load(SAMPLE_PROGRAMS[DEFAULT_SAMPLE])
    st.session_state.editor = SAMPLE_PROGRAMS[DEFAULT_SAMPLE]  # text in the editor
    st.session_state.playing = False  # is Auto Play running?
    st.session_state.errors = []  # program errors to show under the editor
cycle = st.session_state.cycle
cpu = cycle.cpu


def choose_sample():
    st.session_state.editor = SAMPLE_PROGRAMS[st.session_state.sample]


def start_program():
    """Load the editor text, then run the first micro-step."""
    try:
        cycle.load(st.session_state.editor)
        st.session_state.errors = []
        cycle.step()
    except ProgramError as error:
        st.session_state.errors = error.errors


def show_controls():
    """Buttons. Clicking one changes the CPU before anything is drawn."""
    start, auto, pause, previous, next_step, reset = st.columns(6)
    if start.button("▶ Start", help="Load the editor program and run the first step"):
        st.session_state.playing = False
        start_program()
    if auto.button("⏯ Auto Play"):
        st.session_state.playing = True
    if pause.button("⏸ Pause"):
        st.session_state.playing = False
    if previous.button("⏮ Previous"):
        st.session_state.playing = False
        cycle.step_back()
    if next_step.button("⏭ Next Step"):
        st.session_state.playing = False
        cycle.step()
    if reset.button("↺ Reset"):
        st.session_state.playing = False
        cycle.reset()


def show_stage(record):
    """Big banner with the current stage (blue / orange / green)."""
    color = STAGE_COLORS.get(record.stage if record else None, "#64748b")
    text = f"{record.stage} - {record.micro}" if record else "READY - press Next Step"
    st.markdown(f'<div style="background:{color}; color:#0b1220; padding:10px 16px; '
                f'border-radius:10px; font-size:1.3rem; font-weight:700">{text}</div>',
                unsafe_allow_html=True)
    if record:
        st.write(f"**Instruction #{record.instr_no}** `{record.instruction}` - "
                 f"{record.description}")
    if cpu.error:
        st.error(cpu.error)
    elif cpu.halted:
        st.success("Program finished (HLT).")


def show_editor():
    st.subheader("Instruction editor")
    st.selectbox("Sample programs", list(SAMPLE_PROGRAMS), key="sample", on_change=choose_sample)
    st.text_area("Assembly program (loaded at address 100)", key="editor", height=260)
    for line_number, message in st.session_state.errors:
        st.error(f"Line {line_number}: {message}")
    st.caption("Edit the text, then press **Start**. Comments begin with `;`")


def show_diagram(record):
    st.subheader("CPU architecture")
    active = record.active if record else set()
    stage = record.stage if record else None
    st.graphviz_chart(build_cpu_dot(active, stage, cpu.regs), use_container_width=True)
    st.subheader("ALU")
    alu = cycle.last_alu
    if alu:
        op, a, b, result = alu
        st.write(f"**Operation:** {op}   **A:** {a}   **B:** {b}   **Output:** {result}")
        st.pyplot(alu_figure(alu))
    else:
        st.caption("No ALU operation yet.")


def highlight(color, is_hot):
    """Return a row-styling function for pandas tables."""
    return lambda row: [f"background-color: {color}77" if is_hot(row) else ""] * len(row)


def show_registers_and_memory(record):
    color = STAGE_COLORS.get(record.stage if record else None, "#64748b")
    active = record.active if record else set()
    st.subheader("Registers")
    registers = pd.DataFrame({"Register": list(cpu.regs), "Value": [str(v) for v in cpu.regs.values()]})
    st.dataframe(registers.style.apply(highlight(color, lambda r: r["Register"] in active), axis=1),
                 hide_index=True, use_container_width=True)

    st.subheader("Memory (RAM)")
    program_end = cpu.start + len(cpu.program)
    addresses = [a for a, value in enumerate(cpu.memory.cells)
                 if cpu.start <= a < program_end or value != 0]  # program + data
    memory = pd.DataFrame({"Address": addresses,
                           "Value": [str(cpu.memory.cells[a]) for a in addresses]})
    accessed = record.address if record else None
    st.dataframe(memory.style.apply(highlight(color, lambda r: r["Address"] == accessed), axis=1),
                 hide_index=True, use_container_width=True)


def show_history():
    st.subheader("Execution timeline and history")
    if not cycle.history:
        st.caption("History appears here as the program runs.")
        return
    st.plotly_chart(timeline_figure(cycle.history), use_container_width=True)
    rows = [{"Step": r.number, "Instr #": r.instr_no, "Instruction": r.instruction,
             "Stage": r.stage, "Register changes": ", ".join(
                 f"{name}: {old} -> {new}" for name, (old, new) in r.changes.items()),
             "Result": r.description} for r in reversed(cycle.history)]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def show_learning():
    for title, text in LESSONS.items():
        with st.expander(title, expanded=(title == "Fetch-Decode-Execute")):
            st.markdown(text)


def show_quiz():
    st.subheader("Multiple-choice quiz")
    with st.form("quiz"):
        picks = [st.radio(f"{n + 1}. {q[0]}", q[1], index=None, key=f"q{n}")
                 for n, q in enumerate(QUESTIONS)]
        submitted = st.form_submit_button("Submit answers")
    if submitted:
        answers = {n: QUESTIONS[n][1].index(pick) for n, pick in enumerate(picks) if pick}
        st.metric("Score", f"{score_quiz(answers)} / {len(QUESTIONS)}")
        for n, question in enumerate(QUESTIONS):
            mark = "✅" if answers.get(n) == question[2] else "❌"
            st.write(f"{mark} Q{n + 1}: {question[3]}")

    st.subheader("Practice challenges")
    for n, challenge in enumerate(CHALLENGES):
        with st.expander(f"{challenge[0]} - {challenge[1]}"):
            program = st.text_area("Your program", challenge[2], key=f"challenge{n}", height=130)
            if st.button("Check my answer", key=f"check{n}"):
                passed, message = check_challenge(challenge, program)
                (st.success if passed else st.error)(message)


# ---------------------------------- page layout ----------------------------------
st.title("🖥️ CPU Instruction Cycle Visualizer")
speed = st.sidebar.slider("Auto Play delay (seconds)", 0.1, 2.0, 0.6, 0.1)

simulator_tab, learn_tab, quiz_tab = st.tabs(["Simulator", "Learn", "Quiz & Challenges"])
with simulator_tab:
    show_controls()
    last_step = cycle.last
    show_stage(last_step)
    left, center, right = st.columns([1.1, 1.8, 1.1])
    with left:
        show_editor()
    with center:
        show_diagram(last_step)
    with right:
        show_registers_and_memory(last_step)
    show_history()
with learn_tab:
    show_learning()
with quiz_tab:
    show_quiz()

# Auto Play: do one micro-step, wait a moment, redraw the page.
if st.session_state.playing:
    if cpu.halted:
        st.session_state.playing = False
    else:
        time.sleep(speed)
        cycle.step()
        st.rerun()
