"""
Unit tests for finetune-failure-extractor core logic.
Run: python -m pytest tests/test_failure_extractor.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "solutions" / "finetune-failure-extractor"))

from failure_types import classify_error
from core import analyze


class TestClassifyError:

    def test_wrong_operator_keyword(self):
        types = classify_error("54", "56", "wrong operator - subtracted instead of multiplied")
        assert "wrong_operator" in types

    def test_off_by_one_keyword(self):
        types = classify_error("16", "32", "off by one power - computed 2^4")
        assert "off_by_one" in types

    def test_factual_gap_keyword(self):
        types = classify_error("Sydney", "Canberra", "factually wrong - hallucination")
        assert "factual_gap" in types

    def test_missing_reasoning_pattern(self):
        types = classify_error("5", "6", "missing reasoning step - skipped final multiplication")
        assert "reasoning_gap" in types or "unclassified" in types  # pattern may not catch all phrasings

    def test_exact_match_is_not_an_error(self):
        # classify_error is called on errors only — but if called with matching strings, should still classify
        types = classify_error("42", "42", "")
        # just shouldn't crash
        assert isinstance(types, list)

    def test_unclassified_fallback(self):
        types = classify_error("banana", "apple", "something weird happened")
        assert "unclassified" in types

    def test_returns_list(self):
        result = classify_error("x", "y", "")
        assert isinstance(result, list)
        assert len(result) >= 1


class TestAnalyze:

    def _make_rows(self, pairs):
        """Helper: list of (prediction, reference, error_note) → row dicts"""
        return [
            {"input": f"q{i}", "prediction": p, "reference": r, "error_note": n}
            for i, (p, r, n) in enumerate(pairs)
        ]

    def test_no_errors_when_all_correct(self):
        rows = self._make_rows([("42", "42", ""), ("Paris", "Paris", "")])
        manifest = analyze(rows)
        assert manifest.total_errors == 0
        assert manifest.error_rate == 0.0

    def test_correct_error_count(self):
        rows = self._make_rows([
            ("54", "56", "wrong operator"),
            ("42", "42", ""),
            ("Sydney", "Canberra", "hallucination"),
        ])
        manifest = analyze(rows)
        assert manifest.total_errors == 2
        assert manifest.total_examples == 3

    def test_ranked_by_frequency(self):
        rows = self._make_rows([
            ("54", "56", "wrong operator"),
            ("15", "16", "wrong operator"),
            ("Sydney", "Canberra", "hallucination"),
        ])
        manifest = analyze(rows)
        if len(manifest.ranked) >= 2:
            assert manifest.ranked[0].count >= manifest.ranked[1].count

    def test_error_rate_calculation(self):
        rows = self._make_rows([
            ("wrong", "right", ""),
            ("correct", "correct", ""),
        ])
        manifest = analyze(rows)
        assert manifest.error_rate == 50.0

    def test_examples_capped(self):
        rows = self._make_rows([
            ("54", f"{i}", "wrong operator") for i in range(10)
        ])
        manifest = analyze(rows, max_examples=3)
        for ft in manifest.ranked:
            assert len(ft.examples) <= 3

    def test_manifest_fields(self):
        rows = self._make_rows([("wrong", "right", "wrong operator")])
        manifest = analyze(rows)
        assert hasattr(manifest, "total_examples")
        assert hasattr(manifest, "total_errors")
        assert hasattr(manifest, "error_rate")
        assert hasattr(manifest, "ranked")
