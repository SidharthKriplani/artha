"""
Core gap analysis logic for paper-repro-auditor.
Compares paper config vs your config across risk dimensions.
"""

from dataclasses import dataclass, field
from typing import Literal
from risk_factors import RISK_FACTORS


RISK_LEVEL = Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

KEYWORDS_MISMATCH = {
    "not stated": 10,   # paper didn't report → auto HIGH
    "not reported": 10,
    "standard": 5,     # vague → MEDIUM
    "default": 5,
    "n/a": 0,
    "none": 0,
}


@dataclass
class GapResult:
    key: str
    label: str
    paper_value: str
    your_value: str
    risk: RISK_LEVEL
    score: int          # 0-10
    explanation: str
    hint: str


@dataclass
class ReproductionGapReport:
    gaps: list[GapResult] = field(default_factory=list)

    @property
    def overall_risk(self) -> RISK_LEVEL:
        if not self.gaps:
            return "UNKNOWN"
        top = self.gaps[0].score
        if top >= 8:
            return "HIGH"
        if top >= 5:
            return "MEDIUM"
        return "LOW"

    @property
    def high_risk_gaps(self):
        return [g for g in self.gaps if g.risk == "HIGH"]

    @property
    def medium_risk_gaps(self):
        return [g for g in self.gaps if g.risk == "MEDIUM"]

    @property
    def low_risk_gaps(self):
        return [g for g in self.gaps if g.risk == "LOW"]


def _score_gap(paper_val: str, your_val: str, weight: int) -> tuple[int, RISK_LEVEL, str]:
    """Return (score 0-10, risk level, explanation)."""
    p = paper_val.strip().lower()
    y = your_val.strip().lower()

    # Paper didn't document → can't verify → HIGH
    for kw, penalty in KEYWORDS_MISMATCH.items():
        if kw in p and penalty >= 8:
            score = min(weight, 10)
            return score, "HIGH", (
                f"Paper does not report this clearly ('{paper_val}'). "
                f"You cannot know whether your setting matches."
            )

    # Exact match → LOW risk
    if p == y:
        return 0, "LOW", "Settings match exactly."

    # Vague paper description → MEDIUM
    for kw, penalty in KEYWORDS_MISMATCH.items():
        if kw in p and penalty >= 4:
            score = min(weight // 2 + 2, 8)
            return score, "MEDIUM", (
                f"Paper uses vague description ('{paper_val}'). "
                f"Cannot confirm your setting ('{your_val}') matches."
            )

    # Both stated but differ → score by weight
    score = min(weight, 10)
    risk: RISK_LEVEL = "HIGH" if score >= 8 else "MEDIUM" if score >= 5 else "LOW"
    return score, risk, (
        f"Mismatch: paper reports '{paper_val}', you used '{your_val}'. "
        f"This is a high-probability reproduction gap."
    )


def analyze(paper_config: dict[str, str], your_config: dict[str, str]) -> ReproductionGapReport:
    """
    Compare paper_config vs your_config across all risk factors.
    Returns a ReproductionGapReport sorted by descending risk score.
    """
    results = []
    for factor in RISK_FACTORS:
        key = factor["key"]
        paper_val = paper_config.get(key, "not stated").strip() or "not stated"
        your_val = your_config.get(key, "not stated").strip() or "not stated"

        score, risk, explanation = _score_gap(paper_val, your_val, factor["weight"])

        results.append(GapResult(
            key=key,
            label=factor["label"],
            paper_value=paper_val,
            your_value=your_val,
            risk=risk,
            score=score,
            explanation=explanation,
            hint=factor["hint"],
        ))

    results.sort(key=lambda g: g.score, reverse=True)
    return ReproductionGapReport(gaps=results)
