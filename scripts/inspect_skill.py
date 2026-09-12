#!/usr/bin/env python3
"""Print a detailed report on one skill: description, resources, and eval coverage.

Usage:
    python scripts/inspect_skill.py data-scientist
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import SKILLS_DIR, discover_skills, find_relative_references  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_name", help="directory name under skills/")
    args = parser.parse_args()

    skills = {s.name: s for s in discover_skills()}
    skill = skills.get(args.skill_name)
    if skill is None:
        available = ", ".join(sorted(skills)) or "(none found)"
        print(f"Unknown skill '{args.skill_name}'. Available: {available}")
        return 1

    print(f"Skill: {skill.name}\n")
    print("Description:")
    print(f"  {skill.description}\n")

    print("Resources:")
    print(f"  references: {len(skill.references)}")
    print(f"  scripts:    {len(skill.scripts)}")
    print(f"  assets:     {len(skill.assets)}")
    print(f"  examples:   {len(skill.examples)}")
    print()

    cases = skill.eval_cases()
    counts = {"positive-obvious": 0, "positive-ambiguous": 0, "negative": 0}
    for c in cases:
        counts[c.get("category", "")] = counts.get(c.get("category", ""), 0) + 1
    print("Evaluation cases:")
    print(f"  positive (obvious):   {counts.get('positive-obvious', 0)}")
    print(f"  positive (ambiguous): {counts.get('positive-ambiguous', 0)}")
    print(f"  negative:             {counts.get('negative', 0)}")
    print(f"  total:                {len(cases)}")
    print()

    mentioned = find_relative_references(skill.body)
    all_files = skill.references + skill.scripts + skill.assets + skill.examples
    orphaned = [
        f for f in all_files
        if f.relative_to(skill.dir).as_posix() not in mentioned and f.name not in skill.body
    ]

    print("Status:")
    print(f"  structure-valid:   {'yes' if (skill.dir / 'SKILL.md').is_file() else 'no'}")
    print(f"  name-matches-dir:  {'yes' if skill.frontmatter.get('name') == skill.dir.name else 'no'}")
    print(f"  references-valid:  {'yes' if not orphaned else f'no ({len(orphaned)} orphaned file(s))'}")
    print(f"  eval-file-present: {'yes' if cases or (SKILLS_DIR.parent / 'evaluations' / 'activation' / f'{skill.dir.name}.json').is_file() else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
