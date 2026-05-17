# artha-ai.sig — Full Build Context for Learning

## How to use this document

Paste everything below this line into ChatGPT and say:

"You are a senior AI engineer and product thinker. I built this project. 
Read the full context, then have a conversation with me about it. 
Ask me one question at a time. Go one level deeper on every answer I give. 
If I am vague or just repeating what the document says, push back and ask me 
to explain it in my own words. Do not summarise — interrogate."

---

## Who I am

Data scientist with a background in AI/ML, embeddings, RAG, evaluation, and 
metric rigor. I am building in public to position myself for AI PM and 
applied AI roles. I run a tech community called DAI with 1,200+ members.

---

## What artha-ai.sig is

artha-ai.sig is an open-source signal intelligence system that:
1. Scrapes AI/ML developer communities on Reddit for recurring pain points
2. Scores each signal by frequency, engagement, and keyword specificity
3. Runs an intelligence pipeline (embeddings + clustering + evidence packs) 
   to find non-obvious patterns across hundreds of posts
4. Feeds me a ranked digest so I can pick one pain point and build a focused 
   open-source solution for it

The goal is not to build a startup. The goal is to build a consistent public 
record of evidence-based solutions — every solution traceable to a real 
community signal with real upvotes and real discussion.

---

## Why this approach

The AI/ML tooling space is exploding but documentation, evaluation patterns, 
and failure-mode guides lag behind the tools. Builders hit the same walls 
every week. LLMs can generate boilerplate. They cannot generate opinionated, 
tested, real-world patterns born from actual community pain. That gap is the 
opportunity.

The model for this is Shubham Saboo's awesome-llm-apps repository (105K stars 
on GitHub). He started by organising his own experiments publicly. The repo 
grew because it solved a real problem many developers had. The key difference 
in my approach: every solution I build traces back to a specific pain signal 
with evidence — not intuition.

---

## What was built: artha-ai.sig v0 (digest scraper)

File: digest/scraper.py

A Python script that hits Reddit's public JSON API (no API key required) 
across 7 subreddits:
- r/LocalLLaMA, r/MachineLearning, r/LanguageModelHacking (global AI/ML)
- r/SideProject, r/devtools (indie builders)
- r/developersIndia, r/indianstartups (Indian tech community)

For each post it:
- Matches against 40+ pain keywords (frustration, workaround, gap signals)
- Scores each post 1-3 based on upvotes, comment count, keyword density
- Deduplicates using seen_ids.json (never reprocesses the same post)
- Appends results to data/pain_signals.csv

On first run it collected 154 pain signals across all 7 communities.

Key decision: used Reddit's public JSON endpoint instead of the official API 
because Reddit now requires manual approval for new API keys. The public 
endpoint supports read-only access at ~30 requests/minute — more than enough 
for a batch digest running every 2 days.

---

## What was built: artha-ai.sig v1 (intelligence pipeline)

### storage/models.py + storage/database.py
SQLite database with SQLAlchemy. Source-aware schema — every post has a 
"source" field (reddit/hn/github) so the schema never needs to change when 
new data sources are added. Currently only Reddit is implemented. HN and 
GitHub adapters plug in later without schema changes.

### intelligence/embeddings.py
Uses sentence-transformers (all-MiniLM-L6-v2) to convert post text into 
384-dimensional dense vectors. Embeddings are cached to disk — already-seen 
posts are not re-embedded on repeat runs.

Why all-MiniLM-L6-v2: fast, runs locally, no API cost, good semantic quality 
for short-to-medium text. Does not require GPU.

### intelligence/clustering.py
HDBSCAN clustering over post embeddings.

Why HDBSCAN over K-means:
- No fixed k required — cluster count is determined by the data
- Handles noise naturally (outlier posts get reassigned to nearest cluster)
- Works with varying cluster densities — some pain themes are widespread, 
  some are niche
- K-means forces every point into a cluster even if it does not belong

Cluster labels are generated using TF-IDF on post bodies — top 3 distinctive 
terms per cluster joined as a label. This is deliberately not LLM-generated: 
TF-IDF labels are fast, deterministic, and do not require an API call.

### intelligence/scoring.py
Four scoring functions:
1. intensity_score — 0-1 score per post based on upvotes, comments, 
   frustration keyword density
2. quote_quality_score — 0-1 score per sentence based on specificity 
   (length), tool mentions, frustration language
3. extract_workarounds — regex patterns that detect "I currently use X 
   instead / my workaround is" sentences. These are high-signal: they confirm 
   pain is real AND reveal what solution bar the market has already accepted
4. extract_tool_rejections — detects "I tried X but it failed because" 
   patterns. Reveals existing solutions and their specific failure modes

### intelligence/report.py
Converts a cluster of posts into an Evidence Pack — a structured dict with:
- Signal summary (label, frequency, intensity, evidence quality)
- Top ranked quotes (verbatim, with source links)
- Workaround patterns (what people do instead)
- Tool rejections (what people tried and why it failed)
- Detected persona (rule-based: indie builder / ml engineer / researcher etc)
- Reachable communities (where to find these people)

Key design principle: artha-ai.sig presents evidence, never renders verdicts. 
The output says "here is what people are struggling with and what they have 
tried." It does not say "build this startup" or "this is a good opportunity." 
That judgment belongs to the human reading it.

### api/main.py
FastAPI backend with three endpoints:
- POST /scan — triggers pipeline run in background, returns scan_id
- GET /report/{scan_id} — returns evidence pack JSON when ready
- GET /communities — returns seeded community list

### ui/app.py
Streamlit frontend with three modes:
- Run New Scan — triggers API, polls for completion, displays evidence packs
- Load Existing Report — browse past scan results
- Browse Raw Signals — filter/sort the CSV with score and subreddit filters

---

## The optimization objective (added 2026-05-17)

Every solution must clear one bar:

**Does a fully-solving, zero-friction version of this exist for AI/ML builders?**

Not "does something like this exist" — something always exists. The question is whether existing solutions require accounts, complex setup, or solve a slightly different problem. This bar is what differentiates artha-ai.sig from a curated list or ideas repo.

Gap verification is mandatory before any signal is listed as `open`. Enforced at three layers:
1. `track.py --claim` checks SIGNALS.md for a "Gap verification" section — exits with error if missing
2. SIGNALS.md template requires a completed Gap verification section
3. PR template has a mandatory checkbox for it

Two signals were superseded on this basis (2026-05-17):
- SIGNAL-003 (citation hallucination): BibTeX Verifier, RefChecker, CheckIfExist all fully solve it with zero setup
- SIGNAL-007 (RAM vs GPU tradeoffs): LLMfit.io (497 models), LocalLLM.in (within 5% accuracy) fully solve it

---

## What was built: rag-eval-starter (first solution sprint)

Located at: solutions/rag-eval-starter/

This is the first solution built from an artha-ai.sig pain signal.

Signal source: r/LocalLLaMA post — "Evaluated a RAG chatbot and the most 
expensive model was the worst performer. Notes on what actually moved the 
needle." 22 upvotes, 27 comments. The thread confirmed this is a widely 
shared experience: builders pick expensive models assuming cost = quality. 
The real performance drivers are chunk size and retrieval strategy.

### What it builds

A tool that lets any builder test multiple RAG configurations on their own 
documents and see which one actually performs best — with reproducible metrics.

Three entry points:
1. python eval.py — CLI, works in one command with sample data
2. gradio app.py — Gradio web app, upload docs, click Run, see results
3. HuggingFace Spaces — deploy app.py to HF Spaces for public discovery

### Architecture

eval_core.py — all evaluation logic (shared by CLI and Gradio)
eval.py — thin CLI wrapper around eval_core
app.py — Gradio UI wrapper around eval_core

This separation matters: the logic lives in one place. The CLI and Gradio 
app are just different interfaces to the same functions. If the evaluation 
logic changes, it changes once.

### Technical decisions

**Why FAISS over Chroma/Pinecone/Weaviate:**
FAISS runs entirely locally. No account, no API key, no infrastructure. 
The target user is a solo builder. Every additional setup step loses users 
before they see value.

**Why RAGAS for scoring:**
Open-source, most widely referenced evaluation framework in AI/ML communities. 
Lower adoption friction than DeepEval or LangSmith for the target user.

**Why two chunk sizes (256 and 512):**
One configuration teaches nothing. Two configurations with a clear size 
difference force the output to be comparative. The comparison is the insight.

**Why gpt-4o-mini as the evaluator model in RAGAS:**
RAGAS uses LLM-as-judge. Using gpt-4o-mini as the evaluator keeps costs low 
and avoids a confound where the same model evaluates its own answers. In a 
production eval setup you would use a stronger, separate evaluator.

**Why Gradio over Streamlit:**
HuggingFace Spaces runs Gradio apps for free and has organic discovery built 
in. Developers browse Spaces specifically looking for tools. Streamlit has no 
equivalent distribution channel for this audience.

**Known limitation of RAGAS scores:**
RAGAS is LLM-as-judge. Two runs of the same configuration can produce slightly 
different scores. Scores correlate with human judgment but are not ground 
truth. This is documented in the notebook and README — the tool is honest 
about its own limitations.

### PM artifacts included

Every solution sprint produces four artifacts alongside the code:
- problem.md — what pain, who has it, where the signal came from, why 
  existing tools don't solve it
- prd.md — what's in scope, what's deliberately excluded, success criteria
- eval_plan.md — how we know the solution actually works
- CONTEXT.md — every technical decision, tradeoff, what could break, 
  what comes next

These exist because the goal is not just to ship code. The goal is to 
demonstrate product thinking alongside technical execution.

---

## Key architectural decisions across the whole project

**Source-aware schema from day one:**
The Post model has a "source" field even though only Reddit is implemented. 
This costs nothing now and prevents painful refactoring when HN or GitHub 
adapters are added. The schema is designed for the future without building 
the future prematurely.

**No LLM in the clustering pipeline:**
Cluster labels come from TF-IDF, not GPT. This is deliberate. The clustering 
pipeline runs on a schedule, potentially processing hundreds of posts. LLM 
calls at that scale add cost, latency, and an external dependency. TF-IDF 
labels are fast, free, and deterministic. They are human-refinable later.

**Batch jobs, not real-time:**
The scraper runs every 2 days. The intelligence pipeline runs on demand. 
Nothing is real-time. This keeps the system simple and within Reddit's 
rate limits. Real-time would require a message queue, connection pooling, 
and infrastructure that adds zero product value at this stage.

**APScheduler over Celery:**
Celery requires Redis, a worker process, and operational overhead. 
APScheduler is a Python library that runs in-process. For a tool that 
runs batch jobs every 2 days, Celery is engineering theatre. APScheduler 
is the right tool.

**SQLite over Postgres:**
SQLite handles millions of rows. It requires zero infrastructure. It runs 
on the same machine as everything else. There is no concurrent write load 
that would require Postgres. Migrating later is straightforward. Starting 
with Postgres would be premature optimisation.

---

## What was built: rag-eval-starter — multi-provider upgrade (2026-05-17)

rag-eval-starter was upgraded from OpenAI-only to four providers: OpenAI, Anthropic, Google Gemini, Groq.

### Architecture change

Added `get_llm(model_name, api_keys)` and `get_embeddings(api_keys)` factory functions in eval_core.py. A `PROVIDER_MODELS` dict maps provider → model list. A reverse `MODEL_PROVIDER` dict maps model → provider for the factory dispatch. All evaluation functions now accept `api_keys: dict` instead of a bare API key string.

Why this pattern: lazy imports per provider avoid ImportError when a provider's package is not installed or no key is provided. Only the selected provider's library is imported at runtime.

Gradio UI: four accordions (OpenAI open by default, others collapsed). Each has its own API key input and model CheckboxGroup. Results table includes a "provider" column.

HuggingFace Spaces deployment: sdk_version 5.9.1 in README YAML frontmatter. Gradio 4.x was incompatible with Python 3.13 (audioop removed) and newer huggingface_hub (HfFolder removed). Gradio 5 fixed both.

---

## What was built: paper-repro-auditor — SIGNAL-002 (2026-05-17)

Located at: solutions/paper-repro-auditor/

**Signal:** r/MachineLearning — PhD student follows paper setup, cannot hit reported numbers. Gap was a single undocumented preprocessing step. This is the norm, not the exception. 94 upvotes, 53 comments.

**Gap:** Papers With Code tracks availability, not practitioner-side reproduction gaps. NeurIPS checklists are for authors. Nothing takes two configs and outputs ranked risk factors.

**What it does:** CLI tool (interactive or JSON file mode). Compares paper config vs your config across 10 risk dimensions: random seed, data splits, normalization, metric computation, augmentation, checkpoint selection, optimizer + LR schedule, batch size, training duration, hardware/library versions. Outputs HIGH/MEDIUM/LOW per dimension, sorted by risk score, with fix-these-first list. Zero dependencies, pure Python.

**Key design decision:** Vague paper descriptions ("standard settings", "default") automatically score MEDIUM risk. Completely undocumented settings score HIGH. Exact matches score LOW = 0. Scoring is heuristic, not learned — intentional, keeps the tool zero-dependency.

**Known limitation:** Tool is only as good as the user's ability to extract config from the paper. Heavily underreported papers produce many "not stated → HIGH" flags, which is accurate but not specific.

---

## What was built: finetune-failure-extractor — SIGNAL-005 (2026-05-17)

Located at: solutions/finetune-failure-extractor/

**Signal:** r/LocalLLaMA — practitioners fine-tuning small models on verifiable tasks (math, code, reasoning) re-train blindly because they have no way to identify which failure modes repeat. 233 upvotes, 52 comments.

**Gap:** Langfuse does error clustering but requires instrumentation and account setup. W&B tracks metrics but not failure taxonomy. Nothing takes eval output → clusters by failure type → outputs ranked training data manifest.

**What it does:** CLI tool. Reads eval output (CSV, JSON, or JSONL) — needs input, prediction, reference per row, optional error_note. Classifies each error across 7 failure types using regex + keyword matching: wrong operator, off-by-one, missing reasoning step, factual gap, format error, instruction following failure, overconfidence. Outputs ranked manifest: frequency, percentage, examples per type. Training data priority list at bottom. Zero dependencies, pure Python.

**Key design decision:** Pattern matching (not LLM-as-judge) for classification. Deliberate: keeps tool zero-dependency, zero cost, zero latency, fully reproducible. Trade-off: will miss subtle or domain-specific failures. Unclassified bucket catches these for manual review.

**Key design decision:** error_note field in eval output dramatically improves classification accuracy. Teams should add notes during eval review — even short descriptions like "wrong operator" or "hallucination" are enough.

---

## What was built: quant-pareto-bench — SIGNAL-004 (2026-05-17)

Located at: solutions/quant-pareto-bench/

**Signal:** r/LocalLLaMA — builders choose quantization levels (INT4, Q8, F16) based on memory constraints alone, never based on measured quality tradeoffs. The accuracy cost of going smaller is invisible until something breaks in production. 87 upvotes, 41 comments.

**Gap:** GGUF authors publish perplexity numbers but not task-specific accuracy. llama-bench measures tokens/sec only. Nothing takes your prompts + your GGUF files → accuracy vs latency Pareto frontier across quantization levels.

**What it does:** CLI tool. Point at multiple GGUF files of the same model (Q4_K_M, Q8_0, F16, etc.) and provide your prompts with references. Runs each model on every prompt, measures tokens/sec and latency, scores outputs with exact match or gpt-4o-mini as judge. Computes Pareto frontier — which quantization levels are dominated (worse on both axes) and which are worth keeping. Outputs ASCII scatter plot + ranked table. Optional JSON export.

**Key design decision:** Two scoring modes — `exact` (zero dependency, deterministic) and `llm` (gpt-4o-mini, handles natural language). Exact mode is default and free. LLM mode is opt-in for tasks where exact matching would miss semantically correct answers.

**Key design decision:** Pareto frontier, not just ranking. A Q4 model at 90% accuracy and 3x speed is not obviously worse than Q8 at 92% accuracy and 1x speed. The frontier makes the tradeoff explicit and lets the user pick their operating point.

**Known limitation:** llama-cpp-python compiles from source. First-time setup takes 5-15 minutes depending on system. GPU acceleration requires additional compile flags. This is unavoidable given that GGUF loading is the only zero-cost, cross-platform way to benchmark local models.

**Infrastructure note:** CLI-only (no HF Spaces). llama-cpp-python cannot run in a serverless container — it requires the user's local hardware where the GGUF files live. This is the correct architecture: the tool runs where the models are.

---

## What comes next

**Done (Sprint 001, 2026-05-16):**
- rag-eval-starter built and deployed on HuggingFace Spaces
- rag-eval-starter upgraded to 4 providers (OpenAI, Anthropic, Google, Groq)
- Intelligence pipeline (embeddings → HDBSCAN → evidence packs)
- Community infrastructure: CONTRIBUTING.md, CONTRIBUTORS.md, GitHub issue/PR templates

**Done (Sprint 002, 2026-05-17):**
- SIGNAL-002 deployed: paper-repro-auditor (HF Spaces + CLI)
- SIGNAL-004 deployed: quant-pareto-bench (CLI, local GGUF only)
- SIGNAL-005 deployed: finetune-failure-extractor (HF Spaces + CLI)
- SIGNAL-003 and SIGNAL-007 superseded (gap fully closed by existing tools)
- Gap verification enforcement (track.py + SIGNALS.md template + PR template)
- Optimization objective added to README
- Unit tests for all three core modules
- scope.md for all 4 solutions
- solutions/README.md decision guide
- GitHub Actions cron for digest (every 2 days)
- SPRINTS.md sprint log

**Next:**
1. Run digest every 2 days (automated) — review new signals for SIGNAL-008 candidates
2. Post to original Reddit signal threads with tool links (once Reddit account ready)
3. Build SIGNAL-006 (README vs CI config diff) if signal strengthens
4. Add GitHub repo topics: llm, rag, evaluation, fine-tuning, quantization, etc.

The consistency of the loop is the product. One sprint every 2-3 weeks,
maintained over 6-12 months, compounds into a credible public record of
applied AI judgment.
