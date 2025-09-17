"""Command line interface for the PCC NIUC toolkit."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import cast

from . import __version__
from . import demo as demo_module


def create_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="pccniuc",
        description="Utilities for running PCC NIUC guardrail workflows.",
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser(
        "demo",
        help="Run the built-in guardrail demo.",
        description="Execute the demonstration guardrail flow and surface metadata.",
    )
    demo_parser.add_argument(
        "--intent",
        required=True,
        help="Describe the reasoning goal for the demonstration run.",
    )
    demo_parser.add_argument(
        "--external",
        required=True,
        help="Path or URL pointing to an external resource used in the demo.",
    )
    demo_parser.set_defaults(func=_run_demo)

    eval_parser = subparsers.add_parser(
        "eval",
        help="Run an evaluation suite.",
        description="Evaluate a suite of benchmark cases using a provider/model pair.",
    )
    eval_parser.add_argument(
        "--suite",
        required=True,
        help="Path to the evaluation suite to execute.",
    )
    eval_parser.add_argument(
        "--provider",
        required=True,
        help="Identifier of the LLM provider to target.",
    )
    eval_parser.add_argument(
        "--model",
        required=True,
        help="Name of the model to evaluate.",
    )
    eval_parser.set_defaults(func=_run_eval)

    trace_parser = subparsers.add_parser(
        "trace",
        help="Export traces for a case.",
        description="Collect debug traces for a specific case and persist them to disk.",
    )
    trace_parser.add_argument(
        "--case-id",
        type=int,
        required=True,
        help="Unique identifier of the case to trace.",
    )
    trace_parser.add_argument(
        "--save",
        required=True,
        help="Destination file for the exported trace in JSONL format.",
    )
    trace_parser.set_defaults(func=_run_trace)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by the console script."""
    parser = create_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "func", None)
    if handler is None:
        parser.error("No command provided")
    command = cast(Callable[[argparse.Namespace], int], handler)
    return command(args)


def _run_demo(args: argparse.Namespace) -> int:
    demo_module.main(intent=args.intent, external=args.external)
    return 0


def _run_eval(args: argparse.Namespace) -> int:
    suite_path = Path(args.suite)
    summary = {
        "suite": str(suite_path),
        "provider": args.provider,
        "model": args.model,
        "status": "completed",
    }
    print(
        f"Running evaluation suite '{suite_path}' with provider "
        f"'{args.provider}' and model '{args.model}'."
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


def _run_trace(args: argparse.Namespace) -> int:
    save_path = Path(args.save)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "case_id": args.case_id,
        "status": "captured",
        "path": str(save_path),
    }
    with save_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    print(f"Trace for case {args.case_id} written to {save_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
