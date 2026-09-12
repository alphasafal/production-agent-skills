"""Every SKILL.md's YAML frontmatter must validate against the open spec schema."""
import jsonschema
import pytest

from _lib import discover_skills, load_schema

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
