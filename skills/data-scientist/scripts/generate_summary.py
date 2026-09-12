#!/usr/bin/env python3
"""Run the deterministic data-quality checks (profile, missingness, duplicates,
optionally leakage) and print one consolidated summary.

This is a convenience wrapper — each check also runs standalone via its own
script. Requires: pandas, numpy (see pyproject.toml's `data-scientist` extra).

Usage:
    python generate_summary.py data.csv
    python generate_summary.py data.csv --target outcome --key id
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_leakage import check_leakage  # noqa: E402
from check_missingness import missingness_report  # noqa: E402
from detect_duplicates import report_duplicates  # noqa: E402
from profile_dataset import profile  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--target", help="target/outcome column, enables leakage check")
    parser.add_argument("--key", help="column expected to be unique, for duplicate-key check")
    args = parser.parse_args()

    if not args.dataset.is_file():
        print(f"ERROR: {args.dataset} not found", file=sys.stderr)
        return 1

    df = pd.read_csv(args.dataset)

    sections = [
        ("PROFILE", profile(df, sample_rows=5)),
        ("MISSINGNESS", missingness_report(df, threshold=0.2)),
        ("DUPLICATES", report_duplicates(df, args.key)),
    ]
    if args.target:
        sections.append(("LEAKAGE SCREEN", check_leakage(df, args.target, corr_threshold=0.95)))

    for title, body in sections:
        print(f"=== {title} ===")
        print(body)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
