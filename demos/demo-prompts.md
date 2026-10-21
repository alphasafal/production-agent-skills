# Demo Prompts

Copy-pasteable prompts for demonstrating each skill, ordered to match the
root README's "12 skills" table. Each is a `positive-obvious` case pulled
directly from that skill's `evaluations/activation/<skill>.json`, so it's
guaranteed to be a legitimate, tested trigger — not a cherry-picked demo
that doesn't reflect real usage.

## repo-architect
> I just cloned this repo and have no idea how it's structured. Can you map it out for me?

## debugging-investigator
> My API is occasionally returning duplicate payments. Find the root cause and fix it.

(This exact scenario is worked out in full in
`skills/debugging-investigator/examples/duplicate-payment-investigation.md`
and is the one used in the root README's "See it in action" section.)

## production-code-review
> Review this PR before I merge it: [attach the diff at
> `evaluations/fixtures/payments_endpoint.diff`]

## system-design-reviewer
> Here's our proposed architecture for the new notifications service — can you review it before we build it?

## data-scientist
> Here's our customer dataset [`evaluations/fixtures/churn_sample.csv`], build a model to predict churn.

## research-to-decision
> Should we use Kafka or SQS for our order events? Research both and recommend one.

## product-manager
> Our users keep asking for collaborative playlists, can you spec this out into a PRD?

## feature-to-production
> Add rate limiting to our public API — 100 requests per minute per API key. Ship it.

## For the live "before vs. after" comparison

Use `examples/02-debug-a-failure/sample-app/` — it has a real, deterministic
bug. Run the prompt above against an agent with `debugging-investigator`
NOT installed, then again WITH it installed, and compare: does the
un-skilled run jump to a guess, or does it reproduce and gather evidence
first? See `docs/demo-guide.md` for the full recording flow.
