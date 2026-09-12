---
name: Bug / skill didn't behave as expected
about: Report a problem with an existing skill or the tooling
title: ""
labels: bug
---

## Which skill or script?

## What did you expect (per its SKILL.md / --help)?

## What actually happened?

Paste the relevant part of the transcript, or the exact command and error.

## Client and environment

Which agent/client (Claude Code, Codex, Copilot, other)? Which version, if known?

## Would this make a good new evaluation case?

If this is an activation miss (skill triggered when it shouldn't have, or
didn't trigger when it should have), it likely belongs in
`evaluations/activation/<skill>.json` as a new case — feel free to propose
one.
