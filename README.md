# Production Agent Skills

Reusable workflows for AI agents.
Engineering • Data • Product • Research

[![Open Agent Skills format](https://img.shields.io/badge/format-Open%20Agent%20Skills-blue)](https://agentskills.io)
[![Spec validated](https://img.shields.io/badge/skills--ref-8%2F8%20valid-success)](docs/compatibility.md)
[![Skills](https://img.shields.io/badge/skills-8-brightgreen)](#the-8-skills)
[![Evaluations included](https://img.shields.io/badge/evaluations-80%20cases%20%2B%208%20workflows-orange)](evaluations/)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.11%20%7C%203.13-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![CI](https://github.com/alphasafal/production-agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/alphasafal/production-agent-skills/actions/workflows/validate-skills.yml)

> Agents already know a lot.
> The hard part is getting them to follow your process reliably.
>
> This repository turns repeated workflows into portable Agent Skills.

```
                 GENERAL AGENT
                       │
                Skill discovery
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 ENGINEERING          DATA           PRODUCT
       │               │               │
 repo-architect    data-scientist   product-manager
 debugging-       research-to-      feature-to-
 investigator      decision          production
 production-code-
 review
 system-design-
 reviewer
```

- **PROMPT** — what I want right now.
- **TOOL** — something the agent can do (read a file, run a shell command).
- **MCP** — how the agent connects to external systems and data.
- **SUBAGENT** — an isolated worker the agent delegates a bounded task to.
- **SKILL** — reusable procedural knowledge for *how* the work should be done.

Skills don't replace any of the above — they direct how an agent uses them.
See [`docs/skills-vs-tools.md`](docs/skills-vs-tools.md),
[`docs/skills-vs-mcp.md`](docs/skills-vs-mcp.md), and
[`docs/skills-vs-subagents.md`](docs/skills-vs-subagents.md) for the full
distinctions.

## Why this exists

Ask an agent to debug a production issue and, without guardrails, it will
often jump straight to a plausible-looking fix — because nothing forces it
to reproduce the bug and gather evidence first. Ask it to review a diff and
you'll get generic style comments unless something makes it actually check
for concurrency bugs, leaked secrets, or a missing idempotency key. General
capability isn't the bottleneck; a repeatable **procedure** is.

This repo packages eight such procedures as portable
[Agent Skills](https://agentskills.io) — an open format, not a
Claude-specific or Anthropic-specific one — each with a defined workflow,
output contract, and its own evaluation cases proving what it's actually
supposed to do (and not do).

## The 8 Skills

| Skill | What it does | Best used for |
|---|---|---|
| [repo-architect](skills/repo-architect/) | Maps an unfamiliar repo's structure, dependencies, and risks — without touching code | Onboarding to a new codebase before planning a change |
| [debugging-investigator](skills/debugging-investigator/) | Evidence-driven debugging: reproduce → evidence → hypotheses → confirmed root cause → minimal fix → regression test | Bugs, crashes, intermittent failures, production incidents |
| [production-code-review](skills/production-code-review/) | Senior-level review across 12 dimensions, findings ranked P0-P3, FACT vs. LIKELY RISK vs. OPTIONAL IMPROVEMENT | Reviewing a diff/PR before merge |
| [system-design-reviewer](skills/system-design-reviewer/) | Stress-tests a proposed architecture — failure modes, scaling, consistency, cost — before implementation starts | Reviewing an RFC or design doc |
| [data-scientist](skills/data-scientist/) | End-to-end tabular workflow: leakage/missingness checks, naive baseline before modeling, error/slice analysis | Analyzing a dataset or building a predictive model |
| [research-to-decision](skills/research-to-decision/) | Turns research into an auditable decision — sourced evidence, a decision matrix, an ADR | Build-vs-buy and technology-choice decisions |
| [product-manager](skills/product-manager/) | Turns a vague idea into a risk-ranked, right-sized MVP — resists scope explosion | Scoping a feature request into a PRD |
| [feature-to-production](skills/feature-to-production/) | Requirement → tests → implementation → review → deployment checklist → rollback plan | Shipping a well-defined feature end to end |

## Quick Start

```bash
git clone https://github.com/alphasafal/production-agent-skills.git
cd production-agent-skills
python scripts/list_skills.py
```

## Install One Skill

```bash
python scripts/install_skills.py \
  --skill debugging-investigator \
  --target ./my-project/.claude/skills
```

(Use `.agents/skills` instead of `.claude/skills` for Codex/Copilot — see
[`clients/`](clients/) for verified per-client paths.)

## Install All Skills

```bash
python scripts/install_skills.py --all --target ./my-project/.claude/skills
```

Add `--dry-run` to preview first, `--force` to overwrite an existing
install. Full options: `python scripts/install_skills.py --help`.

## How Skills Work

```
Discovery  →  Activation  →  Execution
(name +       (full SKILL.md   (references/scripts loaded
description    body loads)      only when instructions say to)
always loaded)
```

See [`docs/progressive-disclosure.md`](docs/progressive-disclosure.md) for
the full mechanism and why it's what makes skills cheap to keep around in
bulk.

## Anatomy of a Skill

```
skill/
├── SKILL.md          # required: frontmatter + workflow + output contract
├── references/       # optional: detail loaded only when SKILL.md says to
├── scripts/           # optional: deterministic, standalone, runnable code
└── assets/            # optional: templates to fill in
```

See [`docs/skill-anatomy.md`](docs/skill-anatomy.md) for a full annotated
breakdown, including why the `description` field is the single most
important line in the file.

## See it in action

**User:**
> "My API is occasionally returning duplicate payments."

**Without the skill**, a capable agent often jumps straight to a plausible
fix — "let me add a try/catch" or "let me add a retry guard" — with no
evidence it's actually addressing what's causing the duplication.

**With `debugging-investigator`:**

```
Observe → Reproduce → Evidence → Hypotheses → Test → Root cause → Minimal fix → Regression test
```

It reproduces the failure with two concurrent requests, reads the handler
code, finds the check-then-act race on `order.status`, rejects "client
retry" as the cause (the logs show two different source IPs, not one
retrying client), confirms the race directly, adds a unique constraint +
row lock, and adds a test that fails pre-fix and passes post-fix.

Full write-up: [`skills/debugging-investigator/examples/duplicate-payment-investigation.md`](skills/debugging-investigator/examples/duplicate-payment-investigation.md).
Try it yourself against a real, runnable, reproducible version of this
exact bug: [`examples/02-debug-a-failure/`](examples/02-debug-a-failure/).

🎥 Full walkthrough: `[VIDEO LINK — see demos/recording-script.md]`
⭐ GitHub: `github.com/alphasafal/production-agent-skills`

## Composition

Skills compose into pipelines without becoming one mega-skill:

```
research-to-decision → repo-architect → feature-to-production → production-code-review
                                                                        ↓
                                                          debugging-investigator (if needed)
```

See [`docs/composing-skills.md`](docs/composing-skills.md) for this and
two more pipelines (a data-driven product decision, an architecture
change) — and why no skill here auto-invokes another silently.

## Evaluation

Every skill ships 10 activation cases (5 obvious-positive, 2
ambiguous-positive, 3 negative) and one deeper workflow scenario with a
real fixture — see [`evaluations/`](evaluations/).

```bash
python scripts/validate_skills.py -v     # structural + schema + strict-YAML validation
python scripts/run_static_evals.py       # static lexical sanity checks
pytest tests/                            # 105 tests over the tooling's guarantees
```

### What's actually been verified

| Claim | Evidence |
|---|---|
| All 8 skills conform to the open spec | `skills-ref validate` (the reference implementation) passes 8/8, run per-skill in CI |
| Carrying all 8 skills is cheap | Discovery prompt measures **6,346 chars** — under Codex's documented 8,000-char ceiling |
| Tooling works on the Python range it claims | Full suite green on 3.9 / 3.11 / 3.13 (CI matrix) |
| Installation preserves validity | Skills installed into a real cloned repo, then re-validated with `skills-ref` |
| The bundled scripts are correct | Run against the real 891-row Titanic dataset; outputs match independently-computed ground truth |
| The debugging example is real | Bug reproduces 10/10 runs; documented fix resolves it 10/10; regression test fails pre-fix, passes post-fix |

**No fabricated benchmark numbers exist in this repository.**
[`evaluations/results/README.md`](evaluations/results/README.md) is
explicitly `NOT YET BENCHMARKED` — the harness is ready; real before/after
numbers require actually running it (methodology:
[`docs/evaluating-skills.md`](docs/evaluating-skills.md)).

## Compatibility

| | Claude Code | OpenAI Codex | GitHub Copilot |
|---|---|---|---|
| Status | ✅ install/structure tested | 🟡 expected per docs | 🟡 expected per docs |
| Skill path | `.claude/skills/` | `.agents/skills/` | `.agents/skills/`, `.claude/skills/`, or `.github/skills/` |

Full matrix (discovery, script execution, filesystem/network, MCP
dependency, per-row tested status): [`docs/compatibility.md`](docs/compatibility.md).
Per-client detail: [`clients/`](clients/). One canonical `SKILL.md` per
skill, always — see [`docs/architecture.md`](docs/architecture.md) for the
portability strategy.

## Build Your Own Skill

```
skills/my-skill/
└── SKILL.md
```

Start with [`docs/creating-your-first-skill.md`](docs/creating-your-first-skill.md)
for the full walkthrough, including the "is this actually worth a skill"
checklist and the minimum evaluation coverage a real skill needs.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — a skill contribution needs a
`SKILL.md`, ≥5 positive + ≥3 negative activation cases, one worked
example, a clear output contract, and quality checks. See
[`SECURITY.md`](SECURITY.md) for this repo's trust model around bundled
scripts, and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Roadmap

- [ ] Run a real before/after benchmark and fill in `evaluations/results/README.md`
- [ ] Independently verify live auto-activation in a fresh Claude Code session
- [ ] Test installation against a live Codex and Copilot session, update `docs/compatibility.md`
- [ ] Community-contributed skills beyond the initial eight

## License

[MIT](LICENSE)
