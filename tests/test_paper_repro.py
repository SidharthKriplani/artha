"""
Unit tests for paper-repro-auditor core logic.
Run: python -m pytest tests/test_paper_repro.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "solutions" / "paper-repro-auditor"))

from core import analyze, _score_gap


class TestScoreGap:

    def test_exact_match_is_low_risk(self):
        score, risk, _ = _score_gap("42", "42", weight=10)
        assert score == 0
        assert risk == "LOW"

    def test_not_stated_is_high_risk(self):
        score, risk, _ = _score_gap("not stated", "42", weight=10)
        assert risk == "HIGH"
        assert score >= 8

    def test_not_reported_is_high_risk(self):
        score, risk, _ = _score_gap("not reported", "42", weight=10)
        assert risk == "HIGH"

    def test_vague_standard_is_medium_risk(self):
        score, risk, _ = _score_gap("standard", "adam lr=1e-3", weight=8)
        assert risk == "MEDIUM"

    def test_clear_mismatch_scores_by_weight(self):
        score, risk, _ = _score_gap("best val accuracy", "last epoch", weight=8)
        assert risk in ("HIGH", "MEDIUM")
        assert score > 0

    def test_case_insensitive_match(self):
        score, risk, _ = _score_gap("Adam LR=1e-4", "adam lr=1e-4", weight=10)
        assert score == 0
        assert risk == "LOW"


class TestAnalyze:

    def test_returns_all_factors(self):
        report = analyze({}, {})
        assert len(report.gaps) == 10  # all 10 risk factors

    def test_not_stated_paper_gives_overall_high(self):
        paper = {}  # all "not stated"
        yours = {"random_seed": "42", "data_splits": "80/10/10"}
        report = analyze(paper, yours)
        assert report.overall_risk == "HIGH"

    def test_perfect_match_gives_low_risk(self):
        config = {
            "random_seed": "42",
            "data_splits": "80/10/10 random",
            "normalization": "imagenet mean/std",
            "metric_computation": "top-1 accuracy best epoch",
            "augmentation": "random crop + flip",
            "checkpoint_selection": "best val accuracy",
            "optimizer": "sgd lr=0.1 momentum=0.9",
            "batch_size": "256",
            "train_duration": "90 epochs",
            "hardware_env": "v100 pytorch 1.9",
        }
        report = analyze(config, config)
        assert report.overall_risk == "LOW"
        assert len(report.high_risk_gaps) == 0

    def test_gaps_sorted_by_score_descending(self):
        report = analyze({}, {})
        scores = [g.score for g in report.gaps]
        assert scores == sorted(scores, reverse=True)

    def test_high_risk_gaps_property(self):
        report = analyze({}, {"random_seed": "42"})
        high = report.high_risk_gaps
        assert all(g.risk == "HIGH" for g in high)

    def test_json_output_fields(self):
        report = analyze({"random_seed": "not stated"}, {"random_seed": "42"})
        gap = report.gaps[0]
        assert hasattr(gap, "key")
        assert hasattr(gap, "label")
        assert hasattr(gap, "risk")
        assert hasattr(gap, "score")
        assert hasattr(gap, "explanation")
        assert hasattr(gap, "hint")
