#!/usr/bin/env python3
"""Flag features that plausibly leak information about the target.

This is a heuristic screen, not a guarantee — it catches the common,
mechanical cases (near-perfect correlation, suspiciously-named columns,
a feature that is a deterministic function of the target) so a human/agent
can investigate the flagged columns rather than every column equally.

Requires: pandas, numpy (see pyproject.toml's `data-scientist` extra).

Usage:
    python check_leakage.py data.csv --target outcome
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SUSPICIOUS_NAME_SUBSTRINGS = ["leak", "target", "label", "outcome", "result", "future"]


def check_leakage(df: pd.DataFrame, target: str, corr_threshold: float) -> str:
    lines = []
    if target not in df.columns:
        return f"ERROR: target column '{target}' not found in dataset"

    feature_cols = [c for c in df.columns if c != target]
    is_numeric_target = pd.api.types.is_numeric_dtype(df[target])

    lines.append(f"Checking {len(feature_cols)} feature(s) against target '{target}'\n")

    flagged = []

    if is_numeric_target:
        for col in feature_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                valid = df[[col, target]].dropna()
                if len(valid) < 2:
                    continue
                corr = valid[col].corr(valid[target])
                if pd.notna(corr) and abs(corr) >= corr_threshold:
                    flagged.append((col, f"correlation with target = {corr:.3f}"))

    for col in feature_cols:
        lowered = col.lower()
        if any(s in lowered for s in SUSPICIOUS_NAME_SUBSTRINGS):
            flagged.append((col, "column name suggests it may be derived from the target"))

    for col in feature_cols:
        if df[col].nunique(dropna=True) == df[target].nunique(dropna=True) and len(df) > 1:
            try:
                mapping = df[[col, target]].dropna().groupby(col)[target].nunique()
                if (mapping <= 1).all() and len(mapping) > 1:
                    flagged.append((col, "appears to be a deterministic 1:1 encoding of the target"))
            except (TypeError, ValueError):
                pass

    if not flagged:
        lines.append("No leakage signals found by this heuristic screen.")
        lines.append("This does NOT rule out leakage from timing (feature not yet available at")
        lines.append("prediction time) — that requires knowing the data collection process, not")
        lines.append("just the column values. See references/data-leakage.md.")
    else:
        lines.append("Flagged feature(s) — investigate before including in modeling:")
        seen = set()
        for col, reason in flagged:
            key = (col, reason)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"  {col}: {reason}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--target", required=True, help="name of the target/outcome column")
    parser.add_argument("--corr-threshold", type=float, default=0.95, help="abs correlation to flag (default 0.95)")
    args = parser.parse_args()

    if not args.dataset.is_file():
        print(f"ERROR: {args.dataset} not found", file=sys.stderr)
        return 1

    df = pd.read_csv(args.dataset)
    print(check_leakage(df, args.target, args.corr_threshold))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
