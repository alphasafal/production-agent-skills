# Worked example: "add collaborative playlists"

**Prompt:** "Our users keep asking for collaborative playlists, can you spec
this out?"

Abridged workflow:

1. **Problem**: users want to build playlists with friends, but currently
   have to manually share track lists outside the app.
2. **Target user**: users who already share music recommendations with a
   specific small group (identified via the request pattern, not "all users").
3. **Jobs-to-be-done**: "help my friend group agree on a shared set of
   songs for an event/mood without a group chat full of song links."
4. **Current alternative**: sharing individual track links in group chats —
   painful to consolidate, no persistent shared list.
5. **Assumptions** (ranked by risk): (a) users will actually invite others
   to a shared playlist rather than just making more personal playlists —
   **highest risk, untested**; (b) real-time sync is needed vs. periodic
   refresh — lower risk, can start simple; (c) technical feasibility of
   real-time collab — low risk, well-understood problem.
6. **Hypothesis**: "If we let a user invite others to co-edit a playlist,
   at least 15% of created playlists will have 2+ contributors within a
   week of launch" (tests assumption (a) directly).
7. **MVP scope**: one user creates a playlist, can invite others via a
   link, invitees can add/remove tracks. **Cut from v1**: real-time
   collaborative cursors, per-track voting, playlist-level chat — none of
   these test assumption (a); they're premature if nobody actually invites
   collaborators in the first place.
8. **Success metric**: % of new playlists with 2+ contributors within 7
   days (primary, tied directly to hypothesis); guardrail: playlist
   creation rate overall must not drop (a bad multi-user UX could suppress
   solo playlist creation too).
9. **Decision log excerpt**: "Cut per-track voting from v1 — it only
   matters if playlists already have multiple active contributors, which
   is exactly the unproven assumption. Revisit once the primary metric
   validates people actually collaborate."
