# Example 7: Create a Product Spec

**Skill**: [product-manager](../../skills/product-manager/)

## Try it

Ask an agent with `product-manager` installed:

> "Our users keep asking for collaborative playlists, can you spec this out into a PRD?"

## What a correct run produces

A PRD (using
[`skills/product-manager/assets/prd-template.md`](../../skills/product-manager/assets/prd-template.md)),
user stories, success metrics tied to a stated hypothesis, and — this is
the part worth checking closely — a decision log entry naming something
that was **deliberately cut** from v1 scope and why. A run that includes
every plausible feature from the original request hasn't actually applied
the skill's risk-ranking discipline.

## Reference answer

[`skills/product-manager/examples/collaborative-playlist-prd.md`](../../skills/product-manager/examples/collaborative-playlist-prd.md)
— note what it cuts (real-time cursors, per-track voting) and why.

## Grading a real run

See [`evaluations/workflows/product-manager.json`](../../evaluations/workflows/product-manager.json).
