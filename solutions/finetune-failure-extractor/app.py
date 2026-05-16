"""
finetune-failure-extractor — Gradio app for HuggingFace Spaces
"""

import sys
import csv
import json
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from core import analyze, load_eval_output
from failure_types import FAILURE_TYPES

RISK_ICONS = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
RANK_ICONS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]


def run_extraction(file, paste_text, top_n):
    """
    Accepts either a file upload or pasted CSV text.
    Returns summary markdown and a results table.
    """
    rows = []

    if file is not None:
        path = file if isinstance(file, str) else file.name
        try:
            rows = load_eval_output(path)
        except Exception as e:
            return f"❌ Error reading file: {e}", []

    elif paste_text and paste_text.strip():
        try:
            reader = csv.DictReader(io.StringIO(paste_text.strip()))
            rows = list(reader)
        except Exception as e:
            return f"❌ Error parsing pasted CSV: {e}", []
    else:
        return "⚠️ Please upload a file or paste CSV data.", []

    if not rows:
        return "⚠️ No rows found in input.", []

    manifest = analyze(rows, max_examples=2)

    if manifest.total_errors == 0:
        return f"✅ No errors found in {manifest.total_examples} examples — all predictions match references.", []

    # Summary markdown
    lines = [
        f"## Results",
        f"**Total examples:** {manifest.total_examples}  |  "
        f"**Errors:** {manifest.total_errors}  |  "
        f"**Error rate:** {manifest.error_rate}%",
        "",
        "### Failure Mode Ranking",
    ]

    for i, ft in enumerate(manifest.ranked[:int(top_n)]):
        icon = RANK_ICONS[i] if i < len(RANK_ICONS) else f"{i+1}."
        bar = "█" * int(ft.pct / 5)
        lines.append(f"**{icon} {ft.label}** — {ft.pct}% of errors ({ft.count} cases)")
        lines.append(f"`{bar}` {ft.description}")
        if ft.examples:
            ex = ft.examples[0]
            lines.append(f"> **Example:** `{ex.input_text[:80]}` → predicted `{ex.prediction[:60]}`, expected `{ex.reference[:60]}`")
        lines.append("")

    lines += [
        "---",
        "### 🎯 Training Data Priority (next batch)",
        "Add more examples of these failure types, in order:",
    ]
    for i, ft in enumerate(manifest.ranked[:int(top_n)], 1):
        lines.append(f"{i}. **{ft.label}** — {ft.count} cases ({ft.pct}%)")

    # Table
    table = []
    for i, ft in enumerate(manifest.ranked[:int(top_n)], 1):
        ex_text = ""
        if ft.examples:
            ex = ft.examples[0]
            ex_text = f"Input: {ex.input_text[:60]} → Got: {ex.prediction[:40]}"
        table.append([
            i,
            ft.label,
            ft.count,
            f"{ft.pct}%",
            ex_text,
        ])

    return "\n".join(lines), table


# ── Layout ────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Fine-Tune Failure Extractor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
# 🔍 Fine-Tune Failure Extractor
**Stop re-training blindly.** Upload your eval output and get a ranked failure mode manifest — which error types appear most, with examples and a training data priority list.

**Input:** CSV, JSON, or JSONL with columns: `input`, `prediction`, `reference` (+ optional `error_note`)

**Output:** Ranked failure types → what to fix in your next training batch.
    """)

    with gr.Row():
        with gr.Column(scale=2):
            file_input = gr.File(
                label="Upload eval output (CSV / JSON / JSONL)",
                file_types=[".csv", ".json", ".jsonl"],
            )
            gr.Markdown("**Or paste CSV directly:**")
            paste_input = gr.Textbox(
                label="Paste CSV (with header: input,prediction,reference,error_note)",
                lines=8,
                placeholder="input,prediction,reference,error_note\n\"What is 7×8?\",54,56,wrong operator\n\"Capital of France?\",London,Paris,factual gap",
            )
            top_n = gr.Slider(minimum=1, maximum=7, value=5, step=1, label="Show top N failure types")
            run_btn = gr.Button("🚀 Extract Failure Modes", variant="primary", size="lg")

        with gr.Column(scale=3):
            summary_out = gr.Markdown(label="Analysis")
            table_out = gr.Dataframe(
                headers=["Rank", "Failure Type", "Count", "% of Errors", "Example"],
                label="Ranked Failure Manifest",
                wrap=True,
            )

    run_btn.click(
        fn=run_extraction,
        inputs=[file_input, paste_input, top_n],
        outputs=[summary_out, table_out],
    )

    gr.Markdown("""
---
**CSV format:**
```
input,prediction,reference,error_note
"What is 7 × 8?",54,56,wrong operator
"Capital of France?",London,Paris,factual gap
```
`error_note` is optional but dramatically improves classification accuracy.

Built for [ARTHA](https://github.com/SidharthKriplani/artha) · [SIGNAL-005](https://github.com/SidharthKriplani/artha/blob/main/SIGNALS.md)
    """)

if __name__ == "__main__":
    demo.launch()
