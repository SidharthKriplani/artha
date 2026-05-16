---
title: RAG Eval Starter
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# RAG Eval Starter

**Compare RAG configurations on your documents. Find what actually moves the needle.**

Most builders switch to expensive models when RAG quality is poor. The real culprit is almost always retrieval — chunk size, top-k, context quality. This tool makes that visible in minutes.

---

## Three ways to use it

### Option 1 — Gradio app (recommended)
```bash
pip install -r requirements.txt
gradio app.py
```
Upload your documents, paste your QA pairs, pick your models, click Run.

### Option 2 — CLI
```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=sk-..." > .env

# With sample data (works immediately)
python eval.py

# With your own data
python eval.py --docs ./my_docs --questions ./my_qa.json --models gpt-4o-mini gpt-4o
```

### Option 3 — HuggingFace Spaces
1. Create a new Space at huggingface.co/spaces
2. Select **Gradio** as the SDK
3. Upload all files from this folder
4. Enter your OpenAI key in the app — done

---

## What it evaluates

| Metric | What it asks |
|---|---|
| **Faithfulness** | Is the answer grounded in retrieved context, or hallucinated? |
| **Answer Relevancy** | Does the answer actually address the question? |
| **Context Precision** | Are the retrieved chunks useful, or noisy? |

Scores are 0–1. Higher is better. Powered by [RAGAS](https://github.com/explodinggradients/ragas).

> RAGAS uses an LLM as judge. Treat scores as directional, not absolute ground truth.

---

## Repo structure

```
rag-eval-starter/
├── app.py            ← Gradio app (deploy to HF Spaces)
├── eval.py           ← CLI runner
├── eval_core.py      ← shared evaluation logic
├── data/
│   ├── sample_docs/  ← drop your .txt or .pdf files here
│   └── sample_qa.json← your {question, ground_truth} pairs
├── requirements.txt
├── problem.md        ← what pain this solves, where the signal came from
├── prd.md            ← scope, success criteria, what's excluded
├── eval_plan.md      ← how we know this solution works
└── CONTEXT.md        ← technical decisions, tradeoffs, what comes next
```

---

## Signal source

Built from a real community signal on r/LocalLLaMA:
> *"Evaluated a RAG chatbot and the most expensive model was the worst performer. Notes on what actually moved the needle."*
> 22 upvotes · 27 comments

Part of the [ARTHA](https://github.com/SidharthKriplani/artha) open-source signal initiative —
every solution here traces back to a real, verified developer pain point.

---

*Built by [@SidharthKriplani](https://github.com/SidharthKriplani)*
