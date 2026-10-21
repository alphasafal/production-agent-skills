# UI states and forms checklist

## The five states of anything async

For each fetch, mutation, or async prop, find the code path that renders
each state. If there isn't one, it's a finding.

| State | What the user should see | Common defect |
|---|---|---|
| Loading | Skeleton or spinner sized like the content; existing content kept if refreshing | Blank area, then content pops in (layout shift) |
| Empty | Explanation and a next action ("No orders yet — browse products") | Empty table with headers, or nothing |
| Error | What went wrong in plain words, how to recover, input preserved | Raw error string, form reset, or silent failure |
| Partial | Some data loaded, some failed — show what you have and mark the rest | Whole view errors because one request failed |
| Submitting / disabled | Control disabled or `aria-busy`, label changes ("Paying..."), no double submit | Button stays live; second click charges twice |

Success is the sixth state and usually the only one designed.

## Submitting state: the fix

```jsx
const [status, setStatus] = useState('idle'); // idle | submitting | error

async function onSubmit(e) {
  e.preventDefault();
  if (status === 'submitting') return;      // guard against fast double clicks
  setStatus('submitting');
  try {
    await save(values);
    onDone();
  } catch (err) {
    setStatus('error');                     // values untouched
    setError(messageFor(err));
  }
}

<button type="submit" disabled={status === 'submitting'} aria-busy={status === 'submitting'}>
  {status === 'submitting' ? 'Paying...' : `Pay ${amount}`}
</button>
```

Disabling the button is the UI half. For payments, the request should also
carry an idempotency key so a retry after a timeout can't double charge —
flag the missing server-side half as a note to the backend review rather
than a UI finding.

## Error state rules

- **Never clear the user's input on a failed submit.** The exception is a
  security-sensitive field such as CVC or a one-time code, which may be
  cleared on purpose; say so in the message and keep everything else.
- Put the message where the user is looking: next to the field for
  field errors, at the top (and focused or announced) for form-level ones.
- Make it actionable: "Card declined — try another card" beats "Error".
- Announce it: `role="alert"` on the container, or move focus to it.

## Field-level validation

```jsx
<label htmlFor="email">Email</label>
<input
  id="email"
  type="email"
  autoComplete="email"
  aria-invalid={errors.email ? 'true' : 'false'}
  aria-describedby={errors.email ? 'email-error' : undefined}
/>
{errors.email && <p id="email-error" className="field-error">{errors.email}</p>}
```

- Validate on blur or submit, not on every keystroke while the user is
  still typing.
- Don't rely on color alone for errors; include text or an icon with a
  text alternative.
- Mark required fields in the label text, not only with an asterisk color.

## Form plumbing

- Use a real `<form onSubmit>` with a `type="submit"` button so Enter
  submits and password managers recognise the form.
- Give each input a `name` and the right `type` (`email`, `tel`, `url`).
- `autocomplete` tokens save typing and errors, especially on mobile:
  `name`, `email`, `tel`, `street-address`, `postal-code`, `cc-name`,
  `cc-number`, `cc-exp`, `cc-csc`, `one-time-code`, `current-password`,
  `new-password`.
- `inputMode="numeric"` for card numbers, OTPs and PINs (keep
  `type="text"` so leading zeros and spaces survive).
- Don't disable paste on any field.

## Severity guide for state and form findings

- **P0:** a missing state causes harm or blocks the task — double payment,
  data loss, a spinner that never ends on error.
- **P1:** the user loses work or is stranded — form cleared on error, no
  error state at all, error not announced on a primary flow.
- **P2:** missing empty or partial state, missing `autocomplete` on a
  checkout or sign-up form.
- **P3:** copy improvements, nicer skeletons.
