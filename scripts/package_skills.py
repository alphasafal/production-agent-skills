#!/usr/bin/env python3
"""Build the downloadable zips attached to each GitHub Release.

    dist/pack-<pack>.zip          one role pack; unzip it into a skills directory
    dist/all-skills.zip           every skill; unzip it into a skills directory
    dist/claude-app-<skill>.zip   one skill, for "Upload a skill" in the Claude apps
    dist/SHA256SUMS

For people who cannot or would rather not run an installer: download, unzip,
done. Pack and all-skills zips hold the skill directories exactly as they are in
this repository, each at the archive root.

The claude-app zips differ in one line. Anthropic's help article for uploaded
skills gives a 200-character limit for `description`, and this repository's
descriptions are 650-870 characters (the open spec allows 1024, and agents use
that room to decide when to load a skill). So each claude-app zip carries the
skill's `metadata.short_description` as its description; everything else is
byte-for-byte the same. Layout is what the article requires: one folder named
after the skill at the archive root, SKILL.md inside it.

Archives carry no timestamps: rebuilding the same commit on the same Python
gives the same bytes and the same checksums.

    python scripts/package_skills.py              # write dist/
    python scripts/package_skills.py --out /tmp/x
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    FRONTMATTER_RE,
    REPO_ROOT,
    SHORT_DESCRIPTION_MAX_CHARS,
    Skill,
    discover_skills,
    load_packs,
)

FIXED_TIME = (1980, 1, 1, 0, 0, 0)  # the zip format's epoch: no build time in the archive
# A `description:` key and its continuation lines (folded/literal block or indented wrap).
DESCRIPTION_RE = re.compile(r"^description:.*\n(?:[ \t]+.*\n)*", re.MULTILINE)


def skill_files(skill: Skill) -> list[Path]:
    return sorted(
        p for p in skill.dir.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")
    )


def claude_app_skill_md(skill: Skill) -> bytes:
    """SKILL.md with the description swapped for the short one. Nothing else changes."""
    short = skill.short_description
    if not short or len(short) > SHORT_DESCRIPTION_MAX_CHARS:
        raise SystemExit(f"{skill.name}: metadata.short_description missing or over "
                         f"{SHORT_DESCRIPTION_MAX_CHARS} chars — run scripts/validate_skills.py")
    text = (skill.dir / "SKILL.md").read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    new_head, count = DESCRIPTION_RE.subn(lambda _: f"description: >\n  {short}\n", head + "\n", count=1)
    if count != 1:
        raise SystemExit(f"{skill.name}: could not find the description in the frontmatter")
    return (new_head.rstrip("\n") + sep + body).encode("utf-8")


def write_zip(path: Path, skills: list[Skill], claude_app: bool = False) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for skill in skills:
            for file in skill_files(skill):
                rel = file.relative_to(skill.dir).as_posix()
                data = file.read_bytes()
                if claude_app and rel == "SKILL.md":
                    data = claude_app_skill_md(skill)
                info = zipfile.ZipInfo(f"{skill.dir.name}/{rel}", date_time=FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                executable = file.suffix in (".py", ".sh") and "scripts" in file.parts
                info.external_attr = (0o755 if executable else 0o644) << 16
                archive.writestr(info, data)


def build(out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    skills = discover_skills()
    by_name = {s.name: s for s in skills}
    built = []

    for pack, spec in load_packs().items():
        path = out / f"pack-{pack}.zip"
        write_zip(path, [by_name[name] for name in spec["skills"]])
        built.append(path)

    path = out / "all-skills.zip"
    write_zip(path, skills)
    built.append(path)

    for skill in skills:
        path = out / f"claude-app-{skill.name}.zip"
        write_zip(path, [skill], claude_app=True)
        # Fail the build rather than ship an archive the app would reject.
        with zipfile.ZipFile(path) as archive:
            packaged = FRONTMATTER_RE.match(archive.read(f"{skill.name}/SKILL.md").decode("utf-8"))
        frontmatter = yaml.safe_load(packaged.group(1))
        assert frontmatter["name"] == skill.name
        assert len(" ".join(frontmatter["description"].split())) <= SHORT_DESCRIPTION_MAX_CHARS
        assert packaged.group(2) == skill.body, f"{skill.name}: the claude-app body must match the source"
        built.append(path)

    sums = out / "SHA256SUMS"
    sums.write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in sorted(built)
    ))
    return built + [sums]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "dist", help="output directory (default: dist/)")
    args = parser.parse_args()
    built = build(args.out)
    for path in built:
        print(f"{path.stat().st_size:>8}  {path}")
    print(f"\n{len(built) - 1} archives + SHA256SUMS in {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
