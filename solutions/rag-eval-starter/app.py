"""
RAG Eval Starter — Gradio App
Deployable to HuggingFace Spaces with zero config changes.

Local:    gradio app.py
Spaces:   upload this folder to a new HF Space (SDK: Gradio)
"""

import os
import json
import tempfile
from pathlib import Path

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

SAMPLE_QA_PATH  = Path(__file__).parent / "data" / "sample_qa.json"
SAMPLE_DOCS_DIR = Path(__file__).parent / "data" / "sample_docs"

with open(SAMPLE_QA_PATH) as f:
    SAMPLE_QA_TEXT = json.dumps(json.load(f), indent=2)


# ── Evaluation runner ─────────────────────────────────────────────────────────

def run_evaluation(
    api_key: str,
    doc_files,
    qa_text: str,
    model_choices: list,
    chunk_small: int,
    chunk_large: int,
    top_k: int,
    progress=gr.Progress()
):
    if not api_key or not api_key.startswith("sk-"):
        return None, "⚠️ Please enter a valid OpenAI API key.", ""

    os.environ["OPENAI_API_KEY"] = api_key

    try:
        from eval_core import (
            load_docs_from_files, load_docs_from_dir,
            load_qa_from_text, run_full_eval, build_verdict,
            DEFAULT_CONFIGS
        )
    except ImportError as e:
        return None, f"Import error: {e}", ""

    # Load documents
    progress(0.1, desc="Loading documents...")
    try:
        if doc_files:
            docs = load_docs_from_files([f.name for f in doc_files])
        else:
            docs = load_docs_from_dir(SAMPLE_DOCS_DIR)
            gr.Info("No documents uploaded — using sample documents.")
    except Exception as e:
        return None, f"Error loading documents: {e}", ""

    if not docs:
        return None, "No documents found. Upload .txt or .pdf files.", ""

    # Load QA pairs
    progress(0.15, desc="Parsing QA pairs...")
    try:
        questions, ground_truth = load_qa_from_text(qa_text)
    except Exception as e:
        return None, f"Error parsing QA pairs: {e}\n\nExpected format: [{{'question': '...', 'ground_truth': '...'}}]", ""

    if not questions:
        return None, "No QA pairs found.", ""

    if not model_choices:
        return None, "Select at least one model.", ""

    # Build configs from UI inputs
    configs = {
        f"chunk_{chunk_small}_k{top_k}": {
            "chunk_size": chunk_small,
            "chunk_overlap": chunk_small // 10,
            "k": top_k
        },
        f"chunk_{chunk_large}_k{top_k}": {
            "chunk_size": chunk_large,
            "chunk_overlap": chunk_large // 10,
            "k": top_k
        },
    }

    log_messages = []
    def log(msg):
        log_messages.append(msg)
        progress(0.3, desc=msg)

    # Run evaluation
    try:
        progress(0.2, desc="Running RAG pipeline and scoring...")
        df = run_full_eval(
            docs=docs,
            questions=questions,
            ground_truth=ground_truth,
            models=model_choices,
            configs=configs,
            log_fn=log
        )
    except Exception as e:
        return None, f"Evaluation error: {e}", ""

    verdict = build_verdict(df)
    display_cols = ["config", "model", "faithfulness",
                    "answer_relevancy", "context_precision", "avg_score"]

    return df[display_cols], verdict, "\n".join(log_messages)


# ── Gradio UI ─────────────────────────────────────────────────────────────────

with gr.Blocks(
    title="RAG Eval Starter",
    theme=gr.themes.Soft(),
    css=".verdict-box { font-family: monospace; font-size: 0.9em; }"
) as demo:

    gr.Markdown("""
    # 🔍 RAG Eval Starter
    **Compare RAG configurations on your documents. Find what actually moves the needle.**

    Most builders switch to expensive models when RAG quality is poor.
    The real culprit is almost always retrieval — chunk size, top-k, context quality.
    This tool makes that visible.

    *Built from a real r/LocalLLaMA signal · Part of [ARTHA](https://github.com/SidharthKriplani/artha)*
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. Setup")

            api_key = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-...",
                type="password",
                info="Used only for this session. Never stored."
            )

            gr.Markdown("### 2. Your Documents")
            doc_files = gr.File(
                label="Upload .txt or .pdf files",
                file_count="multiple",
                file_types=[".txt", ".pdf"],
            )
            gr.Markdown("_Leave empty to use sample documents_")

            gr.Markdown("### 3. QA Pairs")
            qa_input = gr.Textbox(
                label="Question + Ground Truth pairs (JSON)",
                value=SAMPLE_QA_TEXT,
                lines=10,
                info='Format: [{"question": "...", "ground_truth": "..."}]'
            )

        with gr.Column(scale=1):
            gr.Markdown("### 4. Configuration")

            model_choices = gr.CheckboxGroup(
                choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                value=["gpt-4o-mini"],
                label="Models to compare",
                info="gpt-4o-mini is cheapest. Does gpt-4o actually score better?"
            )

            with gr.Row():
                chunk_small = gr.Slider(
                    128, 512, value=256, step=64,
                    label="Chunk size A (smaller)",
                    info="More precise retrieval, less context per chunk"
                )
                chunk_large = gr.Slider(
                    256, 1024, value=512, step=64,
                    label="Chunk size B (larger)",
                    info="More context per chunk, less precise retrieval"
                )

            top_k = gr.Slider(
                1, 10, value=3, step=1,
                label="Top-K chunks retrieved",
                info="How many chunks to pass to the model"
            )

            run_btn = gr.Button("Run Evaluation", variant="primary", size="lg")

            gr.Markdown("""
            **Metrics explained:**
            - **Faithfulness** — Is the answer grounded in context, or hallucinated?
            - **Answer Relevancy** — Does it actually answer the question?
            - **Context Precision** — Are retrieved chunks useful or noisy?

            > Scores are 0–1. Higher is better. Powered by RAGAS (LLM-as-judge — treat as directional).
            """)

    gr.Markdown("---")
    gr.Markdown("### Results")

    results_table = gr.Dataframe(
        label="Configuration Comparison",
        interactive=False,
        wrap=True
    )

    verdict_box = gr.Textbox(
        label="Verdict",
        lines=8,
        interactive=False,
        elem_classes=["verdict-box"]
    )

    with gr.Accordion("Run log", open=False):
        run_log = gr.Textbox(label="", lines=10, interactive=False)

    run_btn.click(
        fn=run_evaluation,
        inputs=[api_key, doc_files, qa_input,
                model_choices, chunk_small, chunk_large, top_k],
        outputs=[results_table, verdict_box, run_log]
    )

    gr.Markdown("""
    ---
    **Next steps after running:**
    1. Replace sample docs with your own documents
    2. Replace QA pairs with questions your users actually ask
    3. The config with the highest avg score is your starting point
    4. Optimise retrieval *before* switching to a more expensive model

    [View source on GitHub](https://github.com/SidharthKriplani/artha/tree/main/solutions/rag-eval-starter)
    """)


if __name__ == "__main__":
    demo.launch()
