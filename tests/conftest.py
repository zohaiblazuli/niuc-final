"""Test configuration helpers."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_sys_path(path: Path) -> None:
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


ROOT = Path(__file__).resolve().parents[1]
_ensure_sys_path(ROOT)
_ensure_sys_path(ROOT / "src")
