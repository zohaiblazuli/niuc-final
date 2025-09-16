"""Benchmark scenarios for Guardrail evaluations."""

from __future__ import annotations

import random

from pccniuc.guard import Guardrail, GuardResult


def _noop_check(_):
    return GuardResult(True, "pass")


def test_guardrail_benchmark(benchmark):
    guard = Guardrail(_noop_check)
    dataset = [random.random() for _ in range(1000)]
    benchmark(guard.evaluate, dataset)
