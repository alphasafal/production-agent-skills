# What Makes an ADR Useful (vs. a box-checking exercise)

## Understandable without the full research doc

Someone reading the ADR in a year, with no memory of the discussion, should
understand *why* without opening RESEARCH.md. Summarize the load-bearing
evidence inline; don't just link out.

## States what was given up, not just what was gained

"We chose Postgres for its maturity and JSON support" is incomplete. "We
chose Postgres over a dedicated document store, giving up some horizontal
write scalability we don't currently need, in exchange for one less piece
of infrastructure to operate" is an ADR someone can actually evaluate
later if requirements change.

## Names the conditions that would change the decision

A good ADR states what would make this decision wrong in the future (e.g.
"if write volume exceeds X/sec, revisit this") so a future reader can tell
whether those conditions have been met, rather than re-litigating from
scratch.

## Distinguishes reversible from irreversible decisions

An irreversible decision (a data model choice with a hard migration path,
a vendor lock-in) deserves more rigor in the ADR than a reversible one (a
library choice that's easy to swap later). Say which kind this is.

## Avoids false precision

A decision matrix with scores to two decimal places based on subjective
1-5 ratings overstates rigor. It's fine to use simple relative ratings
(better/worse/comparable) when the underlying evidence doesn't support
finer precision.
