# Contributing Guide

Thanks for your interest in improving PCC NIUC Guard!

## Getting Started

1. Fork the repository and clone it locally.
2. Create and activate a Python 3.10+ virtual environment.
3. Install dependencies with `python tasks.py setup`.
4. Run `pre-commit install` to activate formatting and linting on commit.

## Development Workflow

- `python tasks.py lint` runs Ruff, Black, and iSort checks.
- `python tasks.py typecheck` runs mypy against `src/`.
- `python tasks.py test` runs the pytest suite.
- `python tasks.py bench` runs benchmark jobs (powered by pytest-benchmark).

Before opening a pull request:

- Update or add tests for changes.
- Ensure all linters and type checks pass.
- Document user-facing changes in `docs/` or `CHANGELOG.md` (if present).

## Commit Message Guidance

Use conventional commit prefixes when possible, e.g. `feat:`, `fix:`, `docs:`. Keep summaries under 72 characters and include context in the body when useful.

## Code of Conduct

Be respectful, inclusive, and constructive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).
