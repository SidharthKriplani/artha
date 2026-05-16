# ARTHA

**Open-source signal intelligence for AI/ML builders.**

ARTHA monitors developer communities for recurring pain points, scores them by evidence strength, and converts the highest-signal ones into focused open-source solutions — every one traceable to a real complaint with real upvotes.

This is not a collection of ideas. It is a collection of evidence.

---

## The optimization objective

Every solution in this repo must clear one bar:

**Does a fully-solving, zero-friction version of this exist for AI/ML builders?**

Not "does something like this exist" — something always exists. The question is whether the existing solutions require accounts, complex setup, deep expertise, or solve a slightly different problem. If the answer is yes — there is a real gap. If the answer is no — we don't build it.

This is what makes ARTHA different from a curated list or an ideas repo. The signal is real. The gap is verified. The build is justified.

---

## What's inside

### 🔴 Open signals — [`SIGNALS.md`](SIGNALS.md)
7 documented developer pain points, each traced to a real community thread. Four deployed. Three waiting to be built. Read this first.

### 💡 Open ideas — [`IDEAS.md`](IDEAS.md)
Scoped, claimable contribution endpoints — one per open signal. If you want to build something, pick one here.

### ✅ Solutions — [`solutions/`](solutions/)
Open-source tools built directly from high-signal pain points.

| Solution | Signal | What it does | Live |
|---|---|---|---|
| [rag-eval-starter](solutions/rag-eval-starter/) | [SIGNAL-001](SIGNALS.md#-signal-001--rag-evaluation-expensive-models-underperform-cheaper-ones) | Compare RAG configs across OpenAI, Anthropic, Gemini, and Groq. Find what actually moves the needle. | [Try it →](https://huggingface.co/spaces/SidharthKriplani/rag-eval-starter) |
| [paper-repro-auditor](solutions/paper-repro-auditor/) | [SIGNAL-002](SIGNALS.md#-signal-002--ml-paper-reproduction-stuck-below-reported-accuracy) | Paste paper config + your config, get ranked reproduction risk factors. Zero dependencies. | CLI |
| [finetune-failure-extractor](solutions/finetune-failure-extractor/) | [SIGNAL-005](SIGNALS.md#-signal-005--fine-tuning-feedback-loop-has-no-standard-tooling) | Reads eval output, ranks failure modes by frequency, outputs training data priority manifest. Zero dependencies. | CLI |
| [quant-pareto-bench](solutions/quant-pareto-bench/) | [SIGNAL-004](SIGNALS.md#-signal-004--quantization-accuracy-vs-latency-tradeoffs-are-invisible) | Your GGUF files + your prompts → accuracy vs latency Pareto frontier across quantization levels. | CLI |

### 📡 Signal layer — [`digest/`](digest/)
Scans 7 AI/ML and Indian tech communities on Reddit every 2 days. No API key required.
Scores each post 1–3 by engagement, frustration language, and keyword specificity.
New signals auto-commit to [`data/pain_signals.csv`](data/pain_signals.csv) on every run.

**Communities tracked:**
`r/LocalLLaMA` · `r/MachineLearning` · `r/LanguageModelHacking` · `r/SideProject` · `r/devtools` · `r/developersIndia` · `r/indianstartups`

### 🧠 Intelligence layer — [`intelligence/`](intelligence/)
Runs embeddings + HDBSCAN clustering + evidence pack generation on collected signals.
Surfaces workaround patterns, tool rejections, and ICP signals — not just summaries.

### 📋 Signal tracker — [`track.py`](track.py)
Append-only lifecycle manager. Tracks every signal from open → claimed → building → deployed.

```bash
python3 track.py --list
```

---

## Contributing

ARTHA is built to be extended by anyone.

Every open idea in [`IDEAS.md`](IDEAS.md) traces back to a documented pain point. You know the problem is real before you write a line of code.

**To claim an idea and build a solution:**
```bash
python3 track.py --claim SIGNAL-XXX --github your-username
```

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full process. Every contributor appears in [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

---

## Run the signal digest

```bash
pip install requests
python3 digest/scraper.py
```

Results saved to `data/pain_signals.csv`. Scores 1–3. Filter by score = 3 for highest-priority signals.
New signals auto-push to GitHub after each run.

Auto-schedule every 2 days (Mac):
```bash
crontab -e
# Add: 0 8 */2 * * cd ~/Documents/GitHub/artha && python3 digest/scraper.py
```

---

## Run the full intelligence pipeline

```bash
pip install -r requirements.txt

# Start API
uvicorn api.main:app --reload

# Start UI
streamlit run ui/app.py
```

---

## Repo structure

```
artha/
├── SIGNALS.md           ← documented pain points with evidence
├── IDEAS.md             ← open contribution endpoints
├── CONTRIBUTING.md      ← how to build here
├── CONTRIBUTORS.md      ← everyone who shipped something
├── track.py             ← signal lifecycle CLI
├── digest/
│   └── scraper.py       ← Reddit signal scanner, auto-pushes to GitHub
├── intelligence/
│   ├── embeddings.py    ← sentence-transformers pipeline
│   ├── clustering.py    ← HDBSCAN + TF-IDF cluster labels
│   ├── scoring.py       ← quote ranking, workaround extraction
│   └── report.py        ← evidence pack generator
├── storage/             ← SQLite + SQLAlchemy, source-aware schema
├── api/main.py          ← FastAPI backend
├── ui/app.py            ← Streamlit evidence pack viewer
├── data/
│   ├── pain_signals.csv     ← live signal log, updates every 2 days
│   └── signal_tracker.csv   ← solution lifecycle tracker
└── solutions/
    └── rag-eval-starter/    ← RAG config evaluator, live on HuggingFace
```

---

## Philosophy

The output is evidence, not inspiration.

ARTHA does not generate startup ideas or tell you what to build.
It surfaces structured evidence — quotes, workarounds, tool rejections, community distribution — so you can make that judgment yourself.

Every solution in `solutions/` includes `problem.md`, `prd.md`, `eval_plan.md`, and `CONTEXT.md` — the full product and technical thinking behind each build.

---

*Built by [@SidharthKriplani](https://github.com/SidharthKriplani) · Contributions welcome — see [IDEAS.md](IDEAS.md)*
