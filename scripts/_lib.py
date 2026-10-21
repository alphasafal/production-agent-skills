"""Shared helpers for the skill tooling scripts (validate/inspect/list/evals).

Not a skill-facing module — internal to scripts/ only.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
EVALUATIONS_DIR = REPO_ROOT / "evaluations"
SCHEMAS_DIR = REPO_ROOT / "schemas"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


class SkillParseError(Exception):
    pass


@dataclass
class Skill:
    dir: Path
    frontmatter: dict = field(default_factory=dict)
    body: str = ""
    raw_frontmatter: str = ""

    @property
    def name(self) -> str:
        return self.frontmatter.get("name", self.dir.name)

    @property
    def description(self) -> str:
        return self.frontmatter.get("description", "")

    def resource_files(self, subdir: str) -> list[Path]:
        path = self.dir / subdir
        if not path.is_dir():
            return []
        return sorted(
            p for p in path.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")
        )

    @property
    def references(self) -> list[Path]:
        return self.resource_files("references")

    @property
    def scripts(self) -> list[Path]:
        return self.resource_files("scripts")

    @property
    def assets(self) -> list[Path]:
        return self.resource_files("assets")

    @property
    def examples(self) -> list[Path]:
        return self.resource_files("examples")

    def eval_cases(self) -> list[dict]:
        eval_file = EVALUATIONS_DIR / "activation" / f"{self.dir.name}.json"
        if not eval_file.is_file():
            return []
        return json.loads(eval_file.read_text())


def parse_skill_md(skill_md_path: Path) -> tuple[dict, str, str]:
    text = skill_md_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise SkillParseError(
            f"{skill_md_path}: missing YAML frontmatter (file must start with '---')"
        )
    raw_frontmatter, body = match.groups()
    try:
        frontmatter = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError as exc:
        raise SkillParseError(f"{skill_md_path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise SkillParseError(f"{skill_md_path}: frontmatter must be a YAML mapping")
    return frontmatter, body, raw_frontmatter


# The reference implementation (skills-ref, agentskills.io) parses frontmatter with a
# strict YAML subset that PyYAML happily accepts but the spec does not. Checking for
# these locally means CI catches them without requiring the optional external CLI.
FLOW_COLLECTION_RE = re.compile(r"^\s*[^#\s][^:]*:\s*[\[{]")
ANCHOR_ALIAS_TAG_RE = re.compile(r"^\s*[^#\s][^:]*:\s*[&*!]")


def strict_yaml_violations(raw_frontmatter: str) -> list[str]:
    """Frontmatter constructs valid in PyYAML but rejected by the open spec's parser."""
    problems = []
    seen_top_level_keys = set()

    for lineno, line in enumerate(raw_frontmatter.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        if FLOW_COLLECTION_RE.match(line):
            problems.append(
                f"line {lineno}: flow-style collection (`[...]` / `{{...}}`) is not "
                f"accepted by the spec's YAML parser — use a block list/mapping instead: "
                f"{line.strip()[:70]}"
            )

        if ANCHOR_ALIAS_TAG_RE.match(line):
            problems.append(
                f"line {lineno}: YAML anchors/aliases/tags are not portable across "
                f"skill clients: {line.strip()[:70]}"
            )

        if not line.startswith((" ", "\t")) and ":" in line:
            key = line.split(":", 1)[0].strip()
            if key in seen_top_level_keys:
                problems.append(f"line {lineno}: duplicate top-level key '{key}'")
            seen_top_level_keys.add(key)

    return problems


def discover_skills(skills_dir: Path = SKILLS_DIR) -> list[Skill]:
    skills = []
    if not skills_dir.is_dir():
        return skills
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.is_file():
            continue
        frontmatter, body, raw_frontmatter = parse_skill_md(skill_md)
        skills.append(
            Skill(dir=entry, frontmatter=frontmatter, body=body, raw_frontmatter=raw_frontmatter)
        )
    return skills


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / name).read_text())


# Top-level sections every SKILL.md body must contain, in this order. "Red flags" and
# "Common rationalizations" are the anti-shortcut guardrails: agents rarely fail by
# not knowing a procedure, they fail by talking themselves out of following it.
REQUIRED_SECTIONS = [
    "Purpose",
    "When to use",
    "When NOT to use",
    "Required inputs",
    "Workflow",
    "Tool & resource guidance",
    "Output contract",
    "Quality checks",
    "Red flags",
    "Common rationalizations",
    "Edge cases",
    "References",
]
MIN_RED_FLAGS = 3
MIN_RATIONALIZATIONS = 3

H1_RE = re.compile(r"^# (.+?)\s*$", re.MULTILINE)


def section_headings(body: str) -> list[str]:
    """Top-level (`# `) headings in a SKILL.md body, ignoring fenced code blocks."""
    stripped = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    return H1_RE.findall(stripped)


def section_text(body: str, heading: str) -> str:
    """Text between `# <heading>` and the next top-level heading ('' if absent)."""
    match = re.search(rf"^# {re.escape(heading)}\s*$(.*?)(?=^# |\Z)", body, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def count_bullets(text: str) -> int:
    return len(re.findall(r"^\s*[-*] \S", text, re.MULTILINE))


def count_table_rows(text: str) -> int:
    """Data rows of a markdown table (excludes the header and separator rows)."""
    rows = [ln for ln in text.splitlines() if ln.strip().startswith("|")]
    rows = [ln for ln in rows if not re.match(r"^\s*\|[\s:|-]+\|\s*$", ln)]
    return max(len(rows) - 1, 0)


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BARE_PATH_RE = re.compile(r"\b((?:references|scripts|assets|examples)/[A-Za-z0-9_./-]+)\b")


def find_relative_references(body: str) -> set[str]:
    """Extract relative-file-looking references from a SKILL.md body.

    Matches both markdown links and bare paths like `references/foo.md`
    mentioned in prose (progressive-disclosure pointers are usually written
    as plain text, not links).
    """
    found = set()
    for m in MARKDOWN_LINK_RE.finditer(body):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        found.add(target)
    for m in BARE_PATH_RE.finditer(body):
        found.add(m.group(1))
    return found
