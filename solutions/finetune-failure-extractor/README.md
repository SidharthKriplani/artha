# finetune-failure-extractor

**ARTHA solution for [SIGNAL-005](../../SIGNALS.md#signal-005)**

Run eval on your fine-tuned model. Feed the output here. Get a ranked failure mode manifest — most frequent failure types first, with examples — ready to drive your next training data selection.

Zero dependencies. Zero setup. One command.

---

## Quick start

```bash
# CSV input
python extract.py --eval examples/math_eval.csv

# JSON or JSONL input
python extract.py --eval results.json

# Show top 3 types only
python extract.py --eval results.csv --top 3

# Save JSON manifest for downstream use
python extract.py --eval results.csv --save manifest.json
```

No pip install. Python 3.10+.

---

## Input format

Your eval output file needs three columns/fields:

| Field | Required | Description |
|---|---|---|
| `input` | yes | The prompt/question |
| `prediction` | yes | What your model output |
| `reference` | yes | The correct answer |
| `error_note` | no | Human note about the error (improves classification) |

**CSV example:**
```csv
input,prediction,reference,error_note
"What is 7 × 8?",54,56,wrong operator - subtracted instead of multiplied
"What is 2^5?",16,32,off by one power
```

**JSON example:**
```json
[
  {"input": "What is 7 × 8?", "prediction": "54", "reference": "56", "error_note": "wrong operator"},
  {"input": "What is 2^5?", "prediction": "16", "reference": "32"}
]
```

Rows where `prediction == reference` are automatically skipped (correct examples).

---

## Failure types detected

| Type | What it catches |
|---|---|
| Wrong Operator | +/−/×/÷ confusion, wrong logic operator |
| Off-by-One | Indexing errors, fencepost, counting off by 1 |
| Missing Reasoning Step | Skipped intermediate step, invalid inference |
| Factual Gap | Wrong fact, hallucination, wrong entity/value |
| Format Error | JSON schema violation, wrong units, missing field |
| Instruction Following | Ignored constraint, answered different question |
| Overconfidence | Should hedge/refuse but gave definitive wrong answer |

Unmatched errors go into an **Unclassified** bucket for manual review.

---

## Output example

```
==============================================================
  FAILURE MODE MANIFEST
  Total examples : 23
  Errors found   : 11  (47.8% error rate)
  Failure types  : 4 distinct modes
==============================================================

  RANKED FAILURE MODES (top 5)

  #1  Wrong Operator / Operation
      ████ 36.4% of errors (4 cases)
      Model uses the wrong math or logic operator
      Example:
        Input     : What is 7 × 8?
        Predicted : 54
        Reference : 56
        Note      : wrong operator - subtracted instead of multiplied

  #2  Factual / Knowledge Gap
      ███ 27.3% of errors (3 cases)
      ...

==============================================================

  TRAINING DATA PRIORITY (next batch)

  1. Wrong Operator — 4 cases, 36.4% of errors
  2. Factual Gap    — 3 cases, 27.3% of errors
  3. Off-by-One     — 2 cases, 18.2% of errors
```

---

## Files

```
finetune-failure-extractor/
├── extract.py          # CLI entry point
├── core.py             # load + classify + rank logic
├── failure_types.py    # failure taxonomy and pattern matching
├── examples/
│   └── math_eval.csv
├── problem.md
└── README.md
```

---

## Extending the taxonomy

Add new failure types in `failure_types.py` — each entry needs `key`, `label`, `description`, `patterns` (regex list), and `keywords` (string list). No other changes needed.

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md). This solution addresses [SIGNAL-005](../../SIGNALS.md#signal-005).
