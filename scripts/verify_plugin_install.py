#!/usr/bin/env python3
"""End-to-end check that every marketplace plugin installs, LOADS, and contains
exactly the right skills and commands, using the real Claude Code CLI.

`claude plugin validate` checks manifests, but it passed on a layout where every
role pack installed and then failed to load ("conflicting manifests"). This
script catches that class of bug by doing what a user does:

  1. clones this repo's current commit into a temp dir,
  2. adds it as a local marketplace,
  3. installs each plugin, checks `claude plugin list` says it's enabled and
     `claude plugin details` lists exactly the expected skills + commands,
  4. uninstalls everything and removes the marketplace again.

It changes your user-level Claude Code plugin settings while it runs (and puts
them back), so it's on demand, not part of CI. Commit first: it tests HEAD.

    python scripts/verify_plugin_install.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_marketplace  # noqa: E402
from _lib import REPO_ROOT, discover_skills, load_packs  # noqa: E402

MARKETPLACE = "alphasafal-skills"


def run(*args: str) -> str:
    return subprocess.run(["claude", "plugin", *args], capture_output=True, text=True).stdout


def expected() -> dict[str, set[str]]:
    cmds = {name[:-3]: skill for name, skill in build_marketplace.command_skills().items()}
    out = {"production-agent-skills": {s.name for s in discover_skills()} | set(cmds)}
    for pack, spec in load_packs().items():
        out[pack] = set(spec["skills"]) | {c for c, s in cmds.items() if s in spec["skills"]}
    return out


def main() -> int:
    if not shutil.which("claude"):
        print("ERROR: the `claude` CLI is not on PATH.")
        return 1
    if build_marketplace.problems():
        print("Generated files are stale — run scripts/build_marketplace.py and commit first.")
        return 1
    plugins = expected()
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "repo"
        subprocess.run(["git", "clone", "-q", str(REPO_ROOT), str(clone)], check=True)
        print(run("marketplace", "add", str(clone)).strip().splitlines()[-1:])
        try:
            for name, want in plugins.items():
                run("install", f"{name}@{MARKETPLACE}")
                listing = run("list")
                block = listing.split(f"> {name}@{MARKETPLACE}")[1].split("\n  >")[0] \
                    if f"> {name}@{MARKETPLACE}" in listing else ""
                enabled = "enabled" in block
                details = run("details", f"{name}@{MARKETPLACE}")
                m = re.search(r"Skills \((\d+)\)\s+(.*)", details)
                got = {x.strip() for x in m.group(2).split(",")} if m else set()
                cost = re.search(r"Always-on:\s+~([\d,]+) tok", details)
                good = enabled and got == want
                ok &= good
                line = (f"{'✓' if good else '✗'} {name:<24} enabled={enabled} "
                        f"items={len(got)}/{len(want)} always-on≈{cost.group(1) if cost else '?'} tok")
                if not good:
                    error = re.search(r"Error: (.*)", block)
                    line += f"  missing={sorted(want - got)} extra={sorted(got - want)}"
                    line += f"  error={error.group(1)}" if error else ""
                print(line)
        finally:
            for name in plugins:
                run("uninstall", f"{name}@{MARKETPLACE}")
            run("marketplace", "remove", MARKETPLACE)
    print("ALL PLUGINS LOAD CORRECTLY" if ok else "PROBLEMS FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
