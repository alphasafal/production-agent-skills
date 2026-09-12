# Skills vs. MCP

**MCP** (Model Context Protocol) is how an agent connects to external
systems and data — a database, an observability platform, a project
tracker, a company's internal API. It's a *connection* mechanism: it
determines what external tools and data are available to the agent at all.

A **skill** is a *procedure* — it assumes some set of tools/connections
exist (MCP-provided or otherwise) and tells the agent how to use them well
for a specific kind of task.

## Skills in this repo don't require MCP

None of the eight skills in this repository hard-depend on an MCP server.
Each one's `compatibility` frontmatter field and `Tool & resource
guidance` section says explicitly what's needed (filesystem, shell,
sometimes a research/web tool) and calls out where an MCP connection would
*help* without being *required*:

- `debugging-investigator` and `system-design-reviewer` note that a
  connected observability/tracing tool (e.g. via an MCP server) makes
  distributed-systems evidence-gathering much easier — but the skill's
  workflow still works with plain log files and manual reproduction if
  no such connection exists.
- `research-to-decision` benefits from a connected web-research tool for
  sourcing external evidence — and explicitly instructs the agent to mark
  claims as unverified assumptions rather than fabricate a citation when
  no such tool is available.

## Why keep it this way

A skill that hard-requires a specific MCP server only works for people who
have that exact server configured — it stops being portable. By keeping
MCP usage optional and explicitly degrading gracefully (state the
limitation, don't fabricate the missing data), these skills stay usable in
a bare CLI agent and in a fully-connected enterprise setup alike.

## When to reach for MCP instead of (or alongside) a skill

If the actual gap is "the agent can't see X system at all," that's an MCP
problem — no skill can talk to a database it has no connection to. If the
gap is "the agent can see X system but doesn't know the right way to
investigate/query/act on it," that's a skill's job, and it can be layered
on top of whatever MCP connections already exist.
