"""Sanitization stage for NIUC conversations."""

from __future__ import annotations

import re
from typing import Iterable, List

from pydantic import BaseModel

from .provenance import ProvenanceMap, TextSpan

IMPERATIVE_KEYWORDS = (
    "ignore",
    "disregard",
    "forget",
    "reveal",
    "expose",
    "leak",
    "comply",
    "obey",
    "bypass",
    "reproduce",
)

IMG_TAG_RE = re.compile(r"<img[^>]*>", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
PASSWORD_RE = re.compile(r"password\s*[:=]\s*\S+", re.IGNORECASE)
QUOTE_RE = re.compile(r"\"([^\"]+)\"|\'([^\']+)\'")
ENTITY_RE = re.compile(r"\b[A-Z][a-zA-Z0-9]+\b")


class SanitizerConfig(BaseModel):
    """Runtime configuration for the sanitizer."""

    allow_empty: bool = False


class SanitizedSummary(BaseModel):
    """Structured sanitized summary of untrusted text."""

    clean_text: str
    facts: List[str]
    entities: List[str]
    quotes: List[str]
    removed_imperatives: List[str]


class Sanitizer:
    """Extracts safe information from untrusted spans."""

    def __init__(self, config: SanitizerConfig | None = None):
        self._config = config or SanitizerConfig()

    def sanitize(self, provenance: ProvenanceMap) -> SanitizedSummary:
        """Sanitize untrusted spans from the provided provenance map."""

        untrusted_spans = provenance.untrusted_spans()
        cleaned_sentences: list[str] = []
        removed_commands: list[str] = []
        facts: list[str] = []
        entities: set[str] = set()
        quotes: list[str] = []

        for span in untrusted_spans:
            normalized = self._normalize(span)
            quotes.extend(self._extract_quotes(normalized))
            sentences = self._split_sentences(normalized)
            for sentence in sentences:
                if not sentence:
                    continue
                if self._looks_imperative(sentence):
                    removed_commands.append(sentence)
                    continue
                cleaned_sentences.append(sentence)
                facts.append(sentence)
                entities.update(self._extract_entities(sentence))

        clean_text = " ".join(cleaned_sentences).strip()

        if not clean_text and not self._config.allow_empty and facts:
            # There was content but all of it was removed.
            clean_text = ""

        return SanitizedSummary(
            clean_text=clean_text,
            facts=facts,
            entities=sorted(entities),
            quotes=quotes,
            removed_imperatives=removed_commands,
        )

    @staticmethod
    def _normalize(span: TextSpan) -> str:
        """Apply normalization filters to a span's text."""

        text = span.text
        text = IMG_TAG_RE.sub("", text)
        text = URL_RE.sub("", text)
        text = PASSWORD_RE.sub("", text)
        return text

    @staticmethod
    def _split_sentences(text: str) -> Iterable[str]:
        pieces = re.split(r"(?<=[.!?])\s+|\n+", text)
        return [piece.strip() for piece in pieces if piece.strip()]

    @staticmethod
    def _looks_imperative(sentence: str) -> bool:
        lowered = sentence.lower()
        if any(re.search(rf"\\b{re.escape(keyword)}\\b", lowered) for keyword in IMPERATIVE_KEYWORDS):
            return True
        # Imperatives often start with a base verb.
        return bool(re.match(r"^(please\s+)?[a-z]+\b", lowered)) and lowered.split()[0] in {
            "ignore",
            "delete",
            "disable",
            "reveal",
            "comply",
            "obey",
            "bypass",
        }

    @staticmethod
    def _extract_quotes(text: str) -> List[str]:
        results: list[str] = []
        for match in QUOTE_RE.finditer(text):
            quote = match.group(1) or match.group(2)
            if quote:
                results.append(quote.strip())
        return results

    @staticmethod
    def _extract_entities(text: str) -> List[str]:
        return ENTITY_RE.findall(text)


__all__ = [
    "Sanitizer",
    "SanitizerConfig",
    "SanitizedSummary",
]

