# ARTHA

**Open-source signal intelligence for AI/ML builders.**

ARTHA monitors developer communities for recurring pain points, scores them by evidence strength, and converts the highest-signal ones into focused open-source solutions — every one traceable to a real complaint with real upvotes.

---

## The idea

AI/ML builders hit the same walls every week. RAG pipelines that break in production. Evaluation frameworks that are too complex to set up. Agent memory that doesn't hold across sessions. These problems get discussed in Reddit threads and GitHub issues, then forgotten.

ARTHA turns that signal into structured intelligence — and then into usable tools.

Every solution in this repo was born from a specific community thread, not from guesswork.

---

## What's inside

### Signal layer — `digest/`
Scans 7 AI/ML and Indian tech communities on Reddit every 2 days. No API key required.
Scores each post 1–3 by engagement, frustration language, and keyword specificity.
New signals auto-commit to `data/pain_signals.csv` on every run.

**Communities tracked:**
`r/LocalLLaMA` · `r/MachineLearning` · `r/LanguageModelHacking` · `r/SideProject` · `r/devtools` · `r/developersIndia` · `r/indianstartups`

### Intelligence layer — `intelligence/`
Runs embeddings + HDBSCAN clustering + evidence pack generation on collected signals.
Surfaces workaround patterns, tool rejections, and ICP signals — not just summaries.

### Solutions — `solutions/`
Open-source tools built directly from high-signal pain points.

| Solution | Pain Source | Signal | What it does |
|---|---|---|---|
| [rag-eval-starter](solutions/rag-eval-starter/) | r/LocalLLaMA | 22↑ 27💬 | Compare RAG configurations on your documents. Find what actually moves the needle. |

---

## Run the signal digest

```bash
pip install requests
python3 digest/scraper.py
```

Results saved to `data/pain_signals.csv`. Scores 1–3. Filter by score = 3 to see highest-priority signals.

Auto-schedules every 2 days (Mac):
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
├── digest/
│   └── scraper.py           # Reddit signal scanner, auto-pushes to GitHub
├── intelligence/
│   ├── embeddings.py        # sentence-transformers pipeline
│   ├── clustering.py        # HDBSCAN + TF-IDF cluster labels
│   ├── scoring.py           # quote ranking, workaround extraction
│   └── report.py            # evidence pack generator
├── storage/                 # SQLite + SQLAlchemy, source-aware schema
├── api/main.py              # FastAPI backend
├── ui/app.py                # Streamlit evidence pack viewer
├── data/
│   └── pain_signals.csv     # Live signal log — updates every 2 days
└── solutions/               # Open-source tools from real pain signals
    └── rag-eval-starter/
```

---

## Philosophy

The output is evidence, not inspiration.

ARTHA does not generate startup ideas or tell you what to build.
It surfaces structured evidence — quotes, workarounds, tool rejections, community distribution — so you can make that judgment yourself.

Every solution in `solutions/` includes `problem.md`, `prd.md`, `eval_plan.md`, and `CONTEXT.md` — the full product and technical thinking behind each build.

---

*Built by [@SidharthKriplani](https://github.com/SidharthKriplani)*
