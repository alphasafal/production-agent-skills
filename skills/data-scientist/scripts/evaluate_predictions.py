#!/usr/bin/env python3
"""Score predictions against ground truth, and against a naive baseline.

Auto-detects classification vs. regression from the target dtype/cardinality.
Requires: pandas, numpy (see pyproject.toml's `data-scientist` extra).

Usage:
    python evaluate_predictions.py predictions.csv --y-true actual --y-pred predicted
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def is_classification(y_true: pd.Series) -> bool:
    return not pd.api.types.is_float_dtype(y_true) or y_true.nunique() <= 20


def classification_report(y_true: pd.Series, y_pred: pd.Series) -> str:
    lines = []
    accuracy = (y_true == y_pred).mean()
    majority_class = y_true.mode().iloc[0]
    baseline_accuracy = (y_true == majority_class).mean()

    lines.append(f"Task: classification ({y_true.nunique()} classes)")
    lines.append(f"Accuracy:          {accuracy:.4f}")
    lines.append(f"Baseline accuracy: {baseline_accuracy:.4f}  (always predict '{majority_class}')")
    delta = accuracy - baseline_accuracy
    lines.append(f"Delta vs baseline: {delta:+.4f}")
    if delta <= 0:
        lines.append("WARNING: model does not beat the naive majority-class baseline.")

    lines.append("\nPer-class breakdown:")
    for cls in sorted(y_true.unique(), key=str):
        mask_true = y_true == cls
        mask_pred = y_pred == cls
        tp = (mask_true & mask_pred).sum()
        fp = (~mask_true & mask_pred).sum()
        fn = (mask_true & ~mask_pred).sum()
        precision = tp / (tp + fp) if (tp + fp) else float("nan")
        recall = tp / (tp + fn) if (tp + fn) else float("nan")
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else float("nan")
        lines.append(f"  {cls}: precision={precision:.3f} recall={recall:.3f} f1={f1:.3f} support={mask_true.sum()}")

    return "\n".join(lines)


def regression_report(y_true: pd.Series, y_pred: pd.Series) -> str:
    lines = []
    errors = y_true - y_pred
    mae = errors.abs().mean()
    rmse = np.sqrt((errors ** 2).mean())
    baseline_pred = y_true.mean()
    baseline_errors = y_true - baseline_pred
    baseline_mae = baseline_errors.abs().mean()
    baseline_rmse = np.sqrt((baseline_errors ** 2).mean())
    ss_res = (errors ** 2).sum()
    ss_tot = ((y_true - y_true.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")

    lines.append("Task: regression")
    lines.append(f"MAE:            {mae:.4f}   (baseline mean-predictor MAE: {baseline_mae:.4f})")
    lines.append(f"RMSE:           {rmse:.4f}   (baseline mean-predictor RMSE: {baseline_rmse:.4f})")
    lines.append(f"R^2:            {r2:.4f}")
    if mae >= baseline_mae:
        lines.append("WARNING: model does not beat the naive mean-predictor baseline on MAE.")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("predictions", type=Path, help="CSV with true and predicted columns")
    parser.add_argument("--y-true", required=True, help="column name with ground truth")
    parser.add_argument("--y-pred", required=True, help="column name with predictions")
    args = parser.parse_args()

    if not args.predictions.is_file():
        print(f"ERROR: {args.predictions} not found", file=sys.stderr)
        return 1

    df = pd.read_csv(args.predictions)
    for col in (args.y_true, args.y_pred):
        if col not in df.columns:
            print(f"ERROR: column '{col}' not found in {args.predictions}", file=sys.stderr)
            return 1

    y_true, y_pred = df[args.y_true], df[args.y_pred]

    if is_classification(y_true):
        print(classification_report(y_true, y_pred))
    else:
        print(regression_report(y_true, y_pred))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
