"""Frontmatter must satisfy the open spec's strict YAML subset, not just PyYAML.

The reference implementation (skills-ref from agentskills.io) rejects constructs
PyYAML accepts — most notably flow-style collections. Every skill in this repo
failed the official validator on exactly this before these checks existed, so
these tests exist to keep that from regressing.
"""
import pytest

from _lib import discover_skills, strict_yaml_violations

SKILLS = discover_skills()


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_frontmatter_passes_strict_yaml_subset(skill):
    violations = strict_yaml_violations(skill.raw_frontmatter)
    assert not violations, f"{skill.dir.name}: {violations}"


def test_detects_flow_sequence():
    bad = "name: x\nmetadata:\n  composes_with: [a, b]\n"
    assert any("flow-style" in v for v in strict_yaml_violations(bad))


def test_detects_flow_mapping():
    bad = "name: x\nmetadata: {category: engineering}\n"
    assert any("flow-style" in v for v in strict_yaml_violations(bad))


def test_detects_anchor():
    bad = "name: x\ncommon: &base\n"
    assert any("anchors" in v for v in strict_yaml_violations(bad))


def test_detects_duplicate_top_level_key():
    bad = "name: x\ndescription: one\ndescription: two\n"
    assert any("duplicate" in v for v in strict_yaml_violations(bad))


def test_accepts_block_style_list():
    good = "name: x\nmetadata:\n  composes_with:\n    - a\n    - b\n"
    assert strict_yaml_violations(good) == []


def test_ignores_comments_and_blank_lines():
    good = "# a comment: [not, a, list]\n\nname: x\n"
    assert strict_yaml_violations(good) == []
