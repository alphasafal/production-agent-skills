"""Every skill has the minimum required files and no dead-weight empty folders."""
from _lib import SKILLS_DIR, discover_skills


def test_at_least_one_skill_found():
    assert discover_skills(), "no skills discovered under skills/"


def test_every_skill_has_skill_md():
    for entry in SKILLS_DIR.iterdir():
        if entry.is_dir():
            assert (entry / "SKILL.md").is_file(), f"{entry.name} is missing SKILL.md"


def test_no_empty_directories():
    empty = [
        p for p in SKILLS_DIR.rglob("*")
        if p.is_dir() and not any(p.iterdir())
    ]
    assert not empty, f"empty directories found: {empty}"


def test_skill_directory_names_are_kebab_case():
    import re
    pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    for skill in discover_skills():
        assert pattern.match(skill.dir.name), f"'{skill.dir.name}' is not kebab-case"
