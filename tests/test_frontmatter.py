"""Every SKILL.md's YAML frontmatter must validate against the open spec schema."""
import jsonschema
import pytest

from _lib import SHORT_DESCRIPTION_MAX_CHARS, discover_skills, load_schema

SKILLS = discover_skills()
SCHEMA = load_schema("skill-manifest.schema.json")


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_frontmatter_matches_schema(skill):
    jsonschema.validate(instance=skill.frontmatter, schema=SCHEMA)


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_name_matches_directory(skill):
    assert skill.frontmatter.get("name") == skill.dir.name


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_description_present_and_bounded(skill):
    description = skill.description
    assert description, "description is required"
    assert len(description) <= 1024
    assert "<" not in description and ">" not in description


def test_no_duplicate_skill_names():
    names = [s.name for s in SKILLS]
    assert len(names) == len(set(names)), f"duplicate skill names: {names}"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda s: s.name)
def test_short_description_fits_the_claude_app_limit(skill):
    short = skill.short_description
    assert short, "metadata.short_description is required"
    assert len(short) <= SHORT_DESCRIPTION_MAX_CHARS
    assert "<" not in short and ">" not in short
    assert "use " in short.lower(), "say when to use the skill, not only what it does"
