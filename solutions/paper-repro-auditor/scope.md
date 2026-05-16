# Scope & Compatibility — paper-repro-auditor

---

## Who it's for

| Dimension | Detail |
|---|---|
| **Skill level** | Any. If you can read a paper and fill in a form, you can use this. |
| **Role** | ML practitioners, PhD students, researchers, engineers trying to reproduce results from a published paper. |
| **Use case** | One-time diagnostic before starting a reproduction attempt, or after getting stuck below reported numbers. Run it, get a ranked list of what to fix, try again. |
| **Not for** | Automated paper parsing, code-level bug detection, or comparing multiple papers at once. |

---

## Scale

| Dimension | Comfortable range | Hard limit |
|---|---|---|
| Papers per run | 1 | 1 — single paper vs your config |
| Risk dimensions checked | 10 (all) | Fixed set, not configurable |
| Config fields | Any subset of 10 | Missing fields default to "not stated" → HIGH risk |
| Run time | < 1 second | No compute involved |
| Output size | ~50 lines terminal / ~2KB JSON | Negligible |

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
| **RAM** | Negligible |

**Zero dependencies.** Pure Python stdlib only. No install beyond Python itself.

---

## What it covers

- 10 reproduction risk dimensions: random seed, data splits, normalization, metric computation, augmentation, checkpoint selection, optimizer + LR schedule, batch size, training duration, hardware/library versions
- Interactive prompt mode — guided Q&A, no file prep needed
- JSON file mode — paste configs as files, scriptable
- HIGH / MEDIUM / LOW risk scoring per dimension with explanation
- "Fix these first" summary at the end
- Machine-readable JSON output (`--json`)

---

## What it doesn't cover

- **Automatic extraction:** does not read PDFs or parse paper text — you fill in the values manually
- **Code comparison:** only reported configs, not actual implementations
- **Domain-specific steps:** preprocessing steps that aren't in the standard 10 dimensions (e.g. dataset-specific cleaning, custom tokenizers)
- **Multi-paper batch:** one paper vs one config per run
- **Experiment tracking integration:** no W&B, MLflow, or Comet connector

---

## Known limitations

- Scoring is heuristic — not learned from actual reproduction outcome data
- "Not stated" in the paper always flags HIGH: accurate signal, but not specific about what the paper actually used
- Cannot detect implementation bugs — only config-level gaps between what's reported and what you ran
- Papers that report almost nothing ("standard settings throughout") produce mostly HIGH flags with low specificity — the tool is accurate, but the paper is the problem
- Does not rank which of the 10 dimensions matters most for your specific architecture or domain
