"""The plugin marketplace and per-pack command copies are generated from packs.json and stay in sync."""
import json

import build_marketplace
from _lib import discover_skills, load_packs


def test_generated_files_are_in_sync():
    assert build_marketplace.problems() == [], "run: python scripts/build_marketplace.py"


def test_one_plugin_per_pack_plus_the_full_plugin():
    names = [p["name"] for p in build_marketplace.build()["plugins"]]
    assert names[0] == "production-agent-skills"
    assert set(names[1:]) == set(load_packs())


def test_every_entry_is_strict():
    # strict:false + a root plugin.json makes Claude Code refuse to load the
    # plugin ("conflicting manifests") — found by installing from GitHub.
    assert all(p["strict"] is True for p in build_marketplace.build()["plugins"])


def test_root_plugin_json_declares_no_components():
    plugin = json.loads(build_marketplace.PLUGIN.read_text())
    assert "skills" not in plugin and "commands" not in plugin


def test_commands_are_not_in_the_auto_discovered_folder():
    # A top-level commands/ folder would be added to every pack plugin.
    assert not (build_marketplace.REPO_ROOT / "commands").exists()


def test_pack_plugins_carry_only_their_skills_and_commands():
    cmds = build_marketplace.command_skills()
    packs = load_packs()
    files = build_marketplace.pack_command_files()
    for plugin in build_marketplace.build()["plugins"][1:]:
        skills = packs[plugin["name"]]["skills"]
        assert plugin["skills"] == [f"./skills/{s}" for s in skills]
        pack_cmds = [p for p in files if p.parent.parent.name == plugin["name"]]
        assert pack_cmds, plugin["name"]
        assert all(cmds[p.name] in skills for p in pack_cmds)


def test_every_skill_has_a_command():
    covered = set(build_marketplace.command_skills().values())
    assert {s.name for s in discover_skills()} <= covered
