# IDEAS — Open Contribution Endpoints

Every idea here is scoped, validated, and ready to build.

Each one traces back to a real community signal in [SIGNALS.md](SIGNALS.md).
The pain is documented. The gap is real. The scope is defined.

**To claim an idea:** Read [CONTRIBUTING.md](CONTRIBUTING.md), then run:
```bash
python3 track.py --claim SIGNAL-XXX --github your-username
```

---

## IDEA-001 — Paper Reproduction Gap Auditor

**Signal:** [SIGNAL-002](SIGNALS.md#-signal-002--ml-paper-reproduction-stuck-below-reported-accuracy) · 94↑ 53💬

**The gap:** No tool helps you systematically identify *why* you can't reproduce a paper's results before wasting GPU hours re-training.

**What to build:**
A CLI tool that takes two configs — the paper's reported setup and yours — and outputs a ranked list of reproduction risk factors:

- Seed and randomness gaps (reported vs your setup)
- Data split strategy (stratified? random? fixed?)
- Normalization constants (hardcoded vs computed?)
- Augmentation pipeline differences
- Metric computation differences (macro/micro F1, top-1 vs top-5, etc.)
- Checkpoint selection (best epoch vs last epoch vs average?)
- Batch size × gradient accumulation equivalence

**Output:** A `ReproductionGapReport` — each gap scored HIGH/MEDIUM/LOW risk, with a one-line explanation of why it matters.

**Stack:** Python, Pydantic, Rich (for terminal output). No GPU required.

**Scope:** CLI only. No training, no model execution. Pure config auditing.

**Success criteria:** Given a real paper + a user's config, the tool catches at least 3 of the 5 most common reproduction failure modes documented in ML reproducibility literature.

---

## IDEA-002 — BibTeX Citation Hallucination Auditor

**Signal:** [SIGNAL-003](SIGNALS.md#-signal-003--llms-hallucinate-citations-in-academic-writing) · 187↑ 34💬

**The gap:** LLMs confidently insert fake citations. Researchers catch them manually — if at all.

**What to build:**
A CLI tool that takes a `.bib` file and validates every citation against CrossRef and Semantic Scholar:

- Does this paper exist?
- Do the authors match?
- Does the year match?
- Does the venue/journal match?
- Is the DOI resolvable?

**Output:** A per-citation `VERIFIED / SUSPICIOUS / NOT_FOUND` report with confidence scores and suggested corrections where possible.

**Stack:** Python, CrossRef API (free), Semantic Scholar API (free). Zero LLM calls needed — pure lookup.

**Scope:** `.bib` input → terminal report + optional JSON output. No GUI.

**Success criteria:** Correctly flags hallucinated citations at >90% precision on a test set of known-hallucinated vs known-real citations.

---

## IDEA-003 — Local Quantization Pareto Evaluator

**Signal:** [SIGNAL-004](SIGNALS.md#-signal-004--quantization-accuracy-vs-latency-tradeoffs-are-invisible) · 218↑ 46💬

**The gap:** Builders pick quantization levels based on memory constraints, not measured quality tradeoffs.

**What to build:**
A tool that runs a local model at multiple quantization levels (FP16, FP8, INT8, INT4) on a user-provided prompt set and outputs:

- Quality score per quantization level (via RAGAS or a simple correctness check)
- Latency (tokens/sec) per level
- Memory footprint per level
- Pareto frontier visualization: quality vs speed vs memory

**Stack:** Python, llama.cpp or Ollama for inference, matplotlib for Pareto plot.

**Scope:** Local models only (no API calls for inference). Evaluation can use a lightweight judge.

**Note:** Possible integration with [inferencelens](https://github.com/SidharthKriplani/inferencelens).

**Success criteria:** Runs end-to-end on at least 3 quantization levels for a 7B model on consumer hardware (16GB RAM).

---

## IDEA-004 — Fine-Tuning Failure Mode Extractor

**Signal:** [SIGNAL-005](SIGNALS.md#-signal-005--fine-tuning-feedback-loop-has-no-standard-tooling) · 233↑ 52💬

**The gap:** After fine-tuning eval, practitioners know their accuracy — but not *what kind* of mistakes the model keeps making.

**What to build:**
A tool that takes model outputs + ground truth, clusters errors by failure type, and outputs a ranked failure manifest:

- Reasoning gaps (model had the right knowledge but wrong logic)
- Factual gaps (model confidently wrong on a fact)
- Format failures (right answer, wrong output format)
- Off-by-one / boundary errors (common in math/code)
- Hallucinated steps (model invents intermediate reasoning)

**Output:** A `FailureManifest` — ranked list of error clusters with representative examples, failure frequency, and suggested data augmentation strategy for the next training pass.

**Stack:** Python, sentence-transformers for clustering, no fine-tuning infra required.

**Scope:** Evaluation output → failure manifest. No training loop integration needed in v1.

---

## IDEA-005 — README vs CI Config Diff Checker

**Signal:** [SIGNAL-006](SIGNALS.md#-signal-006--open-source-ci-configs-contradict-readmes) · 55↑ 5💬

**The gap:** New contributors follow READMEs that contradict the actual CI setup, wasting hours debugging environments.

**What to build:**
A CLI tool that takes a GitHub repo URL and:

- Parses the README for setup instructions (Python version, install commands, test runner, env vars)
- Parses `.github/workflows/` CI configs for the same
- Diffs them and flags contradictions
- Outputs a trust score for the README + a list of specific contradictions

**Stack:** Python, PyGithub or direct GitHub API, regex + simple NLP for README parsing.

**Scope:** Read-only. No cloning. Pure API-based analysis.

**Success criteria:** Correctly identifies at least 3 real contradictions in 5 popular open source repos known to have README/CI gaps.

---

## IDEA-006 — Local LLM Hardware Fit Calculator

**Signal:** [SIGNAL-007](SIGNALS.md#-signal-007--ram-vs-gpu-tradeoffs-for-local-llm-inference-are-guesswork) · 57↑ 72💬

**The gap:** No reliable offline tool tells you whether a model will fit on your hardware and at what speed.

**What to build:**
A fast offline calculator (web app or CLI) that takes:
- Model name or size (in billions of parameters)
- Quantization level (FP16, INT8, INT4, GGUF Q4_K_M, etc.)
- Context length
- Hardware spec (RAM GB + VRAM GB)

And outputs:
- Will it run? (YES / PARTIAL — CPU offload / NO)
- Where will it run? (full GPU / split GPU+CPU / CPU only)
- Estimated tokens/sec range
- Estimated memory usage breakdown

**Stack:** Python or pure HTML/JS (no backend needed — all math). No model downloads.

**Scope:** Estimation only. Based on known formulas for parameter memory + KV cache + activation memory.

**Success criteria:** Estimates within 15% of actual measured memory usage for 5 common model + quantization combinations.

---

## Proposing a new idea

Have a pain point that's not listed here?

1. Check [SIGNALS.md](SIGNALS.md) — is there already a signal for it?
2. If yes, open an issue: `[IDEA] Solution for SIGNAL-XXX`
3. If no, open an issue: `[SIGNAL] Your pain in one sentence` — document the evidence first

Ideas without evidence don't get added. That's the whole point.
