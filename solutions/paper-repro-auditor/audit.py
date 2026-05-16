#!/usr/bin/env python3
"""
paper-repro-auditor — CLI entry point

Usage:
  python audit.py                     # interactive prompt mode
  python audit.py --paper paper.json --yours yours.json
  python audit.py --paper paper.json --yours yours.json --json

JSON format (both files):
  {
    "random_seed": "42",
    "data_splits": "80/10/10 random",
    "normalization": "mean=[0.485,0.456,0.406] std=[0.229,0.224,0.225]",
    "metric_computation": "top-1 accuracy on val set, best epoch",
    "augmentation": "random crop + horizontal flip",
    "checkpoint_selection": "best val accuracy",
    "optimizer": "SGD lr=0.1 momentum=0.9 weight_decay=1e-4 cosine decay",
    "batch_size": "256",
    "train_duration": "90 epochs",
    "hardware_env": "V100 32GB PyTorch 1.8"
  }
"""

import argparse
import json
import sys
from pathlib import Path

# Support running from within this directory
sys.path.insert(0, str(Path(__file__).parent))

from core import analyze, ReproductionGapReport, GapResult
from risk_factors import RISK_FACTORS

RISK_COLORS = {
    "HIGH":    "\033[91m",  # red
    "MEDIUM":  "\033[93m",  # yellow
    "LOW":     "\033[92m",  # green
    "UNKNOWN": "\033[90m",  # grey
}
RESET = "\033[0m"
BOLD  = "\033[1m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def print_report(report: ReproductionGapReport, use_color: bool = True) -> None:
    def c(text, color):
        return colorize(text, color) if use_color else text

    overall_color = RISK_COLORS.get(report.overall_risk, "")
    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  REPRODUCTION GAP REPORT{RESET}")
    print(f"  Overall risk: {c(report.overall_risk, overall_color)}")
    print(f"  HIGH: {len(report.high_risk_gaps)}  MEDIUM: {len(report.medium_risk_gaps)}  LOW: {len(report.low_risk_gaps)}")
    print(f"{BOLD}{'='*60}{RESET}")

    for i, gap in enumerate(report.gaps, 1):
        color = RISK_COLORS.get(gap.risk, "")
        risk_tag = c(f"[{gap.risk:6}]", color)
        print(f"\n{i:2}. {risk_tag}  {BOLD}{gap.label}{RESET}  (score {gap.score}/10)")
        print(f"    Paper : {gap.paper_value}")
        print(f"    Yours : {gap.your_value}")
        print(f"    {gap.explanation}")
        if gap.risk in ("HIGH", "MEDIUM"):
            print(f"    💡 {gap.hint}")

    print(f"\n{BOLD}{'='*60}{RESET}")
    high = report.high_risk_gaps
    if high:
        print(f"{BOLD}Fix these first:{RESET}")
        for g in high:
            print(f"  • {g.label}: {g.explanation.split('.')[0]}.")
    else:
        print("No HIGH risk gaps found. Run your experiment with the MEDIUM items adjusted and re-evaluate.")
    print()


def interactive_mode() -> tuple[dict, dict]:
    print(f"\n{BOLD}paper-repro-auditor — interactive mode{RESET}")
    print("Answer each question for the PAPER and then for YOUR setup.")
    print("Press Enter to mark as 'not stated'.\n")

    paper_config = {}
    your_config = {}

    for factor in RISK_FACTORS:
        print(f"{BOLD}{factor['label']}{RESET}")
        paper_val = input(f"  Paper  — {factor['paper_question']}\n  > ").strip()
        your_val  = input(f"  Yours  — {factor['your_question']}\n  > ").strip()
        paper_config[factor["key"]] = paper_val or "not stated"
        your_config[factor["key"]] = your_val or "not stated"
        print()

    return paper_config, your_config


def main():
    parser = argparse.ArgumentParser(
        description="Rank reproduction risks between a paper's config and yours."
    )
    parser.add_argument("--paper", metavar="FILE", help="JSON file with paper's config")
    parser.add_argument("--yours", metavar="FILE", help="JSON file with your config")
    parser.add_argument("--json",  action="store_true", help="Output raw JSON report")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    args = parser.parse_args()

    if args.paper and args.yours:
        paper_config = json.loads(Path(args.paper).read_text())
        your_config  = json.loads(Path(args.yours).read_text())
    else:
        paper_config, your_config = interactive_mode()

    report = analyze(paper_config, your_config)

    if args.json:
        out = {
            "overall_risk": report.overall_risk,
            "gaps": [
                {
                    "key": g.key,
                    "label": g.label,
                    "risk": g.risk,
                    "score": g.score,
                    "paper_value": g.paper_value,
                    "your_value": g.your_value,
                    "explanation": g.explanation,
                    "hint": g.hint,
                }
                for g in report.gaps
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        print_report(report, use_color=not args.no_color)


if __name__ == "__main__":
    main()
