#!/usr/bin/env python3
"""Detect exact duplicate rows, and duplicate key values when a key column is given.

Requires: pandas (see pyproject.toml's `data-scientist` extra).

Usage:
    python detect_duplicates.py data.csv
    python detect_duplicates.py data.csv --key customer_id
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


def report_duplicates(df: pd.DataFrame, key: str | None) -> str:
    lines = []
    exact_dupes = df[df.duplicated(keep=False)]
    lines.append(f"Exact duplicate rows: {len(exact_dupes)} ({df.duplicated().sum()} removable)")
    if len(exact_dupes) and len(exact_dupes) <= 20:
        lines.append(exact_dupes.to_string())

    if key:
        if key not in df.columns:
            lines.append(f"\nERROR: key column '{key}' not found in dataset")
            return "\n".join(lines)
        key_counts = df[key].value_counts()
        dup_keys = key_counts[key_counts > 1]
        lines.append(f"\nDuplicate '{key}' values: {len(dup_keys)} key(s) appear more than once")
        if len(dup_keys):
            lines.append(dup_keys.to_string())
            lines.append(
                "\nMultiple rows per key can be legitimate (e.g. one row per event) "
                "or a bug (e.g. one row per entity expected) — confirm which against "
                "the intended grain of this dataset before dropping anything."
            )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--key", help="column that should be unique (e.g. an ID column)")
    args = parser.parse_args()

    if not args.dataset.is_file():
        print(f"ERROR: {args.dataset} not found", file=sys.stderr)
        return 1

    df = pd.read_csv(args.dataset)
    print(report_duplicates(df, args.key))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
