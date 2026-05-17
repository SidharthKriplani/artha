# SIGNALS — Open Pain Points

This document lists the highest-signal developer pain points captured by artha-ai.sig's digest.
Every entry traces back to a real community thread with real upvotes and real discussion.

These are not ideas. They are documented problems waiting for tools.

**Before listing any signal as open, gap verification is mandatory.** See the template below.

If you want to build a solution for one, read [CONTRIBUTING.md](CONTRIBUTING.md) and claim it in [IDEAS.md](IDEAS.md).

---

## How to read this

Each signal includes:
- **Source** — the original thread (real people, real frustration)
- **The pain** — what people are actually stuck on
- **Gap verification** — what was searched, what was found, why the gap is real or closed
- **What's missing** — the specific tool gap (only if verified open)
- **Signal strength** — upvotes · comments · score (1–3)

Status legend: `open` · `claimed` · `building` · `deployed` · `superseded` (gap closed by existing tool) · `parked` (deprioritized)

---

## ✅ SIGNAL-001 — RAG evaluation: expensive models underperform cheaper ones

**Status:** `deployed` → [rag-eval-starter](solutions/rag-eval-starter/)

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tdusvx/) · 22↑ · 27💬 · score 2

**The pain:**
Builders switch to expensive models when RAG quality is poor, assuming cost = quality. The bottleneck is almost always retrieval — chunk size, top-k, context quality. Nobody measures this before spending.

**Gap verification** (searched: 2026-05-16)
- RAGAS quickstart exists but is single-provider and doesn't surface retrieval parameters as the primary variable
- Existing notebooks (Pinecone, NVIDIA AI Blueprints) are single-provider, require infra setup
- Arize Phoenix is self-hosted and observability-first — not a config comparison tool
- No existing tool does multi-provider RAG config comparison with retrieval parameter sweeps in a Gradio app, zero infra
- **Conclusion: gap is real but narrow. Differentiator is multi-provider + chunk size as variable + HF Spaces deployment.**

**What was built:** [rag-eval-starter](solutions/rag-eval-starter/) — compare RAG configs across OpenAI, Anthropic, Gemini, and Groq. Live on [HuggingFace Spaces](https://huggingface.co/spaces/SidharthKriplani/rag-eval-starter).

---

## ✅ SIGNAL-002 — ML paper reproduction: stuck below reported accuracy

**Status:** `deployed` → [paper-repro-auditor](solutions/paper-repro-auditor/)

**Source:** [r/MachineLearning](https://www.reddit.com/r/MachineLearning/comments/1t4dkew/) · 94↑ · 53💬 · score 3

**The pain:**
A PhD student implements a paper's method, follows the described setup, and cannot hit the reported numbers. The paper says "standard settings." Three weeks later, they discover the gap was a single preprocessing step the authors never documented. This is not rare — it is the norm.

**Gap verification** (searched: 2026-05-17)
- Papers With Code tracks code availability but doesn't audit gaps between your setup and the paper's
- NeurIPS reproducibility checklists are for paper *authors*, not practitioners trying to reproduce
- No tool takes two configs (paper's reported + yours) and outputs ranked reproduction risk factors
- **Conclusion: gap is real. Nothing exists for structured practitioner-side reproduction gap analysis.**

**What was built:** [paper-repro-auditor](solutions/paper-repro-auditor/) — paste paper config + your config, get ranked reproduction risk factors across 10 dimensions. Zero dependencies, pure Python.

---

## ⬛ SIGNAL-003 — LLMs hallucinate citations in academic writing

**Status:** `superseded` — gap closed by existing tools

**Source:** [r/MachineLearning](https://www.reddit.com/r/MachineLearning/comments/1t5anla/) · 187↑ · 34💬 · score 2

**Gap verification** (searched: 2026-05-17)
- **BibTeX Verifier** — 100% in-browser, CrossRef + Semantic Scholar, flags wrong authors/years/venues, exports corrected BibTeX. Zero setup.
- **RefChecker** — validates against CrossRef, Semantic Scholar, OpenAlex, DBLP, ACL Anthology. Free.
- **CheckIfExist** — multi-source validation, batch BibTeX processing, instant results.
- **Conclusion: gap is closed. Multiple zero-friction tools fully solve this. Do not build.**

---

## ✅ SIGNAL-004 — Quantization accuracy vs latency tradeoffs are invisible

**Status:** `deployed` → [quant-pareto-bench](solutions/quant-pareto-bench/)

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tdb4ic/) · 218↑ · 46💬 · score 3

**The pain:**
Builders choose quantization levels (FP8, INT4, GPTQ, AWQ) based on memory constraints, not measured quality tradeoffs. No standard way to know: "for this model, at this task, what does INT4 actually cost me in accuracy vs what it saves me in latency and memory?"

**Gap verification** (searched: 2026-05-17)
- LLM Quant Bench (gguf-bench.com) measures quantization accuracy cost — but for specific models on fixed benchmarks only
- No tool lets you bring your own prompts and your own model and get a Pareto frontier across quantization levels
- **Conclusion: gap is real but narrow. Own-prompt, own-model quantization comparison has no existing tool.**

**What was built:** [quant-pareto-bench](solutions/quant-pareto-bench/) — bring your own GGUF files + prompts, get tokens/sec, accuracy, and a Pareto frontier across quantization levels. Exact match or LLM judge scoring. ASCII scatter plot. Runs on CPU.

---

## ✅ SIGNAL-005 — Fine-tuning feedback loop has no standard tooling

**Status:** `deployed` → [finetune-failure-extractor](solutions/finetune-failure-extractor/)

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tde3m1/) · 233↑ · 52💬 · score 3

**The pain:**
Practitioners fine-tuning small models on verifiable tasks (math, code, reasoning) have no way to identify which specific failure modes the model keeps repeating, prioritize those in the next training batch, and measure whether a run fixed them. They re-train blindly and hope metrics improve.

**Gap verification** (searched: 2026-05-17)
- Langfuse does error clustering but requires instrumentation, account setup, observability infrastructure
- Weights & Biases tracks training metrics but not failure mode taxonomy
- No tool takes eval output → clusters errors by failure type → outputs a ranked manifest for next training data selection
- **Conclusion: gap is real. No zero-friction practitioner-side failure mode extractor exists.**

**What was built:** [finetune-failure-extractor](solutions/finetune-failure-extractor/) — reads eval output (CSV/JSON/JSONL), classifies errors into 7 failure types, outputs a ranked manifest for next training data selection. Zero dependencies, pure Python.

---

## 🔴 SIGNAL-006 — Open source CI configs contradict READMEs

**Status:** `open`

**Source:** [r/developersIndia](https://www.reddit.com/r/developersIndia/comments/1ten61r/) · 55↑ · 5💬 · score 2

**The pain:**
New contributors follow a project's README to set up their dev environment, spend hours debugging, then discover the CI config uses a completely different setup — different Python version, different test runner, different env vars. The README is aspirational. The CI is ground truth.

**Gap verification** (searched: 2026-05-17)
- RepoHealth runs 33 checks on docs + CI quality — but checks *presence*, not *contradictions between them*
- GitGroomer, Repo Doctor check README quality against community standards — not README vs CI diff
- No tool specifically diffs what a README *says* against what the CI *does* for the same setup steps
- **Conclusion: gap is real but weak signal (55↑ 5💬). Build only after higher-priority signals are deployed.**

**Build this:** See [IDEAS.md](IDEAS.md#idea-005)

---

## ⬛ SIGNAL-007 — RAM vs GPU tradeoffs for local LLM inference are guesswork

**Status:** `superseded` — gap closed by existing tools

**Source:** [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1tdyf75/) · 57↑ · 72💬 · score 2

**Gap verification** (searched: 2026-05-17)
- **LLMfit.io** — 497 models, 133 providers, VRAM fit check + tokens/sec estimate, NVIDIA/Apple Silicon/AMD, zero install
- **LocalLLM.in** — empirically-tested formulas within 5% of actual VRAM usage, covers 2025 models (Llama 4, DeepSeek-R1, Qwen3)
- **Overchat.ai** — GPU + CPU offload simulation
- **Conclusion: gap is fully closed. Multiple zero-friction tools solve this completely. Do not build.**

---

## Signal template — mandatory for all new entries

When adding a new signal, copy this template. A signal cannot be listed as `open` without a completed gap verification section.

```markdown
## 🔴 SIGNAL-XXX — [Pain in one sentence]

**Status:** `open`

**Source:** [r/subreddit](url) · ↑ · 💬 · score

**The pain:**
[2-3 sentences. What the person was trying to do, what broke, what it cost them.]

**Gap verification** (searched: YYYY-MM-DD)
- [Tool name] — [what it does and why it doesn't fully solve this]
- [Tool name] — [what it does and why it doesn't fully solve this]
- **Conclusion: gap is real / gap is closed. [One sentence reason.]**

**What's missing:** [Only include if gap is real. Specific tool description.]

**Build this:** See [IDEAS.md](IDEAS.md#idea-XXX)
```

---

## Adding a signal

1. Open an issue titled `[SIGNAL] Your pain in one sentence`
2. Describe: what you were trying to do, what broke, what you tried, what's missing
3. Link to community threads — Reddit, HN, GitHub issues, Stack Overflow
4. **Search for existing solutions first.** Document what you found and why the gap is still real.

Signals without community evidence and gap verification do not get added.
