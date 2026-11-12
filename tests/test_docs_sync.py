"""The README and the installers' own help must not drift from the catalog."""
import re

from _lib import REPO_ROOT, discover_skills, load_packs
from build_marketplace import command_skills

README = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
SKILLS = [s.name for s in discover_skills()]
RAW_INSTALL_URL = "https://raw.githubusercontent.com/alphasafal/production-agent-skills/main/install.sh"


def test_readme_links_every_skill():
    for name in SKILLS:
        assert f"](skills/{name}/)" in README, f"README does not link skills/{name}/"


def test_readme_counts_match_the_catalog():
    assert f"badge/skills-{len(SKILLS)}-" in README
    assert f"badge/role%20packs-{len(load_packs())}-" in README
    assert f"## The {len(SKILLS)} skills" in README


def test_readme_role_table_matches_packs_json():
    for pack, spec in load_packs().items():
        row = next((line for line in README.splitlines() if f"| `{pack}` |" in line), None)
        assert row, f"README role table has no row for pack {pack}"
        assert re.findall(r"\]\(skills/([a-z0-9-]+)/\)", row) == spec["skills"], pack


def test_readme_lists_every_slash_command():
    for filename in command_skills():
        assert f"`/{filename[:-3]}`" in README, f"README does not list /{filename[:-3]}"


def test_one_line_install_points_at_a_file_that_exists():
    assert RAW_INSTALL_URL in README
    assert (REPO_ROOT / "install.sh").is_file()
    # The same command is repeated in the docs people land on from the README.
    for doc in ["docs/faq.md", "clients/claude-code.md", "clients/codex.md",
                "clients/github-copilot.md", "clients/cursor.md", "clients/gemini-cli.md"]:
        assert RAW_INSTALL_URL in (REPO_ROOT / doc).read_text(encoding="utf-8"), doc


def test_relative_links_in_top_level_docs_resolve():
    link = re.compile(r"\]\((?!https?://|#|mailto:)([^)#\s]+)(?:#[^)]*)?\)")
    for doc in ["README.md", "docs/faq.md", "docs/prompt-cheatsheet.md", "SECURITY.md",
                "clients/README.md", "clients/claude-apps.md", "clients/cursor.md",
                "clients/gemini-cli.md", "docs/compatibility.md"]:
        path = REPO_ROOT / doc
        for target in link.findall(path.read_text(encoding="utf-8")):
            assert (path.parent / target).exists(), f"{doc}: broken link to {target}"


def test_readme_has_a_one_step_plugin_install_line_for_every_plugin():
    # `claude plugin validate` asks for one per plugin the marketplace lists.
    for name in ["production-agent-skills", *load_packs()]:
        line = f"/plugin install {name} --marketplace alphasafal/production-agent-skills"
        assert line in README, f"README is missing: {line}"


def test_plugin_icon_is_a_square_png_the_directory_accepts():
    import struct
    data = (REPO_ROOT / ".claude-plugin" / "icon.png").read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = struct.unpack(">II", data[16:24])
    assert width == height and 512 <= width <= 2048
    assert len(data) < 2 * 1024 * 1024
