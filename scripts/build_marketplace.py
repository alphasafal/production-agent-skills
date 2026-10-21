#!/usr/bin/env python3
"""Generate .claude-plugin/marketplace.json from packs.json.

The marketplace offers one plugin with every skill and command, plus one plugin
per role pack containing just that pack's skills and their slash commands, so a
user can install exactly their role:

    /plugin install production-agent-skills@alphasafal-skills   # everything
    /plugin install sre@alphasafal-skills                       # one role

Run after editing packs.json, adding a skill, or adding a command:

    python scripts/build_marketplace.py          # rewrite the file
    python scripts/build_marketplace.py --check  # exit 1 if it's out of date (CI)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import REPO_ROOT, discover_skills, load_packs  # noqa: E402

MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = REPO_ROOT / ".claude-plugin" / "plugin.json"
COMMANDS_DIR = REPO_ROOT / "commands"
COMMAND_SKILL_RE = re.compile(r"Use the `([a-z0-9-]+)` skill")


def command_skills() -> dict[str, str]:
    """Map each command file (relative path) to the skill it invokes."""
    out = {}
    for path in sorted(COMMANDS_DIR.glob("*.md")):
        m = COMMAND_SKILL_RE.search(path.read_text())
        if m:
            out[f"./commands/{path.name}"] = m.group(1)
    return out


def build() -> dict:
    plugin = json.loads(PLUGIN.read_text())
    skills = {s.name for s in discover_skills()}
    cmds = command_skills()
    unknown = {c: s for c, s in cmds.items() if s not in skills}
    if unknown:
        raise SystemExit(f"commands reference unknown skills: {unknown}")

    homepage = plugin["homepage"]
    entries = [{
        "name": plugin["name"],
        "version": plugin["version"],
        "source": "./",
        "description": plugin["description"],
        "homepage": homepage,
        "license": plugin["license"],
        "keywords": plugin["keywords"],
    }]
    for pack, spec in load_packs().items():
        pack_cmds = [c for c, s in cmds.items() if s in spec["skills"]]
        entries.append({
            "name": pack,
            "version": plugin["version"],
            "source": "./",
            "strict": False,
            "description": f"{spec['title']} pack: {spec['description']} "
                           f"Skills: {', '.join(spec['skills'])}.",
            "homepage": homepage,
            "license": plugin["license"],
            "keywords": ["skills", pack] + [k for k in plugin["keywords"] if k != "skills"][:4],
            "skills": [f"./skills/{s}" for s in spec["skills"]],
            "commands": pack_cmds,
        })
    return {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": "alphasafal-skills",
        "description": "Evaluated, portable Agent Skills for engineering, SRE, security, data and product "
                       "roles. Install everything, or just your role's pack.",
        "owner": plugin["author"],
        "plugins": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if marketplace.json is out of date")
    args = parser.parse_args()
    text = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not MARKETPLACE.is_file() or MARKETPLACE.read_text() != text:
            print("marketplace.json is out of date — run: python scripts/build_marketplace.py")
            return 1
        print("marketplace.json is up to date.")
        return 0
    MARKETPLACE.write_text(text)
    print(f"Wrote {MARKETPLACE.relative_to(REPO_ROOT)} ({len(build()['plugins'])} plugins)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
