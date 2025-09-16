# Agent Operations Guide

Welcome to PCC NIUC Guard. This document captures expectations for AI coding agents working in this repo.

## Environment

- Target Python: 3.10 - 3.12.
- Install tooling with `python tasks.py setup` (uses pip extras defined in `pyproject.toml`).
- Always run inside a virtual environment; do not pollute the system interpreter.

## Core Commands

- Run the full formatter suite: `python tasks.py lint`.
- Static type checks: `python tasks.py typecheck`.
- Tests (unit + pytest plugins): `python tasks.py test`.
- Benchmarks: `python tasks.py bench` (collects pytest benchmarks when available).
- Demo driver for quick validation: `python tasks.py run-demo`.

## Data Dependencies

Some integrations require local fixture datasets. Pull the latest sample bundle with:

```bash
python scripts/pull_datasets.py
```

The script is idempotent and safe to run multiple times.

## Repository Conventions

- Library code lives under `src/pccniuc/`; keep modules importable without side effects.
- Mirror code structure under `tests/` and prefer `pytest` style assertions.
- Maintain type coverage - new modules should have `mypy`-clean annotations.
- Prefer functional, side-effect free helpers; when stateful, document expectations via docstrings.
- Document developer-facing workflows in `docs/` and keep `AGENTS.md` updated as tooling evolves.

Thanks for keeping automation-friendly practices in mind and leaving the tree tidy after each task.
