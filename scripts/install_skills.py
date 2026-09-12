#!/usr/bin/env python3
"""Copy one or more canonical skills/ into a client's skills directory.

This does not hard-code a "correct" target path for any vendor — pass
whatever directory your client reads skills from (see clients/*.md for the
paths each client documents). Examples:

    python scripts/install_skills.py --list

    python scripts/install_skills.py \\
        --skill debugging-investigator \\
        --target ./my-project/.claude/skills

    python scripts/install_skills.py \\
        --all \\
        --target ./my-project/.agents/skills \\
        --dry-run

Safety:
    - Never overwrites an existing skill directory unless --force is given.
    - --dry-run prints the plan without touching the filesystem.
    - Copies the full skill directory (SKILL.md + references/scripts/assets/examples),
      never a partial copy.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import discover_skills  # noqa: E402


def print_available(skills) -> None:
    print("Available skills:")
    for skill in skills:
        print(f"  ✓ {skill.name}")


def install_one(skill, target_root: Path, dry_run: bool, force: bool) -> bool:
    """Returns True if the skill was (or would be) installed, False if skipped."""
    dest = target_root / skill.name

    if dest.exists() and not force:
        print(f"SKIP  {skill.name}: {dest} already exists (use --force to overwrite)")
        return False

    if dest.exists() and force:
        action = "would remove and recopy" if dry_run else "removing and recopying"
        print(f"{'DRY-RUN' if dry_run else 'FORCE'} {skill.name}: {action} {dest}")
        if not dry_run:
            shutil.rmtree(dest)

    if dry_run:
        print(f"DRY-RUN {skill.name}: would copy {skill.dir} -> {dest}")
        return True

    shutil.copytree(
        skill.dir, dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    copied_files = sorted(p for p in dest.rglob("*") if p.is_file())
    print(f"OK    {skill.name}: copied {len(copied_files)} file(s) to {dest}")
    for f in copied_files:
        print(f"        {f.relative_to(dest)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="list available skills and exit")
    parser.add_argument("--skill", action="append", default=[], help="skill name to install (repeatable)")
    parser.add_argument("--all", action="store_true", help="install every skill")
    parser.add_argument("--target", type=Path, help="destination skills directory")
    parser.add_argument("--dry-run", action="store_true", help="print what would happen without doing it")
    parser.add_argument("--force", action="store_true", help="overwrite an existing installed skill")
    args = parser.parse_args()

    skills = discover_skills()

    if args.list:
        print_available(skills)
        return 0

    if not args.all and not args.skill:
        parser.error("pass --skill NAME (repeatable), --all, or --list")

    if args.target is None:
        parser.error("--target is required unless using --list")

    target_root = args.target
    if target_root.exists() and not target_root.is_dir():
        print(f"ERROR: --target {target_root} exists and is not a directory")
        return 1

    # Resolve the selection before touching the filesystem, so a typo'd skill
    # name doesn't leave an empty target directory behind.
    by_name = {s.name: s for s in skills}
    if args.all:
        selected = skills
    else:
        selected = []
        for name in args.skill:
            if name not in by_name:
                print(f"ERROR: unknown skill '{name}'. Run --list to see available skills.")
                return 1
            selected.append(by_name[name])

    if not target_root.exists():
        if args.dry_run:
            print(f"DRY-RUN: would create target directory {target_root}")
        else:
            target_root.mkdir(parents=True, exist_ok=True)
            print(f"Created target directory {target_root}")

    installed = 0
    for skill in selected:
        if install_one(skill, target_root, args.dry_run, args.force):
            installed += 1

    print(f"\n{installed}/{len(selected)} skill(s) {'would be ' if args.dry_run else ''}installed to {target_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
