"""Unit tests for guard module."""

from pccniuc.guard import Guardrail, GuardResult


def _always_pass(_):
    return GuardResult(True, "ok")


def _always_fail(_):
    return GuardResult(False, "bad")


def test_guardrail_passes_when_all_checks_succeed():
    guard = Guardrail(_always_pass)
    result = guard.evaluate([1, 2, 3])
    assert result.passed
    assert result.message == "All checks passed"


def test_guardrail_returns_first_failed_result():
    guard = Guardrail(_always_pass, _always_fail)
    result = guard.evaluate([1, 2, 3])
    assert not result.passed
    assert result.message == "bad"


def test_guardrail_requires_at_least_one_check():
    try:
        Guardrail()
    except ValueError as exc:
        assert "at least one" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Guardrail accepted no checks")
