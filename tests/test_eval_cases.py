"""Every evaluations/activation/<skill>.json must validate and meet coverage minimums."""
import json

import jsonschema
import pytest

from _lib import EVALUATIONS_DIR, discover_skills, load_schema

SKILLS = discover_skills()
SCHEMA = load_schema("evaluation.schema.json")


def _cases_for(skill_dir_name: str):
    eval_file = EVALUATIONS_DIR / "activation" / f"{skill_dir_name}.json"
    assert eval_file.is_file(), f"missing eval file: {eval_file}"
    return json.loads(eval_file.read_text())


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_eval_file_exists_and_parses(skill):
    _cases_for(skill.dir.name)


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_every_case_matches_schema(skill):
    for case in _cases_for(skill.dir.name):
        jsonschema.validate(instance=case, schema=SCHEMA)


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_coverage_minimums(skill):
    cases = _cases_for(skill.dir.name)
    counts = {"positive-obvious": 0, "positive-ambiguous": 0, "negative": 0}
    for case in cases:
        counts[case["category"]] = counts.get(case["category"], 0) + 1
    assert counts["positive-obvious"] >= 5, skill.dir.name
    assert counts["positive-ambiguous"] >= 2, skill.dir.name
    assert counts["negative"] >= 3, skill.dir.name


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_case_ids_unique_and_scoped(skill):
    cases = _cases_for(skill.dir.name)
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids)), f"duplicate ids in {skill.dir.name}"
    for case in cases:
        assert case["skill"] == skill.dir.name


WORKFLOW_REQUIRED_KEYS = {
    "id", "skill", "scenario", "fixture", "required_behaviors",
    "expected_artifacts", "grading_notes",
}


@pytest.mark.parametrize("skill", SKILLS, ids=[s.dir.name for s in SKILLS])
def test_workflow_eval_exists_and_has_required_keys(skill):
    workflow_file = EVALUATIONS_DIR / "workflows" / f"{skill.dir.name}.json"
    assert workflow_file.is_file(), f"missing workflow eval: {workflow_file}"
    case = json.loads(workflow_file.read_text())
    missing = WORKFLOW_REQUIRED_KEYS - case.keys()
    assert not missing, f"{workflow_file}: missing keys {missing}"
    assert case["skill"] == skill.dir.name
