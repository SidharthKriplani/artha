"""
RAG Eval Starter — Core evaluation logic
Shared by both the CLI (eval.py) and the Gradio app (app.py).
Supports OpenAI, Anthropic, Google Gemini, and Groq.
"""

import os
import json
from pathlib import Path

import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision


# ── Model registry ────────────────────────────────────────────────────────────

PROVIDER_MODELS = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
    "anthropic": ["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022"],
    "google": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
    "groq": ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
}

# Flat model → provider lookup
MODEL_PROVIDER = {
    m: p for p, models in PROVIDER_MODELS.items() for m in models
}

DEFAULT_CONFIGS = {
    "chunk_256_k3": {"chunk_size": 256, "chunk_overlap": 25, "k": 3},
    "chunk_512_k5": {"chunk_size": 512, "chunk_overlap": 50, "k": 5},
}

SAMPLE_DOCS_DIR = Path(__file__).parent / "data" / "sample_docs"
SAMPLE_QA_FILE  = Path(__file__).parent / "data" / "sample_qa.json"


# ── LLM factory ───────────────────────────────────────────────────────────────

def get_llm(model_name: str, api_keys: dict):
    """Return a LangChain chat model for any supported provider."""
    provider = MODEL_PROVIDER.get(model_name, "openai")

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name, temperature=0,
            api_key=api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")
        )
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_name, temperature=0,
            api_key=api_keys.get("anthropic") or os.environ.get("ANTHROPIC_API_KEY")
        )
    elif provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model_name, temperature=0,
            google_api_key=api_keys.get("google") or os.environ.get("GOOGLE_API_KEY")
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model_name, temperature=0,
            api_key=api_keys.get("groq") or os.environ.get("GROQ_API_KEY")
        )
    else:
        raise ValueError(f"Unknown provider for model: {model_name}")


def get_embeddings(api_keys: dict):
    """Use OpenAI embeddings if key available, else free HuggingFace embeddings."""
    openai_key = api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")
    if openai_key:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_evaluator_llm(api_keys: dict):
    """
    Pick the evaluator LLM for RAGAS (LLM-as-judge).
    Prefers gpt-4o-mini for consistency; falls back to first available provider.
    """
    if api_keys.get("openai") or os.environ.get("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o-mini", temperature=0,
            api_key=api_keys.get("openai") or os.environ.get("OPENAI_API_KEY")
        )
    elif api_keys.get("anthropic"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-3-haiku-20240307", temperature=0,
                             api_key=api_keys["anthropic"])
    elif api_keys.get("google"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0,
                                      google_api_key=api_keys["google"])
    elif api_keys.get("groq"):
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0,
                        api_key=api_keys["groq"])
    else:
        raise ValueError("No API key provided for any supported provider.")


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
    return [p["question"] for p in pairs], [p["ground_truth"] for p in pairs]


def load_qa_from_text(text: str) -> tuple[list, list]:
    pairs = json.loads(text)
    return [p["question"] for p in pairs], [p["ground_truth"] for p in pairs]


# ── RAG pipeline ──────────────────────────────────────────────────────────────

def build_retriever(docs: list, chunk_size: int, chunk_overlap: int, k: int,
                    api_keys: dict = None):
    api_keys = api_keys or {}
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)
    embeddings = get_embeddings(api_keys)
    vectorstore = FAISS.from_documents(chunks, embeddings)
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
                    ground_truth: list, api_keys: dict = None,
                    log_fn=print) -> dict:
    api_keys = api_keys or {}
    log_fn(f"  [{config_name} × {model_name}] building index...")
    retriever, n_chunks = build_retriever(
        docs, cfg["chunk_size"], cfg["chunk_overlap"], cfg["k"], api_keys
    )
    log_fn(f"  [{config_name} × {model_name}] {n_chunks} chunks → running RAG...")

    llm = get_llm(model_name, api_keys)
    answers, contexts = run_rag(retriever, llm, questions)

    log_fn(f"  [{config_name} × {model_name}] scoring with RAGAS...")
    ragas_data = Dataset.from_dict({
        "question":     questions,
        "answer":       answers,
        "contexts":     contexts,
        "ground_truth": ground_truth,
    })
    evaluator_llm = get_evaluator_llm(api_keys)
    scores = evaluate(
        ragas_data,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=evaluator_llm,
    )

    return {
        "config":            config_name,
        "model":             model_name,
        "provider":          MODEL_PROVIDER.get(model_name, "unknown"),
        "chunk_size":        cfg["chunk_size"],
        "top_k":             cfg["k"],
        "faithfulness":      round(scores["faithfulness"],      3),
        "answer_relevancy":  round(scores["answer_relevancy"],  3),
        "context_precision": round(scores["context_precision"], 3),
    }


def run_full_eval(docs: list, questions: list, ground_truth: list,
                  models: list, configs: dict = None,
                  api_keys: dict = None, log_fn=print) -> pd.DataFrame:
    configs  = configs  or DEFAULT_CONFIGS
    api_keys = api_keys or {}
    results  = []

    for config_name, cfg in configs.items():
        for model_name in models:
            result = evaluate_config(
                config_name, cfg, docs, model_name,
                questions, ground_truth, api_keys, log_fn
            )
            results.append(result)
            log_fn(f"  ✓ {config_name} × {model_name}: "
                   f"faith={result['faithfulness']} | "
                   f"rel={result['answer_relevancy']} | "
                   f"prec={result['context_precision']}")

    df = pd.DataFrame(results)
    df["avg_score"] = df[["faithfulness", "answer_relevancy", "context_precision"]].mean(axis=1).round(3)
    df = df.sort_values("avg_score", ascending=False).reset_index(drop=True)
    return df


def build_verdict(df: pd.DataFrame) -> str:
    best  = df.iloc[0]
    worst = df.iloc[-1]
    gap   = round(best["avg_score"] - worst["avg_score"], 3)

    lines = [
        f"Best:  {best['config']} + {best['model']}  (avg: {best['avg_score']})",
        f"Worst: {worst['config']} + {worst['model']} (avg: {worst['avg_score']})",
        f"Gap:   {gap}",
        "",
    ]

    if gap > 0.1:
        lines.append("→ Large gap. Retrieval config matters more than model choice here.")
    elif gap > 0.05:
        lines.append("→ Moderate gap. Optimise retrieval before spending on a larger model.")
    else:
        lines.append("→ Small gap on this dataset. Try with your own documents for a clearer signal.")

    # Cross-provider insight if multiple providers tested
    providers_tested = df["provider"].unique()
    if len(providers_tested) > 1:
        lines.append("")
        lines.append("Cross-provider comparison:")
        provider_avgs = df.groupby("provider")["avg_score"].mean().sort_values(ascending=False)
        for provider, avg in provider_avgs.items():
            lines.append(f"  {provider}: {round(avg, 3)}")

    return "\n".join(lines)
