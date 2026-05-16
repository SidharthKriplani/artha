# Scope & Compatibility — finetune-failure-extractor

---

## Who it's for

| Dimension | Detail |
|---|---|
| **Skill level** | Intermediate. You need to have run an eval loop and have its output in a file. |
| **Role** | ML engineers and researchers fine-tuning small models on verifiable tasks: math, factual Q&A, classification, structured output, reasoning chains. |
| **Use case** | After each eval run — before deciding what training data to add next. Feed the output here, get a ranked manifest of failure types, prioritize accordingly. |
| **Not for** | Open-ended generation quality (summarization, creative writing), real-time model monitoring, or tasks where multiple valid answers exist. |

---

## Scale

| Dimension | Comfortable range | Hard limit |
|---|---|---|
| Eval examples | 20–10,000 rows | No hard limit; tested up to ~5,000 |
| Minimum useful errors | ~20 errors | Below 20 errors, rankings are noisy |
| File size | Up to ~50MB CSV/JSON | No hard limit — loads into memory |
| Failure types detected | 7 built-in | Extensible via `failure_types.py` |
| Run time | < 2 seconds for 1,000 rows | Linear with row count |

---

## Environment

| Dimension | Status |
|---|---|
| **Mac** | ✅ Tested |
| **Linux** | ✅ Tested |
| **Windows** | ✅ Works (pure Python) |
| **Python version** | 3.10+ required |
| **GPU** | Not required |
| **Internet** | Not required |
| **API keys** | None needed |
| **Disk** | ~0 MB extra |
| **RAM** | Negligible for typical eval sizes |

**Zero dependencies.** Pure Python stdlib only.

---

## What it covers

- Input formats: CSV, JSON (list or `{"examples": [...]}` wrapper), JSONL
- Required fields: `input`, `prediction`, `reference`
- Optional field: `error_note` — human annotation that dramatically improves classification accuracy
- 7 failure types: wrong operator/operation, off-by-one/boundary error, missing reasoning step, factual/knowledge gap, format/output structure error, instruction following failure, overconfidence/missing uncertainty
- Unclassified bucket for errors that don't match any pattern
- Ranked output: most frequent failure type first
- Per-type examples with input, prediction, reference
- Training data priority list at the bottom of the report
- JSON export (`--save`, `--json`)

---

## What it doesn't cover

- **Model execution:** does not generate predictions — you must provide eval output
- **Non-English tasks:** patterns are English-only; classification degrades for other languages
- **Open-ended generation:** designed for tasks where `prediction ≠ reference` means incorrect — not for summarization or creative tasks with multiple valid outputs
- **Continuous/float scores:** expects string prediction vs string reference
- **Code generation:** no code-specific failure patterns (syntax errors, off-by-one in loops, etc.) — contributions welcome
- **Statistical significance:** no confidence intervals or significance testing on rankings

---

## Known limitations

- Pattern matching is imperfect — subtle or domain-specific failures go to the Unclassified bucket
- High Unclassified rate is a signal: either add `error_note` to your eval process, or extend `failure_types.py` with domain-specific patterns
- Does not suggest which specific training examples to add — only which failure *type* to prioritize
- Small eval sets (< 50 errors) produce noisy rankings — collect more eval data before acting on the manifest
- A single error can match multiple failure types — it is counted once per type it matches
