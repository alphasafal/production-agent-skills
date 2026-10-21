"""Every SKILL.md has the standard sections, including the anti-shortcut guardrails."""
import validate_skills
from _lib import (
    MIN_RATIONALIZATIONS,
    MIN_RED_FLAGS,
    REQUIRED_SECTIONS,
    Skill,
    count_bullets,
    count_table_rows,
    discover_skills,
    section_headings,
    section_text,
)


def test_every_skill_has_all_required_sections_in_order():
    for skill in discover_skills():
        headings = [h for h in section_headings(skill.body) if h in REQUIRED_SECTIONS]
        assert headings == REQUIRED_SECTIONS, f"{skill.name}: sections are {headings}"


def test_every_skill_has_enough_red_flags_and_rationalizations():
    for skill in discover_skills():
        flags = count_bullets(section_text(skill.body, "Red flags"))
        rats = count_table_rows(section_text(skill.body, "Common rationalizations"))
        assert flags >= MIN_RED_FLAGS, f"{skill.name}: only {flags} red flags"
        assert rats >= MIN_RATIONALIZATIONS, f"{skill.name}: only {rats} rationalizations"


def _report_for(body: str) -> validate_skills.Report:
    report = validate_skills.Report()
    skill = Skill(dir=__import__("pathlib").Path("fake-skill"), body=body)
    validate_skills.check_required_sections(skill, report)
    return report


def _full_body(flags: int = 3, rats: int = 3) -> str:
    parts = []
    for s in REQUIRED_SECTIONS:
        parts.append(f"# {s}\n")
        if s == "Red flags":
            parts += [f"- flag {i}\n" for i in range(flags)]
        elif s == "Common rationalizations":
            parts.append("| Rationalization | Reality |\n|---|---|\n")
            parts += [f"| \"excuse {i}\" | reality {i} |\n" for i in range(rats)]
        else:
            parts.append("text\n")
    return "\n".join(parts)


def test_validator_accepts_complete_body():
    assert not _report_for(_full_body()).errors


def test_validator_rejects_missing_guardrail_sections():
    body = _full_body().replace("# Red flags", "# Something else")
    errors = _report_for(body).errors
    assert any("missing required section '# Red flags'" in e for e in errors)


def test_validator_rejects_thin_guardrails():
    errors = _report_for(_full_body(flags=1, rats=1)).errors
    assert any("Red flags" in e and "bullet" in e for e in errors)
    assert any("Common rationalizations" in e and "row" in e for e in errors)


def test_headings_inside_code_fences_are_ignored():
    body = "```\n# Workflow\n```\n" + _full_body().replace("# Workflow", "# Not workflow")
    errors = _report_for(body).errors
    assert any("'# Workflow'" in e for e in errors)
