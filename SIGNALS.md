# SIGNALS — Open Pain Points

This document lists the highest-signal unsolved developer pain points captured by ARTHA's digest.
Every entry traces back to a real community thread with real upvotes and real discussion.

These are not ideas. They are documented problems waiting for tools.

If you want to build a solution for one, read [CONTRIBUTING.md](CONTRIBUTING.md) and claim it in [IDEAS.md](IDEAS.md).

---

## How to read this

Each signal includes:
- **Source** — the original thread (real people, real frustration)
- **The pain** — what people are actually stuck on
- **What exists** — current workarounds and why they fall short
- **What's missing** — the tool gap
- **Signal strength** — upvotes · comments · score (1–3)

---

## ✅ SIGNAL-001 — RAG evaluation: expensive models underperform cheaper ones

**Status:** `deployed` → [rag-eval-starter](solutions/rag-eval-starter/)

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tdusvx/) · 22↑ · 27💬 · score 2

**The pain:**
Builders switch to expensive models (gpt-4o, Claude Opus) when RAG quality is poor, assuming cost = quality. In practice, the bottleneck is almost always retrieval — chunk size, top-k, context quality. Nobody measures this before spending.

**What exists:** Manual testing, intuition, occasional notebooks.

**What was built:** [rag-eval-starter](solutions/rag-eval-starter/) — compare RAG configs across models and providers with RAGAS scores. Live on [HuggingFace Spaces](https://huggingface.co/spaces/SidharthKriplani/rag-eval-starter).

---

## 🔴 SIGNAL-002 — ML paper reproduction: stuck below reported accuracy

**Status:** `open`

**Source:** [r/MachineLearning](https://www.reddit.com/r/MachineLearning/comments/1t4dkew/) · 94↑ · 53💬 · score 3

**The pain:**
A PhD student implements a paper's method, follows the described setup, and cannot hit the reported numbers. The paper says "standard settings." The code repository doesn't exist or is incomplete. Three weeks later, they discover the gap was a single preprocessing step the authors never documented.

This is not a rare experience. It is the norm. The failure is almost never the idea — it is the undocumented gap between what the paper reports and what the paper actually did.

**What exists:** Manual comparison, emailing authors (rarely works), GitHub issues on paper repos.

**What's missing:** A structured reproduction gap auditor — paste the paper's reported config and your config, get a ranked list of high-risk undocumented differences: seed, data splits, normalization, metric computation, augmentation, checkpoint selection strategy.

**Build this:** See [IDEAS.md](IDEAS.md#idea-001)

---

## 🔴 SIGNAL-003 — LLMs hallucinate citations in academic writing

**Status:** `open`

**Source:** [r/MachineLearning](https://www.reddit.com/r/MachineLearning/comments/1t5anla/) · 187↑ · 34💬 · score 2

**The pain:**
Researchers use LLMs to draft or edit academic writing. The LLMs confidently insert citations that look real but are fabricated — wrong authors, wrong years, wrong venues, or entirely nonexistent papers. The hallucinated citations pass casual review because they're formatted correctly.

One commenter: *"5 hallucinated citations of my own papers in the past two months — papers I wrote, citing versions that don't exist."*

**What exists:** Manual verification against Google Scholar, CrossRef. Slow. Easy to miss.

**What's missing:** A `.bib` file auditor — validates every citation against CrossRef/Semantic Scholar, flags unresolvable entries, checks author/year/venue consistency, outputs a confidence score per citation.

**Build this:** See [IDEAS.md](IDEAS.md#idea-002)

---

## 🔴 SIGNAL-004 — Quantization accuracy vs latency tradeoffs are invisible

**Status:** `open`

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tdb4ic/) · 218↑ · 46💬 · score 3

**The pain:**
Builders deploying local LLMs choose quantization levels (FP8, INT4, GPTQ, AWQ) based on memory constraints, not measured quality tradeoffs. There is no standard way to know: "for this model, at this task, what does INT4 actually cost me in accuracy vs what it saves me in latency and memory?"

**What exists:** Benchmarks for specific models published in papers. Not usable for arbitrary model + task combinations.

**What's missing:** A local quantization evaluator — run your model at multiple quantization levels on your own prompts, measure quality degradation and latency/memory savings, output a Pareto frontier so you can make an informed tradeoff decision.

**Note:** Related to [inferencelens](https://github.com/SidharthKriplani/inferencelens) — possible integration or extension.

**Build this:** See [IDEAS.md](IDEAS.md#idea-003)

---

## 🔴 SIGNAL-005 — Fine-tuning feedback loop has no standard tooling

**Status:** `open`

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tde3m1/) · 233↑ · 52💬 · score 3

**The pain:**
Practitioners fine-tuning small models on verifiable tasks (math, code, reasoning) have no standard way to identify *which specific failure modes* the model keeps repeating, prioritize those in the next training batch, and measure whether a training run actually fixed them. They re-train blindly and hope metrics improve.

**What exists:** Loss curves, eval benchmarks. Neither tells you *what kind of mistake* the model keeps making.

**What's missing:** A failure-mode extractor for fine-tuning — run eval, cluster errors by type (wrong operator, off-by-one, reasoning gap, factual gap), output a ranked failure manifest that can directly feed the next training data selection pass.

**Build this:** See [IDEAS.md](IDEAS.md#idea-004)

---

## 🔴 SIGNAL-006 — Open source CI configs contradict READMEs

**Status:** `open`

**Source:** [r/developersIndia](https://www.reddit.com/r/developersIndia/comments/1ten61r/) · 55↑ · 5💬 · score 2

**The pain:**
New open source contributors follow a project's README to set up their dev environment, spend hours debugging, then discover the CI config uses a completely different setup — different Python version, different test runner, different environment variables. The README is aspirational. The CI is ground truth.

**What exists:** Reading both files manually and comparing.

**What's missing:** A repo health checker — given a GitHub repo URL, diff the README setup instructions against the CI config, flag contradictions, output a "trust score" for the README. Runs in seconds, saves hours.

**Build this:** See [IDEAS.md](IDEAS.md#idea-005)

---

## 🔴 SIGNAL-007 — RAM vs GPU tradeoffs for local LLM inference are guesswork

**Status:** `open`

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tdyf75/) · 57↑ · 72💬 · score 2

**The pain:**
Local LLM users with high RAM but limited VRAM (or vice versa) have no reliable way to predict: "will this model run on my hardware, and at what speed?" They rely on community posts, trial and error, and OOM crashes.

**What exists:** Scattered community threads, rule-of-thumb calculators that don't account for context length or quantization.

**What's missing:** A hardware fit calculator — given model size, quantization, context length, and hardware spec (RAM + VRAM), predict: will it run, where will it run (CPU/GPU/split), and estimated tokens/sec. No install, no download — just a fast offline estimator.

**Build this:** See [IDEAS.md](IDEAS.md#idea-006)

---

## Adding a signal

If you've hit a pain point not listed here:

1. Open an issue titled `[SIGNAL] Your pain in one sentence`
2. Describe: what you were trying to do, what broke, what you tried, what's missing
3. Link to any Reddit/HN/GitHub threads where others describe the same thing

If the signal is real and specific, it gets added here.
