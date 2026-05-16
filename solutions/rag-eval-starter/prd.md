# PRD: RAG Eval Starter

## What We Are Building

A minimal, runnable RAG evaluation notebook that lets any builder test multiple retrieval + model configurations on their own documents and get structured metric output.

---

## In Scope

- Single Jupyter notebook as the primary artifact
- Accepts: a folder of .txt or .pdf documents + a list of question-answer pairs
- Tests: at least 2 retrieval strategies (naive top-k vs. with reranking) × 2 models
- Outputs: per-configuration scores on 3 metrics: Faithfulness, Answer Relevance, Context Precision
- Uses RAGAS for scoring (most widely known, open-source)
- Works with OpenAI API (most common setup among target users)
- Sample dataset included so it runs out of the box with zero user data

## Out of Scope

- UI or web interface
- Async / batch evaluation at scale
- Fine-tuned evaluator models
- Support for every vector DB (FAISS only for v1 — zero infrastructure required)
- Automated CI eval pipelines

---

## Success Criteria

- Runs end-to-end in under 30 minutes on a new machine
- Produces a comparison table showing metric scores per configuration
- Sample dataset produces meaningful, non-trivial score differences between configurations (proves the eval is actually discriminating)
- README explains every metric in one plain-English sentence

---

## What We Are Not Claiming

This is not a production eval framework. It is a starting point. The goal is to give builders a working baseline they can extend, not a complete solution.
