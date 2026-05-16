"""
RAG Eval Starter — Gradio App
Supports OpenAI, Anthropic, Google Gemini, and Groq.
Use any combination — one provider, all four, or anything in between.
"""

import os
import json
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
    # API keys
    openai_key, anthropic_key, google_key, groq_key,
    # Models
    openai_models, anthropic_models, google_models, groq_models,
    # Docs + QA
    doc_files, qa_text,
    # Config
    chunk_small, chunk_large, top_k,
    progress=gr.Progress()
):
    api_keys = {
        "openai":    openai_key.strip()    if openai_key    else "",
        "anthropic": anthropic_key.strip() if anthropic_key else "",
        "google":    google_key.strip()    if google_key    else "",
        "groq":      groq_key.strip()      if groq_key      else "",
    }

    all_models = (openai_models or []) + (anthropic_models or []) + \
                 (google_models or []) + (groq_models or [])

    if not all_models:
        return None, "⚠️ Select at least one model.", ""

    # Validate keys for selected models
    from eval_core import MODEL_PROVIDER
    for m in all_models:
        provider = MODEL_PROVIDER.get(m, "openai")
        if not api_keys.get(provider):
            return None, f"⚠️ No API key provided for {provider} (needed for {m}).", ""

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
            paths = [f if isinstance(f, str) else f.name for f in doc_files]
            docs = load_docs_from_files(paths)
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
        return None, f"Error parsing QA: {e}\n\nExpected: [{{'question': '...', 'ground_truth': '...'}}]", ""

    if not questions:
        return None, "No QA pairs found.", ""

    configs = {
        f"chunk_{chunk_small}_k{top_k}": {
            "chunk_size": chunk_small, "chunk_overlap": chunk_small // 10, "k": top_k
        },
        f"chunk_{chunk_large}_k{top_k}": {
            "chunk_size": chunk_large, "chunk_overlap": chunk_large // 10, "k": top_k
        },
    }

    log_messages = []
    def log(msg):
        log_messages.append(msg)
        progress(0.3, desc=msg)

    try:
        progress(0.2, desc="Running RAG pipeline and scoring...")
        df = run_full_eval(
            docs=docs, questions=questions, ground_truth=ground_truth,
            models=all_models, configs=configs,
            api_keys=api_keys, log_fn=log
        )
    except Exception as e:
        return None, f"Evaluation error: {e}", ""

    verdict = build_verdict(df)
    display_cols = ["config", "model", "provider", "faithfulness",
                    "answer_relevancy", "context_precision", "avg_score"]
    return df[display_cols], verdict, "\n".join(log_messages)


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="RAG Eval Starter", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🔍 RAG Eval Starter
    **Compare RAG configurations across models and providers. Find what actually moves the needle.**

    Test any combination — one model, one provider, or mix OpenAI vs Claude vs Gemini vs Groq.
    Enter only the API keys for providers you want to test.

    *Built from a real r/LocalLLaMA signal · Part of [ARTHA](https://github.com/SidharthKriplani/artha)*
    """)

    with gr.Row():
        # ── Left column: keys + docs + QA ──
        with gr.Column(scale=1):

            gr.Markdown("### 🔑 API Keys")
            gr.Markdown("_Enter keys only for the providers you want to test._")

            with gr.Accordion("OpenAI", open=True):
                openai_key = gr.Textbox(label="OpenAI API Key", placeholder="sk-...",
                                        type="password", info="Also used as RAGAS evaluator if available.")
                openai_models = gr.CheckboxGroup(
                    choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                    value=["gpt-4o-mini"], label="Models"
                )

            with gr.Accordion("Anthropic (Claude)", open=False):
                anthropic_key = gr.Textbox(label="Anthropic API Key", placeholder="sk-ant-...",
                                           type="password")
                anthropic_models = gr.CheckboxGroup(
                    choices=["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"],
                    value=[], label="Models"
                )

            with gr.Accordion("Google (Gemini)", open=False):
                google_key = gr.Textbox(label="Google API Key", placeholder="AIza...",
                                        type="password")
                google_models = gr.CheckboxGroup(
                    choices=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
                    value=[], label="Models"
                )

            with gr.Accordion("Groq (fast + free tier)", open=False):
                groq_key = gr.Textbox(label="Groq API Key", placeholder="gsk_...",
                                      type="password")
                groq_models = gr.CheckboxGroup(
                    choices=["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
                    value=[], label="Models"
                )

            gr.Markdown("### 📄 Your Documents")
            doc_files = gr.File(label="Upload .txt or .pdf files",
                                file_count="multiple", file_types=[".txt", ".pdf"])
            gr.Markdown("_Leave empty to use sample documents_")

            gr.Markdown("### ❓ QA Pairs")
            qa_input = gr.Textbox(
                label="Question + Ground Truth pairs (JSON)",
                value=SAMPLE_QA_TEXT, lines=8,
                info='Format: [{"question": "...", "ground_truth": "..."}]'
            )

        # ── Right column: config + results ──
        with gr.Column(scale=1):

            gr.Markdown("### ⚙️ Retrieval Configuration")

            with gr.Row():
                chunk_small = gr.Slider(128, 512, value=256, step=64,
                                        label="Chunk size A (smaller)",
                                        info="More precise retrieval, less context per chunk")
                chunk_large = gr.Slider(256, 1024, value=512, step=64,
                                        label="Chunk size B (larger)",
                                        info="More context per chunk, less precise retrieval")

            top_k = gr.Slider(1, 10, value=3, step=1,
                              label="Top-K chunks retrieved",
                              info="How many chunks to pass to the model")

            run_btn = gr.Button("▶ Run Evaluation", variant="primary", size="lg")

            gr.Markdown("""
            **Metrics (RAGAS, 0–1, higher is better):**
            - **Faithfulness** — Is the answer grounded in retrieved context, or hallucinated?
            - **Answer Relevancy** — Does it actually answer the question?
            - **Context Precision** — Are retrieved chunks useful or noisy?

            > RAGAS uses LLM-as-judge. Treat scores as directional, not ground truth.
            """)

            gr.Markdown("### 📊 Results")

            results_table = gr.Dataframe(label="Configuration × Model Comparison",
                                         interactive=False, wrap=True)

            verdict_box = gr.Textbox(label="Verdict", lines=10, interactive=False)

            with gr.Accordion("Run log", open=False):
                run_log = gr.Textbox(label="", lines=8, interactive=False)

    run_btn.click(
        fn=run_evaluation,
        inputs=[
            openai_key, anthropic_key, google_key, groq_key,
            openai_models, anthropic_models, google_models, groq_models,
            doc_files, qa_input,
            chunk_small, chunk_large, top_k
        ],
        outputs=[results_table, verdict_box, run_log]
    )

    gr.Markdown("""
    ---
    **After running:** The config + model with the highest avg score is your baseline.
    Optimise retrieval *before* switching to a more expensive model — that's the core insight.

    [View source on GitHub](https://github.com/SidharthKriplani/artha/tree/main/solutions/rag-eval-starter)
    """)


if __name__ == "__main__":
    demo.launch()
