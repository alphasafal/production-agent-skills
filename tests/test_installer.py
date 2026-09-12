"""install_skills.py: copies whole skill directories, never overwrites without --force."""
import importlib

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
