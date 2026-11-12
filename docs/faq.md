# FAQ

## Is it free?

Yes. Everything here is [MIT licensed](../LICENSE): use it at work, change
it, ship it inside your own product. There is no account, no API key and no
paid tier. A skill is a folder of Markdown (plus a few optional scripts) that
your agent reads from your disk.

## What do I need?

An agent that supports [Agent Skills](https://agentskills.io): Claude Code,
Codex, Cursor, GitHub Copilot, Gemini CLI and others. The skills add no
cost of their own; you pay only for whatever agent you already use.

## What is the fastest way to install?

From your project folder:

```bash
curl -fsSL https://raw.githubusercontent.com/alphasafal/production-agent-skills/main/install.sh | sh -s -- --pack backend-engineer
```

Replace `backend-engineer` with your role (`--list` shows them all), or use
`--all`. In Claude Code the plugin route also gives you slash commands; see
the [README](../README.md#install).

## Where do the files go?

| You use | Project install | With `--global` |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex, Copilot, Cursor, Gemini CLI | `.agents/skills/` | `~/.agents/skills/` |

With no `--agent`, the installer picks `.claude/skills/` if the project has
a `.claude` folder and `.agents/skills/` otherwise, and prints which one it
chose. Anything else: `--target DIR`.

## Project or global?

Project (the default) puts the skills in the repository, so you can commit
them and the whole team gets the same ones. `--global` puts them in your
home directory for every project on your machine.

## How do I update?

Run the same command again with `--force`. Without it, skills that are
already installed are left alone, so a local edit is never overwritten by
accident.

Claude Code plugin users: `/plugin marketplace update alphasafal-skills`
fetches the latest catalog, and turning on auto-update for the marketplace
(`/plugin`, **Marketplaces** tab) keeps installed plugins current.

## How do I remove them?

Same command with `--uninstall`, for example
`... | sh -s -- --pack backend-engineer --uninstall`. It only deletes
directories that contain a `SKILL.md`. Or delete the folders yourself; a
skill is nothing more than its folder.

## Do I need all 15?

No, and on Codex you should not: it caps the skill list it reads at about
8,000 characters, and every role pack is kept under that. Install the pack
for your role and add single skills with `--skill` when you need them.

## How do I use a skill once it is installed?

Restart the agent, then describe the task normally: "this test is flaky,
find out why", "review this PR before I merge". The agent loads the
matching skill by itself. The [prompt cheatsheet](prompt-cheatsheet.md) has
phrasings for every skill. To force one, name it ("use the
debugging-investigator skill"), or in Claude Code type `/` and pick it.

## A skill did not load. What now?

1. Restart the agent; most read the skills directory at startup.
2. Check the folder is where your agent looks (table above) and that the
   folder name was not changed.
3. Name the skill explicitly in your message.
4. If the phrasing you used seems like it should have worked, open an issue
   with the prompt. Those become new cases in `evaluations/activation/`.

## I am not on macOS or Linux, or cannot run scripts

- **Windows:** `npx skills add alphasafal/production-agent-skills` (needs
  Node), or clone the repository and run
  `python scripts/install_skills.py --pack sre --agent claude`. `install.sh`
  needs a POSIX shell and is only tested on Linux and macOS.
- **No terminal at all, or no network on the target machine:** download
  `pack-<role>.zip` or `all-skills.zip` from the
  [latest release](https://github.com/alphasafal/production-agent-skills/releases/latest)
  and unzip it into the skills directory.

## Can I use these in the Claude desktop or web app?

Each release has a `claude-app-<skill>.zip` per skill built to Anthropic's
documented upload rules. See [`clients/claude-apps.md`](../clients/claude-apps.md)
for the steps and for what has and has not been tested.

## Is piping a script into my shell safe?

Read [`SECURITY.md`](../SECURITY.md): it lists exactly what `install.sh`
does (one download, copy, clean up) and three ways to install without
piping anything.

## Does anything get sent anywhere?

Not by this repository. The skills are local files; the installer makes
one request to download the repository from GitHub and nothing else.
Third-party tools such as `npx skills` have their own policies.

## Can I change a skill?

Yes. Edit the installed copy for your team's conventions, or fork the
repository. If you change a `description`, run
`python scripts/run_routing_evals.py` in a clone: descriptions decide
which skill loads, and a small edit can pull prompts away from a
neighbouring skill.

## Are the benchmark numbers real?

Every number is from a recorded run, with the date, model and run count
next to it, and the gaps are listed alongside the wins:
[`evaluations/results/README.md`](../evaluations/results/README.md). They
were measured in Claude Code with one model; they are not a promise about
every agent.

## How do I add my own skill?

[`docs/creating-your-first-skill.md`](creating-your-first-skill.md), then
[`CONTRIBUTING.md`](../CONTRIBUTING.md).
