"""
Core logic: load eval output, classify errors, produce ranked failure manifest.
"""

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from collections import Counter

from failure_types import FAILURE_TYPES, classify_error


@dataclass
class FailureRecord:
    index: int
    input_text: str
    prediction: str
    reference: str
    error_note: str
    failure_types: list[str]


@dataclass
class FailureTypeStats:
    key: str
    label: str
    description: str
    count: int
    pct: float
    examples: list[FailureRecord]


@dataclass
class FailureManifest:
    total_examples: int
    total_errors: int
    error_rate: float
    ranked: list[FailureTypeStats]

    def top_n(self, n: int = 3) -> list[FailureTypeStats]:
        return self.ranked[:n]


# ── loaders ────────────────────────────────────────────────────────────────

def load_csv(path: Path) -> list[dict]:
    """
    CSV must have columns: input, prediction, reference
    Optional: error_note
    Rows where prediction == reference are treated as correct.
    """
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(path: Path) -> list[dict]:
    """
    JSON: list of objects with keys: input, prediction, reference, [error_note]
    """
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        # allow {"examples": [...]} wrapper
        data = data.get("examples", data.get("data", []))
    return data


def load_eval_output(path: str | Path) -> list[dict]:
    path = Path(path)
    if path.suffix == ".csv":
        return load_csv(path)
    elif path.suffix in (".json", ".jsonl"):
        if path.suffix == ".jsonl":
            rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
            return rows
        return load_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv, .json, or .jsonl")


# ── analysis ───────────────────────────────────────────────────────────────

def analyze(rows: list[dict], max_examples: int = 3) -> FailureManifest:
    """
    Classify each error row and return a ranked FailureManifest.
    """
    total = len(rows)
    errors: list[FailureRecord] = []

    for i, row in enumerate(rows):
        pred = str(row.get("prediction", "")).strip()
        ref  = str(row.get("reference", "")).strip()
        inp  = str(row.get("input", "")).strip()
        note = str(row.get("error_note", "")).strip()

        # skip correct examples
        if pred == ref:
            continue

        types = classify_error(pred, ref, note)
        errors.append(FailureRecord(
            index=i,
            input_text=inp,
            prediction=pred,
            reference=ref,
            error_note=note,
            failure_types=types,
        ))

    # count per type
    type_counts: Counter = Counter()
    type_examples: dict[str, list[FailureRecord]] = {ft["key"]: [] for ft in FAILURE_TYPES}
    type_examples["unclassified"] = []

    for err in errors:
        for t in err.failure_types:
            type_counts[t] += 1
            if len(type_examples.get(t, [])) < max_examples:
                type_examples.setdefault(t, []).append(err)

    # build ranked list (only types with at least 1 occurrence)
    label_map = {ft["key"]: ft["label"] for ft in FAILURE_TYPES}
    desc_map  = {ft["key"]: ft["description"] for ft in FAILURE_TYPES}
    label_map["unclassified"] = "Unclassified"
    desc_map["unclassified"]  = "Errors that didn't match any failure pattern. Review manually."

    ranked = []
    for key, count in type_counts.most_common():
        ranked.append(FailureTypeStats(
            key=key,
            label=label_map.get(key, key),
            description=desc_map.get(key, ""),
            count=count,
            pct=round(count / len(errors) * 100, 1) if errors else 0.0,
            examples=type_examples.get(key, []),
        ))

    return FailureManifest(
        total_examples=total,
        total_errors=len(errors),
        error_rate=round(len(errors) / total * 100, 1) if total else 0.0,
        ranked=ranked,
    )
