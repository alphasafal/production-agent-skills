#!/usr/bin/env python3
"""Copy one or more canonical skills/ into a client's skills directory.

Name your agent and the installer uses the directory that agent's own
documentation gives (see clients/*.md for each source), or pass --target for
any other directory. Examples:

    python scripts/install_skills.py --list

    python scripts/install_skills.py --pack sre --agent claude

    python scripts/install_skills.py --all --agent cursor --global

    python scripts/install_skills.py --pack sre --target ./my-project/.claude/skills

    python scripts/install_skills.py \\
        --skill debugging-investigator \\
        --target ./my-project/.claude/skills

    python scripts/install_skills.py \\
        --all \\
        --target ./my-project/.agents/skills \\
        --dry-run

    python scripts/install_skills.py --pack sre --agent claude --uninstall

Safety:
    - Never overwrites an existing skill directory unless --force is given.
    - --dry-run prints the plan without touching the filesystem.
    - Copies the full skill directory (SKILL.md + references/scripts/assets/examples),
      never a partial copy.
    - --uninstall only removes a directory that contains a SKILL.md.

The same options work without cloning the repository: see install.sh.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import discover_skills, load_packs  # noqa: E402


def print_available(skills) -> None:
    print("Available skills:")
    for skill in skills:
        print(f"  ✓ {skill.name}")
    packs = load_packs()
    if packs:
        print("\nRole packs (--pack NAME):")
        for name, spec in packs.items():
            print(f"  {name:<18} {spec['title']}: {', '.join(spec['skills'])}")


# Where each agent reads skills from: (inside a project, for every project of
# the user). Each path is taken from that vendor's documentation, cited in
# clients/*.md. install.sh implements the same table; tests/test_install_sh.py
# checks the two agree.
AGENT_DIRS = {
    "claude": (".claude/skills", "~/.claude/skills"),
    "codex": (".agents/skills", "~/.agents/skills"),
    "copilot": (".agents/skills", "~/.agents/skills"),
    "cursor": (".agents/skills", "~/.agents/skills"),
    "gemini": (".agents/skills", "~/.agents/skills"),
    "universal": (".agents/skills", "~/.agents/skills"),
}


def agent_target(agent: str, global_scope: bool) -> Path:
    project, user = AGENT_DIRS[agent]
    return Path(user).expanduser() if global_scope else Path(project)


def uninstall_one(skill, target_root: Path, dry_run: bool) -> bool:
    """Returns True if the skill was (or would be) removed, False if it wasn't there."""
    dest = target_root / skill.name
    if not dest.exists():
        print(f"SKIP  {skill.name}: not installed in {target_root}")
        return False
    if not (dest / "SKILL.md").is_file():
        raise SystemExit(f"ERROR: {dest} has no SKILL.md, refusing to delete it")
    if dry_run:
        print(f"DRY-RUN {skill.name}: would remove {dest}")
        return True
    shutil.rmtree(dest)
    print(f"OK    {skill.name}: removed {dest}")
    return True


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
    parser.add_argument("--pack", action="append", default=[],
                        help="install a role pack from packs.json (repeatable); see --list")
    parser.add_argument("--all", action="store_true", help="install every skill")
    parser.add_argument("--agent", action="append", default=[], choices=sorted(AGENT_DIRS),
                        help="install where this agent reads skills (repeatable); see clients/")
    parser.add_argument("--global", dest="global_scope", action="store_true",
                        help="with --agent: install for all of your projects (home directory)")
    parser.add_argument("--target", type=Path, help="any other destination skills directory")
    parser.add_argument("--uninstall", action="store_true", help="remove the selected skills instead")
    parser.add_argument("--dry-run", action="store_true", help="print what would happen without doing it")
    parser.add_argument("--force", action="store_true", help="overwrite an existing installed skill")
    args = parser.parse_args()

    skills = discover_skills()

    if args.list:
        print_available(skills)
        return 0

    if not args.all and not args.skill and not args.pack:
        parser.error("pass --skill NAME, --pack NAME (both repeatable), --all, or --list")

    if args.target is not None and (args.agent or args.global_scope):
        parser.error("pass either --target or --agent/--global, not both")
    if args.target is None and not args.agent:
        parser.error("say where to install: --agent NAME (repeatable) or --target DIR")

    targets = [args.target] if args.target is not None else list(
        dict.fromkeys(agent_target(a, args.global_scope) for a in args.agent)
    )
    for target_root in targets:
        if target_root.exists() and not target_root.is_dir():
            print(f"ERROR: target {target_root} exists and is not a directory")
            return 1

    # Resolve the selection before touching the filesystem, so a typo'd skill
    # name doesn't leave an empty target directory behind.
    by_name = {s.name: s for s in skills}
    packs = load_packs()
    requested = list(args.skill)
    for pack in args.pack:
        if pack not in packs:
            print(f"ERROR: unknown pack '{pack}'. Available: {', '.join(packs)}")
            return 1
        requested += packs[pack]["skills"]
    requested = list(dict.fromkeys(requested))  # de-duplicate, keep order

    if args.all:
        selected = skills
    else:
        selected = []
        for name in requested:
            if name not in by_name:
                print(f"ERROR: unknown skill '{name}'. Run --list to see available skills.")
                return 1
            selected.append(by_name[name])

    for target_root in targets:
        if args.uninstall:
            removed = sum(uninstall_one(skill, target_root, args.dry_run) for skill in selected)
            print(f"\n{removed}/{len(selected)} skill(s) {'would be ' if args.dry_run else ''}"
                  f"removed from {target_root}")
            continue

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

        print(f"\n{installed}/{len(selected)} skill(s) {'would be ' if args.dry_run else ''}"
              f"installed to {target_root}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
