#!/usr/bin/env python3
"""Profile a tabular dataset: shape, dtypes, missingness overview, sample rows.

Requires: pandas, numpy (see pyproject.toml's `data-scientist` extra).

Usage:
    python profile_dataset.py data.csv
    python profile_dataset.py data.csv --rows 10
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
except ImportError as exc:
    raise SystemExit(
        f"This script needs {exc.name}. Install with:  pip install pandas numpy\n"
        f"(or, from the repo root:  pip install -e '.[data-scientist]')"
    ) from exc


def profile(df: pd.DataFrame, sample_rows: int) -> str:
    lines = []
    lines.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns\n")

    lines.append("Columns:")
    for col in df.columns:
        dtype = df[col].dtype
        n_missing = df[col].isna().sum()
        n_unique = df[col].nunique(dropna=True)
        lines.append(f"  {col:<30} {str(dtype):<10} missing={n_missing:<6} unique={n_unique}")
    lines.append("")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        lines.append("Numeric summary:")
        lines.append(df[numeric_cols].describe().to_string())
        lines.append("")

    lines.append(f"Sample rows (first {sample_rows}):")
    lines.append(df.head(sample_rows).to_string())
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", type=Path, help="path to a CSV file")
    parser.add_argument("--rows", type=int, default=5, help="number of sample rows to print")
    args = parser.parse_args()

    if not args.dataset.is_file():
        print(f"ERROR: {args.dataset} not found", file=sys.stderr)
        return 1

    df = pd.read_csv(args.dataset)
    print(profile(df, args.rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
