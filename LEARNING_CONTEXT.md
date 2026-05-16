# ARTHA — Full Build Context for Learning

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

## What ARTHA is

ARTHA is an open-source signal intelligence system that:
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

## What was built: ARTHA v0 (digest scraper)

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

## What was built: ARTHA v1 (intelligence pipeline)

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

Key design principle: ARTHA presents evidence, never renders verdicts. 
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

## What was built: rag-eval-starter (first solution sprint)

Located at: solutions/rag-eval-starter/

This is the first solution built from an ARTHA pain signal.

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

## What comes next

1. Install dependencies on local Mac: pip install -r requirements.txt
2. Deploy rag-eval-starter to HuggingFace Spaces
3. Find the original Reddit thread and reply with the tool link (substance 
   first, link only if directly relevant)
4. Run ARTHA scraper again in 2 days, review new signals
5. Pick second pain point, build second solution sprint
6. After 5-6 solutions, create a curated index in solutions/README.md — 
   this becomes the collection repo equivalent to awesome-llm-apps

The consistency of the loop is the product. One sprint every 2-3 weeks, 
maintained over 6-12 months, compounds into a credible public record of 
applied AI judgment.
