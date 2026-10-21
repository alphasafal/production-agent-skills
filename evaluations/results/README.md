# Evaluation Results

Every number on this page comes from a recorded run of
`scripts/run_behavioral_evals.py`. Nothing is estimated or simulated.

| | |
|---|---|
| Date | 2026-10-21 |
| Agent and grader model | `claude-sonnet-5-5` (all 632 transcripts, rounds 1–3), Claude Code 2.1.306 |
| Runs | Workflows: 3 per arm per scenario. Activation: 1 per prompt (2 for the round-3 re-checks). |
| Raw output | `evaluations/results/runs/` (gitignored; run IDs listed below) |

## Headline

| | Without skill | With skill |
|---|---:|---:|
| Required behaviors observed — 15 standard scenarios | 54% | **93%** |
| Required behaviors observed — 5 pressure scenarios | 63% | **85%** |
| Forbidden behaviors — standard scenarios, all runs | 24 | **6** |

| Activation (all 12 skills installed together) | |
|---|---:|
| Obvious prompts that load the right skill | **71/75** |
| Ambiguous prompts that load the right skill | **27/30** |
| Negative prompts where the skill correctly stays quiet | **45/45** |
| Times the *wrong* skill was loaded | **1** (not reproduced on 2 re-runs; see round 3) |

## Method

- **Workflow scenarios** (`evaluations/workflows/**`) run in a throwaway git
  workspace outside the repo containing only the scenario's
  `workspace_files` — fixtures with planted problems and decoys. The
  **baseline** arm has no skill; the **with-skill** arm has only that skill
  installed, *without its `examples/`* (several worked examples answer the
  exact scenario, so including them would leak the answer).
- A **separate grader call**, not told which arm it is reading, checks the
  transcript and workspace diff against the scenario's
  `required_behaviors`, `forbidden_behaviors` and `expected_artifacts`. If
  the scenario has a `reference_answer`, only the grader sees it.
- **"Required behaviors"** is the mean fraction of a scenario's required
  behaviors the grader observed, across the 3 runs of that arm.
- **Activation** installs all 12 skills in one empty workspace, sends each
  `evaluations/activation/` prompt with a neutral line asking the agent to
  proceed on stated assumptions if something referenced is missing (applied
  identically to every prompt), allows 6 read-only turns, and records which
  skill the agent loads.

## Workflow results

### Standard scenarios

| Scenario | Without skill | With skill | Δ | Forbidden behaviors (without → with) | Skill loaded | Source |
|---|---:|---:|---:|---|---:|---|
| `data-scientist-workflow-01` | 50% | **100%** | +50 pts | 3 → 0 | 3/3 | round 2 (round 1: 100% with skill, loaded 3/3) |
| `debugging-investigator-workflow-01` | 27% | **87%** | +60 pts | 6 → 2 | 3/3 | round 2 (round 1: 87% with skill, loaded 3/3) |
| `deploy-pipeline-reviewer-workflow-01` | 73% | **100%** | +27 pts | 0 → 0 | 3/3 | round 1 |
| `feature-to-production-workflow-01` | 20% | **80%** | +60 pts | 3 → 1 | 3/3 | round 2 (round 1: 27% with skill, loaded 0/3) |
| `incident-responder-workflow-01` | 33% | **73%** | +40 pts | 0 → 0 | 3/3 | round 1 |
| `product-manager-workflow-01` | 8% | **100%** | +92 pts | 3 → 0 | 3/3 | round 1 |
| `production-code-review-workflow-01` | 80% | **100%** | +20 pts | 0 → 0 | 3/3 | round 1 |
| `repo-architect-workflow-01` | 33% | **100%** | +67 pts | 3 → 2 | 3/3 | round 1 |
| `research-to-decision-workflow-01` | 42% | **100%** | +58 pts | 0 → 0 | 3/3 | round 1 |
| `security-auditor-workflow-01` | 100% | **100%** | +0 pts | 0 → 0 | 3/3 | round 1 |
| `system-design-reviewer-workflow-01` | 83% | **83%** | +0 pts | 0 → 0 | 3/3 | round 2 (round 1: 83% with skill, loaded 3/3) |
| `threat-modeler-workflow-01` | 60% | **100%** | +40 pts | 0 → 0 | 3/3 | round 1 |
| `test-first-developer-workflow-01` | 40% | **73%** | +33 pts | 3 → 1 | 3/3 | round 3 |
| `spec-and-plan-workflow-01` | 73% | **100%** | +27 pts | 3 → 0 | 3/3 | round 3 |
| `frontend-ui-reviewer-workflow-01` | 93% | **93%** | +0 pts | 0 → 0 | 3/3 | round 3 |
| **Mean** | **54%** | **93%** | **+39 pts** | | | |

### Pressure scenarios (the prompt argues for skipping the workflow)

| Scenario | Without skill | With skill | Δ | Forbidden behaviors (without → with) | Skill loaded | Source |
|---|---:|---:|---:|---|---:|---|
| `data-scientist-pressure-sunk-cost` | 75% | **92%** | +17 pts | 0 → 0 | 0/3 | round 2 (round 1: 83% with skill, loaded 0/3) |
| `debugging-investigator-pressure-time` | 58% | **100%** | +42 pts | 0 → 0 | 3/3 | round 2 (round 1: 58% with skill, loaded 0/3) |
| `feature-to-production-pressure-skip-tests` | 75% | **75%** | +0 pts | 0 → 0 | 3/3 | round 2 (round 1: 75% with skill, loaded 0/3) |
| `product-manager-pressure-scope` | 8% | **58%** | +50 pts | 3 → 3 | 3/3 | round 1 |
| `production-code-review-pressure-authority` | 100% | **100%** | +0 pts | 0 → 0 | 3/3 | round 1 |
| **Mean** | **63%** | **85%** | **+22 pts** | | | |

"Source: round 2" means the scenario was re-run after the round-1 findings
below; the round-1 figure is kept beside it.

## Activation results

| Skill | Obvious | Ambiguous | Negative (must stay quiet) | Round 1 obvious |
|---|---:|---:|---:|---:|
| data-scientist | 3/5 | 2/2 | 3/3 | 5/5 |
| debugging-investigator | 5/5 | 2/2 | 3/3 | 5/5 |
| deploy-pipeline-reviewer | 5/5 | 2/2 | 3/3 | 5/5 |
| feature-to-production | 5/5 | 2/2 | 3/3 | 2/5 |
| frontend-ui-reviewer | 5/5 | 1/2 | 3/3 | — |
| incident-responder | 4/5 | 2/2 | 3/3 | 4/5 |
| product-manager | 4/5 | 2/2 | 3/3 | 4/5 |
| production-code-review | 5/5 | 2/2 | 3/3 | 4/5 |
| repo-architect | 5/5 | 1/2 | 3/3 | 5/5 |
| research-to-decision | 5/5 | 2/2 | 3/3 | 5/5 |
| security-auditor | 5/5 | 2/2 | 3/3 | 5/5 |
| spec-and-plan | 5/5 | 2/2 | 3/3 | — |
| system-design-reviewer | 5/5 | 2/2 | 3/3 | 0/5 |
| test-first-developer | 4/5 | 2/2 | 3/3 | — |
| threat-modeler | 5/5 | 2/2 | 3/3 | 5/5 |
| **Total** | **70/75** | **28/30** | **45/45** | 49/60 |

Activation table above is round 3: all 150 prompts, all 15 skills installed together (run `20261021-055604-activation`).
Remaining misses in that run:

- `data-scientist-pos-02`: expected `data-scientist`, loaded nothing
- `data-scientist-pos-03`: expected `data-scientist`, loaded nothing
- `frontend-ui-reviewer-amb-02`: expected `frontend-ui-reviewer`, loaded nothing
- `incident-responder-pos-04`: expected `incident-responder`, loaded nothing
- `product-manager-pos-04`: expected `product-manager`, loaded spec-and-plan
- `repo-architect-amb-02`: expected `repo-architect`, loaded nothing
- `test-first-developer-pos-05`: expected `test-first-developer`, loaded nothing

## What round 1 found, and what changed

Round 1 (run `20261021-035657-workflow`, `20261021-041549-activation`)
surfaced three problems. Round 2 re-measured after fixing them.

1. **Skills that didn't load.** `system-design-reviewer` loaded on 0/5
   obvious prompts and `feature-to-production` on 2/5; the agent decided it
   could review a design or add a feature without them. Part of this was the
   harness — it capped activation at 2 turns, and agents often look for the
   referenced file first — so the harness was fixed (6 read-only turns,
   neutral suffix). A controlled re-run with the fixed harness and the *old*
   descriptions still gave 1/5 and 2/5, so the descriptions were rewritten to
   say when to load the skill ("load it first … even before you have read or
   asked for the document"). Round 2: **5/5 and 5/5**.
2. **Skills that didn't load under pressure.** In round 1, three pressure
   prompts ("URGENT … just push a quick fix", "skip the tests", "just write
   it up") never loaded the skill (0/3 each), so those rows measured nothing.
   Descriptions now name those request shapes. Round 2: debugging under time
   pressure loads 3/3 and goes **58% → 100%**; feature-to-production loads
   3/3. data-scientist under sunk-cost pressure **still loads 0/3** — open
   problem below.
3. **The feature-to-production review step.** Even with the skill loaded,
   the agent skipped the review stage and said so. A red flag and a
   rationalization for exactly that were added; with the skill now loading,
   the standard scenario went **27% → 80%**.

## Round 3: three new skills

Added `test-first-developer`, `spec-and-plan` and `frontend-ui-reviewer`,
each benchmarked the same way (3 runs per arm, blind grader).

- **spec-and-plan 73% → 100%**, forbidden behaviors 3 → 0. Without the
  skill, the agent split work by layer and silently resolved ambiguities in
  the brief. With it, it raised open questions and produced vertical slices.
- **test-first-developer 40% → 73%.** All 3 baseline runs edited the code
  and the tests in a single step and never saw a test fail. With the skill,
  2 of 3 runs went red before every rule. Not yet 100%: the boundary tests
  were weak in all 3 with-skill runs. The ordering test used amounts where
  both orders give the same rounded total, so it can't catch the bug it
  targets, and rounding wasn't tested. One run also skipped the red step for
  some rules.
- **frontend-ui-reviewer 93% → 93%.** The baseline already finds almost
  every planted issue in this fixture, so it can't show what the skill adds.
  It needs a harder fixture (see gaps).
- **The first wrong-skill load.** Round-3 activation loaded `spec-and-plan`
  on `product-manager-pos-04` ("turn this rough feature idea into something
  our engineering team can actually build"). Two follow-up runs of that
  prompt loaded nothing, never the wrong skill, so it's a sometimes-misroute
  rather than a systematic one. A description reword that tried to prevent
  it was measured and rejected: spec-and-plan's ambiguous prompts fell from
  4/4 to 0/4 (runs `20261021-060850` vs `20261021-073551`).

## Known gaps (honest list)

- **`frontend-ui-reviewer` shows no measurable gain** (93% → 93%). The fixture
  is too easy for the baseline and needs subtler issues (focus restore order,
  `aria-live` timing, CLS from late-loading fonts).
- **`test-first-developer` reaches 73%, not 100%.** The consistent miss is
  weak boundary cases: ordering tests with values that can't tell the two
  orders apart, and no rounding test. The skill's `references/test-design-patterns.md`
  should push harder on choosing values that make a wrong implementation fail.
- **`product-manager-pos-04`** sometimes misroutes to `spec-and-plan` (1 of 3
  runs) and otherwise loads nothing.

- **data-scientist under sunk-cost pressure doesn't load the skill** (0/3).
  The agent still scores 92% vs. 75% without it, but that comes from the
  model, not the skill. Its activation also dipped from 5/5 to 3/5 between
  rounds on two obvious prompts.
- **No measurable difference where the baseline is already perfect:**
  `security-auditor` (standard scenario) and `production-code-review` under
  authority pressure both score 100% without the skill. Those fixtures are
  too easy to show what the skill adds and need harder versions.
- **`system-design-reviewer` shows no difference** (83% → 83%) on the URL
  shortener scenario; the baseline catches most of it unaided.
- **`feature-to-production` under skip-the-tests pressure**: the skill now
  loads but the score didn't move (75% → 75%).
- One run per activation prompt: treat single misses as noise until repeated.
- Same model as agent and grader. A different grader model would
  strengthen the result.

## Run IDs

| Run | What |
|---|---|
| `20261021-035657-workflow` | Round 1: all 17 scenarios × 2 arms × 3 runs |
| `20261021-041549-activation` | Round 1: all 120 activation prompts |
| `20261021-041928`, `-041959`, `-042105`, `-042143` (activation) | Harness checks on two skills: fixed harness with old descriptions |
| `20261021-042315-activation` | Round 2: all 120 activation prompts |
| `20261021-055002`, `-055132`, `-055432` (workflow) | Round 3: test-first-developer, spec-and-plan, frontend-ui-reviewer |
| `20261021-055604-activation` | Round 3: all 150 activation prompts, 15 skills installed |
| `20261021-060653`, `-060850`, `-073551`, `-073904` (activation) | Round 3: 2-run re-checks of product-manager and spec-and-plan, tried vs. original wording |
| `20261021-043053`, `-043226`, `-043354`, `-044646` (workflow) | Round 2: feature-to-production, debugging-investigator, data-scientist, system-design-reviewer |

## Reproduce

```bash
python scripts/run_behavioral_evals.py --runs 3              # all workflow scenarios
python scripts/run_behavioral_evals.py --mode activation     # all activation prompts
```
