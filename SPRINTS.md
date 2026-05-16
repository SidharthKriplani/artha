# Sprint Log

A record of what was built, when, and which signal it traces to.

Every entry is a completed sprint — not a plan, not a proposal. Real work, real dates, real evidence.

---

## Sprint 002 — 2026-05-17

**Signals addressed:** SIGNAL-002, SIGNAL-004, SIGNAL-005

**What was built:**

**[paper-repro-auditor](solutions/paper-repro-auditor/)** — SIGNAL-002
CLI tool that compares a paper's reported config against your config across 10 reproduction risk dimensions. Zero dependencies, pure Python. Interactive or JSON file mode. Outputs ranked HIGH/MEDIUM/LOW gaps with explanations and a fix-these-first list.

**[finetune-failure-extractor](solutions/finetune-failure-extractor/)** — SIGNAL-005
CLI tool that reads eval output (CSV/JSON/JSONL) and classifies errors into 7 failure types using pattern matching. Outputs a ranked failure manifest with training data priority list. Zero dependencies, pure Python.

**[quant-pareto-bench](solutions/quant-pareto-bench/)** — SIGNAL-004
CLI tool that benchmarks multiple GGUF quantization levels on your own prompts. Measures tokens/sec, latency, accuracy (exact match or LLM judge), and builds a Pareto frontier. Runs on CPU.

**Infrastructure built this sprint:**
- Gap verification enforcement added to `track.py` — blocks claiming a signal without a documented gap verification section in SIGNALS.md
- SIGNAL-003 and SIGNAL-007 marked superseded after gap investigation found fully-solving existing tools
- Optimization objective formalized in README and CONTRIBUTING.md
- `scope.md` added to all solutions — mandatory for all future contributions
- GitHub issue and PR templates with gap verification checklist
- `run_intelligence.py` — standalone intelligence pipeline runner on pain_signals.csv
- Digest pipeline upgrade: `--no-push` flag for CI compatibility

**Signals investigated and superseded:**
- SIGNAL-003 (BibTeX citation hallucination): BibTeX Verifier, RefChecker, CheckIfExist fully solve this with zero setup
- SIGNAL-007 (RAM vs GPU tradeoffs): LLMfit.io (497 models), LocalLLM.in (within 5% accuracy) fully solve this

---

## Sprint 001 — 2026-05-16

**Signal addressed:** SIGNAL-001

**What was built:**

**[rag-eval-starter](solutions/rag-eval-starter/)** — SIGNAL-001
Gradio app that evaluates RAG configurations across OpenAI, Anthropic, Google Gemini, and Groq. Upload your documents, pick your models, run RAGAS evaluation, see which config actually moves the needle. Live on HuggingFace Spaces.

**Technical decisions:**
- FAISS for vector store — no account, no infra, runs locally
- RAGAS for evaluation — most widely referenced open-source eval framework
- Two chunk sizes (256, 512) — forces comparative output; one config teaches nothing
- Gradio over Streamlit — HuggingFace Spaces is a distribution channel, Streamlit has no equivalent

**Infrastructure built this sprint:**
- Reddit pain signal scraper across 7 communities (no API key, public JSON endpoint)
- SQLite storage with source-aware schema (Post model supports Reddit/HN/GitHub)
- Embedding pipeline (sentence-transformers all-MiniLM-L6-v2, disk-cached)
- HDBSCAN clustering + TF-IDF cluster labeling
- Evidence pack generator: top quotes, workaround patterns, tool rejections, persona inference
- FastAPI backend + Streamlit UI for intelligence layer
- APScheduler for batch job scheduling
- `track.py` — append-only signal lifecycle tracker (open→claimed→building→deployed)
- SIGNALS.md, IDEAS.md, CONTRIBUTING.md, CONTRIBUTORS.md
- GitHub issue templates and PR template

---

## How to read this log

Each sprint entry documents:
- Which signals were addressed
- What was built (one paragraph per solution)
- Key technical decisions (not just what, but why)
- What was investigated and ruled out

The log exists because the consistency of the loop is the product. One sprint every 2–3 weeks, documented, compounding over time.
