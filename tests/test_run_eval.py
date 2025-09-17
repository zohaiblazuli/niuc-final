"""Tests for the benchmarking evaluation helpers."""

from bench.run_eval import evaluate_suite


def test_evaluate_suite_treats_allow_decision_as_permitted() -> None:
    """Regression test for case-insensitive ``decision`` parsing."""

    def detector(_case: object) -> dict[str, str]:
        return {"decision": "allow"}

    results = evaluate_suite([{"input": "example"}], detector)
    assert len(results) == 1
    assert results[0].blocked is False

