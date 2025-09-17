"""Provider-agnostic LLM client interfaces for NIUC."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMRequest(BaseModel):
    """Input payload for a language-model completion."""

    prompt: str
    temperature: float = 0.0
    max_tokens: int | None = None


class LLMResponse(BaseModel):
    """Output payload from a language-model completion."""

    text: str
    tokens_used: int = 0
    latency_ms: float | None = None


class LLMClient(ABC):
    """Abstract base class for sync LLM clients."""

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute a completion request."""


class _UnavailableClient(LLMClient):
    """Backend placeholder that raises an informative error."""

    def __init__(self, provider: str):
        self._provider = provider

    def complete(self, request: LLMRequest) -> LLMResponse:  # pragma: no cover - error path
        raise RuntimeError(
            f"Provider '{self._provider}' is not available in the offline environment"
        )


class OllamaLocalClient(LLMClient):
    """Deterministic local backend used for tests and demos."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        summary = request.prompt.strip()
        token_estimate = max(1, len(summary.split()))
        return LLMResponse(text=summary, tokens_used=token_estimate, latency_ms=0.0)


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"Environment variable '{var_name}' must be set for this backend")
    return value


def create_client(provider: str | None = None) -> LLMClient:
    """Factory that returns a configured LLM client."""

    provider = (provider or os.getenv("NIUC_LLM_PROVIDER") or "ollama_local").lower()
    if provider == "ollama_local":
        return OllamaLocalClient()
    if provider == "openai_api":  # pragma: no cover - requires network
        _require_env("OPENAI_API_KEY")
        return _UnavailableClient(provider)
    if provider == "anthropic_api":  # pragma: no cover - requires network
        _require_env("ANTHROPIC_API_KEY")
        return _UnavailableClient(provider)
    if provider == "gemini_api":  # pragma: no cover - requires network
        _require_env("GEMINI_API_KEY")
        return _UnavailableClient(provider)
    raise ValueError(f"Unknown LLM provider '{provider}'")


__all__ = [
    "LLMClient",
    "LLMRequest",
    "LLMResponse",
    "OllamaLocalClient",
    "create_client",
]

