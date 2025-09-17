"""Utilities for running detector evaluation suites."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

__all__ = ["EvaluationResult", "evaluate_suite", "_extract_blocked"]

_TRUE_STRINGS = {"true", "t", "1", "yes", "y"}
_FALSE_STRINGS = {"false", "f", "0", "no", "n"}


@dataclass(slots=True)
class EvaluationResult:
    """Normalized representation of a detector decision for a single case."""

    case: Any
    blocked: bool
    raw_decision: Any


def _coerce_bool(value: Any, *, field: str) -> bool:
    """Coerce *value* into a boolean.

    Strings such as ``"true"`` or ``"false"`` are accepted for convenience.
    ``ValueError`` is raised when the value cannot be interpreted as a boolean.
    """

    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().casefold()
        if lowered in _TRUE_STRINGS:
            return True
        if lowered in _FALSE_STRINGS:
            return False
    raise ValueError(f"Cannot coerce {field} value {value!r} to bool.")


def _normalize_decision(decision: Any) -> bool:
    """Normalize a detector decision to a blocked flag."""

    if isinstance(decision, bool):
        return decision
    if isinstance(decision, str):
        lowered = decision.strip().casefold()
        if lowered == "block":
            return True
        if lowered == "allow":
            return False
        raise ValueError(f"Unrecognised decision value: {decision!r}")
    raise ValueError(f"Unsupported decision type: {type(decision)!r}")


def _extract_blocked(result: Any) -> bool:
    """Extract the ``blocked`` flag from *result*.

    ``result`` may already be a boolean, contain a ``"blocked"`` key, or
    provide a ``"decision"`` field indicating whether the detector chose to
    block or allow the sample.  ``ValueError`` is raised when the structure is
    not understood.
    """

    if isinstance(result, Mapping):
        if "blocked" in result:
            return _coerce_bool(result["blocked"], field="blocked")
        if "decision" in result:
            return _normalize_decision(result["decision"])
    if isinstance(result, bool):
        return result
    if isinstance(result, str):
        return _normalize_decision(result)
    raise ValueError(f"Unable to determine blocked flag from {result!r}")


def evaluate_suite(cases: Iterable[Any], detector: Callable[[Any], Any]) -> list[EvaluationResult]:
    """Run *detector* across *cases* and return normalized results."""

    evaluations: list[EvaluationResult] = []
    for case in cases:
        raw_decision = detector(case)
        blocked = _extract_blocked(raw_decision)
        evaluations.append(
            EvaluationResult(case=case, blocked=blocked, raw_decision=raw_decision)
        )
    return evaluations

