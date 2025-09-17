"""Unit tests for guard module."""

import pytest

from pccniuc.guard import Guardrail, GuardResult


def _always_pass(_):
    return GuardResult(True, "ok")


def _always_fail(_):
    return GuardResult(False, "bad")


def _bool_pass(_):
    return True


def _bool_fail(_):
    return False


def _tuple_fail(_):
    return False, "tuple failure"


def _bad_result(_):
    return "invalid"


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


def test_guardrail_accepts_boolean_results():
    guard = Guardrail(_bool_pass)
    result = guard.evaluate([1, 2, 3])
    assert result.passed
    assert result.message == "All checks passed"


def test_guardrail_uses_default_message_for_boolean_failures():
    guard = Guardrail(_bool_fail)
    result = guard.evaluate([1, 2, 3])
    assert not result.passed
    assert result.message == "_bool_fail returned False"


def test_guardrail_accepts_tuple_results():
    guard = Guardrail(_always_pass, _tuple_fail)
    result = guard.evaluate([1, 2, 3])
    assert not result.passed
    assert result.message == "tuple failure"


def test_guardrail_rejects_unknown_result_types():
    guard = Guardrail(_bad_result)
    with pytest.raises(TypeError):
        guard.evaluate([1, 2, 3])
