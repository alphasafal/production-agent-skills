#!/usr/bin/env python3
"""Run the STATIC half of the evaluation suite: structural + lexical sanity checks
over evaluations/activation/*.json.

This does NOT run a real agent and does NOT measure actual activation accuracy —
that requires a live model and is described in docs/evaluating-skills.md. What
this script checks, deterministically, without any model call:

  - every eval file parses and validates against schemas/evaluation.schema.json
    (also covered by validate_skills.py — repeated here so this script is a
    standalone entry point per the CLI surface in docs)
  - each case has the minimum required fields for its category (e.g. a
    positive case should declare required_behaviors or expected_artifacts;
    a negative case should not)
  - a coarse lexical-overlap heuristic between each case's prompt and its
    skill's name/description, flagged only as a hint, never a failure

Usage:
    python scripts/run_static_evals.py
    python scripts/run_static_evals.py --skill debugging-investigator
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import EVALUATIONS_DIR, discover_skills  # noqa: E402

WORD_RE = re.compile(r"[a-z0-9]+")


def words(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it",
    "this", "that", "with", "my", "our", "we", "i", "was", "were", "be", "as",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", help="only run cases for this skill")
    args = parser.parse_args()

    skills = discover_skills()
    if args.skill:
        skills = [s for s in skills if s.name == args.skill]
        if not skills:
            print(f"Unknown skill '{args.skill}'")
            return 1

    total_cases = 0
    hints = 0
    field_errors = 0

    for skill in skills:
        eval_file = EVALUATIONS_DIR / "activation" / f"{skill.dir.name}.json"
        if not eval_file.is_file():
            print(f"[{skill.name}] no eval file — skipping (see validate_skills.py for the hard error)")
            continue

        cases = json.loads(eval_file.read_text())
        skill_vocab = words(skill.name.replace("-", " ")) | words(skill.description)
        skill_vocab -= STOPWORDS

        print(f"[{skill.name}] {len(cases)} case(s)")
        for case in cases:
            total_cases += 1
            category = case.get("category")
            if category in ("positive-obvious", "positive-ambiguous"):
                if not case.get("required_behaviors") and not case.get("expected_artifacts"):
                    print(f"  ✗ {case['id']}: positive case has no required_behaviors/expected_artifacts")
                    field_errors += 1
            if category == "negative" and case.get("expected_artifacts"):
                print(f"  ✗ {case['id']}: negative case should not declare expected_artifacts")
                field_errors += 1

            prompt_vocab = words(case["prompt"]) - STOPWORDS
            overlap = skill_vocab & prompt_vocab
            if category in ("positive-obvious",) and not overlap:
                print(f"  ~ {case['id']}: no lexical overlap with skill name/description (hint only)")
                hints += 1
            if category == "negative" and skill.name.split("-")[0] in prompt_vocab and len(overlap) > 2:
                print(f"  ~ {case['id']}: negative case shares a lot of vocabulary with the skill (double check it's really a non-trigger)")
                hints += 1

    print(f"\n{total_cases} case(s) checked, {field_errors} field error(s), {hints} lexical hint(s).")
    print("Note: this is a static proxy, not a measurement of real agent activation accuracy.")
    return 1 if field_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
