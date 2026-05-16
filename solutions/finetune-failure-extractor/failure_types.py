"""
Failure mode taxonomy for fine-tuned model eval outputs.
Each type has: key, label, description, keywords/patterns to match.
"""

import re

FAILURE_TYPES = [
    {
        "key": "wrong_operator",
        "label": "Wrong Operator / Operation",
        "description": "Model uses the wrong math or logic operator (+/−/×/÷, and/or, etc.)",
        "patterns": [
            r"\b(added|subtracted|multiplied|divided)\b",
            r"\bshould (add|subtract|multiply|divide)\b",
            r"\binstead of (adding|subtracting|multiplying|dividing)\b",
            r"\bwrong (operator|operation|sign)\b",
            r"\b(\+|-|\*|/) instead\b",
        ],
        "keywords": ["wrong operator", "wrong operation", "incorrect sign",
                     "should add", "should subtract", "should multiply"],
    },
    {
        "key": "off_by_one",
        "label": "Off-by-One / Boundary Error",
        "description": "Answer is exactly one step off — indexing, counting, fencepost errors.",
        "patterns": [
            r"\boff.by.one\b",
            r"\b(one|1) (too|short|fewer|more|extra|off)\b",
            r"\bshould be \d+ but (got|predicted|output) \d+\b",
            r"\bboundary\b",
            r"\bindex(ing)? error\b",
        ],
        "keywords": ["off by one", "one too", "fencepost", "boundary error",
                     "should be n-1", "should be n+1"],
    },
    {
        "key": "reasoning_gap",
        "label": "Missing Reasoning Step",
        "description": "Model skips an intermediate step; conclusion doesn't follow from stated premises.",
        "patterns": [
            r"\bskip(ped|s)? (a |the )?(step|intermediate|reasoning)\b",
            r"\b(missing|omitted) step\b",
            r"\bjump(ed|s)? to\b",
            r"\bdoesn.t follow\b",
            r"\binvalid (conclusion|inference|deduction)\b",
            r"\bincomplete reasoning\b",
        ],
        "keywords": ["skipped step", "missing step", "jumped to", "doesn't follow",
                     "invalid conclusion", "incomplete reasoning", "leap"],
    },
    {
        "key": "factual_gap",
        "label": "Factual / Knowledge Gap",
        "description": "Model states a wrong fact — wrong value, wrong entity, hallucination.",
        "patterns": [
            r"\bhallucin\w+\b",
            r"\bwrong (fact|value|date|name|entity|number)\b",
            r"\bincorrect (fact|value|date|name|entity|number)\b",
            r"\bfactually (wrong|incorrect|false)\b",
            r"\bdoesn.t exist\b",
            r"\bmade.?up\b",
        ],
        "keywords": ["hallucination", "wrong fact", "wrong value", "incorrect fact",
                     "factually wrong", "doesn't exist", "made up", "fabricated"],
    },
    {
        "key": "format_error",
        "label": "Format / Output Structure Error",
        "description": "Correct answer in the wrong format — JSON schema violation, wrong units, missing field.",
        "patterns": [
            r"\b(wrong|invalid|bad) format\b",
            r"\b(missing|extra) (field|key|column|bracket|quote)\b",
            r"\bwrong (unit|units|currency|scale)\b",
            r"\b(not valid|invalid) JSON\b",
            r"\bschema (violation|error|mismatch)\b",
            r"\bparsing (error|failed|failure)\b",
        ],
        "keywords": ["wrong format", "missing field", "invalid json", "wrong unit",
                     "schema violation", "parsing error", "format error"],
    },
    {
        "key": "instruction_follow",
        "label": "Instruction Following Failure",
        "description": "Model ignores part of the instruction — doesn't constrain output, answers a different question.",
        "patterns": [
            r"\bignore(d|s)? (the |a )?(instruction|constraint|rule|format)\b",
            r"\bdoesn.t follow (the |a )?(instruction|constraint|rule)\b",
            r"\bwrong (task|question|problem)\b",
            r"\bwent off.?topic\b",
            r"\bnot asked\b",
            r"\banswered (a )?different (question|task)\b",
        ],
        "keywords": ["ignored instruction", "ignored constraint", "doesn't follow",
                     "wrong task", "off topic", "not asked", "different question"],
    },
    {
        "key": "overconfidence",
        "label": "Overconfidence / Missing Uncertainty",
        "description": "Model gives definitive answer when it should hedge, refuse, or express uncertainty.",
        "patterns": [
            r"\b(should|must) (say|express|output|indicate) (uncertainty|\"i don.t know\"|unknown)\b",
            r"\boverconfiden\w+\b",
            r"\bshould (hedge|refuse|abstain)\b",
            r"\bno (valid|correct) answer\b",
            r"\bunanswerable\b",
        ],
        "keywords": ["overconfident", "should hedge", "should refuse",
                     "no valid answer", "unanswerable", "express uncertainty"],
    },
]


def classify_error(prediction: str, reference: str, error_note: str = "") -> list[str]:
    """
    Return a list of matching failure type keys for a single error.
    Checks error_note first, then falls back to comparing prediction vs reference.
    """
    text = (error_note + " " + prediction + " " + reference).lower()
    matched = []

    for ft in FAILURE_TYPES:
        # keyword match
        if any(kw in text for kw in ft["keywords"]):
            matched.append(ft["key"])
            continue
        # regex match
        for pat in ft["patterns"]:
            if re.search(pat, text, re.IGNORECASE):
                matched.append(ft["key"])
                break

    return matched if matched else ["unclassified"]
