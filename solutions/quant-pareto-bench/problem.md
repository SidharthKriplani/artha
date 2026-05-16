# Problem: Quantization Pareto Bench

## What already exists

**LLM Quant Bench (gguf-bench.com)** — measures quantization accuracy cost for specific models on fixed benchmarks. You cannot bring your own prompts or your own model.

**llama.cpp perplexity mode** — measures perplexity on a fixed dataset (wikitext). Not a task-specific accuracy measure. Not user-configurable.

**LLMfit.io / LocalLLM.in** — predict VRAM usage and tokens/sec from model specs. Do not run prompts. Do not measure task-specific accuracy at all.

**Manual benchmarking** — what everyone actually does: download multiple GGUF files, run them one by one, record outputs manually. Unstructured, no Pareto analysis.

## The gap

No tool lets you bring your own prompts (your actual task) and your own model (your specific GGUF), run them across quantization levels, and get a Pareto frontier of accuracy vs latency.

The gap is: **own-prompt, own-model, Pareto-frontier output**. All three together. No existing tool does this.

## What this tool does

Install llama-cpp-python. Point at multiple GGUF files of the same base model (different quantization levels). Provide your prompts (optional: with reference answers). Get: tokens/sec per model, latency per model, accuracy score per model (exact match or LLM judge), Pareto frontier showing which quantization levels are dominated and which are optimal. ASCII scatter plot. Ranked recommendation.

## What it does NOT do

- Does not download models (you must have the GGUF files already)
- Does not support non-GGUF formats (HuggingFace safetensors, GPTQ, AWQ) — those require different loaders
- LLM judge mode requires an OpenAI API key
- Exact match scoring works well for verifiable tasks (math, factual Q&A, code) but not open-ended generation

## Honest assessment

The tool is only as useful as the prompts provided. Built-in sample prompts (factual Q&A) are a starting point. For domain-specific tasks (code generation, medical Q&A, reasoning chains), the user must supply task-appropriate prompts with reference answers to get meaningful accuracy numbers.

llama-cpp-python installation compiles from source. It works on Mac (CPU + Metal) and Linux (CPU + CUDA). Windows requires additional setup. This is the one real friction point — but it is the same friction as using llama.cpp itself, which the target audience (r/LocalLLaMA) has already cleared.
