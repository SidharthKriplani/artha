# quant-pareto-bench

**ARTHA solution for [SIGNAL-004](../../SIGNALS.md#signal-004)**

Benchmark multiple GGUF quantization levels of the same model on **your prompts**. Get tokens/sec, latency, accuracy scores, and a Pareto frontier showing exactly which quantization levels are worth keeping.

---

## Quick start

```bash
pip install llama-cpp-python

# Two GGUF files, built-in sample prompts
python bench.py --models llama-3.2-3b-Q4_K_M.gguf llama-3.2-3b-Q8_0.gguf

# Your own prompts with reference answers
python bench.py \
  --models Q2_K.gguf Q4_K_M.gguf Q8_0.gguf F16.gguf \
  --prompts examples/math_prompts.csv

# LLM judge for open-ended prompts (requires OpenAI key)
python bench.py --models Q4_K_M.gguf Q8_0.gguf --prompts prompts.csv \
  --mode llm --openai-key sk-...

# Apple Silicon — enable Metal for GPU offload
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python
python bench.py --models Q4_K_M.gguf Q8_0.gguf --n-gpu-layers -1

# Save JSON for downstream plotting
python bench.py --models Q4_K_M.gguf Q8_0.gguf --save results.json
```

---

## What it measures

| Metric | How |
|---|---|
| Tokens/sec | Completion tokens ÷ generation time, averaged across prompts |
| Avg latency | Wall-clock time per prompt, averaged |
| Accuracy | Exact match (numeric proximity + word overlap) or LLM judge |
| File size | GGUF file size in MB |
| Pareto-optimal | ★ if no other quant beats it on both speed AND accuracy |

---

## Output example

```
======================================================================
  QUANTIZATION PARETO REPORT
  Models benchmarked : 4
  Accuracy scoring   : yes
======================================================================

  Quant          tok/s    Latency   Accuracy   Size MB  Status
  ------------ -------- ---------- ---------- ---------  --------------
  Q8_0           38.2      820 ms       0.90      4200  ★ Pareto-optimal
  Q4_K_M         61.4      510 ms       0.85      2400  ★ Pareto-optimal
  Q2_K           94.1      330 ms       0.61      1200  dominated
  F16            19.8     1580 ms       0.92      8300  dominated

  RECOMMENDATION
  For max speed    → Q4_K_M (61.4 tok/s)
  For max accuracy → Q8_0 (accuracy 0.90)
```

---

## Prompts CSV format

```csv
prompt,reference
What is 15 × 7?,105
What is the capital of Japan?,Tokyo
Explain gradient descent in one sentence.,
```

- `reference` column is optional. Without it: speed-only report, no accuracy scoring.
- For open-ended prompts without clear references: use `--mode llm` (requires OpenAI key).
- For verifiable tasks (math, code, factual): `--mode exact` works well, no API key needed.

---

## Installation notes

llama-cpp-python compiles from source. Requirements:
- Python 3.10+, pip, cmake, C++ compiler
- Mac: `brew install cmake` if not present
- Linux: `apt install cmake build-essential`

For GPU acceleration:
- Apple Silicon: `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python`
- CUDA: `CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python`

---

## Files

```
quant-pareto-bench/
├── bench.py            # CLI entry point
├── runner.py           # GGUF loading + prompt execution (llama-cpp-python)
├── scorer.py           # exact match + LLM judge scoring
├── pareto.py           # Pareto frontier + ASCII visualization
├── examples/
│   └── math_prompts.csv
├── problem.md
└── README.md
```

---

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md). This solution addresses [SIGNAL-004](../../SIGNALS.md#signal-004).

Obvious extensions: HTML/matplotlib Pareto plot, support for HF transformers + bitsandbytes (INT8/INT4), multi-run averaging for statistical stability.
