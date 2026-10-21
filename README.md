# Production Agent Skills

**Evaluated, production-grade skills for AI coding agents — organized by role.**
Test-first development, specs and plans, frontend UI review, debugging, code
review, incident response, deploy pipelines, threat modeling, security audits,
system design, data science, decisions and PRDs: each a
procedure a senior engineer would follow, packaged as a portable
[Agent Skill](https://agentskills.io) that works in Claude Code, Codex,
Cursor, Copilot, Cline and 15+ more agents.

[![Skills](https://img.shields.io/badge/skills-15-brightgreen)](#the-15-skills)
[![Role packs](https://img.shields.io/badge/role%20packs-7-blue)](#pick-your-role)
[![Spec validated](https://img.shields.io/badge/skills--ref-15%2F15%20valid-success)](docs/compatibility.md)
[![Routing](https://img.shields.io/badge/routing-75%2F75%20rank--1-success)](evaluations/README.md#tier-2-routing-scriptsrun_routing_evalspy)
[![Behavioral evals](https://img.shields.io/badge/benchmarked-with%20vs.%20without%20skill-orange)](evaluations/results/README.md)
[![CI](https://github.com/alphasafal/production-agent-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/alphasafal/production-agent-skills/actions/workflows/validate-skills.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

> **Benchmarked, not just written.** On 15 scenarios with planted problems,
> the same agent did **54%** of the required work without these skills and
> **93%** with them (blind-graded, 3 runs per arm, `claude-sonnet-5-5`).
> Under pressure prompts ("prod is on fire, skip the tests"): **63% → 85%**.
> Activation: 143/150 prompts load the right skill; all 45 should-stay-quiet
> prompts stay quiet. [Full results and known gaps →](evaluations/results/README.md)

## Pick your role

Install only what your job needs — each pack is small enough for every
agent's skill budget.

| Role | Skills | Claude Code |
|---|---|---|
| **Backend / full-stack engineer** | [repo-architect](skills/repo-architect/), [feature-to-production](skills/feature-to-production/), [test-first-developer](skills/test-first-developer/), [debugging-investigator](skills/debugging-investigator/), [production-code-review](skills/production-code-review/) | `/plugin install backend-engineer@alphasafal-skills` |
| **Frontend engineer** | [frontend-ui-reviewer](skills/frontend-ui-reviewer/), [test-first-developer](skills/test-first-developer/), [feature-to-production](skills/feature-to-production/), [production-code-review](skills/production-code-review/) | `/plugin install frontend-engineer@alphasafal-skills` |
| **Tech lead / architect** | [spec-and-plan](skills/spec-and-plan/), [system-design-reviewer](skills/system-design-reviewer/), [research-to-decision](skills/research-to-decision/), [production-code-review](skills/production-code-review/), [repo-architect](skills/repo-architect/), [threat-modeler](skills/threat-modeler/) | `/plugin install tech-lead@alphasafal-skills` |
| **SRE / DevOps** | [incident-responder](skills/incident-responder/), [deploy-pipeline-reviewer](skills/deploy-pipeline-reviewer/), [debugging-investigator](skills/debugging-investigator/) | `/plugin install sre@alphasafal-skills` |
| **Security engineer** | [threat-modeler](skills/threat-modeler/), [security-auditor](skills/security-auditor/), [production-code-review](skills/production-code-review/) | `/plugin install security@alphasafal-skills` |
| **Data scientist / analyst** | [data-scientist](skills/data-scientist/), [research-to-decision](skills/research-to-decision/) | `/plugin install data-scientist@alphasafal-skills` |
| **Product manager** | [product-manager](skills/product-manager/), [research-to-decision](skills/research-to-decision/), [data-scientist](skills/data-scientist/) | `/plugin install product-manager@alphasafal-skills` |

First time in Claude Code? Add the marketplace once:
`/plugin marketplace add alphasafal/production-agent-skills` — then install
a role above, or everything with
`/plugin install production-agent-skills@alphasafal-skills`.

<details>
<summary><b>Any other agent</b> (Codex, Cursor, Copilot, Cline, Gemini CLI, …) — one command per role</summary>

```bash
# Backend / full-stack engineer
npx skills add alphasafal/production-agent-skills --skill repo-architect --skill feature-to-production --skill test-first-developer --skill debugging-investigator --skill production-code-review
# Frontend engineer
npx skills add alphasafal/production-agent-skills --skill frontend-ui-reviewer --skill test-first-developer --skill feature-to-production --skill production-code-review
# Tech lead / architect
npx skills add alphasafal/production-agent-skills --skill spec-and-plan --skill system-design-reviewer --skill research-to-decision --skill production-code-review --skill repo-architect --skill threat-modeler
# SRE / DevOps
npx skills add alphasafal/production-agent-skills --skill incident-responder --skill deploy-pipeline-reviewer --skill debugging-investigator
# Security engineer
npx skills add alphasafal/production-agent-skills --skill threat-modeler --skill security-auditor --skill production-code-review
# Data scientist / analyst
npx skills add alphasafal/production-agent-skills --skill data-scientist --skill research-to-decision
# Product manager
npx skills add alphasafal/production-agent-skills --skill product-manager --skill research-to-decision --skill data-scientist

# Everything
npx skills add alphasafal/production-agent-skills
```

No Node? `python scripts/install_skills.py --pack sre --target ./.claude/skills`
(see [`clients/`](clients/) for each agent's skills directory).
</details>

## Why this exists

Ask an agent to debug a production issue and it will often jump straight
to a plausible-looking fix, because nothing makes it reproduce the bug
first. Ask it to review a deploy pipeline and you get YAML style notes
while `pull_request_target` hands your secrets to any fork. General
capability isn't the bottleneck; a repeatable **procedure** is — one that
holds when the prompt says *"prod is on fire, skip the tests."*

Every skill here has a defined workflow, an output contract, red flags and
rationalizations that keep it on track under pressure, and its own
evaluation suite — including a benchmark against the same agent *without*
the skill.

## The 15 skills

| Skill | Role | What it makes the agent do |
|---|---|---|
| [test-first-developer](skills/test-first-developer/) | Engineering | Red → green → refactor: discover the repo's test runner, see every new test fail first, minimal code, full suite |
| [spec-and-plan](skills/spec-and-plan/) | Tech lead | Scoped ticket → spec with open questions and testable acceptance criteria → vertical-slice task plan |
| [frontend-ui-reviewer](skills/frontend-ui-reviewer/) | Frontend | Keyboard and screen-reader paths, every UI state, contrast, mobile layout, layout shift and bundle bloat; P0–P3 with fixes |
| [debugging-investigator](skills/debugging-investigator/) | Engineering | Reproduce → evidence → competing hypotheses → confirmed root cause → minimal fix → regression test |
| [production-code-review](skills/production-code-review/) | Engineering | Review a diff across 12 dimensions; findings ranked P0–P3, FACT vs. LIKELY RISK, and a merge verdict |
| [feature-to-production](skills/feature-to-production/) | Engineering | Acceptance criteria → tests → smallest change → review → deployment checklist → rollback plan |
| [repo-architect](skills/repo-architect/) | Engineering | Map an unfamiliar codebase — entry points, data flow, risks — without touching code |
| [system-design-reviewer](skills/system-design-reviewer/) | Tech lead | Stress-test an RFC: failure modes, scaling, consistency, caching, cost — before anything is built |
| [research-to-decision](skills/research-to-decision/) | Tech lead / PM | Sourced evidence, explicit criteria, trade-offs, and an ADR you can defend |
| [incident-responder](skills/incident-responder/) | SRE | Live incident: measure impact, correlate changes, **mitigate first**, status updates, blameless postmortem |
| [deploy-pipeline-reviewer](skills/deploy-pipeline-reviewer/) | DevOps | Review CI/CD, Dockerfiles, migrations and rollout before they touch prod; go/no-go with fixes |
| [threat-modeler](skills/threat-modeler/) | Security | Trust boundaries, STRIDE threats as concrete attacks, ranked mitigations as testable requirements |
| [security-auditor](skills/security-auditor/) | Security | Audit existing code; every finding traced from input to sink, ranked by exploitability, with a fix |
| [data-scientist](skills/data-scientist/) | Data | Leakage and missingness checks, naive baseline first, error and slice analysis |
| [product-manager](skills/product-manager/) | Product | Vague idea → risk-ranked assumptions → right-sized MVP → PRD; resists scope explosion |

## Slash commands (Claude Code)

Skills activate on their own from what you ask. Commands run one now:

| Command | Skill | | Command | Skill |
|---|---|---|---|---|
| `/test-first` | test-first-developer | | `/decide` | research-to-decision |
| `/plan` | spec-and-plan | | `/incident` | incident-responder |
| `/ui-review` | frontend-ui-reviewer | | `/pipeline-review` | deploy-pipeline-reviewer |
| `/investigate` | debugging-investigator | | `/threat-model` | threat-modeler |
| `/pr-review` | production-code-review | | `/security-audit` | security-auditor |
| `/ship-feature` | feature-to-production | | `/analyze-data` | data-scientist |
| `/map-repo` | repo-architect | | `/prd` | product-manager |
| `/design-review` | system-design-reviewer | |  | |

## What a skill is (and isn't)

- **PROMPT** — what you want right now.
- **TOOL** — something the agent can do (read a file, run a command).
- **MCP** — how the agent reaches external systems and data.
- **SUBAGENT** — an isolated worker for a bounded task.
- **SKILL** — reusable procedural knowledge for *how* the work should be done.

Skills don't replace the others — they direct how an agent uses them. See
[`docs/skills-vs-tools.md`](docs/skills-vs-tools.md),
[`docs/skills-vs-mcp.md`](docs/skills-vs-mcp.md) and
[`docs/skills-vs-subagents.md`](docs/skills-vs-subagents.md).

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

## Why these skills hold up under pressure

Agents rarely skip a step because they don't know it. They skip it because
a plausible reason shows up: *"it's obviously the cache"*, *"the CTO
already approved it"*, *"we'll add tests next sprint"*. Every skill here
names those reasons in advance:

- **`# Red flags`** — observable signs the workflow is being skipped right
  now ("you are editing code and can't name the command that reproduces
  the failure").
- **`# Common rationalizations`** — the excuse, and why it doesn't hold.

| Rationalization | Reality |
|---|---|
| "Adding a retry makes it go away." | Making a symptom go away is not a root cause. Retries around a race usually make duplicates *more* likely. |
| "This feature is the best predictor — great!" | Too-good features are the first leakage suspect. Ask when the value becomes known. |
| "The author knows this code better than me." | Then ask a precise question in the review. Deference is not a review outcome. |

The validator requires both sections in every skill, and the
[pressure scenarios](evaluations/workflows/pressure/) test whether they
work: prompts that argue *for* skipping the workflow.

## Anatomy of a Skill

```
skill/
├── SKILL.md          # required: frontmatter + workflow + output contract + red flags
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

Four tiers, from free-and-deterministic to real-agent-and-measured. Full
methodology: [`evaluations/README.md`](evaluations/README.md).

| Tier | Question | Command | In CI |
|---|---|---|---|
| Structure | Spec-valid? All 12 sections? Within the discovery budget? | `python scripts/validate_skills.py` | ✅ gated |
| Routing | Does each prompt reach the right skill out of all 15? | `python scripts/run_routing_evals.py` | ✅ gated |
| Activation | Does a real agent load the right skill? | `python scripts/run_behavioral_evals.py --mode activation` | on demand |
| Behavior | Is the work better *with* the skill than without? | `python scripts/run_behavioral_evals.py` | on demand |

### Results

Measured 2026-10-21 with `claude-sonnet-5-5` (agent and blind grader), 3 runs per arm:

| | Without skill | With skill |
|---|---:|---:|
| Required behaviors, 15 standard scenarios | 54% | **93%** |
| Required behaviors, 5 pressure scenarios | 63% | **85%** |
| Forbidden behaviors (e.g. fixing before reproducing), all standard runs | 24 | **6** |
| Activation: right skill loads / wrong skill loads | — | **143/150 / 1** |

Biggest gains: product-manager 8% → 100%, repo-architect 33% → 100%,
debugging-investigator 27% → 87%, feature-to-production 20% → 80%,
test-first-developer 40% → 73%, spec-and-plan 73% → 100%. Where the baseline
is already near-perfect (security-auditor, system-design-reviewer,
frontend-ui-reviewer) the fixtures are too easy to show a difference; that, and every other open
gap, is listed on the results page.

Full tables, per-scenario breakdown and method: [`evaluations/results/README.md`](evaluations/results/README.md).

### What's verified, and how

| Claim | Evidence |
|---|---|
| All 15 skills conform to the open spec | `skills-ref validate` (the reference implementation) passes 15/15 in CI |
| Every skill has all 12 sections, incl. red flags + rationalizations | `validate_skills.py` fails the build otherwise |
| Each prompt routes to the right skill, catalog-wide | 75/75 obvious prompts rank their skill #1 of 15; 21/21 "belongs to another skill" negatives route there; CI-gated |
| Skills change what the agent does | Blind-graded with-vs-without benchmark across 3 rounds, 162 workflow runs; see Results above |
| Routing generalizes beyond the tuned prompts | 24 held-out prompts never used for tuning: 14/24 rank #1, 23/24 top-3 |
| Every role pack is cheap to carry | Largest pack's discovery prompt is 5,629 bytes, under Codex's 8,000 ceiling — enforced per pack in CI with `skills-ref to-prompt` |
| Reference answers never leak to the agent | Validator rejects any scenario whose `workspace_files` include a reference answer or spoiler |
| The bundled scripts are correct | Run against the real 891-row Titanic dataset; outputs match independently-computed ground truth |
| The debugging example is real | Bug reproduces 10/10 runs; documented fix resolves it 10/10 |

```bash
python scripts/validate_skills.py -v     # structure, schema, strict YAML, sections
python scripts/run_routing_evals.py      # catalog-wide routing (free, deterministic)
pytest tests/                            # 222 tests over the tooling's guarantees
python scripts/run_behavioral_evals.py --dry-run   # see what a real run would do
```

**No fabricated benchmark numbers exist in this repository.** Every
number above comes from a recorded run, labelled with date, model and run
count.

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

- [x] Run a real before/after benchmark and fill in `evaluations/results/README.md`
- [x] Measure live auto-activation in Claude Code (`--mode activation`)
- [x] Package as a Claude Code plugin with slash commands
- [ ] Re-run the benchmark on every skill change that affects behavior, and publish the delta in the PR
- [ ] Test installation against a live Codex and Copilot session, update `docs/compatibility.md`
- [ ] Behavioral evals for Codex / Copilot (the runner is CLI-agnostic in shape; only Claude Code is wired)
- [ ] More roles: frontend (accessibility + Core Web Vitals), QA/test strategy, ML engineering
- [ ] Community-contributed skills (see [CONTRIBUTING.md](CONTRIBUTING.md))

## License

[MIT](LICENSE)
