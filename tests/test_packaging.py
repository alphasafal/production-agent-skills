"""package_skills.py: the zips attached to releases."""
import hashlib
import zipfile

import pytest
import yaml

import package_skills
from _lib import FRONTMATTER_RE, REPO_ROOT, SHORT_DESCRIPTION_MAX_CHARS, discover_skills, load_packs

SKILLS = discover_skills()


@pytest.fixture(scope="module")
def dist(tmp_path_factory):
    out = tmp_path_factory.mktemp("dist")
    package_skills.build(out)
    return out


def names(path):
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def source_files(skill):
    return {f"{skill.dir.name}/{p.relative_to(skill.dir).as_posix()}" for p in package_skills.skill_files(skill)}


def test_one_archive_per_pack_and_skill_plus_everything(dist):
    expected = {f"pack-{p}.zip" for p in load_packs()}
    expected |= {f"claude-app-{s.name}.zip" for s in SKILLS}
    expected |= {"all-skills.zip", "SHA256SUMS"}
    assert {p.name for p in dist.iterdir()} == expected


def test_pack_archive_is_the_repository_content_unchanged(dist):
    by_name = {s.name: s for s in SKILLS}
    for pack, spec in load_packs().items():
        with zipfile.ZipFile(dist / f"pack-{pack}.zip") as archive:
            want = set().union(*(source_files(by_name[n]) for n in spec["skills"]))
            assert set(archive.namelist()) == want
            for name in archive.namelist():
                assert archive.read(name) == (REPO_ROOT / "skills" / name).read_bytes(), name


def test_all_skills_archive_has_every_skill_at_the_root(dist):
    roots = {n.split("/")[0] for n in names(dist / "all-skills.zip")}
    assert roots == {s.name for s in SKILLS}


@pytest.mark.parametrize("skill", SKILLS, ids=lambda s: s.name)
def test_claude_app_archive_meets_the_documented_upload_rules(dist, skill):
    path = dist / f"claude-app-{skill.name}.zip"
    listing = names(path)
    # One folder at the root, named after the skill, with SKILL.md inside it.
    assert {n.split("/")[0] for n in listing} == {skill.name}
    assert f"{skill.name}/SKILL.md" in listing
    assert set(listing) == source_files(skill)

    with zipfile.ZipFile(path) as archive:
        text = archive.read(f"{skill.name}/SKILL.md").decode("utf-8")
    frontmatter_text, body = FRONTMATTER_RE.match(text).groups()
    frontmatter = yaml.safe_load(frontmatter_text)
    assert frontmatter["name"] == skill.name and len(skill.name) <= 64
    description = " ".join(frontmatter["description"].split())
    assert description == skill.short_description
    assert len(description) <= SHORT_DESCRIPTION_MAX_CHARS
    # Only the description differs from the source.
    assert body == skill.body
    assert {k: v for k, v in frontmatter.items() if k != "description"} == \
           {k: v for k, v in skill.frontmatter.items() if k != "description"}


def test_no_build_artifacts_in_any_archive(dist):
    for path in dist.glob("*.zip"):
        assert not [n for n in names(path) if "__pycache__" in n or n.endswith((".pyc", ".pyo"))]


def test_checksums_match_and_builds_are_reproducible(dist, tmp_path):
    sums = dict(reversed(line.split("  ")) for line in (dist / "SHA256SUMS").read_text().splitlines())
    assert set(sums) == {p.name for p in dist.glob("*.zip")}
    for name, digest in sums.items():
        assert hashlib.sha256((dist / name).read_bytes()).hexdigest() == digest

    package_skills.build(tmp_path)
    assert (tmp_path / "SHA256SUMS").read_text() == (dist / "SHA256SUMS").read_text()
