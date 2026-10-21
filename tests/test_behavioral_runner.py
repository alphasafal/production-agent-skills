"""The behavioral runner's offline guarantees: isolation, parsing and scoring. No model calls."""
import json
import shutil
import subprocess
import sys

import run_behavioral_evals as rb
from _lib import REPO_ROOT


def _debug_case():
    return next(c for c in rb.load_workflows("debugging-investigator", "standard"))


def test_baseline_workspace_has_inputs_but_no_skill_or_answer():
    ws = rb.build_workspace(_debug_case(), [])
    try:
        names = {p.name for p in ws.rglob("*") if ".git" not in p.parts}
        assert {"app.py", "reproduce_bug.py"} <= names
        assert "BUG_SPOILER.md" not in names
        assert not (ws / ".claude").exists()
        assert not str(ws).startswith(str(REPO_ROOT)), "workspace must live outside the repo"
    finally:
        shutil.rmtree(ws)


def test_with_skill_workspace_installs_only_that_skill():
    ws = rb.build_workspace(_debug_case(), ["debugging-investigator"])
    try:
        installed = [p.name for p in (ws / ".claude" / "skills").iterdir()]
        assert installed == ["debugging-investigator"]
        assert (ws / ".claude" / "skills" / "debugging-investigator" / "SKILL.md").is_file()
    finally:
        shutil.rmtree(ws)


def test_installed_skill_excludes_worked_examples():
    ws = rb.build_workspace(_debug_case(), ["debugging-investigator", "data-scientist"])
    try:
        for name in ("debugging-investigator", "data-scientist"):
            installed = ws / ".claude" / "skills" / name
            assert (installed / "SKILL.md").is_file()
            assert not (installed / "examples").exists(), f"{name}: examples/ leaked into eval workspace"
        assert (ws / ".claude" / "skills" / "data-scientist" / "scripts").is_dir()
        assert (ws / ".claude" / "skills" / "data-scientist" / "references").is_dir()
    finally:
        shutil.rmtree(ws)


def test_workspace_starts_as_a_clean_git_baseline():
    ws = rb.build_workspace(_debug_case(), [])
    try:
        status = subprocess.run(["git", "status", "--porcelain"], cwd=ws, capture_output=True, text=True)
        assert status.stdout.strip() == ""
    finally:
        shutil.rmtree(ws)


def test_prompt_lists_workspace_files():
    prompt = rb.scenario_prompt(_debug_case())
    assert "app.py" in prompt and "reproduce_bug.py" in prompt


def _assistant(*blocks):
    return {"type": "assistant", "message": {"content": list(blocks)}}


def test_skill_loading_detected_from_skill_tool_or_read():
    events = [
        _assistant({"type": "tool_use", "name": "Skill", "input": {"skill": "repo-architect"}}),
        _assistant({"type": "tool_use", "name": "Read",
                    "input": {"file_path": "/w/.claude/skills/data-scientist/SKILL.md"}}),
        _assistant({"type": "tool_use", "name": "Read", "input": {"file_path": "/w/app.py"}}),
    ]
    loaded = rb.skills_loaded(events, ["repo-architect", "data-scientist", "product-manager"])
    assert loaded == ["repo-architect", "data-scientist"]


def test_condense_truncates_long_transcripts():
    events = [_assistant({"type": "text", "text": "x" * 50_000}) for _ in range(4)]
    text = rb.condense(events)
    assert len(text) <= rb.TRANSCRIPT_CHAR_BUDGET + 100
    assert "truncated" in text


def test_score_rates():
    g = {"required": [{"observed": True}, {"observed": False}, {"observed": True}, {"observed": True}],
         "forbidden": [{"occurred": True}, {"occurred": False}],
         "artifacts": [{"produced": False}]}
    s = rb.score(g)
    assert s == {"required_rate": 0.75, "forbidden_count": 1, "artifact_rate": 0.0}


def test_grader_error_scores_as_missing_not_zero():
    assert rb.score({"error": "x"})["required_rate"] is None


def test_pressure_scenarios_exist_and_are_loaded():
    pressure = rb.load_workflows(None, "pressure")
    assert len(pressure) >= 3
    assert all(c["kind"] == "pressure" for c in pressure)


def test_dry_run_makes_no_calls_and_succeeds():
    for mode in ("workflow", "activation"):
        proc = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "run_behavioral_evals.py"),
                               "--mode", mode, "--dry-run"], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "Dry run" in proc.stdout


def test_reference_answers_never_reach_the_agent():
    for case in rb.load_workflows(None, None):
        sources = {i["from"] for i in case.get("workspace_files", [])}
        assert case.get("reference_answer") not in sources
        assert not any("SPOILER" in s.upper() for s in sources), case["id"]


def test_summaries_render():
    rows = [{"id": "x", "skill": "s", "kind": "standard", "arm": a, "run": 1, "skill_loaded": a == "with_skill",
             "required_rate": r, "forbidden_count": f, "artifact_rate": None, "error": "", "seconds": 1}
            for a, r, f in (("baseline", 0.4, 2), ("with_skill", 0.8, 1))]
    md = rb.summarize_workflows(rows, {"started": "t", "model": None, "grader_model": None, "runs": 1})
    assert "+40 pts" in md and "2 → 1" in md
    act = [{"id": "a", "skill": "s", "category": "negative", "run": 1, "expected": None,
            "loaded": ["s"], "correct": False, "error": ""}]
    assert "Misroutes" in rb.summarize_activation(act, {"started": "t", "model": None, "runs": 1})
    json.dumps(rows)
