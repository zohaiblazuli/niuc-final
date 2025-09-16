"""Utility to prepare local datasets for development."""

from __future__ import annotations

import pathlib

DATASETS = {
    "sample_metrics.csv": "metric,value\naccuracy,0.99\nprecision,0.97\n",
}


def main() -> None:
    data_dir = pathlib.Path("examples") / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for filename, contents in DATASETS.items():
        path = data_dir / filename
        path.write_text(contents, encoding="utf-8")
    print(f"Wrote {len(DATASETS)} dataset(s) to {data_dir}")


if __name__ == "__main__":
    main()
