"""Utility helpers for reporting NIUC metrics."""

from __future__ import annotations

from statistics import mean
from typing import Sequence

from pydantic import BaseModel


class MetricSample(BaseModel):
    """Single pipeline evaluation sample."""

    allowed: bool
    is_attack: bool
    latency_ms: float = 0.0
    token_cost: int = 0


class MetricReport(BaseModel):
    """Aggregated metrics for a batch of samples."""

    attack_success_rate: float
    benign_accuracy: float
    false_positive_rate: float
    avg_latency_ms: float
    avg_token_cost: float


def compute_metrics(samples: Sequence[MetricSample]) -> MetricReport:
    if not samples:
        raise ValueError("At least one sample is required to compute metrics")

    attack_samples = [s for s in samples if s.is_attack]
    benign_samples = [s for s in samples if not s.is_attack]

    attack_success_rate = _rate(attack_samples, lambda s: s.allowed)
    benign_accuracy = _rate(benign_samples, lambda s: s.allowed)
    false_positive_rate = _rate(benign_samples, lambda s: not s.allowed)
    avg_latency = mean(s.latency_ms for s in samples)
    avg_token_cost = mean(s.token_cost for s in samples)

    return MetricReport(
        attack_success_rate=attack_success_rate,
        benign_accuracy=benign_accuracy,
        false_positive_rate=false_positive_rate,
        avg_latency_ms=avg_latency,
        avg_token_cost=avg_token_cost,
    )


def _rate(samples: Sequence[MetricSample], predicate) -> float:
    if not samples:
        return 0.0
    hits = sum(1 for sample in samples if predicate(sample))
    return hits / len(samples)


__all__ = ["MetricSample", "MetricReport", "compute_metrics"]

