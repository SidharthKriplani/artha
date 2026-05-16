#!/usr/bin/env python3
"""
finetune-failure-extractor — CLI entry point

Usage:
  python extract.py --eval results.csv
  python extract.py --eval results.json --top 5
  python extract.py --eval results.jsonl --json
  python extract.py --eval results.csv --save manifest.json

Input file formats:
  CSV:   columns: input, prediction, reference, [error_note]
  JSON:  list of {input, prediction, reference, [error_note]}
  JSONL: one JSON object per line
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import analyze, load_eval_output, FailureManifest, FailureTypeStats

BOLD  = "\033[1m"
RESET = "\033[0m"
RED   = "\033[91m"
YEL   = "\033[93m"
GRN   = "\033[92m"
GREY  = "\033[90m"


def rank_color(rank: int) -> str:
    if rank == 1: return RED
    if rank == 2: return YEL
    if rank == 3: return YEL
    return GREY


def print_manifest(manifest: FailureManifest, top: int, use_color: bool) -> None:
    def c(text, color): return f"{color}{text}{RESET}" if use_color else text

    print()
    print(f"{BOLD}{'='*62}{RESET}")
    print(f"{BOLD}  FAILURE MODE MANIFEST{RESET}")
    print(f"  Total examples : {manifest.total_examples}")
    print(f"  Errors found   : {manifest.total_errors}  ({manifest.error_rate}% error rate)")
    print(f"  Failure types  : {len(manifest.ranked)} distinct modes")
    print(f"{BOLD}{'='*62}{RESET}")

    if not manifest.ranked:
        print("\n  No errors found — all predictions match references.")
        return

    print(f"\n{BOLD}  RANKED FAILURE MODES (top {min(top, len(manifest.ranked))}){RESET}\n")

    for i, ft in enumerate(manifest.ranked[:top], 1):
        col = rank_color(i) if use_color else ""
        bar_len = int(ft.pct / 2)
        bar = "█" * bar_len
        print(f"  {c(f'#{i}', col)}  {BOLD}{ft.label}{RESET}")
        print(f"      {c(bar, col)} {ft.pct}% of errors ({ft.count} cases)")
        print(f"      {ft.description}")

        if ft.examples:
            print(f"      {BOLD}Example:{RESET}")
            ex = ft.examples[0]
            inp_preview = ex.input_text[:120] + "…" if len(ex.input_text) > 120 else ex.input_text
            print(f"        Input      : {inp_preview}")
            print(f"        Predicted  : {ex.prediction[:100]}")
            print(f"        Reference  : {ex.reference[:100]}")
            if ex.error_note:
                print(f"        Note       : {ex.error_note}")
        print()

    print(f"{BOLD}{'='*62}{RESET}")
    print(f"\n{BOLD}  TRAINING DATA PRIORITY (next batch){RESET}")
    print("  Focus on examples of these types, in order:\n")
    for i, ft in enumerate(manifest.ranked[:top], 1):
        print(f"  {i}. {ft.label}  — {ft.count} cases, {ft.pct}% of errors")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Extract and rank failure modes from fine-tuning eval output."
    )
    parser.add_argument("--eval",  required=True, metavar="FILE",
                        help="Eval output file (.csv, .json, or .jsonl)")
    parser.add_argument("--top",   type=int, default=5,
                        help="Show top N failure types (default: 5)")
    parser.add_argument("--json",  action="store_true",
                        help="Output raw JSON manifest")
    parser.add_argument("--save",  metavar="FILE",
                        help="Save JSON manifest to file")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI colors")
    args = parser.parse_args()

    rows = load_eval_output(args.eval)
    manifest = analyze(rows, max_examples=3)

    if args.json or args.save:
        out = {
            "total_examples": manifest.total_examples,
            "total_errors":   manifest.total_errors,
            "error_rate":     manifest.error_rate,
            "ranked": [
                {
                    "rank":        i + 1,
                    "key":         ft.key,
                    "label":       ft.label,
                    "description": ft.description,
                    "count":       ft.count,
                    "pct":         ft.pct,
                    "examples": [
                        {
                            "index":      ex.index,
                            "input":      ex.input_text,
                            "prediction": ex.prediction,
                            "reference":  ex.reference,
                            "error_note": ex.error_note,
                        }
                        for ex in ft.examples
                    ],
                }
                for i, ft in enumerate(manifest.ranked)
            ],
        }
        if args.save:
            Path(args.save).write_text(json.dumps(out, indent=2))
            print(f"Manifest saved to {args.save}")
        if args.json:
            print(json.dumps(out, indent=2))
        if not args.json:
            print_manifest(manifest, args.top, use_color=not args.no_color)
    else:
        print_manifest(manifest, args.top, use_color=not args.no_color)


if __name__ == "__main__":
    main()
