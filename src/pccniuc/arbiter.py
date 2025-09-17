"""Arbiter module coordinating policy enforcement."""

from __future__ import annotations

from pydantic import BaseModel

from .policy import PolicyEvaluator, PolicyInput, PlannedToolCall
from .sanitizer import SanitizedSummary


class ArbiterDecision(BaseModel):
    """Decision returned by the arbiter."""

    allowed: bool
    reasons: list[str]


class Arbiter:
    """High level policy enforcement orchestrator."""

    def __init__(self, evaluator: PolicyEvaluator | None = None):
        self._evaluator = evaluator or PolicyEvaluator()

    def decide(
        self,
        final_text: str,
        planned_tool_calls: list[PlannedToolCall],
        sanitized: SanitizedSummary,
    ) -> ArbiterDecision:
        """Evaluate the NIUC policy for the given response."""

        policy_input = PolicyInput(
            final_text=final_text,
            planned_tool_calls=planned_tool_calls,
            sanitized=sanitized,
        )
        policy_decision = self._evaluator.evaluate(policy_input)
        return ArbiterDecision(
            allowed=policy_decision.allowed,
            reasons=policy_decision.reasons,
        )


__all__ = ["Arbiter", "ArbiterDecision"]

