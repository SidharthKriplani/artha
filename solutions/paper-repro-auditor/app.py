"""
paper-repro-auditor — Gradio app for HuggingFace Spaces
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from core import analyze
from risk_factors import RISK_FACTORS

RISK_COLORS = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}


def run_audit(*values):
    """
    Accepts 20 text inputs: paper_val_0..9, your_val_0..9
    Returns a formatted results string and a table.
    """
    n = len(RISK_FACTORS)
    paper_vals = values[:n]
    your_vals  = values[n:]

    paper_config = {RISK_FACTORS[i]["key"]: (paper_vals[i] or "not stated") for i in range(n)}
    your_config  = {RISK_FACTORS[i]["key"]: (your_vals[i]  or "not stated") for i in range(n)}

    report = analyze(paper_config, your_config)

    # Build table rows
    table = []
    for gap in report.gaps:
        icon = RISK_COLORS.get(gap.risk, "⚪")
        table.append([
            f"{icon} {gap.risk}",
            gap.label,
            gap.paper_value,
            gap.your_value,
            gap.explanation,
        ])

    # Summary text
    high = len(report.high_risk_gaps)
    med  = len(report.medium_risk_gaps)
    low  = len(report.low_risk_gaps)

    summary_lines = [
        f"## Overall risk: {RISK_COLORS.get(report.overall_risk, '')} {report.overall_risk}",
        f"**🔴 HIGH: {high}   🟡 MEDIUM: {med}   🟢 LOW: {low}**",
        "",
    ]

    if report.high_risk_gaps:
        summary_lines.append("### Fix these first:")
        for g in report.high_risk_gaps:
            summary_lines.append(f"- **{g.label}**: {g.explanation.split('.')[0]}.")
            summary_lines.append(f"  > 💡 {g.hint}")

    return "\n".join(summary_lines), table


# ── Build inputs ──────────────────────────────────────────────────────────────

paper_inputs = []
your_inputs  = []

for factor in RISK_FACTORS:
    paper_inputs.append(gr.Textbox(
        label=factor["paper_question"],
        placeholder="not stated",
        lines=1,
    ))
    your_inputs.append(gr.Textbox(
        label=factor["your_question"],
        placeholder="not stated",
        lines=1,
    ))

# ── Layout ────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Paper Reproduction Gap Auditor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# 📄 Paper Reproduction Gap Auditor
**Stuck below a paper's reported accuracy?** Fill in the paper's config and yours across 10 risk dimensions. Get a ranked list of what's most likely causing the gap.

*Zero dependencies. Every field you leave blank is marked as HIGH risk — that's accurate, not harsh.*
    """)

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📰 Paper's reported config")
            for inp in paper_inputs:
                inp.render()
        with gr.Column():
            gr.Markdown("### 🛠️ Your config")
            for inp in your_inputs:
                inp.render()

    run_btn = gr.Button("🔍 Audit Reproduction Gaps", variant="primary", size="lg")

    summary_out = gr.Markdown(label="Summary")
    table_out   = gr.Dataframe(
        headers=["Risk", "Dimension", "Paper", "Yours", "Explanation"],
        label="Ranked Gap Report",
        wrap=True,
    )

    run_btn.click(
        fn=run_audit,
        inputs=paper_inputs + your_inputs,
        outputs=[summary_out, table_out],
    )

    gr.Markdown("""
---
Built for [artha-ai.sig](https://github.com/SidharthKriplani/artha) · [SIGNAL-002](https://github.com/SidharthKriplani/artha/blob/main/SIGNALS.md)
    """)

if __name__ == "__main__":
    demo.launch()
