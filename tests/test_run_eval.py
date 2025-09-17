"""Tests for the benchmark evaluation CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from bench.run_eval import _print_summary


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_print_summary_handles_zero_attack_cases() -> None:
    lines: list[str] = []
    _print_summary(
        "benign-only",
        attack_cases=0,
        attack_successes=0,
        benign_cases=2,
        benign_correct=2,
        printer=lines.append,
    )
    assert len(lines) == 1
    assert "ASR: n/a" in lines[0]
    assert "Benign accuracy: 100.0%" in lines[0]


def test_cli_reports_benign_accuracy_for_zero_attack_family() -> None:
    repo = _repo_root()
    script = repo / "bench" / "run_eval.py"
    cases_dir = repo / "bench" / "cases"
    result = subprocess.run(
        [sys.executable, str(script), str(cases_dir)],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = result.stdout
    assert "benign-only" in stdout
    assert "ASR: n/a" in stdout
    assert "Benign accuracy: 100.0% (2/2)" in stdout
