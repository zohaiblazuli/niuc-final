"""NIUC guard pipeline orchestrating sanitization and policy enforcement."""

from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel

from .arbiter import Arbiter, ArbiterDecision
from .llm_client import LLMRequest, create_client
from .policy import PlannedToolCall
from .provenance import Message, Origin, ProvenanceMap, build_provenance
from .sanitizer import Sanitizer, SanitizedSummary


class PipelineInput(BaseModel):
    """Input payload for the NIUC pipeline."""

    messages: Sequence[Message]


class PipelineResult(BaseModel):
    """Result payload containing final text and enforcement metadata."""

    allowed: bool
    final_text: str
    sanitized: SanitizedSummary
    planned_tool_calls: list[PlannedToolCall]
    decision: ArbiterDecision


class Pipeline:
    """Three-stage NIUC pipeline."""

    def __init__(
        self,
        *,
        sanitizer: Sanitizer | None = None,
        arbiter: Arbiter | None = None,
        llm_provider: str | None = None,
    ):
        self._sanitizer = sanitizer or Sanitizer()
        self._arbiter = arbiter or Arbiter()
        self._llm = create_client(llm_provider)

    def run(self, messages: Sequence[Message]) -> PipelineResult:
        provenance = build_provenance(messages)
        sanitized = self._sanitizer.sanitize(provenance)
        user_intent = self._extract_user_intent(provenance)
        prompt = self._build_prompt(user_intent, sanitized)
        llm_response = self._llm.complete(LLMRequest(prompt=prompt))
        planned_tool_calls: list[PlannedToolCall] = []
        decision = self._arbiter.decide(
            final_text=llm_response.text,
            planned_tool_calls=planned_tool_calls,
            sanitized=sanitized,
        )

        final_text = llm_response.text if decision.allowed else ""
        return PipelineResult(
            allowed=decision.allowed,
            final_text=final_text,
            sanitized=sanitized,
            planned_tool_calls=planned_tool_calls,
            decision=decision,
        )

    @staticmethod
    def _extract_user_intent(provenance: ProvenanceMap) -> str:
        for span in reversed(provenance.spans):
            if span.origin is Origin.USER:
                return span.text.strip()
        return ""

    @staticmethod
    def _build_prompt(user_intent: str, sanitized: SanitizedSummary) -> str:
        lines = ["Sanitized summary:", sanitized.clean_text or "<empty>"]
        if sanitized.facts:
            lines.append("Facts: " + "; ".join(sanitized.facts))
        if sanitized.entities:
            lines.append("Entities: " + ", ".join(sanitized.entities))
        if user_intent:
            lines.append(f"User intent: {user_intent}")
        return "\n".join(lines)


__all__ = ["Pipeline", "PipelineInput", "PipelineResult"]

