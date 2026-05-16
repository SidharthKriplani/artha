"""
Accuracy scoring for quant-pareto-bench.

Two modes:
  exact  — checks if reference answer appears in output (good for math/code/factual)
  llm    — uses OpenAI gpt-4o-mini as judge (good for open-ended prompts)

Returns a score 0.0–1.0 per (output, reference) pair.
"""

import re
import os


def score_exact(output: str, reference: str) -> float:
    """
    Returns 1.0 if reference (or any token from it) appears in output,
    with partial credit for numeric proximity.
    """
    out = output.strip().lower()
    ref = reference.strip().lower()

    # exact substring match
    if ref in out:
        return 1.0

    # try to match numbers within 1% tolerance
    ref_nums = re.findall(r"-?\d+\.?\d*", ref)
    out_nums = re.findall(r"-?\d+\.?\d*", out)
    if ref_nums and out_nums:
        try:
            r = float(ref_nums[0])
            o = float(out_nums[0])
            if r == 0:
                return 1.0 if o == 0 else 0.0
            return 1.0 if abs(r - o) / abs(r) < 0.01 else 0.0
        except ValueError:
            pass

    # word overlap (jaccard)
    ref_words = set(ref.split())
    out_words = set(out.split())
    if not ref_words:
        return 0.0
    overlap = len(ref_words & out_words) / len(ref_words)
    return round(overlap, 2)


def score_llm(
    prompt: str,
    output: str,
    reference: str,
    api_key: str | None = None,
) -> float:
    """
    Use gpt-4o-mini as judge. Returns 0.0, 0.5, or 1.0.
    Requires OPENAI_API_KEY env var or api_key argument.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package required for LLM judge mode. pip install openai")

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set. Use --mode exact or provide --openai-key.")

    client = OpenAI(api_key=key)

    system = (
        "You are a strict answer evaluator. Given a question, a model output, and a "
        "reference answer, score the output as: 1 (correct), 0.5 (partially correct), "
        "or 0 (incorrect). Reply with ONLY the number."
    )
    user = f"Question: {prompt}\nModel output: {output}\nReference: {reference}"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": user}],
        max_tokens=5,
        temperature=0,
    )
    raw = resp.choices[0].message.content.strip()
    try:
        return float(raw)
    except ValueError:
        return 0.5  # fallback if model returns unexpected text


def score_outputs(
    prompts: list[str],
    outputs: list[str],
    references: list[str] | None,
    mode: str = "exact",
    api_key: str | None = None,
) -> list[float]:
    """
    Score a list of outputs against references.
    Returns a list of scores 0.0–1.0.
    If no references provided, returns None-scores (accuracy unavailable).
    """
    if not references:
        return [None] * len(outputs)

    scores = []
    for prompt, output, reference in zip(prompts, outputs, references):
        if mode == "llm":
            s = score_llm(prompt, output, reference, api_key=api_key)
        else:
            s = score_exact(output, reference)
        scores.append(s)
    return scores
