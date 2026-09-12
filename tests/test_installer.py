"""install_skills.py: copies whole skill directories, never overwrites without --force."""
import importlib

from _lib import discover_skills

install_skills = importlib.import_module("install_skills")

FIRST_SKILL = discover_skills()[0]


def test_install_one_copies_full_directory(tmp_path):
    installed = install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    assert installed
    dest = tmp_path / FIRST_SKILL.name
    assert (dest / "SKILL.md").is_file()
    src_files = {p.relative_to(FIRST_SKILL.dir) for p in FIRST_SKILL.dir.rglob("*") if p.is_file()}
    dest_files = {p.relative_to(dest) for p in dest.rglob("*") if p.is_file()}
    assert src_files == dest_files


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


def test_install_one_force_overwrites(tmp_path):
    install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=False)
    (tmp_path / FIRST_SKILL.name / "SENTINEL").write_text("stale")

    installed_again = install_skills.install_one(FIRST_SKILL, tmp_path, dry_run=False, force=True)

    assert installed_again
    assert not (tmp_path / FIRST_SKILL.name / "SENTINEL").exists()
