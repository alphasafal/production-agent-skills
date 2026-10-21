# Answer key: frontend-ui-reviewer-workflow-02 (account settings, hard)

Grader-only. The dialog "passed the checklist" (role, aria-modal, name,
Escape, initial focus, focus trap), so a checklist review finds nothing. Every
planted issue only shows up by tracing behavior across files or across time.

## Planted issues

| # | Issue | Where | Why it matters | Expected fix | Severity |
|---|---|---|---|---|---|
| 1 | Delete button is only `aria-disabled`; `onClick` still runs and `handleDelete` has no guard | `DeleteAccountDialog.jsx:67-68`, `:37-41` | Clicking (or Enter/Space) deletes the account **without typing DELETE**, and a second click during the 1-3 s request sends a second non-idempotent delete (500 + on-call page per README) | Guard in the handler (`if (!canDelete \|\| deleting) return;`) and/or use the real `disabled` attribute; also handle rejection | P0 |
| 2 | `aria-hidden="true"` set on `#app-root`, but the dialog renders **inside** `#app-root` (README: no portal) | `DeleteAccountDialog.jsx:12` | The whole dialog, including its focused heading, is removed from the accessibility tree; screen-reader users get silence or "blank" on a destructive action | Render the dialog in a portal outside `#app-root` (or hide siblings only), or use native `<dialog>` + `showModal()` / `inert` on siblings | P0/P1 |
| 3 | Focus is not returned to the "Delete account…" trigger on close | `DeleteAccountDialog.jsx:31-34` (cleanup), `AccountSettings.jsx:97` (no trigger ref) | After Cancel/Escape, focus lands on `<body>`; keyboard and SR users lose their place | Store `document.activeElement` (or a trigger ref) on open and `.focus()` it in cleanup | P1 |
| 4 | The error toast's `aria-live` region is mounted together with its message | `AccountSettings.jsx:78-79` | Live regions announce *changes* to a region that already exists; inserting region+text at once is commonly not announced, so the save failure is silent for SR users | Keep the live region always mounted (empty) and change its text, or use `role="alert"` | P2 |
| 5 | `aria-describedby="emailError"` but the error's id is `email-error` | `AccountSettings.jsx:56`, `:59` | The validation message is never associated with the field; `aria-invalid` says "invalid" with no reason | Make the ids match (`aria-describedby="email-error"`, ideally only when the error exists) | P2 |
| 6 | `.btn:focus { outline: none }` with a `:focus-visible` replacement only for `.btn-primary` | `settings.css:44-51` | Reset, Delete account…, Cancel and the dialog's Delete button have **no visible focus indicator** for keyboard users (WCAG 2.4.7) | Replace with `.btn:focus-visible { outline: 2px solid var(--color-focus); }` for all buttons | P2 |
| 7 | Layout shift: verify-email banner inserted above the content after a 300-900 ms fetch, with no reserved space; `@font-face` has no `font-display` | `AccountSettings.jsx:39-43`, `settings.css:26-30`, `settings.css:1-4` | Page content jumps down after load (CLS), and text is invisible or swaps late while Inter loads | Reserve space or render the banner from server state / below the header; add `font-display: swap` (plus preload/size-adjust) | P2/P3 |
| 8 | Toast dismiss button is 20x20 px | `settings.css:58-63` | Below the 24x24 px WCAG 2.5.8 minimum, and well under 44x44 on mobile (40% of traffic) | Make the hit area at least 24x24 (44x44 preferred) with padding | P3 |

Extra credit (not gated): `deleteAccount()` rejection is unhandled (button
stuck on "Deleting…", no error shown); `handleSave` has no submitting state;
unused `useRef` import.

## Decoys: must NOT be reported as defects

- `<p role="status" className="save-status">` (`AccountSettings.jsx:73`) is
  **always mounted** and only its text changes, which is the correct
  live-region pattern. Contrast it with #4.
- `<h2 tabIndex={-1} ref={headingRef}>` (`DeleteAccountDialog.jsx:54`) is the
  correct way to make a heading programmatically focusable as the dialog's
  initial focus target without adding it to the Tab order.
- The Dismiss icon button (`AccountSettings.jsx:81-85`) has `aria-label` and
  its SVG is `aria-hidden` with `focusable="false"`. Its accessible name is
  correct; only its size (#8) is a defect.

## Expected conclusion

Not shippable. #1 is a P0 data-loss bug (it deletes without confirmation and
double-deletes). #2 makes the dialog unusable with a screen reader. The
"passed the dialog checklist" claim in the README is the trap: a good review
says why that checklist pass doesn't cover these.
