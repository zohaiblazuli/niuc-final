"""CLI demo for PCC NIUC Guard."""

from __future__ import annotations

from collections.abc import Sequence

from .guard import Guardrail, GuardResult


def _min_threshold(threshold: float):
    def check(values: Sequence[float]) -> GuardResult:
        if min(values, default=threshold) < threshold:
            return GuardResult(False, f"Minimum value dropped below {threshold}")
        return GuardResult(True, "Minimum threshold satisfied")

    return check


def main() -> None:
    guard = Guardrail(_min_threshold(0.8))
    sequence = [0.95, 0.9, 0.85]
    result = guard.evaluate(sequence)
    print("Sequence:", sequence)
    print("Result:", result.message)


if __name__ == "__main__":
    main()
