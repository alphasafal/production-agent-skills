# Skills vs. Tools

A **tool** is a capability the agent can invoke — read a file, run a shell
command, query a database, call an API. Tools answer "what can the agent
*do*."

A **skill** is knowledge about *how* and *when* to use whatever tools are
available to accomplish a specific kind of task well. Skills answer "what
should the agent do, in what order, and with what care."

## They're not competing — a skill directs tool use

`skills/debugging-investigator/SKILL.md` doesn't invent new tools. It tells
the agent, using whatever shell/filesystem/log-reading tools it already
has: reproduce first, collect evidence before hypothesizing, never make a
speculative change. The skill is the discipline; the tools are how that
discipline gets carried out.

`skills/data-scientist/scripts/` is the one place in this repo where a
skill *bundles* tool-like functionality — small, deterministic Python
scripts (`profile_dataset.py`, `check_leakage.py`, etc.) that the agent
runs via its normal shell-execution tool. These aren't a new tool
*mechanism* — the agent still just "runs a shell command" — they're
pre-written, tested, deterministic logic so the agent doesn't reimplement
(and potentially get wrong) "compute missingness per column" from scratch
every time.

## Rule of thumb

- If the correct behavior is **deterministic and reusable code**, write a
  script and put it in `scripts/` — see `data-scientist`'s scripts for
  concrete examples of this pattern.
- If the correct behavior is **judgment applied in the right order with
  the right checks**, that's the SKILL.md instructions, not a script — see
  `production-code-review`'s severity/classification rubric, which
  couldn't be reduced to a deterministic script.
- Most real workflows are a mix of both — see
  [progressive-disclosure.md](progressive-disclosure.md) for how a skill
  keeps judgment and deterministic execution cleanly separated.
