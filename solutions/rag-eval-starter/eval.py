"""
RAG Eval Starter — CLI
Usage:
    python eval.py
    python eval.py --docs ./my_docs --questions ./my_qa.json
    python eval.py --docs ./my_docs --questions ./my_qa.json --models gpt-4o-mini gpt-4o
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Compare RAG configurations on your documents."
    )
    parser.add_argument(
        "--docs", type=str,
        default="data/sample_docs",
        help="Folder containing .txt or .pdf documents (default: sample docs)"
    )
    parser.add_argument(
        "--questions", type=str,
        default="data/sample_qa.json",
        help="JSON file with [{question, ground_truth}] pairs (default: sample QA)"
    )
    parser.add_argument(
        "--models", nargs="+",
        default=["gpt-4o-mini"],
        help="OpenAI model(s) to compare (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--output", type=str,
        default="results.csv",
        help="Path to save results CSV (default: results.csv)"
    )
    args = parser.parse_args()

    # Validate API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set.")
        print("Add it to a .env file or run: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    from eval_core import (
        load_docs_from_dir, load_qa, run_full_eval, build_verdict
    )

    docs_dir = Path(args.docs)
    qa_path  = Path(args.questions)

    if not docs_dir.exists():
        print(f"Error: docs folder not found: {docs_dir}")
        sys.exit(1)
    if not qa_path.exists():
        print(f"Error: QA file not found: {qa_path}")
        sys.exit(1)

    print("\n=== RAG Eval Starter ===\n")
    print(f"Docs:      {docs_dir}")
    print(f"Questions: {qa_path}")
    print(f"Models:    {args.models}")
    print()

    print("Loading documents...")
    docs = load_docs_from_dir(docs_dir)
    print(f"  {len(docs)} document(s) loaded")

    print("Loading QA pairs...")
    questions, ground_truth = load_qa(qa_path)
    print(f"  {len(questions)} QA pairs loaded")

    print("\nRunning evaluation...\n")
    df = run_full_eval(
        docs=docs,
        questions=questions,
        ground_truth=ground_truth,
        models=args.models,
        log_fn=print
    )

    print("\n=== Results ===\n")
    print(df[["config", "model", "faithfulness",
              "answer_relevancy", "context_precision", "avg_score"]].to_string(index=False))

    print("\n=== Verdict ===\n")
    print(build_verdict(df))

    df.to_csv(args.output, index=False)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
