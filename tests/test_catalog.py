"""install-index.tsv and docs/prompt-cheatsheet.md are generated and stay in sync with their sources."""
import build_catalog
from _lib import discover_skills, load_packs


def rows(kind):
    return [
        line.split("\t")
        for line in build_catalog.build_index().splitlines()
        if line.startswith(kind + "\t")
    ]


def test_generated_files_are_in_sync():
    assert build_catalog.problems() == [], "run: python scripts/build_catalog.py"


def test_index_has_every_pack_with_its_skills_in_order():
    packs = load_packs()
    assert [(r[1], r[3].split()) for r in rows("pack")] == [(n, s["skills"]) for n, s in packs.items()]


def test_index_has_every_skill_with_a_command_and_a_prompt():
    skills = discover_skills()
    index = rows("skill")
    assert [r[1] for r in index] == [s.name for s in skills]
    for _, name, command, prompt in index:
        assert command.startswith("/"), f"{name}: no slash command"
        assert len(prompt) > 10, f"{name}: no starter prompt"


def test_index_rows_have_exactly_four_fields():
    # install.sh reads fields by position with cut/awk; an extra tab would shift them.
    assert all(len(r) == 4 for r in rows("pack") + rows("skill"))


def test_cheatsheet_prompts_come_from_the_activation_suite():
    sheet = build_catalog.build_cheatsheet()
    for skill in discover_skills():
        assert f"## {skill.name}\n" in sheet
        prompts = build_catalog.obvious_prompts(skill)[:build_catalog.PROMPTS_PER_SKILL]
        assert len(prompts) == build_catalog.PROMPTS_PER_SKILL
        for prompt in prompts:
            assert f'- "{prompt}"' in sheet


def test_cheatsheet_handoffs_point_at_real_skills():
    names = {s.name for s in discover_skills()}
    for skill in discover_skills():
        for _, target in build_catalog.handoffs(skill):
            assert target in names and target != skill.name
