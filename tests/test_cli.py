from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pccniuc import cli

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"


def test_parser_requires_subcommand() -> None:
    parser = cli.create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_parses_demo_arguments() -> None:
    parser = cli.create_parser()
    args = parser.parse_args(
        [
            "demo",
            "--intent",
            "safety run",
            "--external",
            "path/to/resource",
        ]
    )
    assert args.intent == "safety run"
    assert args.external == "path/to/resource"


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    if cwd is None:
        cwd = REPO_ROOT
    env = os.environ.copy()
    existing_path = env.get("PYTHONPATH")
    src_path = str(SRC_ROOT)
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{existing_path}" if existing_path else src_path
    )
    return subprocess.run(
        [sys.executable, "-m", "pccniuc.cli", *args],
        check=True,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def test_demo_command_runs(tmp_path: Path) -> None:
    external = tmp_path / "intent.txt"
    external.write_text("demo reference", encoding="utf-8")
    result = _run_cli(
        "demo",
        "--intent",
        "walkthrough",
        "--external",
        str(external),
    )
    assert "Sequence:" in result.stdout
    assert "walkthrough" in result.stdout
    assert str(external) in result.stdout


def test_eval_command_runs(tmp_path: Path) -> None:
    suite = tmp_path / "bench" / "cases"
    suite.mkdir(parents=True)
    result = _run_cli(
        "eval",
        "--suite",
        str(suite),
        "--provider",
        "ollama",
        "--model",
        "llama3",
    )
    lines = result.stdout.strip().splitlines()
    assert any("Running evaluation suite" in line for line in lines)
    payload = json.loads(lines[-1])
    assert payload == {
        "model": "llama3",
        "provider": "ollama",
        "status": "completed",
        "suite": str(suite),
    }


def test_trace_command_runs(tmp_path: Path) -> None:
    save_path = tmp_path / "trace" / "42.jsonl"
    result = _run_cli(
        "trace",
        "--case-id",
        "42",
        "--save",
        str(save_path),
    )
    assert save_path.exists()
    content = save_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1
    payload = json.loads(content[0])
    assert payload == {
        "case_id": 42,
        "path": str(save_path),
        "status": "captured",
    }
    assert f"Trace for case 42 written to {save_path}" in result.stdout
