"""Simple guardrail primitives for NIUC pipelines."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass


@dataclass
class GuardResult:
    """Represents the outcome of a guardrail check."""

    passed: bool
    message: str = ""


GuardCheckResult = GuardResult | bool | tuple[bool, str | None]
GuardCheck = Callable[[Sequence[float]], GuardCheckResult]


def _describe_check(check: Callable[..., object]) -> str:
    """Return a human readable name for a guard check."""

    name = getattr(check, "__name__", "")
    return name or check.__class__.__name__


def _coerce_result(check: GuardCheck, result: GuardCheckResult) -> GuardResult:
    """Normalize various guard check return types to :class:`GuardResult`."""

    if isinstance(result, GuardResult):
        return result
    if isinstance(result, bool):
        message = "" if result else f"{_describe_check(check)} returned False"
        return GuardResult(result, message)
    if isinstance(result, tuple):
        if not result:
            raise ValueError(f"{_describe_check(check)} returned an empty tuple")
        if len(result) > 2:
            raise ValueError(
                f"{_describe_check(check)} returned a tuple with more than two elements"
            )
        passed = result[0]
        message = result[1] if len(result) == 2 else ""
        if not isinstance(passed, bool):
            raise TypeError(
                f"{_describe_check(check)} returned a tuple whose first element "
                f"is not a bool (got {type(passed).__name__})"
            )
        if message is None:
            message = ""
        elif not isinstance(message, str):
            raise TypeError(
                f"{_describe_check(check)} returned a tuple whose second element "
                f"is not a string (got {type(message).__name__})"
            )
        return GuardResult(passed, message)
    raise TypeError(
        f"{_describe_check(check)} returned unsupported result type "
        f"{type(result).__name__}"
    )


class Guardrail:
    """Evaluate a sequence against guard conditions."""

    def __init__(self, *checks: GuardCheck):
        if not checks:
            raise ValueError("Guardrail requires at least one check")
        self._checks = checks

    def evaluate(self, values: Iterable[float]) -> GuardResult:
        sequence = list(values)
        for check in self._checks:
            result = _coerce_result(check, check(sequence))
            if not result.passed:
                return result
        return GuardResult(True, "All checks passed")
