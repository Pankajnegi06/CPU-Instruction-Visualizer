"""visualizer.py - diagrams and charts (Student 3).

Pure functions: they receive CPU data and return a diagram or figure.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from instruction_cycle import STAGE_COLORS

IDLE_FILL, IDLE_LINE, TEXT = "#1f2937", "#475569", "#e5e7eb"
REGISTER_NODES = ["PC", "MAR", "MDR", "IR", "R1", "R2", "ACC"]
# Data paths drawn between components: (from, to)
CONNECTIONS = [("PC", "MAR"), ("MAR", "RAM"), ("RAM", "MDR"), ("MDR", "IR"), ("IR", "CU"),
               ("CU", "ALU"), ("R1", "ALU"), ("R2", "ALU"), ("ALU", "ACC"), ("MDR", "R1"),
               ("IO", "RAM")]


def build_cpu_dot(active, stage, regs):
    """Graphviz description of the CPU. Active parts get the stage colour."""
    color = STAGE_COLORS.get(stage, "#64748b")

    def node(name, label, shape="box"):
        on = name in active
        fill, border = (color, "white") if on else (IDLE_FILL, IDLE_LINE)
        font = "#0b1220" if on else TEXT
        return (f'{name} [label="{label}", shape={shape}, fillcolor="{fill}", '
                f'color="{border}", fontcolor="{font}", penwidth={3 if on else 1}];')

    lines = ['digraph CPU {',
             'bgcolor="transparent"; rankdir=LR;',
             f'node [style="rounded,filled", fontcolor="{TEXT}"]; edge [color="{IDLE_LINE}"];',
             f'subgraph cluster_cpu {{ label="CPU"; color="{IDLE_LINE}"; fontcolor="{TEXT}";',
             node("CU", "Control Unit (CU)"), node("ALU", "ALU", "trapezium")]
    for name in REGISTER_NODES:
        value = str(regs[name]).replace('"', "'")
        lines.append(node(name, f"{name}\\n{value}"))
    lines += ["}", node("RAM", "RAM", "cylinder"), node("IO", "Input / Output")]
    for source, target in CONNECTIONS:
        lit = source in active and target in active  # both ends in use
        lines.append(f'{source} -> {target} [color="{color if lit else IDLE_LINE}", '
                     f'penwidth={3 if lit else 1}];')
    lines.append("}")
    return "\n".join(lines)


def timeline_figure(history):
    """Plotly timeline: one coloured bar per micro-step."""
    figure = go.Figure()
    for stage, color in STAGE_COLORS.items():
        steps = [r.number for r in history if r.stage == stage]
        figure.add_trace(go.Bar(x=steps, y=[1] * len(steps), name=stage, marker_color=color))
    figure.update_layout(template="plotly_dark", height=160, barmode="stack",
                         margin=dict(l=10, r=10, t=10, b=30), yaxis=dict(visible=False),
                         xaxis=dict(title="Micro-step"), paper_bgcolor="rgba(0,0,0,0)",
                         plot_bgcolor="rgba(0,0,0,0)")
    return figure


def alu_figure(alu):
    """Matplotlib bar chart of the inputs and output of one ALU operation."""
    op, a, b, result = alu
    labels, values, colors = ["A"], [a], ["#3b82f6"]
    if b is not None:
        labels.append("B")
        values.append(b)
        colors.append("#f59e0b")
    labels.append("Result")
    values.append(result)
    colors.append("#22c55e")

    figure, axes = plt.subplots(figsize=(4, 2))
    figure.patch.set_facecolor("#0e1117")
    axes.set_facecolor("#0e1117")
    axes.bar_label(axes.bar(labels, values, color=colors), color=TEXT)
    axes.set_title(f"ALU: {op}", color=TEXT)
    axes.tick_params(colors=TEXT)
    figure.tight_layout()
    return figure
