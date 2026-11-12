"""install.sh: the no-clone installer. Run here against this checkout instead of a download."""
import os
import shutil
import subprocess

import pytest

import install_skills
from _lib import REPO_ROOT, discover_skills, load_packs

SH = shutil.which("sh")
pytestmark = pytest.mark.skipif(SH is None, reason="needs a POSIX sh")

SCRIPT = REPO_ROOT / "install.sh"
ALL_SKILLS = [s.name for s in discover_skills()]


def run(args, cwd, home=None, check=True):
    env = dict(os.environ, PAS_SOURCE_DIR=str(REPO_ROOT), HOME=str(home or cwd / "home"))
    proc = subprocess.run([SH, str(SCRIPT), *args], cwd=cwd, env=env, capture_output=True, text=True)
    if check:
        assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc


def files(root):
    return {
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")
    }


def test_pack_installs_whole_skill_directories(tmp_path):
    run(["--pack", "sre"], tmp_path)
    installed = tmp_path / ".agents" / "skills"
    assert sorted(p.name for p in installed.iterdir()) == sorted(load_packs()["sre"]["skills"])
    for name in load_packs()["sre"]["skills"]:
        assert files(installed / name) == files(REPO_ROOT / "skills" / name)
    assert not list(installed.rglob("__pycache__"))


def test_all_installs_every_skill(tmp_path):
    run(["--all"], tmp_path)
    assert sorted(p.name for p in (tmp_path / ".agents" / "skills").iterdir()) == ALL_SKILLS


def test_detects_claude_code_project(tmp_path):
    (tmp_path / ".claude").mkdir()
    run(["--skill", "repo-architect"], tmp_path)
    assert (tmp_path / ".claude" / "skills" / "repo-architect" / "SKILL.md").is_file()
    assert not (tmp_path / ".agents").exists()


@pytest.mark.parametrize("agent", sorted(install_skills.AGENT_DIRS))
@pytest.mark.parametrize("global_scope", [False, True])
def test_agent_directories_match_the_python_installer(tmp_path, agent, global_scope):
    home = tmp_path / "home"
    project = tmp_path / "project"
    project.mkdir()
    run(["--skill", "repo-architect", "--agent", agent] + (["--global"] if global_scope else []),
        project, home=home)
    project_dir, user_dir = install_skills.AGENT_DIRS[agent]
    expected = home / user_dir.replace("~/", "") if global_scope else project / project_dir
    assert (expected / "repo-architect" / "SKILL.md").is_file()


def test_several_agents_in_one_run(tmp_path):
    run(["--skill", "repo-architect", "--agent", "claude", "--agent", "codex"], tmp_path)
    assert (tmp_path / ".claude" / "skills" / "repo-architect").is_dir()
    assert (tmp_path / ".agents" / "skills" / "repo-architect").is_dir()


def test_target_with_spaces(tmp_path):
    target = tmp_path / "my project" / "skills dir"
    run(["--skill", "repo-architect", "--target", str(target)], tmp_path)
    assert (target / "repo-architect" / "SKILL.md").is_file()


def test_existing_skill_is_kept_without_force_and_replaced_with_it(tmp_path):
    run(["--skill", "repo-architect"], tmp_path)
    sentinel = tmp_path / ".agents" / "skills" / "repo-architect" / "SENTINEL"
    sentinel.write_text("local edit")

    out = run(["--skill", "repo-architect"], tmp_path).stdout
    assert "skip" in out and sentinel.is_file()

    run(["--skill", "repo-architect", "--force"], tmp_path)
    assert not sentinel.exists()
    assert (sentinel.parent / "SKILL.md").is_file()


def test_dry_run_changes_nothing(tmp_path):
    out = run(["--all", "--dry-run"], tmp_path).stdout
    assert "(dry run)" in out
    assert list(tmp_path.iterdir()) == []


def test_uninstall_removes_only_what_was_selected(tmp_path):
    run(["--pack", "sre", "--skill", "repo-architect"], tmp_path)
    run(["--pack", "sre", "--uninstall"], tmp_path)
    assert [p.name for p in (tmp_path / ".agents" / "skills").iterdir()] == ["repo-architect"]


def test_uninstall_refuses_a_directory_that_is_not_a_skill(tmp_path):
    precious = tmp_path / ".agents" / "skills" / "repo-architect"
    precious.mkdir(parents=True)
    (precious / "notes.txt").write_text("not a skill")
    proc = run(["--skill", "repo-architect", "--uninstall"], tmp_path, check=False)
    assert proc.returncode == 1 and "refusing" in proc.stderr
    assert (precious / "notes.txt").is_file()


@pytest.mark.parametrize("args, message", [
    (["--pack", "no-such-pack"], "unknown pack"),
    (["--skill", "no-such-skill"], "unknown skill"),
    (["--all", "--agent", "no-such-agent"], "unknown agent"),
    (["--all", "--bogus"], "unknown option"),
    (["--pack"], "needs a value"),
    ([], "nothing selected"),
])
def test_bad_input_fails_before_touching_the_filesystem(tmp_path, args, message):
    proc = run(args, tmp_path, check=False)
    assert proc.returncode == 1
    assert message in proc.stderr
    assert list(tmp_path.iterdir()) == []


def test_list_shows_every_pack_and_skill(tmp_path):
    out = run(["--list"], tmp_path).stdout
    for name in list(load_packs()) + ALL_SKILLS:
        assert name in out


def test_help_names_every_pack_and_agent(tmp_path):
    out = run(["--help"], tmp_path).stdout
    for name in list(load_packs()) + sorted(install_skills.AGENT_DIRS):
        assert name in out, f"install.sh --help does not mention {name}"


def test_closing_hint_is_a_prompt_from_the_eval_suite(tmp_path):
    out = run(["--skill", "incident-responder"], tmp_path).stdout
    first_prompt = next(s for s in discover_skills() if s.name == "incident-responder").eval_cases()[0]["prompt"]
    assert first_prompt in out
