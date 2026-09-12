"""Every references/scripts/assets path a SKILL.md points to must actually exist."""
import pytest

from _lib import discover_skills, find_relative_references

SKILLS = discover_skills()


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_referenced_paths_exist(skill):
    mentioned = find_relative_references(skill.body)
    missing = [rel for rel in mentioned if not (skill.dir / rel).exists()]
    assert not missing, f"{skill.dir.name}: SKILL.md points to missing paths: {missing}"


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_scripts_are_syntactically_valid_python(skill):
    import ast
    for script in skill.scripts:
        if script.suffix == ".py":
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
