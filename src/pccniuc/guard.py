"""Simple guardrail primitives for NIUC pipelines."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass


@dataclass
class GuardResult:
    """Represents the outcome of a guardrail check."""

    passed: bool
    message: str = ""


class Guardrail:
    """Evaluate a sequence against guard conditions."""

    def __init__(self, *checks: Callable[[Sequence[float]], GuardResult]):
        if not checks:
            raise ValueError("Guardrail requires at least one check")
        self._checks = checks

    def evaluate(self, values: Iterable[float]) -> GuardResult:
        sequence = list(values)
        for check in self._checks:
            result = check(sequence)
            if not result.passed:
                return result
        return GuardResult(True, "All checks passed")
