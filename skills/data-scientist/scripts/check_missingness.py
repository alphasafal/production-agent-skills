#!/usr/bin/env python3
"""Report missingness per column and flag columns whose missingness co-occurs,
which is a hint that data isn't missing purely at random.

Requires: pandas, numpy (see pyproject.toml's `data-scientist` extra).

Usage:
    python check_missingness.py data.csv
    python check_missingness.py data.csv --threshold 0.3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError as exc:
    raise SystemExit(
        f"This script needs {exc.name}. Install with:  pip install pandas numpy\n"
        f"(or, from the repo root:  pip install -e '.[data-scientist]')"
    ) from exc


def missingness_report(df: pd.DataFrame, threshold: float) -> str:
    lines = []
    missing = df.isna().sum().sort_values(ascending=False)
    pct = (missing / len(df) * 100).round(2)

    lines.append("Missingness by column:")
    any_missing = False
    for col in df.columns:
        if missing[col] > 0:
            any_missing = True
            flag = " <-- above threshold" if pct[col] / 100 >= threshold else ""
            lines.append(f"  {col:<30} {missing[col]:<8} ({pct[col]}%){flag}")
    if not any_missing:
        lines.append("  (no missing values found)")
        return "\n".join(lines)

    missing_cols = [c for c in df.columns if missing[c] > 0]
    if len(missing_cols) >= 2:
        null_indicators = df[missing_cols].isna().astype(int)
        corr = null_indicators.corr()
        related = []
        for i, col_a in enumerate(missing_cols):
            for col_b in missing_cols[i + 1:]:
                value = corr.loc[col_a, col_b]
                if pd.notna(value) and abs(value) >= 0.5:
                    related.append(
                        f"  {col_a} <-> {col_b}: {value:.2f} "
                        f"(missingness likely related — investigate a shared cause, not MCAR)"
                    )
        if related:
            lines.append("\nCo-occurrence of missingness (correlation of is-null indicators):")
            lines.extend(related)
        else:
            lines.append(
                "\nNo pair of columns has strongly co-occurring missingness "
                "(all |correlation| < 0.5), which is consistent with — but does not "
                "prove — missing-at-random."
            )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--threshold", type=float, default=0.2, help="fraction missing to flag (default 0.2)")
    args = parser.parse_args()

    if not args.dataset.is_file():
        print(f"ERROR: {args.dataset} not found", file=sys.stderr)
        return 1

    df = pd.read_csv(args.dataset)
    print(missingness_report(df, args.threshold))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
