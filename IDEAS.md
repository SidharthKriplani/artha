# IDEAS — Open Contribution Endpoints

Every idea here is scoped, validated, and ready to build.

Each one traces back to a real community signal in [SIGNALS.md](SIGNALS.md).
The pain is documented. The gap is real. The scope is defined.

**To claim an idea:** Read [CONTRIBUTING.md](CONTRIBUTING.md), then run:
```bash
python3 track.py --claim SIGNAL-XXX --github your-username
```

---

## Open ideas

### IDEA-005 — README vs CI Config Diff Checker

**Signal:** [SIGNAL-006](SIGNALS.md#-signal-006--open-source-ci-configs-contradict-readmes) · 55↑ 5💬 · score 2

**The gap:** New contributors follow READMEs that contradict the actual CI setup, wasting hours debugging environments. No tool specifically diffs what a README *says* against what the CI *does* for the same setup steps.

**What to build:**
A CLI tool that takes a GitHub repo URL and:

- Parses the README for setup instructions (Python version, install commands, test runner, env vars)
- Parses `.github/workflows/` CI configs for the same
- Diffs them and flags contradictions
- Outputs a trust score for the README + a list of specific contradictions

**Stack:** Python, GitHub API (no auth needed for public repos), regex + simple NLP for README parsing.

**Scope:** Read-only. No cloning. Pure API-based analysis.

**Note:** Weak signal (55↑, 5💬) — consider waiting for stronger evidence before claiming. Check SIGNALS.md for the gap verification.

**Success criteria:** Correctly identifies at least 3 real contradictions in 5 popular open source repos known to have README/CI gaps.

---

## Deployed — no longer open for contribution

These ideas have been built. If you want to improve them, open a PR against the existing solution.

| Idea | Signal | Solution | Status |
|---|---|---|---|
| Paper Reproduction Gap Auditor | [SIGNAL-002](SIGNALS.md#-signal-002--ml-paper-reproduction-stuck-below-reported-accuracy) | [paper-repro-auditor](solutions/paper-repro-auditor/) | ✅ deployed |
| Local Quantization Pareto Evaluator | [SIGNAL-004](SIGNALS.md#-signal-004--quantization-accuracy-vs-latency-tradeoffs-are-invisible) | [quant-pareto-bench](solutions/quant-pareto-bench/) | ✅ deployed |
| Fine-Tuning Failure Mode Extractor | [SIGNAL-005](SIGNALS.md#-signal-005--fine-tuning-feedback-loop-has-no-standard-tooling) | [finetune-failure-extractor](solutions/finetune-failure-extractor/) | ✅ deployed |
| RAG Evaluation Starter | [SIGNAL-001](SIGNALS.md#-signal-001--rag-evaluation-expensive-models-underperform-cheaper-ones) | [rag-eval-starter](solutions/rag-eval-starter/) | ✅ deployed |

## Superseded — gap already closed

These ideas were investigated but existing tools fully solve them. No build needed.

| Idea | Signal | Why superseded |
|---|---|---|
| BibTeX Citation Hallucination Auditor | [SIGNAL-003](SIGNALS.md#-signal-003--llms-hallucinate-citations-in-academic-writing) | BibTeX Verifier, RefChecker, CheckIfExist all solve this with zero setup |
| Local LLM Hardware Fit Calculator | [SIGNAL-007](SIGNALS.md#-signal-007--ram-vs-gpu-tradeoffs-for-local-llm-inference-are-guesswork) | LLMfit.io (497 models), LocalLLM.in (within 5% accuracy) fully solve this |

---

## Proposing a new idea

Have a pain point that's not listed here?

1. Check [SIGNALS.md](SIGNALS.md) — is there already a signal for it?
2. If yes, open an issue: `[IDEA] Solution for SIGNAL-XXX`
3. If no, open an issue: `[SIGNAL] Your pain in one sentence` — document the evidence first

Ideas without evidence don't get added. That's the whole point.
