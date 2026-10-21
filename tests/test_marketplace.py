"""The plugin marketplace is generated from packs.json and stays in sync with it."""
import build_marketplace
from _lib import load_packs


def test_marketplace_file_is_in_sync():
    assert build_marketplace.main.__module__  # importable
    import json
    built = build_marketplace.build()
    on_disk = json.loads(build_marketplace.MARKETPLACE.read_text())
    assert on_disk == built, "run: python scripts/build_marketplace.py"


def test_one_plugin_per_pack_plus_the_full_plugin():
    names = [p["name"] for p in build_marketplace.build()["plugins"]]
    assert names[0] == "production-agent-skills"
    assert set(names[1:]) == set(load_packs())


def test_pack_plugins_carry_only_their_skills_and_commands():
    cmds = build_marketplace.command_skills()
    packs = load_packs()
    for plugin in build_marketplace.build()["plugins"][1:]:
        skills = packs[plugin["name"]]["skills"]
        assert plugin["skills"] == [f"./skills/{s}" for s in skills]
        assert all(cmds[c] in skills for c in plugin["commands"])


def test_every_skill_has_a_command():
    from _lib import discover_skills
    covered = set(build_marketplace.command_skills().values())
    assert {s.name for s in discover_skills()} <= covered
