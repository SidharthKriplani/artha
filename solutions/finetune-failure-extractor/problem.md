# Problem: Fine-Tuning Failure Mode Extractor

## What already exists

**Langfuse** — error clustering for LLM apps, but requires account setup, instrumentation, observability infrastructure. Not a zero-friction local tool.

**Weights & Biases** — tracks training metrics (loss curves, accuracy). Does not cluster or categorize failure types from eval output.

**Manual review** — what everyone actually does; no structure, no prioritization, no cross-run comparison.

**LLM-as-judge eval** (OpenAI evals, RAGAS) — scores outputs but doesn't cluster failure modes or produce a ranked manifest for training data selection.

## The gap

No tool takes raw eval output (input / prediction / reference triples) and outputs a ranked failure mode manifest — grouped by type, sorted by frequency, with examples — that directly feeds next training data prioritization.

Gap is specific and narrow: the missing piece is pattern-based failure taxonomy + frequency ranking, not evaluation scoring.

## What this tool does

Zero dependencies. Pure Python. Run in one command.

Reads eval output (CSV, JSON, or JSONL). Classifies each error across 7 failure types: wrong operator, off-by-one, missing reasoning step, factual gap, format error, instruction following failure, overconfidence. Outputs a ranked manifest: most frequent failure types first, with count, percentage, and concrete examples per type. Bottom of report: ordered training data priority list for next run.

## What it does NOT do

- Does not run the model or generate predictions
- Does not use an LLM to classify errors (pattern matching only — intentional; keeps it zero-dependency)
- Does not suggest specific training examples to add (that requires your dataset)
- Pattern matching will miss subtle or domain-specific failure modes — unclassified bucket catches these for manual review

## Honest assessment

Pattern-matching classification is imperfect. High-quality `error_note` fields in the eval output dramatically improve accuracy. For domain-specific fine-tuning (medical, legal, code), the taxonomy may need extension. The "unclassified" bucket is a signal to review manually and potentially add new patterns.
