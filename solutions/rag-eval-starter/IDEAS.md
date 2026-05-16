# IDEAS — rag-eval-starter

Open contribution endpoints for this solution.
Each idea is scoped and ready to build.

To claim one: `python3 ../../track.py --claim SIGNAL-001 --github your-username`
Then open a PR referencing the idea number.

---

## IDEA-A — Add Ollama support for fully local evaluation

**What:** Add Ollama as a provider so the entire evaluation (generation + RAGAS scoring) runs locally with no API costs.

**Why:** The target audience includes builders who don't want to send documents to external APIs. A fully local path removes the biggest adoption barrier.

**Scope:** New provider entry in `eval_core.py` via `langchain-ollama`. UI accordion for Ollama (no API key needed, just model name). RAGAS evaluator falls back to a local model.

**Success criteria:** End-to-end eval runs on `llama3` via Ollama with no internet connection after model download.

---

## IDEA-B — Add Cohere embed-v3 as embedding option

**What:** Allow users to choose Cohere's embed-v3 as the embedding model instead of OpenAI's text-embedding-3-small.

**Why:** Cohere embeddings are competitive with OpenAI's and some users already have Cohere keys. More embedding options = more meaningful comparisons.

**Scope:** New `get_embeddings()` branch in `eval_core.py`. Cohere API key field in UI. Dropdown to select embedding model (OpenAI / Cohere / HuggingFace local).

---

## IDEA-C — Export results as a PDF report

**What:** After evaluation, add a "Download Report" button that generates a clean PDF with the results table, verdict, config details, and signal source.

**Why:** People want to share eval results with teammates or include them in research notes. A PDF is more shareable than a screenshot.

**Scope:** Use `reportlab` or `weasyprint`. PDF includes: config summary, results table, verdict text, timestamp, link to signal source.

---

## IDEA-D — Add batch evaluation mode

**What:** Allow users to run evaluation across a sweep of chunk sizes and top-k values automatically (e.g. chunk_sizes=[128,256,512], top_k=[2,3,5]) instead of just two configs.

**Why:** Two configs give a directional signal. A sweep gives a proper optimization surface.

**Scope:** Grid search over user-specified ranges. Results table shows all combinations sorted by avg score. Verdict identifies the optimal region, not just best/worst.

---

## IDEA-E — Add context window utilization metric

**What:** Track what percentage of each model's context window is actually being used by the retrieved chunks, and whether hitting the limit degrades scores.

**Why:** Context window saturation is a common hidden failure mode in RAG — you retrieve top-k chunks but they push earlier context out. This makes it visible.

**Scope:** New column in results: `ctx_utilization_%`. Warning in verdict if any config exceeds 80% context usage.

---

## IDEA-F — HuggingFace dataset integration

**What:** Allow users to load QA pairs directly from a HuggingFace dataset (e.g. `squad`, `natural_questions`) instead of pasting JSON.

**Why:** Lowers setup friction for users who want to test on standard benchmarks rather than their own QA pairs.

**Scope:** New input option: HF dataset name + split + question/answer column names. Pulls first N rows for eval.
