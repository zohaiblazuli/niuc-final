"""Task runner for PCC NIUC Guard."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def run_command(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def task_setup(_: argparse.Namespace) -> None:
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])


def task_lint(_: argparse.Namespace) -> None:
    run_command([sys.executable, "-m", "ruff", "check", "src", "tests"])
    run_command([sys.executable, "-m", "black", "--check", "src", "tests"])
    run_command([sys.executable, "-m", "isort", "--check-only", "src", "tests"])


def task_typecheck(_: argparse.Namespace) -> None:
    run_command([sys.executable, "-m", "mypy", "src"])


def task_test(_: argparse.Namespace) -> None:
    run_command([sys.executable, "-m", "pytest"])


def task_bench(_: argparse.Namespace) -> None:
    run_command([sys.executable, "-m", "pytest", "--benchmark-only"])


def task_run_demo(_: argparse.Namespace) -> None:
    run_command([sys.executable, "-m", "pccniuc.demo"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task runner for PCC NIUC Guard")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tasks = {
        "setup": task_setup,
        "lint": task_lint,
        "typecheck": task_typecheck,
        "test": task_test,
        "bench": task_bench,
        "run-demo": task_run_demo,
    }

    for name, handler in tasks.items():
        sub = subparsers.add_parser(name, help=f"Run the {name} task")
        sub.set_defaults(func=handler)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
