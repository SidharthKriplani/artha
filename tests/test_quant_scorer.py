"""
Unit tests for quant-pareto-bench scorer and pareto logic.
Run: python -m pytest tests/test_quant_scorer.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "solutions" / "quant-pareto-bench"))

from scorer import score_exact, score_outputs
from pareto import ModelPoint, compute_pareto, _is_pareto_optimal


class TestScoreExact:

    def test_exact_string_match(self):
        assert score_exact("Paris", "Paris") == 1.0

    def test_substring_match(self):
        assert score_exact("The answer is 42.", "42") == 1.0

    def test_case_insensitive(self):
        assert score_exact("paris", "Paris") == 1.0

    def test_numeric_exact(self):
        assert score_exact("105", "105") == 1.0

    def test_numeric_within_tolerance(self):
        # 100 vs 100.5 is within 1%
        assert score_exact("100.5", "100") == 1.0

    def test_numeric_outside_tolerance(self):
        # 54 vs 56 — >1% difference
        assert score_exact("54", "56") == 0.0

    def test_complete_mismatch(self):
        score = score_exact("banana", "apple")
        assert score < 1.0

    def test_empty_reference(self):
        # shouldn't crash
        result = score_exact("something", "")
        assert isinstance(result, float)

    def test_partial_word_overlap(self):
        score = score_exact("The capital is Tokyo Japan", "Tokyo")
        assert score == 1.0  # substring match


class TestScoreOutputs:

    def test_returns_list_of_correct_length(self):
        scores = score_outputs(["q1", "q2"], ["42", "Paris"], ["42", "London"])
        assert len(scores) == 2

    def test_none_references_returns_none_scores(self):
        scores = score_outputs(["q1"], ["42"], None)
        assert scores == [None]

    def test_correct_answers_score_1(self):
        scores = score_outputs(["q"], ["42"], ["42"])
        assert scores[0] == 1.0

    def test_wrong_answers_score_below_1(self):
        scores = score_outputs(["q"], ["wrong"], ["right"])
        assert scores[0] < 1.0


class TestParetoFrontier:

    def _make_point(self, label, tps, acc):
        return ModelPoint(
            quant_label=label,
            model_path=f"{label}.gguf",
            avg_tokens_per_second=tps,
            avg_accuracy=acc,
            avg_latency_ms=1000 / tps,
            file_size_mb=None,
        )

    def test_single_point_is_optimal(self):
        p = self._make_point("Q4_K_M", 60.0, 0.85)
        assert _is_pareto_optimal(p, [p]) is True

    def test_dominated_point_is_not_optimal(self):
        good = self._make_point("Q8_0",   40.0, 0.90)
        fast = self._make_point("Q4_K_M", 60.0, 0.85)
        bad  = self._make_point("Q2_K",   30.0, 0.70)  # slower AND less accurate than good
        assert _is_pareto_optimal(bad, [good, fast, bad]) is False

    def test_pareto_optimal_on_both_axes(self):
        fast_accurate = self._make_point("Q4_K_M", 60.0, 0.85)
        slow_accurate = self._make_point("F16",    20.0, 0.92)
        fast_bad      = self._make_point("Q2_K",   90.0, 0.60)
        all_points = [fast_accurate, slow_accurate, fast_bad]
        # Q4_K_M: beats slow_accurate on speed, beats fast_bad on accuracy → optimal
        assert _is_pareto_optimal(fast_accurate, all_points) is True
        # F16: best accuracy, even though slow → optimal
        assert _is_pareto_optimal(slow_accurate, all_points) is True

    def test_compute_pareto_sorted_by_speed(self):
        points = [
            self._make_point("Q4", 60.0, 0.85),
            self._make_point("Q8", 40.0, 0.90),
            self._make_point("F16", 20.0, 0.92),
        ]
        result = compute_pareto(points)
        speeds = [p.avg_tokens_per_second for p, _ in result]
        assert speeds == sorted(speeds, reverse=True)

    def test_no_accuracy_all_optimal(self):
        p1 = ModelPoint("Q4", "q4.gguf", 60.0, None, 100.0, None)
        p2 = ModelPoint("Q8", "q8.gguf", 40.0, None, 150.0, None)
        assert _is_pareto_optimal(p1, [p1, p2]) is True
        assert _is_pareto_optimal(p2, [p1, p2]) is True
