# Recording Script (5-7 minutes)

Companion to `demos/demo-prompts.md` and `demos/expected-behavior.md`. Times
are approximate — pace to what feels natural, not the clock.

---

## 0:00–0:20 — Hook

> "I finished the Agent Skills course from Anthropic and DeepLearning.AI.
> But instead of posting the certificate, I turned what I learned into an
> open-source skills library."

Show the repo landing on GitHub for two seconds, then cut to terminal/editor.

## 0:20–1:00 — The problem

Show, side by side or in sequence:

```
PROMPT   = what I want right now
SKILL    = how the work should repeatedly be done
```

> "A prompt asks for something once. A skill stores the procedure — the
> steps, the checks, the output format — so it works the same way every
> time, for anyone who installs it."

## 1:00–1:45 — Architecture

Show a quick diagram (the README's ASCII diagram works, or read
`docs/skills-vs-tools.md` / `skills-vs-mcp.md` / `skills-vs-subagents.md`
aloud in one sentence each):

```
Agent
├── Skills     — the procedure
├── Tools      — what the agent can do
├── MCP        — connections to external systems
└── Subagents  — isolated delegated workers
```

> "Skills don't replace any of these — they direct how the agent uses them."

## 1:45–2:20 — Inside a skill

Open `skills/debugging-investigator/` in the editor. Show:

```
SKILL.md
references/   (6 files: web, database, network, concurrency, distributed, performance)
examples/
```

> "The agent only loads name and description at startup. The full
> SKILL.md loads when a task matches. And these reference files only load
> when SKILL.md actually points to them — that's progressive disclosure."

Briefly scroll `SKILL.md`'s workflow section (OBSERVE → REPRODUCE →
COLLECT EVIDENCE → ... → EXPLAIN ROOT CAUSE).

## 2:20–3:50 — Live demo

Open `examples/02-debug-a-failure/sample-app/` (deliberately buggy).

Ask the agent:

> "My endpoint occasionally creates duplicate orders. Investigate and fix it."

Narrate as it runs through the skill's workflow:

1. Observes the symptom
2. Reproduces it (a script firing concurrent requests)
3. Collects evidence (reads the handler, the logs)
4. Forms 2-3 hypotheses
5. Tests and rejects the wrong ones
6. Confirms the concurrency root cause
7. Applies the minimal fix
8. Adds a regression test and reruns it

See `examples/02-debug-a-failure/sample-app/BUG_SPOILER.md` beforehand so
you can narrate confidently without reading it on camera.

## 3:50–4:30 — Show the other skills

Quick `python scripts/list_skills.py` in the terminal, scrolling through
all 15 one-liners. Optionally `python scripts/inspect_skill.py data-scientist`
to show the resource/eval-coverage report.

## 4:30–5:10 — Composition

Show `docs/composing-skills.md`'s Pipeline A:

```
repo-architect → feature-to-production → production-code-review
```

> "Skills compose — each one owns a stage, and hands off explicitly. No
> mega-skill secretly running everything at once."

## 5:10–5:40 — Portability

> "This isn't locked to one vendor — it's the open SKILL.md format."

Show `docs/compatibility.md`'s matrix on screen. Read the legend once:

> "✅ means I actually tested it. 🟡 means it's expected to work based on
> that vendor's own docs, but I haven't verified it live myself. I'm not
> going to tell you something's tested when it isn't."

## 5:40–6:10 — GitHub

Show, in order: `README.md`, `skills/`, `evaluations/`, `docs/`.

> "You can clone it, install one skill, modify it, or contribute your own."

## 6:10–End — CTA

> "If you use one of these skills on a real project, open an issue and
> tell me what worked and what failed. The goal isn't more prompts — it's
> better operating procedures for agents."

Show: `github.com/alphasafal/production-agent-skills` (once pushed).
