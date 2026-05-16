# CONTEXT: RAG Eval Starter

## The Problem This Solves

Builders pick expensive models assuming cost correlates with RAG quality. It frequently does not. The real performance drivers are chunk size, retrieval strategy, and context quality — not the language model. This notebook makes that visible with a reproducible, runnable harness.

The signal came from a real r/LocalLLaMA thread where someone shared that their most expensive model configuration was the worst performer. 27 comments confirmed this was a widely shared experience, not an edge case.

---

## Why This Approach

**Why RAGAS over DeepEval or LangSmith?**
RAGAS is open-source, well-documented, and the most commonly referenced evaluation framework in AI/ML communities. Most target users have already heard of it. Lower adoption friction than alternatives.

**Why FAISS over Chroma, Pinecone, or Weaviate?**
FAISS runs entirely locally. No account, no API key, no infrastructure. The target user is a solo builder or early-stage team. Eliminating infrastructure setup removes the most common reason people abandon evaluation frameworks before running them once.

**Why a notebook over a Python script or CLI?**
The target user evaluates interactively. They want to see intermediate outputs, modify configurations inline, and understand what is happening at each step. A notebook is the right format for exploratory evaluation work.

**Why two retrieval configurations instead of one?**
One configuration teaches nothing. Two configurations with different chunk sizes and k values force the output to be comparative. The comparison is the insight.

---

## Key Technical Decisions

**Chunk sizes: 256 and 512 tokens**
These are the two most common starting points in practice. 256 is precise but loses surrounding context. 512 preserves more context but dilutes retrieval signal. The gap between them on a real dataset is informative.

**Evaluator model: gpt-4o-mini**
RAGAS uses an LLM as judge. Using gpt-4o-mini as the evaluator keeps costs low and avoids a confound — the same model evaluating its own answers. In a production eval setup you would use a separate, stronger evaluator. For a starter harness, gpt-4o-mini is a reasonable tradeoff.

**Metrics: Faithfulness, Answer Relevance, Context Precision**
These three cover the three places a RAG pipeline can fail: generation (faithfulness), answer quality (relevance), and retrieval quality (context precision). Together they tell you whether a problem is in retrieval or generation — which is the key diagnostic question.

---

## Tradeoffs Made

**RAGAS scores are LLM-as-judge — treat them as directional, not absolute.**
The metrics correlate with human judgment but are not ground truth. Two runs of the same configuration can produce slightly different scores. This is documented in the notebook and in the README.

**No reranking in v1.**
Reranking would improve retrieval quality significantly but adds another dependency and another variable to explain. Keeping v1 to chunk size and k keeps the comparison clean. Reranking is the obvious next extension.

**Sample dataset is synthetic.**
The included documents and QA pairs are written to illustrate the problem, not to represent a specific domain. Users will only see meaningful score differences on their own data. This is stated clearly in the notebook.

---

## What Could Break

- RAGAS API compatibility changes — the library has moved fast and had breaking changes between minor versions. Pin the version in requirements.txt.
- OpenAI rate limits on the evaluation step — if running many QA pairs, the LLM-as-judge calls can hit rate limits. Add a sleep between evaluations for larger datasets.
- FAISS on Apple Silicon — occasional installation issues. `faiss-cpu` via pip generally works; conda is more reliable if pip fails.

---

## What Comes Next

- Add a reranking configuration using a cross-encoder model
- Support Chroma and Qdrant as vector store options
- Add a cost estimator: how many API tokens did each configuration consume
- Multi-document evaluation: test across 3-5 documents to surface document-level variation
