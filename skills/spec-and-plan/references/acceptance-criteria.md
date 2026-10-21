# Writing acceptance criteria that become tests

An acceptance criterion is a test someone has not written yet. If two
engineers could read it and write tests that disagree, it is not done.

## Format

```
AC-n: <short name>
Given <state of the world, with concrete values>
When <one action by one actor>
Then <observable result: response, page, row, email, event>
```

Rules:

- **One behavior per criterion.** "Then the comment is saved and the user is
  notified and the badge updates" is three criteria.
- **Concrete values.** "After 30 days", "the 21st mention in one comment",
  "a user already muted on this document". Not "after a while", "too many",
  "existing".
- **Observable result.** Something a test can assert: HTTP status, rendered
  text, a row with a field value, an email to a specific address, a log or
  event name. Not "the user understands", "it feels fast".
- **Name the actor.** Author, commenter, read-only guest, anonymous, a user
  of another workspace. Permission bugs live in the actor you didn't name.
- **Reference assumptions.** If a value comes from an assumption, cite it:
  "Then no second email is sent (A-2: 15-minute digest window)". When the
  assumption changes, you know which criteria move.

## Coverage checklist

For each user-facing capability, write criteria for:

1. The happy path.
2. Each actor who must NOT be able to do it (permission boundary).
3. Each limit or quota (at the limit, one over).
4. Each lifetime (before expiry, after expiry, after revoke or delete).
5. Duplicates and retries (same action twice, double-click, resend).
6. Identity variations (deactivated account, signed in as someone else,
   case differences in a handle or email).
7. Each failure the user can see, and what they see.

Not every capability needs all seven, but you should be able to say why one
doesn't apply.

## Untestable to testable

| Untestable | Testable |
|---|---|
| Mentions work well. | Given a commenter on document D, when they post a comment containing `@lena`, then a notification row exists for Lena referencing the comment and one email is sent to Lena's address. |
| Notifications aren't spammy. | Given Lena was mentioned on D at 10:00, when she is mentioned again on D at 10:05, then she receives one email at 10:15 listing both mentions (A-2), not two. |
| Handles errors gracefully. | Given the email provider returns 5xx, when a mention notification is due, then the row stays `pending` with `attempts` incremented and is retried within 10 minutes. |
| Only people with access get notified. | Given Lena has no access to D, when someone writes `@lena` on D, then no notification is created and the author sees "Lena can't see this document". |
| Autocomplete is fast. | Given a workspace with 5,000 users, when the author types `@le`, then suggestions return in under 200 ms p95 in the staging load test. |
| Respects limits. | Given a comment with 21 distinct mentions, when it is posted, then it is rejected with "Mention up to 20 people per comment" and nothing is saved. |

## Smells

- "Should" without a "then". Rewrite as an observable result.
- A criterion that only restates the feature name.
- No criterion mentions an actor other than the happy-path one.
- Criteria that test the implementation ("the service calls `notify()`")
  rather than behavior ("an email is delivered to Lena").
