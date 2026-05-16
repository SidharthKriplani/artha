# Solutions

Every tool here traces back to a real developer pain point — a Reddit thread with real upvotes and real discussion. Nothing is built on intuition.

---

## Which tool do I need?

**I'm evaluating a RAG pipeline and don't know if my model or my retrieval is the bottleneck**
→ [rag-eval-starter](#rag-eval-starter)

**I implemented a paper and can't hit the reported numbers**
→ [paper-repro-auditor](#paper-repro-auditor)

**I fine-tuned a model and it keeps making the same mistakes but I don't know which ones to fix**
→ [finetune-failure-extractor](#finetune-failure-extractor)

**I have multiple GGUF quantization files and want to know the real accuracy cost of going smaller**
→ [quant-pareto-bench](#quant-pareto-bench)

---

## rag-eval-starter

**Signal:** [SIGNAL-001](../SIGNALS.md#-signal-001--rag-evaluation-expensive-models-underperform-cheaper-ones) — builders switch to expensive models when RAG quality is poor, assuming cost = quality. The bottleneck is almost always retrieval.

**What it does:** Upload your documents. Pick models across OpenAI, Anthropic, Google, and Groq. Run RAGAS evaluation. See which config actually moves the needle — chunk size, model, or provider.

**Zero config:** [Try it live on HuggingFace Spaces](https://huggingface.co/spaces/SidharthKriplani/rag-eval-starter) — no install needed.

| | |
|---|---|
| **Skill level** | Beginner — just need an API key |
| **Setup** | `pip install -r requirements.txt` or use HF Spaces |
| **Who it's for** | Anyone evaluating a RAG stack before committing to a model |

→ [View solution](rag-eval-starter/) · [Scope & limitations](rag-eval-starter/scope.md)

---

## paper-repro-auditor

**Signal:** [SIGNAL-002](../SIGNALS.md#-signal-002--ml-paper-reproduction-stuck-below-reported-accuracy) — PhD students implement papers exactly as described and can't hit reported numbers. The gap is almost always an undocumented preprocessing step.

**What it does:** Fill in the paper's reported config and your config across 10 dimensions. Get a ranked list of HIGH/MEDIUM/LOW reproduction risks — sorted by how likely each gap is to explain the missing accuracy.

**Zero dependencies:** pure Python, no install beyond Python 3.10.

| | |
|---|---|
| **Skill level** | Any — guided prompts or JSON files |
| **Setup** | None — pure Python stdlib |
| **Who it's for** | ML practitioners stuck below a paper's reported numbers |

→ [View solution](paper-repro-auditor/) · [Try it on HF Spaces](https://huggingface.co/spaces/sidharthkriplani/paper-repro-auditor) · [Scope & limitations](paper-repro-auditor/scope.md)

---

## finetune-failure-extractor

**Signal:** [SIGNAL-005](../SIGNALS.md#-signal-005--fine-tuning-feedback-loop-has-no-standard-tooling) — practitioners fine-tune models blindly because they have no structured way to identify which failure modes repeat.

**What it does:** Feed your eval output (CSV, JSON, or JSONL). Get a ranked failure mode manifest: which error types appear most, with examples and a training data priority list at the bottom.

**Zero dependencies:** pure Python, no install beyond Python 3.10.

| | |
|---|---|
| **Skill level** | Intermediate — need an eval output file |
| **Setup** | None — pure Python stdlib |
| **Who it's for** | Anyone fine-tuning small models on verifiable tasks |

→ [View solution](finetune-failure-extractor/) · [Try it on HF Spaces](https://huggingface.co/spaces/sidharthkriplani/finetune-failure-extractor) · [Scope & limitations](finetune-failure-extractor/scope.md)

---

## quant-pareto-bench

**Signal:** [SIGNAL-004](../SIGNALS.md#-signal-004--quantization-accuracy-vs-latency-tradeoffs-are-invisible) — builders choose quantization levels (INT4, Q8, F16) based on memory constraints, not measured quality tradeoffs.

**What it does:** Point at multiple GGUF files of the same model. Provide your prompts. Get tokens/sec, latency, accuracy scores, and a Pareto frontier — which quantization levels are dominated and which are worth keeping.

| | |
|---|---|
| **Skill level** | Intermediate — need GGUF files and llama-cpp-python |
| **Setup** | `pip install llama-cpp-python` (compiles from source) |
| **Who it's for** | Local LLM builders choosing between quantization levels |

→ [View solution](quant-pareto-bench/) · [Scope & limitations](quant-pareto-bench/scope.md)

---

## Contributing a solution

Read [CONTRIBUTING.md](../CONTRIBUTING.md). Pick an open signal from [IDEAS.md](../IDEAS.md). Claim it with `track.py`. Build it. Every solution must include `README.md`, `problem.md`, `scope.md`, and `requirements.txt`.
