"""Role packs are valid, cover every skill, fit the discovery budget, and install correctly."""
import shutil
import subprocess

import install_skills
import validate_skills
from _lib import DISCOVERY_BUDGET_CHARS, discover_skills, estimate_discovery_chars, load_packs


def test_every_pack_lists_real_skills():
    names = {s.name for s in discover_skills()}
    for pack, spec in load_packs().items():
        assert spec["skills"], pack
        assert set(spec["skills"]) <= names, (pack, set(spec["skills"]) - names)


def test_every_skill_is_in_some_pack():
    covered = {n for spec in load_packs().values() for n in spec["skills"]}
    missing = {s.name for s in discover_skills()} - covered
    assert not missing, missing


def test_every_pack_fits_the_discovery_budget():
    by_name = {s.name: s for s in discover_skills()}
    for pack, spec in load_packs().items():
        size = estimate_discovery_chars([by_name[n] for n in spec["skills"]])
        assert size <= DISCOVERY_BUDGET_CHARS, f"{pack}: {size} bytes"


def test_estimate_matches_skills_ref_exactly_when_available():
    if not shutil.which("skills-ref"):
        return
    skills = discover_skills()
    prefix = len(str(skills[0].dir.parent)) + 1
    out = subprocess.run(["skills-ref", "to-prompt", *[str(s.dir) for s in skills]],
                         capture_output=True, text=True, check=True).stdout
    assert estimate_discovery_chars(skills, prefix) == len(out.encode("utf-8"))


def test_validator_rejects_unknown_skill_in_pack(monkeypatch):
    monkeypatch.setattr(validate_skills, "load_packs",
                        lambda: {"x": {"title": "x", "skills": ["no-such-skill"]}})
    report = validate_skills.Report()
    validate_skills.check_packs(discover_skills(), report)
    assert any("unknown skill 'no-such-skill'" in e for e in report.errors)


def test_install_pack_installs_exactly_its_skills(tmp_path, monkeypatch):
    pack, spec = next(iter(load_packs().items()))
    monkeypatch.setattr("sys.argv", ["install_skills.py", "--pack", pack, "--target", str(tmp_path)])
    assert install_skills.main() == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(spec["skills"])


def test_unknown_pack_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["install_skills.py", "--pack", "nope", "--target", str(tmp_path)])
    assert install_skills.main() == 1
    assert not any(tmp_path.iterdir())
