#!/usr/bin/env python3
"""Static validation for every skill in skills/ and every case in evaluations/activation/.

Checks performed:
  - SKILL.md frontmatter parses and matches schemas/skill-manifest.schema.json
  - name: matches the parent directory name exactly; no duplicates across skills/
  - description: present, within length bounds, states what+when
  - SKILL.md body: not absurdly long (progressive disclosure — detail belongs in references/)
  - every references/scripts/assets path mentioned in the body actually exists
  - every file under references/scripts/assets/examples is reachable (no orphaned dead weight)
  - scripts/*.py that import third-party packages document that in a header comment
  - no empty directories anywhere under skills/
  - evaluations/activation/<skill>.json validates against schemas/evaluation.schema.json
  - optional: shells out to `skills-ref validate` per skill if that CLI is on PATH

Exit code 0 if no errors (warnings are non-fatal). Run with -v for warnings too.
"""
from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import (  # noqa: E402
    EVALUATIONS_DIR,
    REPO_ROOT,
    SKILLS_DIR,
    Skill,
    SkillParseError,
    discover_skills,
    find_relative_references,
    load_schema,
    strict_yaml_violations,
)

MIN_SKILL_MD_LINES = 15
MAX_SKILL_MD_LINES = 400

# sys.stdlib_module_names is Python 3.10+; fall back to a common-module list on 3.9.
_FALLBACK_STDLIB = {
    "os", "sys", "re", "json", "csv", "io", "math", "statistics", "collections",
    "itertools", "functools", "pathlib", "argparse", "subprocess", "shutil",
    "typing", "dataclasses", "datetime", "time", "random", "logging", "unittest",
    "abc", "enum", "copy", "textwrap", "string", "glob", "tempfile", "hashlib",
    "sqlite3", "urllib", "http", "socket", "threading", "multiprocessing",
    "ast", "inspect", "warnings", "traceback", "contextlib", "operator",
    "decimal", "fractions", "uuid", "base64", "struct", "pickle", "gzip",
    "zipfile", "tarfile", "configparser", "difflib", "pprint",
}
STDLIB_MODULES = set(getattr(sys, "stdlib_module_names", ())) or _FALLBACK_STDLIB


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def check_frontmatter(skill: Skill, schema: dict, report: Report) -> None:
    try:
        jsonschema.validate(instance=skill.frontmatter, schema=schema)
    except jsonschema.ValidationError as exc:
        report.error(f"{skill.dir.name}: frontmatter schema violation: {exc.message}")
        return

    if skill.frontmatter.get("name") != skill.dir.name:
        report.error(
            f"{skill.dir.name}: frontmatter 'name: {skill.frontmatter.get('name')}' "
            f"does not match directory name"
        )

    description = skill.description
    if len(description.split()) < 8:
        report.warn(f"{skill.dir.name}: description looks too short to convey what+when")
    lowered = description.lower()
    if "use when" not in lowered and "use for" not in lowered and "use to" not in lowered:
        report.warn(
            f"{skill.dir.name}: description should explicitly say when to use the skill"
        )


def check_strict_yaml(skill: Skill, report: Report) -> None:
    for problem in strict_yaml_violations(skill.raw_frontmatter):
        report.error(f"{skill.dir.name}: {problem}")


def check_duplicates(skills: list[Skill], report: Report) -> None:
    seen: dict[str, str] = {}
    for skill in skills:
        name = skill.name
        if name in seen:
            report.error(
                f"duplicate skill name '{name}': {seen[name]} and {skill.dir.name}"
            )
        seen[name] = skill.dir.name


def check_body_length(skill: Skill, report: Report) -> None:
    n_lines = len(skill.body.strip().splitlines())
    if n_lines < MIN_SKILL_MD_LINES:
        report.warn(f"{skill.dir.name}: SKILL.md body is only {n_lines} lines — likely incomplete")
    if n_lines > MAX_SKILL_MD_LINES:
        report.error(
            f"{skill.dir.name}: SKILL.md body is {n_lines} lines (max {MAX_SKILL_MD_LINES}) — "
            f"move detail into references/ (progressive disclosure)"
        )


def check_references_exist(skill: Skill, report: Report) -> None:
    mentioned = find_relative_references(skill.body)
    for rel in mentioned:
        target = skill.dir / rel
        if not target.exists():
            report.error(f"{skill.dir.name}: SKILL.md references '{rel}' which does not exist")

    all_files = skill.references + skill.scripts + skill.assets + skill.examples
    for f in all_files:
        rel = f.relative_to(skill.dir).as_posix()
        top_two = "/".join(rel.split("/")[:2])
        if rel not in mentioned and top_two not in mentioned and f.name not in skill.body:
            report.warn(
                f"{skill.dir.name}: '{rel}' exists but is never referenced from SKILL.md "
                f"(orphaned resource, or reference it explicitly for progressive disclosure)"
            )


def check_script_dependencies(skill: Skill, report: Report) -> None:
    sibling_modules = {s.stem for s in skill.scripts if s.suffix == ".py"}
    for script in skill.scripts:
        if script.suffix != ".py":
            continue
        try:
            tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            report.error(f"{skill.dir.name}: {script.name} has a syntax error: {exc}")
            continue

        third_party = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods = [node.module.split(".")[0]]
            else:
                continue
            for mod in mods:
                if (
                    mod not in STDLIB_MODULES
                    and mod not in {"__future__"}
                    and mod not in sibling_modules
                ):
                    third_party.add(mod)

        if third_party:
            header = "\n".join(script.read_text(encoding="utf-8").splitlines()[:15])
            undocumented = [m for m in third_party if m not in header]
            if undocumented:
                report.warn(
                    f"{skill.dir.name}: {script.name} imports {sorted(undocumented)} "
                    f"without naming them in its header docstring/comments"
                )


def check_empty_dirs(report: Report) -> None:
    for path in sorted(SKILLS_DIR.rglob("*")):
        if path.is_dir() and not any(path.iterdir()):
            report.error(f"empty directory: {path.relative_to(REPO_ROOT)}")


def check_evaluations(skills: list[Skill], report: Report) -> None:
    schema = load_schema("evaluation.schema.json")
    skill_names = {s.name for s in skills}
    activation_dir = EVALUATIONS_DIR / "activation"
    if not activation_dir.is_dir():
        report.error("evaluations/activation/ directory is missing")
        return

    for skill in skills:
        eval_file = activation_dir / f"{skill.dir.name}.json"
        if not eval_file.is_file():
            report.error(f"{skill.dir.name}: no evaluation file at {eval_file.relative_to(REPO_ROOT)}")
            continue
        try:
            cases = json.loads(eval_file.read_text())
        except json.JSONDecodeError as exc:
            report.error(f"{eval_file.relative_to(REPO_ROOT)}: malformed JSON: {exc}")
            continue

        if not isinstance(cases, list):
            report.error(f"{eval_file.relative_to(REPO_ROOT)}: must be a JSON array of cases")
            continue

        categories = {"positive-obvious": 0, "positive-ambiguous": 0, "negative": 0}
        seen_ids = set()
        for case in cases:
            try:
                jsonschema.validate(instance=case, schema=schema)
            except jsonschema.ValidationError as exc:
                report.error(f"{eval_file.relative_to(REPO_ROOT)}: {exc.message}")
                continue
            if case["skill"] != skill.dir.name:
                report.error(
                    f"{eval_file.relative_to(REPO_ROOT)}: case '{case['id']}' has skill "
                    f"'{case['skill']}', expected '{skill.dir.name}'"
                )
            if case["skill"] not in skill_names:
                report.error(f"{eval_file.relative_to(REPO_ROOT)}: unknown skill '{case['skill']}'")
            if case["id"] in seen_ids:
                report.error(f"{eval_file.relative_to(REPO_ROOT)}: duplicate case id '{case['id']}'")
            seen_ids.add(case["id"])
            categories[case["category"]] = categories.get(case["category"], 0) + 1

        if categories["positive-obvious"] < 5:
            report.warn(f"{skill.dir.name}: fewer than 5 positive-obvious eval cases")
        if categories["positive-ambiguous"] < 2:
            report.warn(f"{skill.dir.name}: fewer than 2 positive-ambiguous eval cases")
        if categories["negative"] < 3:
            report.warn(f"{skill.dir.name}: fewer than 3 negative eval cases")


def run_skills_ref(skills: list[Skill], report: Report) -> None:
    binary = shutil.which("skills-ref")
    if not binary:
        report.warn("skills-ref CLI not found on PATH — skipping optional external validation")
        return
    for skill in skills:
        result = subprocess.run(
            [binary, "validate", str(skill.dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            report.error(f"{skill.dir.name}: skills-ref validate failed:\n{result.stdout}{result.stderr}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--verbose", action="store_true", help="also print warnings")
    args = parser.parse_args()

    report = Report()

    try:
        skills = discover_skills()
    except SkillParseError as exc:
        print(f"ERROR: {exc}")
        return 1

    if not skills:
        print("ERROR: no skills found under skills/")
        return 1

    schema = load_schema("skill-manifest.schema.json")

    for skill in skills:
        check_frontmatter(skill, schema, report)
        check_strict_yaml(skill, report)
        check_body_length(skill, report)
        check_references_exist(skill, report)
        check_script_dependencies(skill, report)

    check_duplicates(skills, report)
    check_empty_dirs(report)
    check_evaluations(skills, report)
    run_skills_ref(skills, report)

    print(f"Validated {len(skills)} skill(s).\n")

    if report.errors:
        print(f"ERRORS ({len(report.errors)}):")
        for e in report.errors:
            print(f"  ✗ {e}")
        print()

    if args.verbose and report.warnings:
        print(f"WARNINGS ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"  ! {w}")
        print()
    elif report.warnings:
        print(f"{len(report.warnings)} warning(s) (run with -v to see them)\n")

    if report.ok:
        print("PASS: no errors.")
        return 0
    print("FAIL: errors found above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
