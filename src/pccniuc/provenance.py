"""Utilities for tracking provenance of conversation text."""

from __future__ import annotations

from enum import Enum
from typing import Iterable, List, Sequence

from pydantic import BaseModel, ConfigDict, Field


class TrustLevel(str, Enum):
    """Represents the trust level of a text span."""

    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"


class Origin(str, Enum):
    """The original source that produced a span of text."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    EXTERNAL = "external"

    @property
    def trust(self) -> TrustLevel:
        """Return the implied :class:`TrustLevel` for the origin."""

        if self in {Origin.SYSTEM, Origin.ASSISTANT}:
            return TrustLevel.TRUSTED
        return TrustLevel.UNTRUSTED


class Message(BaseModel):
    """Structured representation of a conversation message."""

    role: Origin
    content: str

    model_config = ConfigDict(frozen=True)


class TextSpan(BaseModel):
    """A contiguous span of text with provenance metadata."""

    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    text: str
    origin: Origin
    tag: TrustLevel

    @property
    def byte_length(self) -> int:
        """Length of the span in bytes."""

        return self.end - self.start


class ProvenanceMap(BaseModel):
    """Aggregated text with provenance spans."""

    text: str
    spans: List[TextSpan]

    def untrusted_spans(self) -> List[TextSpan]:
        """Return spans marked as untrusted."""

        return [span for span in self.spans if span.tag is TrustLevel.UNTRUSTED]

    def trusted_spans(self) -> List[TextSpan]:
        """Return spans marked as trusted."""

        return [span for span in self.spans if span.tag is TrustLevel.TRUSTED]

    def iter_spans(self, tag: TrustLevel | None = None) -> Iterable[TextSpan]:
        """Iterate over spans optionally filtered by trust level."""

        if tag is None:
            yield from self.spans
        else:
            yield from (span for span in self.spans if span.tag is tag)


def build_provenance(messages: Sequence[Message]) -> ProvenanceMap:
    """Construct a :class:`ProvenanceMap` from ordered messages.

    The resulting map concatenates message content with newline separators
    and tracks byte ranges for each span using UTF-8 encoding.
    """

    spans: list[TextSpan] = []
    pieces: list[str] = []
    byte_cursor = 0

    for index, message in enumerate(messages):
        if index:
            separator = "\n"
            pieces.append(separator)
            byte_cursor += len(separator.encode("utf-8"))

        encoded = message.content.encode("utf-8")
        start = byte_cursor
        end = start + len(encoded)
        spans.append(
            TextSpan(
                start=start,
                end=end,
                text=message.content,
                origin=message.role,
                tag=message.role.trust,
            )
        )
        pieces.append(message.content)
        byte_cursor = end

    return ProvenanceMap(text="".join(pieces), spans=spans)


__all__ = [
    "TrustLevel",
    "Origin",
    "Message",
    "TextSpan",
    "ProvenanceMap",
    "build_provenance",
]

