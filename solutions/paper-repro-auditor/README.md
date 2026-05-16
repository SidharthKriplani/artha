# paper-repro-auditor

**ARTHA solution for [SIGNAL-002](../../SIGNALS.md#signal-002)**

Paste the paper's reported config and your config. Get a ranked list of reproduction risk factors — sorted by how likely each gap is to explain missing accuracy.

Zero dependencies. Zero setup. Runs in one command.

---

## Quick start

```bash
# Interactive mode — guided prompts
python audit.py

# JSON file mode
python audit.py --paper examples/resnet_paper.json --yours examples/resnet_mine.json

# Machine-readable output
python audit.py --paper examples/resnet_paper.json --yours examples/resnet_mine.json --json
```

No pip install needed. Python 3.10+.

---

## What it checks

| Factor | Why it matters |
|---|---|
| Random Seed | Uncontrolled seeds → ±3–8% variance |
| Data Splits | Leakage / different strategy → inflated results |
| Normalization | Fit-on-all vs fit-on-train is silent leakage |
| Metric Computation | Macro vs micro F1 → 5–15% swing on imbalanced data |
| Augmentation | Often omitted from paper descriptions |
| Checkpoint Selection | Best-val vs last-epoch → 2–6% difference |
| Optimizer & LR Schedule | Warmup, weight decay rarely spelled out |
| Batch Size | Effective batch = batch × accumulation × gpus |
| Training Duration | "Until convergence" ≠ reproducible |
| Hardware / Library | Float precision, cuDNN determinism |

---

## Output example

```
============================================================
  REPRODUCTION GAP REPORT
  Overall risk: HIGH
  HIGH: 3  MEDIUM: 4  LOW: 3
============================================================

 1. [HIGH  ]  Random Seed / Reproducibility  (score 10/10)
    Paper : not stated
    Yours : 42
    Paper does not report this clearly. You cannot know whether your setting matches.
    💡 Uncontrolled seeds cause ±3–8% accuracy variance on many benchmarks.

 2. [HIGH  ]  Checkpoint Selection  (score 8/10)
    Paper : best val accuracy
    Yours : last epoch
    Mismatch: paper reports 'best val accuracy', you used 'last epoch'.
    💡 Best-val vs last-epoch can differ by 2–6%.
...
```

---

## JSON config format

Both `--paper` and `--yours` accept a JSON file with any subset of these keys:

```json
{
  "random_seed": "42",
  "data_splits": "80/10/10 random",
  "normalization": "mean/std ImageNet values",
  "metric_computation": "top-1 accuracy, best epoch",
  "augmentation": "random crop + horizontal flip",
  "checkpoint_selection": "best val accuracy",
  "optimizer": "SGD lr=0.1 momentum=0.9 cosine decay",
  "batch_size": "256",
  "train_duration": "90 epochs",
  "hardware_env": "V100 32GB PyTorch 1.8"
}
```

Missing keys default to `"not stated"` → flagged as HIGH risk.

---

## Files

```
paper-repro-auditor/
├── audit.py          # CLI entry point
├── core.py           # gap analysis logic
├── risk_factors.py   # factor definitions and weights
├── examples/
│   ├── resnet_paper.json
│   └── resnet_mine.json
├── problem.md
└── README.md
```

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md). This solution addresses [SIGNAL-002](../../SIGNALS.md#signal-002).

Obvious extensions: PDF auto-extraction, web UI, additional risk factors (loss function, class weighting, evaluation protocol).
