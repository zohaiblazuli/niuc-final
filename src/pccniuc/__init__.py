"""Core PCC NIUC Guard package."""

from ._version import __version__
from .guard import Guardrail

__all__ = ["Guardrail", "__version__"]
