#!/usr/bin/env python3
"""List every skill under skills/ with a one-line summary.

Usage:
    python scripts/list_skills.py
    python scripts/list_skills.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import discover_skills  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    skills = discover_skills()

    if args.json:
        print(json.dumps(
            [{"name": s.name, "description": s.description, "path": str(s.dir)} for s in skills],
            indent=2,
        ))
        return 0

    print(f"Available skills ({len(skills)}):\n")
    for skill in skills:
        first_sentence = skill.description.split(". ")[0].rstrip(".") + "."
        print(f"  {skill.name}")
        print(f"    {first_sentence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
