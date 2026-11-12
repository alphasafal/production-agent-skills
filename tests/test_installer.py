"""install_skills.py: copies whole skill directories, never overwrites without --force."""
import importlib

import pytest

from _lib import discover_skills

install_skills = importlib.import_module("install_skills")

FIRST_SKILL = discover_skills()[0]


def _meaningful_files(root):
    """Files the installer is expected to copy — build artifacts are excluded by design."""
    return {
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".pyc", ".pyo")
    }


def test_install_one_copies_full_directory(tmp_path):
    installed = install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    assert installed
    dest = tmp_path / FIRST_SKILL.name
    assert (dest / "SKILL.md").is_file()
    assert _meaningful_files(FIRST_SKILL.dir) == _meaningful_files(dest)


def test_install_one_excludes_build_artifacts(tmp_path):
    pycache = FIRST_SKILL.dir / "scripts" / "__pycache__"
    created_dir = not pycache.exists()
    pycache.mkdir(parents=True, exist_ok=True)
    artifact = pycache / "installer-test-artifact.pyc"
    artifact.write_bytes(b"stale")
    try:
        install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
        copied = list((tmp_path / FIRST_SKILL.name).rglob("*.pyc"))
        assert not copied, f"installer copied build artifacts: {copied}"
    finally:
        artifact.unlink(missing_ok=True)
        if created_dir and not any(pycache.iterdir()):
            pycache.rmdir()


def test_install_one_skips_existing_without_force(tmp_path):
    install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    (tmp_path / FIRST_SKILL.name / "SENTINEL").write_text("do not touch")

    installed_again = install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)

    assert not installed_again
    assert (tmp_path / FIRST_SKILL.name / "SENTINEL").is_file()


def test_install_one_dry_run_touches_nothing(tmp_path):
    installed = install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=True, force=False)
    assert installed
    assert not (tmp_path / FIRST_SKILL.name).exists()


def test_unknown_skill_leaves_no_target_directory(tmp_path, monkeypatch, capsys):
    target = tmp_path / "should-not-exist"
    monkeypatch.setattr(
        "sys.argv",
        ["install_skills.py", "--skill", "no-such-skill", "--target", str(target)],
    )

    exit_code = install_skills.main()

    assert exit_code == 1
    assert not target.exists(), "a failed install must not leave an empty target directory"
    assert "unknown skill" in capsys.readouterr().out


def test_install_one_force_overwrites(tmp_path):
    install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    (tmp_path / FIRST_SKILL.name / "SENTINEL").write_text("stale")

    installed_again = install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=True)

    assert installed_again
    assert not (tmp_path / FIRST_SKILL.name / "SENTINEL").exists()


def _run_main(monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["install_skills.py", *argv])
    return install_skills.main()


def test_agent_flag_installs_into_that_agents_project_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert _run_main(monkeypatch, "--skill", FIRST_SKILL.name, "--agent", "claude", "--agent", "cursor") == 0
    assert (tmp_path / ".claude" / "skills" / FIRST_SKILL.name / "SKILL.md").is_file()
    assert (tmp_path / ".agents" / "skills" / FIRST_SKILL.name / "SKILL.md").is_file()


def test_global_flag_installs_under_the_home_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    assert _run_main(monkeypatch, "--skill", FIRST_SKILL.name, "--agent", "claude", "--global") == 0
    assert (tmp_path / ".claude" / "skills" / FIRST_SKILL.name / "SKILL.md").is_file()


def test_uninstall_removes_the_skill_and_nothing_else(tmp_path, monkeypatch):
    install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    (tmp_path / "keep-me").mkdir()

    assert _run_main(monkeypatch, "--skill", FIRST_SKILL.name, "--target", str(tmp_path), "--uninstall") == 0

    assert [p.name for p in tmp_path.iterdir()] == ["keep-me"]


def test_uninstall_dry_run_touches_nothing(tmp_path):
    install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    assert install_skills.uninstall_one(FIRST_SKILL, tmp_path, dry_run=True)
    assert (tmp_path / FIRST_SKILL.name / "SKILL.md").is_file()


def test_uninstall_refuses_a_directory_without_skill_md(tmp_path):
    impostor = tmp_path / FIRST_SKILL.name
    impostor.mkdir()
    (impostor / "notes.txt").write_text("not a skill")
    with pytest.raises(SystemExit):
        install_skills.uninstall_one(FIRST_SKILL, tmp_path, dry_run=False)
    assert (impostor / "notes.txt").is_file()


def test_target_and_agent_together_are_rejected(tmp_path, monkeypatch):
    with pytest.raises(SystemExit):
        _run_main(monkeypatch, "--all", "--target", str(tmp_path), "--agent", "claude")
