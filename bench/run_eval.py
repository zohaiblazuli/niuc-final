"""Utilities to summarize evaluation cases for NIUC guardrails."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator


DEFAULT_CASES_DIR = Path(__file__).parent / "cases"


@dataclass
class FamilyStats:
    """Aggregated statistics for a single attack family."""

    attack_cases: int = 0
    attack_successes: int = 0
    benign_cases: int = 0
    benign_correct: int = 0

    def register_attack(self, success: bool) -> None:
        self.attack_cases += 1
        if success:
            self.attack_successes += 1

    def register_benign(self, correct: bool) -> None:
        self.benign_cases += 1
        if correct:
            self.benign_correct += 1

    def benign_accuracy(self) -> float | None:
        if self.benign_cases == 0:
            return None
        return self.benign_correct / self.benign_cases


def _coerce_flag(entry: object, key: str) -> bool:
    """Return a boolean flag from a JSON entry."""

    if isinstance(entry, dict):
        if key not in entry:
            raise ValueError(f"Missing '{key}' field in {entry!r}")
        value = entry[key]
    else:
        value = entry

    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        value_lower = value.strip().lower()
        if value_lower in {"true", "1", "yes", "y"}:
            return True
        if value_lower in {"false", "0", "no", "n"}:
            return False
    raise ValueError(f"Unsupported flag value {value!r}")


def _iter_family_files(cases_dir: Path) -> Iterator[Path]:
    for path in sorted(cases_dir.glob("*.json")):
        if path.is_file():
            yield path


def _load_family_stats(path: Path) -> tuple[str, FamilyStats]:
    data = json.loads(path.read_text(encoding="utf-8"))
    family = data.get("family") or path.stem
    stats = FamilyStats()

    for attack_entry in data.get("attacks", []):
        stats.register_attack(_coerce_flag(attack_entry, "success"))

    for benign_entry in data.get("benign", []):
        stats.register_benign(_coerce_flag(benign_entry, "correct"))

    return family, stats


def _collect_stats(cases_dir: Path) -> dict[str, FamilyStats]:
    stats_by_family: dict[str, FamilyStats] = {}
    for path in _iter_family_files(cases_dir):
        family, stats = _load_family_stats(path)
        existing = stats_by_family.get(family)
        if existing is None:
            stats_by_family[family] = stats
        else:
            existing.attack_cases += stats.attack_cases
            existing.attack_successes += stats.attack_successes
            existing.benign_cases += stats.benign_cases
            existing.benign_correct += stats.benign_correct
    return stats_by_family


def _format_percent(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    percentage = (numerator / denominator) * 100
    return f"{percentage:.1f}%"


def _print_summary(
    family: str,
    attack_cases: int,
    attack_successes: int,
    benign_cases: int,
    benign_correct: int,
    *,
    printer: Callable[[str], None] = print,
) -> None:
    """Emit a human-readable summary for a family."""

    attack_metric = _format_percent(attack_successes, attack_cases)
    benign_metric = _format_percent(benign_correct, benign_cases)

    attack_details = f"ASR: {attack_metric} ({attack_successes}/{attack_cases})"
    if attack_cases == 0:
        attack_details = "ASR: n/a (0/0)"

    if benign_cases == 0:
        benign_details = "Benign accuracy: n/a"
    else:
        benign_details = (
            f"Benign accuracy: {benign_metric} ({benign_correct}/{benign_cases})"
        )

    printer(f"{family}: {attack_details} | {benign_details}")


def _run(cases_dir: Path, *, printer: Callable[[str], None] = print) -> None:
    stats_by_family = _collect_stats(cases_dir)
    if not stats_by_family:
        printer(f"No cases found in {cases_dir}")
        return

    for family in sorted(stats_by_family):
        stats = stats_by_family[family]
        _print_summary(
            family,
            stats.attack_cases,
            stats.attack_successes,
            stats.benign_cases,
            stats.benign_correct,
            printer=printer,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize attack and benign evaluation cases",
    )
    parser.add_argument(
        "cases_dir",
        nargs="?",
        type=Path,
        default=DEFAULT_CASES_DIR,
        help="Directory containing family JSON definitions",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    cases_dir = args.cases_dir
    if not cases_dir.exists() or not cases_dir.is_dir():
        parser.error(f"Cases directory does not exist: {cases_dir}")
    _run(cases_dir)


if __name__ == "__main__":
    main()
