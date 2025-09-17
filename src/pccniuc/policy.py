"""Policy evaluation for NIUC guardrails."""

from __future__ import annotations

from typing import Iterable, List

from pydantic import BaseModel, Field

from .provenance import TrustLevel
from .sanitizer import SanitizedSummary


class ToolArgument(BaseModel):
    """Structured representation of a single tool argument."""

    key: str
    value: str
    provenance: TrustLevel = TrustLevel.TRUSTED


class PlannedToolCall(BaseModel):
    """Tool invocation the model plans to execute."""

    name: str
    arguments: List[ToolArgument] = Field(default_factory=list)


class PolicyInput(BaseModel):
    """Inputs required to evaluate the NIUC policy."""

    final_text: str
    planned_tool_calls: List[PlannedToolCall] = Field(default_factory=list)
    sanitized: SanitizedSummary


class PolicyDecision(BaseModel):
    """Outcome of policy evaluation."""

    allowed: bool
    reasons: List[str] = Field(default_factory=list)


class PolicyEvaluator:
    """Evaluate NIUC guardrail policies."""

    def evaluate(self, data: PolicyInput) -> PolicyDecision:
        violations: list[str] = []

        violations.extend(self._check_removed_imperatives(data))
        violations.extend(self._check_tool_arguments(data.planned_tool_calls))

        return PolicyDecision(allowed=not violations, reasons=violations)

    @staticmethod
    def _check_removed_imperatives(data: PolicyInput) -> List[str]:
        violations: list[str] = []
        lowered_final = data.final_text.lower()
        for imperative in data.sanitized.removed_imperatives:
            if imperative.lower() in lowered_final:
                violations.append(
                    "Final response attempted to repeat an untrusted imperative"
                )
        return violations

    @staticmethod
    def _check_tool_arguments(tool_calls: Iterable[PlannedToolCall]) -> List[str]:
        violations: list[str] = []
        for call in tool_calls:
            for argument in call.arguments:
                if argument.provenance is TrustLevel.UNTRUSTED:
                    violations.append(
                        f"Tool `{call.name}` argument `{argument.key}` derives from untrusted text"
                    )
        return violations


__all__ = [
    "PolicyEvaluator",
    "PolicyDecision",
    "PolicyInput",
    "PlannedToolCall",
    "ToolArgument",
]

