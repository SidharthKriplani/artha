# Scope & Compatibility — quant-pareto-bench

---

## Who it's for

| Dimension | Detail |
|---|---|
| **Skill level** | Intermediate. You need to know what GGUF is and have llama.cpp or llama-cpp-python experience. |
| **Role** | Local LLM builders (r/LocalLLaMA audience) who already have GGUF files and want to know the real accuracy cost of quantization on *their* task — not a generic benchmark. |
| **Use case** | One-time decision support: "should I use Q4_K_M or Q8_0 for my specific prompts?" Run once per model family, per task type. |
| **Not for** | Academic benchmarking on standard datasets, cloud API comparison, or continuous performance monitoring. |

---

## Scale

| Dimension | Comfortable range | Hard limit |
|---|---|---|
| Models compared per run | 2–6 GGUF files | No hard limit; memory is the constraint |
| Prompts per run | 5–50 | No hard limit; runtime scales linearly |
| Model size | 1B–13B parameters on CPU | 70B+ requires GPU offload or very high RAM |
| Tokens per response | 64–256 (recommended) | Up to context window |
| Run time | 2–30 min depending on model size and prompt count | — |

---

## Environment

| Dimension | Status |
|---|---|
| **Mac (Intel)** | ✅ CPU mode tested |
| **Mac (Apple Silicon)** | ✅ Metal GPU offload supported — `CMAKE_ARGS="-DLLAMA_METAL=on"` |
| **Linux** | ✅ CPU + CUDA supported — `CMAKE_ARGS="-DLLAMA_CUDA=on"` |
| **Windows** | ⚠️ llama-cpp-python requires MSVC; more complex setup |
| **Python version** | 3.10+ required |
| **GPU** | Optional — CPU mode works, GPU significantly faster |
| **Internet** | Not required after install |
| **API keys** | None for exact match mode. OpenAI key needed for `--mode llm` only. |
| **Disk** | GGUF files (1–10GB each) must be present locally |
| **RAM** | ~2× model file size minimum (e.g. 4GB GGUF needs ~8GB RAM) |

**Dependencies:** `llama-cpp-python` (compiles from source — requires cmake + C++ compiler).

---

## What it covers

- Any GGUF format model: Q2_K, Q3_K_M, Q4_0, Q4_K_M, Q5_K_M, Q6_K, Q8_0, F16
- Two accuracy scoring modes:
  - `--mode exact` — no API key, works for math/factual/classification tasks
  - `--mode llm` — gpt-4o-mini as judge, works for open-ended prompts
- Custom prompts via CSV (`--prompts`) or 10 built-in factual Q&A samples
- Pareto frontier: which quantization levels dominate, which are optimal
- ASCII scatter plot of speed vs accuracy
- Ranked recommendation: best for speed, best for accuracy
- JSON export (`--save`, `--json`) for downstream plotting

---

## What it doesn't cover

- **Non-GGUF formats:** HuggingFace safetensors, GPTQ, AWQ, EXL2, ONNX
- **Cloud APIs:** OpenAI, Anthropic, Google — local GGUF inference only
- **Multi-turn / chat:** single prompt→response per eval — no conversation context
- **Automatic model download:** you must have the GGUF files on disk before running
- **Statistical averaging:** single run per model — no multi-seed averaging or confidence intervals
- **Perplexity measurement:** use llama.cpp's built-in perplexity mode for that

---

## Known limitations

- Cold-start model loading time is included in latency measurements — first prompt is slower
- Exact match scoring is too strict for open-ended prompts; use `--mode llm` for those
- LLM judge mode (gpt-4o-mini) adds cost (~$0.001–0.01 per run) and an external dependency
- Models are loaded and unloaded sequentially — total runtime = sum of all model runtimes
- llama-cpp-python compilation fails on some Windows setups without full MSVC toolchain
- Quantization label is inferred from filename — use standard naming (e.g. `model-Q4_K_M.gguf`) for correct detection
