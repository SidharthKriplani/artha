# ARTHA

**Evidence-backed open-source build engine for AI/ML builders.**

The system finds the problems. The community builds the tools. The tools build credibility for everyone involved.

This is not a collection of ideas. It is a collection of evidence.

---

## How it works

```
Reddit / community pain
        ↓
  signal detection          ← scraper scans 7 communities every 2 days
        ↓
  gap verification          ← does a fully-solving, zero-friction version exist?
        ↓
   open idea                ← scoped, claimable in IDEAS.md
        ↓
  contributor claims        ← track.py --claim SIGNAL-XXX
        ↓
   tool shipped             ← solution/ with problem.md, prd.md, eval_plan.md
        ↓
  portfolio credibility     ← HuggingFace Spaces, real users, public demos
        ↓
 more contributors / better signals
```

---

## Why this exists

AI/ML tooling moves fast. Documentation, evaluation patterns, and failure-mode guides lag behind. Builders hit the same walls every week.

LLMs can generate boilerplate. They cannot generate opinionated, tested, real-world patterns born from actual community pain.

Every solution here traces back to a specific Reddit thread with real upvotes and real discussion. The signal is real. The gap is verified. The build is justified.

---

## The one bar every solution must clear

**Does a fully-solving, zero-friction version of this exist for AI/ML builders?**

Not "does something like this exist" — something always exists. The question is whether existing solutions require accounts, complex setup, or solve a slightly different problem. If yes — real gap. If no — we don't build it.

Two signals have been superseded on this basis. See [SIGNALS.md](SIGNALS.md).

---

## Solutions

Every solution is traceable to a real pain signal.

| Solution | Signal | Builder | What it does | Evidence | Live |
|---|---|---|---|---|---|
| [rag-eval-starter](solutions/rag-eval-starter/) | [SIGNAL-001](SIGNALS.md#-signal-001--rag-evaluation-expensive-models-underperform-cheaper-ones) | [@SidharthKriplani](https://github.com/SidharthKriplani) | Compare RAG configs across OpenAI, Anthropic, Gemini, Groq. Find what actually moves the needle. | [Thread](https://www.reddit.com/r/LocalLLaMA/comments/1hjsgce/) · score 3 | [Try it →](https://huggingface.co/spaces/SidharthKriplani/rag-eval-starter) |
| [paper-repro-auditor](solutions/paper-repro-auditor/) | [SIGNAL-002](SIGNALS.md#-signal-002--ml-paper-reproduction-stuck-below-reported-accuracy) | [@SidharthKriplani](https://github.com/SidharthKriplani) | Paste paper config + your config, get ranked reproduction risk factors. Zero dependencies. | [Thread](https://www.reddit.com/r/MachineLearning/comments/1ak9hgz/) · score 3 | [Try it →](https://huggingface.co/spaces/sidharthkriplani/paper-repro-auditor) |
| [finetune-failure-extractor](solutions/finetune-failure-extractor/) | [SIGNAL-005](SIGNALS.md#-signal-005--fine-tuning-feedback-loop-has-no-standard-tooling) | [@SidharthKriplani](https://github.com/SidharthKriplani) | Upload eval output, get ranked failure modes and training data priority list. Zero dependencies. | [Thread](https://www.reddit.com/r/LocalLLaMA/comments/1f8b9jz/) · score 3 | [Try it →](https://huggingface.co/spaces/sidharthkriplani/finetune-failure-extractor) |
| [quant-pareto-bench](solutions/quant-pareto-bench/) | [SIGNAL-004](SIGNALS.md#-signal-004--quantization-accuracy-vs-latency-tradeoffs-are-invisible) | [@SidharthKriplani](https://github.com/SidharthKriplani) | Your GGUF files + prompts → accuracy vs latency Pareto frontier across quantization levels. | [Thread](https://www.reddit.com/r/LocalLLaMA/comments/1f1g1q4/) · score 3 | CLI |

Open ideas waiting to be claimed → [`IDEAS.md`](IDEAS.md)

---

## Contribute in 10 minutes

1. Read [`SIGNALS.md`](SIGNALS.md) — pick an open signal
2. Verify the gap yourself (mandatory — see [CONTRIBUTING.md](CONTRIBUTING.md))
3. Claim it:
```bash
python3 track.py --claim SIGNAL-XXX --github your-username
```
4. Build it — your solution folder needs `README.md`, `problem.md`, `scope.md`, `requirements.txt`
5. Open a PR — you appear in [`CONTRIBUTORS.md`](CONTRIBUTORS.md)

**Claim expiry:** claims auto-free after 7 days if not moved to `building` or `deployed`. Move status to keep your claim alive: `python3 track.py --update SIGNAL-XXX --status building`

You know the problem is real before you write a line of code.

---

## Flagship trace: rag-eval-starter

The full chain from pain to deployed tool:

| Step | What happened |
|---|---|
| **Pain** | r/LocalLLaMA: "Evaluated a RAG chatbot and the most expensive model was the worst performer." 22 upvotes, 27 comments. |
| **Signal** | Scored 3/3 — high engagement, clear frustration, specific workaround pattern detected |
| **Gap** | Existing tools require instrumentation, accounts, or solve a different problem. Zero-friction config comparison didn't exist. |
| **PRD** | [solutions/rag-eval-starter/prd.md](solutions/rag-eval-starter/prd.md) |
| **Eval plan** | [solutions/rag-eval-starter/eval_plan.md](solutions/rag-eval-starter/eval_plan.md) |
| **Live** | [HuggingFace Spaces →](https://huggingface.co/spaces/SidharthKriplani/rag-eval-starter) |

Every solution in `solutions/` follows this same chain.

---

## What's inside

**[`SIGNALS.md`](SIGNALS.md)** — 7 documented pain points, each traced to a real community thread. Status: open / claimed / deployed / superseded.

**[`IDEAS.md`](IDEAS.md)** — Scoped, claimable contribution endpoints. One per open signal.

**[`digest/`](digest/)** — Reddit signal scanner. Runs automatically every 2 days via GitHub Actions. Scores posts 1–3. No API key required. Results committed to [`data/pain_signals.csv`](data/pain_signals.csv).

**[`intelligence/`](intelligence/)** — Embeddings + HDBSCAN clustering + evidence pack generation. Surfaces workaround patterns, tool rejections, ICP signals.

**[`SPRINTS.md`](SPRINTS.md)** — Every completed sprint: what was built, which signal it traces to, key decisions.

**[`track.py`](track.py)** — Append-only signal lifecycle CLI.

```bash
python3 track.py --list
```

**Communities tracked:**
`r/LocalLLaMA` · `r/MachineLearning` · `r/LanguageModelHacking` · `r/SideProject` · `r/devtools` · `r/developersIndia` · `r/indianstartups`

---

## Run the intelligence pipeline locally

```bash
pip install -r requirements.txt
python3 run_intelligence.py
```

Results saved to `intelligence_report.json`. Pass `--top 5` to limit output, `--save` to write JSON.

---

## Repo structure

```
artha/
├── SIGNALS.md               ← documented pain points with evidence
├── IDEAS.md                 ← open contribution endpoints
├── CONTRIBUTING.md          ← how to build here
├── CONTRIBUTORS.md          ← everyone who shipped something
├── SPRINTS.md               ← sprint log
├── track.py                 ← signal lifecycle CLI
├── run_intelligence.py      ← standalone intelligence pipeline runner
├── deploy_spaces.py         ← HuggingFace Spaces deployment script
├── digest/
│   └── scraper.py           ← Reddit scanner, auto-commits every 2 days (GH Actions)
├── intelligence/
│   ├── embeddings.py        ← sentence-transformers pipeline
│   ├── clustering.py        ← HDBSCAN + TF-IDF cluster labels
│   ├── scoring.py           ← quote ranking, workaround extraction
│   └── report.py            ← evidence pack generator
├── .github/workflows/
│   └── digest.yml           ← scheduled signal scan (every 2 days, 06:00 UTC)
├── storage/                 ← SQLite + SQLAlchemy, source-aware schema
├── api/main.py              ← FastAPI backend
├── ui/app.py                ← Streamlit evidence pack viewer
├── data/
│   ├── pain_signals.csv     ← live signal log, updates every 2 days
│   └── signal_tracker.csv   ← solution lifecycle tracker
└── solutions/
    ├── README.md            ← decision guide: which tool do I need?
    ├── rag-eval-starter/
    ├── paper-repro-auditor/
    ├── finetune-failure-extractor/
    └── quant-pareto-bench/
```

---

*Built by [@SidharthKriplani](https://github.com/SidharthKriplani) · Contributions welcome — see [IDEAS.md](IDEAS.md)*
