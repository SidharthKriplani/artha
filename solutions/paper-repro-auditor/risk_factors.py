"""
Risk factor definitions for paper reproduction gap analysis.
Each factor has: key, label, description, questions for paper vs your config.
"""

RISK_FACTORS = [
    {
        "key": "random_seed",
        "label": "Random Seed / Reproducibility",
        "weight": 10,
        "paper_question": "What random seed(s) does the paper report? (e.g. 42, 'not stated', '3 runs avg')",
        "your_question": "What seed did you use?",
        "hint": "Uncontrolled seeds cause ±3–8% accuracy variance on many benchmarks.",
    },
    {
        "key": "data_splits",
        "label": "Data Splits",
        "weight": 10,
        "paper_question": "How does the paper split data? (e.g. '80/10/10 random', 'official splits', 'k-fold=5')",
        "your_question": "How did you split your data?",
        "hint": "Leakage or different split strategy is the #1 source of inflated results.",
    },
    {
        "key": "normalization",
        "label": "Normalization / Preprocessing",
        "weight": 9,
        "paper_question": "What normalization does the paper describe? (mean/std values, min-max, none, 'standard')",
        "your_question": "What normalization did you apply?",
        "hint": "Fit-on-train vs fit-on-all is a silent leakage bug. Missing steps are rarely documented.",
    },
    {
        "key": "metric_computation",
        "label": "Metric Computation",
        "weight": 9,
        "paper_question": "How is the metric computed? (e.g. macro-F1, micro-F1, accuracy, 'best epoch', 'last epoch')",
        "your_question": "How did you compute the metric?",
        "hint": "Macro vs micro F1 alone can swing 5–15% on imbalanced datasets.",
    },
    {
        "key": "augmentation",
        "label": "Data Augmentation",
        "weight": 7,
        "paper_question": "What augmentation does the paper use? (e.g. 'random crop+flip', 'mixup α=0.2', 'none', 'not stated')",
        "your_question": "What augmentation did you apply?",
        "hint": "Authors often omit augmentation details or list them in appendices.",
    },
    {
        "key": "checkpoint_selection",
        "label": "Checkpoint Selection",
        "weight": 8,
        "paper_question": "How does the paper pick the reported checkpoint? (e.g. 'best val loss', 'epoch 50', 'early stopping patience=10')",
        "your_question": "How did you select your checkpoint?",
        "hint": "Best-val vs last-epoch can differ by 2–6% — and authors sometimes report whichever is higher.",
    },
    {
        "key": "optimizer",
        "label": "Optimizer & LR Schedule",
        "weight": 8,
        "paper_question": "What optimizer and LR schedule does the paper use? (e.g. 'Adam lr=1e-4, cosine decay', 'SGD momentum=0.9, step LR')",
        "your_question": "What optimizer and schedule did you use?",
        "hint": "Warmup steps, weight decay, and LR schedule are routinely omitted from paper descriptions.",
    },
    {
        "key": "batch_size",
        "label": "Batch Size & Gradient Accumulation",
        "weight": 6,
        "paper_question": "What batch size does the paper use? (e.g. '256', '32 × 8 GPUs', 'not stated')",
        "your_question": "What batch size did you use?",
        "hint": "Effective batch size = batch × accumulation steps × num_gpus. Papers rarely spell this out.",
    },
    {
        "key": "train_duration",
        "label": "Training Duration",
        "weight": 5,
        "paper_question": "How long does the paper train? (e.g. '100 epochs', '10k steps', 'until convergence')",
        "your_question": "How long did you train?",
        "hint": "'Until convergence' is not a reproducible stopping criterion.",
    },
    {
        "key": "hardware_env",
        "label": "Hardware / Library Versions",
        "weight": 4,
        "paper_question": "What hardware/framework does the paper report? (e.g. 'V100 32GB, PyTorch 1.9', 'not stated')",
        "your_question": "What hardware/framework did you use?",
        "hint": "Float precision, cuDNN determinism, and library versions cause silent numerical differences.",
    },
]
