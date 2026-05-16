#!/usr/bin/env python3
"""
quant-pareto-bench — CLI entry point

Compare multiple GGUF quantization levels of the same model on your own prompts.
Get accuracy scores, latency, tokens/sec, and a Pareto frontier.

Usage:
  # Minimal: two GGUF files, default sample prompts
  python bench.py --models Q4_K_M.gguf Q8_0.gguf

  # With your own prompts + reference answers
  python bench.py --models Q4_K_M.gguf Q8_0.gguf F16.gguf --prompts prompts.csv

  # LLM judge for open-ended prompts
  python bench.py --models Q4_K_M.gguf Q8_0.gguf --prompts prompts.csv --mode llm --openai-key sk-...

  # JSON output for plotting
  python bench.py --models Q4_K_M.gguf Q8_0.gguf --json

Prompts CSV format:
  prompt,reference
  "What is 7 × 8?",56
  "Name the capital of France.",Paris

If no reference column: accuracy scoring is skipped, speed-only report.
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from runner import run_model, BenchResult
from scorer import score_outputs
from pareto import ModelPoint, print_report

SAMPLE_PROMPTS = [
    ("What is 15 × 7?", "105"),
    ("What is the capital of Japan?", "Tokyo"),
    ("What is 2 to the power of 10?", "1024"),
    ("How many days are in a leap year?", "366"),
    ("What is the square root of 169?", "13"),
]


def load_prompts(path: str) -> tuple[list[str], list[str] | None]:
    """Returns (prompts, references). References is None if no reference column."""
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if not rows:
        raise ValueError(f"Empty prompts file: {path}")
    prompts = [r["prompt"] for r in rows]
    references = [r["reference"] for r in rows] if "reference" in rows[0] else None
    return prompts, references


def get_file_size_mb(path: str) -> float | None:
    try:
        return Path(path).stat().st_size / (1024 * 1024)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark GGUF quantization levels: accuracy vs latency Pareto frontier."
    )
    parser.add_argument("--models", nargs="+", required=True, metavar="GGUF",
                        help="Paths to GGUF files (different quant levels of the same base model)")
    parser.add_argument("--prompts", metavar="CSV",
                        help="CSV with 'prompt' and optional 'reference' columns")
    parser.add_argument("--mode", choices=["exact", "llm"], default="exact",
                        help="Accuracy scoring mode: exact match or LLM judge (default: exact)")
    parser.add_argument("--openai-key", metavar="KEY",
                        help="OpenAI API key for LLM judge mode")
    parser.add_argument("--max-tokens", type=int, default=128,
                        help="Max tokens per response (default: 128)")
    parser.add_argument("--n-ctx", type=int, default=2048,
                        help="Context window size (default: 2048)")
    parser.add_argument("--n-gpu-layers", type=int, default=0,
                        help="GPU layers to offload (0 = CPU only, -1 = all layers)")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON results")
    parser.add_argument("--save", metavar="FILE",
                        help="Save JSON results to file")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI colors")
    parser.add_argument("--verbose", action="store_true",
                        help="Show llama.cpp loading logs")
    args = parser.parse_args()

    # validate model files
    for m in args.models:
        if not Path(m).exists():
            print(f"Error: model file not found: {m}", file=sys.stderr)
            sys.exit(1)

    # load prompts
    if args.prompts:
        prompts, references = load_prompts(args.prompts)
    else:
        print("No --prompts provided. Using built-in sample prompts (factual Q&A).")
        prompts    = [p for p, _ in SAMPLE_PROMPTS]
        references = [r for _, r in SAMPLE_PROMPTS]

    # run each model
    bench_results: list[BenchResult] = []
    for model_path in args.models:
        print(f"\nBenchmarking {Path(model_path).name} …")
        result = run_model(
            model_path=model_path,
            prompts=prompts,
            n_ctx=args.n_ctx,
            max_tokens=args.max_tokens,
            n_gpu_layers=args.n_gpu_layers,
            verbose=args.verbose,
        )
        bench_results.append(result)
        print(f"  → {result.avg_tokens_per_second:.1f} tok/s avg  |  "
              f"{result.avg_latency_ms:.0f} ms avg latency")

    # score accuracy
    model_points: list[ModelPoint] = []
    for result in bench_results:
        outputs = [pr.output for pr in result.prompt_results]
        scores = score_outputs(
            prompts=prompts,
            outputs=outputs,
            references=references,
            mode=args.mode,
            api_key=args.openai_key,
        )
        valid_scores = [s for s in scores if s is not None]
        avg_accuracy = sum(valid_scores) / len(valid_scores) if valid_scores else None

        model_points.append(ModelPoint(
            quant_label=result.quant_label,
            model_path=result.model_path,
            avg_tokens_per_second=result.avg_tokens_per_second,
            avg_accuracy=avg_accuracy,
            avg_latency_ms=result.avg_latency_ms,
            file_size_mb=get_file_size_mb(result.model_path),
        ))

    # output
    if args.json or args.save:
        out = {
            "models": [
                {
                    "quant_label":           mp.quant_label,
                    "model_path":            mp.model_path,
                    "avg_tokens_per_second": mp.avg_tokens_per_second,
                    "avg_accuracy":          mp.avg_accuracy,
                    "avg_latency_ms":        mp.avg_latency_ms,
                    "file_size_mb":          mp.file_size_mb,
                    "prompt_results": [
                        {
                            "prompt":          pr.prompt,
                            "output":          pr.output,
                            "output_tokens":   pr.output_tokens,
                            "latency_ms":      pr.total_latency_ms,
                            "tokens_per_second": pr.tokens_per_second,
                        }
                        for pr in br.prompt_results
                    ],
                }
                for mp, br in zip(model_points, bench_results)
            ]
        }
        if args.save:
            Path(args.save).write_text(json.dumps(out, indent=2))
            print(f"\nResults saved to {args.save}")
        if args.json:
            print(json.dumps(out, indent=2))

    if not args.json:
        print_report(model_points, use_color=not args.no_color)


if __name__ == "__main__":
    main()
