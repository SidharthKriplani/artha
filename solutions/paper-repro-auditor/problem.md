# Problem: Paper Reproduction Gap Auditor

## What already exists

**Papers With Code** — tracks code availability for papers; doesn't audit gaps between reported setup and your setup.

**NeurIPS / ICML reproducibility checklists** — authored by paper writers, not practitioners trying to reproduce from the outside.

**ML reproducibility surveys** (Pineau et al., 2021) — academic analysis of what's typically missing; not a practitioner tool.

**Manual reading + diff** — what everyone actually does; unstructured, time-consuming, misses interactions.

## The gap

No tool takes two structured configs — the paper's reported setup and the practitioner's actual setup — and outputs ranked reproduction risk factors with explanations and hints.

The gap is **narrow and specific**: the artifact needed is a structured gap auditor, not a training framework, not a benchmark runner, not a code availability tracker.

## What this tool does

Zero dependencies. Pure Python. Run in one command.

Takes a paper config and your config (interactive prompts or JSON files). Compares them across 10 reproduction risk dimensions (seed, data splits, normalization, metric computation, augmentation, checkpoint selection, optimizer, batch size, training duration, hardware/library versions). Outputs a ranked gap report: HIGH / MEDIUM / LOW per dimension with explanations.

## What it does NOT do

- Does not read PDFs or extract config automatically (that's a future extension)
- Does not run experiments or verify outputs
- Does not compare code — only reported configs
- Scoring is heuristic, not learned from data

## Honest assessment

The tool is useful in proportion to how well the practitioner can answer the questions about the paper. Papers with severe underreporting will produce many "not stated → HIGH" flags, which is accurate but not specific. The value is in forcing a structured comparison that practitioners currently do informally and incompletely.
