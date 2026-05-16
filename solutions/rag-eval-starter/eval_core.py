"""
RAG Eval Starter — Core evaluation logic
Shared by both the CLI (eval.py) and the Gradio app (app.py).
"""

import os
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass

import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision


# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_CONFIGS = {
    "chunk_256_k3": {"chunk_size": 256, "chunk_overlap": 25,  "k": 3},
    "chunk_512_k5": {"chunk_size": 512, "chunk_overlap": 50,  "k": 5},
}

SAMPLE_DOCS_DIR = Path(__file__).parent / "data" / "sample_docs"
SAMPLE_QA_FILE  = Path(__file__).parent / "data" / "sample_qa.json"


# ── Document loading ──────────────────────────────────────────────────────────

def load_docs_from_dir(docs_dir: Path) -> list:
    docs = []
    for f in Path(docs_dir).iterdir():
        if f.suffix == ".txt":
            docs.extend(TextLoader(str(f)).load())
        elif f.suffix == ".pdf":
            docs.extend(PyPDFLoader(str(f)).load())
    return docs


def load_docs_from_files(file_paths: list) -> list:
    """Load from a list of file paths (used by Gradio file upload)."""
    docs = []
    for fp in file_paths:
        fp = Path(fp)
        if fp.suffix == ".txt":
            docs.extend(TextLoader(str(fp)).load())
        elif fp.suffix == ".pdf":
            docs.extend(PyPDFLoader(str(fp)).load())
    return docs


def load_qa(qa_path: Path) -> tuple[list, list]:
    with open(qa_path) as f:
        pairs = json.load(f)
    questions    = [p["question"]    for p in pairs]
    ground_truth = [p["ground_truth"] for p in pairs]
    return questions, ground_truth


def load_qa_from_text(text: str) -> tuple[list, list]:
    """Parse QA pairs from JSON string (used by Gradio text input)."""
    pairs = json.loads(text)
    questions    = [p["question"]    for p in pairs]
    ground_truth = [p["ground_truth"] for p in pairs]
    return questions, ground_truth


# ── RAG pipeline ──────────────────────────────────────────────────────────────

def build_retriever(docs: list, chunk_size: int, chunk_overlap: int, k: int):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks     = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore= FAISS.from_documents(chunks, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": k}), len(chunks)


def run_rag(retriever, llm, questions: list) -> tuple[list, list]:
    chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, return_source_documents=True
    )
    answers, contexts = [], []
    for q in questions:
        result = chain.invoke({"query": q})
        answers.append(result["result"])
        contexts.append([doc.page_content for doc in result["source_documents"]])
    return answers, contexts


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_config(config_name: str, cfg: dict, docs: list,
                    model_name: str, questions: list,
                    ground_truth: list, log_fn=print) -> dict:
    """
    Run one (config × model) evaluation. Returns a result dict.
    log_fn: callable for progress messages (print for CLI, gr.update for Gradio).
    """
    log_fn(f"  [{config_name} × {model_name}] building index...")
    retriever, n_chunks = build_retriever(
        docs,
        chunk_size=cfg["chunk_size"],
        chunk_overlap=cfg["chunk_overlap"],
        k=cfg["k"]
    )
    log_fn(f"  [{config_name} × {model_name}] {n_chunks} chunks → running RAG...")

    llm     = ChatOpenAI(model=model_name, temperature=0)
    answers, contexts = run_rag(retriever, llm, questions)

    log_fn(f"  [{config_name} × {model_name}] scoring with RAGAS...")
    ragas_data = Dataset.from_dict({
        "question":    questions,
        "answer":      answers,
        "contexts":    contexts,
        "ground_truth":ground_truth,
    })
    evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    scores = evaluate(
        ragas_data,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=evaluator_llm,
    )

    return {
        "config":            config_name,
        "model":             model_name,
        "chunk_size":        cfg["chunk_size"],
        "top_k":             cfg["k"],
        "faithfulness":      round(scores["faithfulness"],      3),
        "answer_relevancy":  round(scores["answer_relevancy"],  3),
        "context_precision": round(scores["context_precision"], 3),
    }


def run_full_eval(docs: list, questions: list, ground_truth: list,
                  models: list, configs: dict = None,
                  log_fn=print) -> pd.DataFrame:
    """
    Run all (config × model) combinations. Returns sorted results DataFrame.
    """
    configs = configs or DEFAULT_CONFIGS
    results = []

    for config_name, cfg in configs.items():
        for model_name in models:
            result = evaluate_config(
                config_name, cfg, docs, model_name,
                questions, ground_truth, log_fn
            )
            results.append(result)
            log_fn(f"  ✓ {config_name} × {model_name}: "
                   f"faithfulness={result['faithfulness']} | "
                   f"relevancy={result['answer_relevancy']} | "
                   f"precision={result['context_precision']}")

    df = pd.DataFrame(results)
    df["avg_score"] = df[["faithfulness", "answer_relevancy", "context_precision"]].mean(axis=1).round(3)
    df = df.sort_values("avg_score", ascending=False).reset_index(drop=True)
    return df


def build_verdict(df: pd.DataFrame) -> str:
    best  = df.iloc[0]
    worst = df.iloc[-1]
    gap   = round(best["avg_score"] - worst["avg_score"], 3)

    lines = [
        f"Best:  {best['config']} + {best['model']}  (avg score: {best['avg_score']})",
        f"Worst: {worst['config']} + {worst['model']} (avg score: {worst['avg_score']})",
        f"Gap:   {gap}",
        "",
    ]

    if gap > 0.1:
        lines.append("→ Significant gap. Retrieval config matters more than the model here.")
    elif gap > 0.05:
        lines.append("→ Moderate gap. Optimise retrieval before scaling to a larger model.")
    else:
        lines.append("→ Small gap on this dataset. Try with your own documents.")

    if "gpt-4o" in df["model"].values and "gpt-4o-mini" in df["model"].values:
        gpt4o_avg = df[df["model"] == "gpt-4o"]["avg_score"].mean()
        mini_avg  = df[df["model"] == "gpt-4o-mini"]["avg_score"].mean()
        diff      = round(gpt4o_avg - mini_avg, 3)
        lines.append("")
        lines.append(f"gpt-4o avg:      {round(gpt4o_avg, 3)}")
        lines.append(f"gpt-4o-mini avg: {round(mini_avg, 3)}")
        if diff < 0.05:
            lines.append(f"→ Score gap: {diff}. The expensive model may not justify the cost on this pipeline.")
        else:
            lines.append(f"→ Score gap: {diff}. Evaluate whether quality gain justifies ~10x cost.")

    return "\n".join(lines)
