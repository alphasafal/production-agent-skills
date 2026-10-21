# Answer key: frontend-ui-reviewer fixture (React checkout modal)

Fixture: `evaluations/fixtures/frontend-ui-reviewer/`. Eight planted issues
and two decoys. Severities are the expected range; a run may justify one
level either way if it names who is affected and how badly.

## 1. Close and Pay are clickable divs — P0

- **Location:** `CheckoutModal.jsx:17-19` (`<div className="modal-close"
  onClick={onClose}>`) and `PaymentForm.jsx:79-81` (`<div
  className="pay-button" onClick={handlePay}>`).
- **Why it matters:** no role, no `tabIndex`, no key handler. Keyboard and
  switch users cannot reach or activate either control, so they cannot pay
  and cannot dismiss a modal that covers the page. Screen readers announce
  plain text. The form's `onSubmit` only calls `preventDefault`, so Enter in
  a field does nothing either.
- **Fix:** `<button type="button" aria-label="Close checkout"
  onClick={onClose}>` and `<button type="submit">` with the payment logic
  moved into `<form onSubmit>`.

## 2. Inputs have placeholder only, no label — P1

- **Location:** `PaymentForm.jsx:34-65` — name (36), email (42), card (48),
  expiry (55), CVC (61).
- **Why it matters:** no `<label>`, `aria-label` or `aria-labelledby`.
  Placeholder vanishes on input and is not a reliable accessible name;
  screen-reader users hear "edit text" for five fields.
- **Fix:** visible `<label htmlFor>` per field with matching `id`; add
  `name`, `autoComplete` (`cc-name`, `email`, `cc-number`, `cc-exp`,
  `cc-csc`) and `inputMode="numeric"` for card/expiry/CVC. (Missing
  autocomplete is expected but not gated.)

## 3. Modal focus management and Escape — P1

- **Location:** `CheckoutModal.jsx:13-14` (backdrop and `.modal` divs) and
  the component as a whole (no effect, ref or key handler).
- **Why it matters:** no `role="dialog"`, `aria-modal` or
  `aria-labelledby` (the `<h2>Checkout</h2>` at line 16 is the natural
  name). Focus is not moved in on open, Tab escapes to the page behind,
  Escape does nothing, and focus is not restored to the trigger on close.
- **Fix:** native `<dialog>` with `showModal()` and `onCancel` → `onClose`,
  or a maintained trap (Radix/Headless UI/focus-trap-react); store
  `document.activeElement` on open and refocus it on close.

## 4. No submitting state; error clears the form — P0 / P1

- **Location:** `PaymentForm.jsx:16-30` (`handlePay`), `:27`
  (`setForm(EMPTY)`), `:77` (error), `:79` (Pay control).
- **Why it matters:** nothing tracks in-flight state, so a second click
  during the 1-4 s charge (README) sends a second `chargeCard` — a double
  charge (P0). On failure the catch resets every field, so the user retypes
  name, email and card (P1). The error paragraph at line 77 has no
  `role="alert"`, so screen-reader users aren't told it failed (expected,
  not gated).
- **Fix:** `status` state (`idle | submitting | error`); early return when
  submitting; `disabled` + `aria-busy` + "Paying..." label; keep form values
  on error (clearing only CVC is acceptable if stated); `role="alert"` on the
  error. Note that a server-side idempotency key is the other half.

## 5. Product image: no alt, no dimensions — P1 (alt) / P2 (CLS)

- **Location:** `CheckoutModal.jsx:23`; `.product-image` in
  `styles.css:46-49` sets no width, height or aspect-ratio.
- **Why it matters:** screen readers read the URL or filename; the image
  loads after the modal renders and pushes the product info, price and form
  down — the Pay control moves.
- **Fix:** `alt={item.name}` and `width`/`height` attributes (e.g. 96x96)
  or `aspect-ratio` on `.product-image`.

## 6. Whole-library imports for one call each — P2

- **Location:** `CheckoutModal.jsx:2` (`import moment from 'moment'`, used
  once at `:10`) and `PaymentForm.jsx:2` (`import _ from 'lodash'`, used once
  at `:21` for `_.trim`).
- **Why it matters:** roughly 70 KB + 25 KB min+gzip on a checkout path
  where ~70% of traffic is mobile.
- **Fix:** `form.card.trim()`; `new Intl.DateTimeFormat('en-IN', { weekday:
  'short', day: 'numeric', month: 'short' }).format(date)` with a `Date`
  three days ahead.

## 7. Low-contrast price and terms text — P1

- **Location:** `styles.css:53` (`.price { color: #aaa }`) and `:110`
  (`.terms { color: #aaa }`) on the modal's `#fff` background (`:22`).
- **Why it matters:** `#aaaaaa` on `#ffffff` is 2.3:1; AA needs 4.5:1 for
  the 12px terms and the 18px (not bold, so not "large") price. Low-vision
  users and anyone in sunlight on a phone can't read the price they are
  paying.
- **Fix:** use the existing `var(--color-muted)` (`#57606a`, 6.4:1) or
  `var(--color-text)`. Also a consistency finding: hard-coded colors next to
  defined tokens.

## 8. Fixed 600px modal width — P1/P2

- **Location:** `styles.css:21` (`.modal { width: 600px; }`).
- **Why it matters:** at the README's 390px median viewport the modal is
  wider than the screen; content and the Pay control are clipped or need
  horizontal scrolling. No max-height either, so tall content can't scroll.
- **Fix:** `width: min(600px, calc(100vw - 32px)); max-height: 90vh;
  overflow-y: auto;` with full-screen sheet layout at small breakpoints.

## Decoys — must NOT be flagged

- **Decorative truck icon**, `CheckoutModal.jsx:30-35`: `alt=""` plus
  `aria-hidden="true"`, next to the text "Arrives by ...". This is the
  correct pattern for a decorative image. Reporting it as "missing alt" or
  "hidden from screen readers" is a false positive and fails the run.
- **Save-card checkbox**, `PaymentForm.jsx:68-74`: `id="save-card"` with
  `<label htmlFor="save-card">`. It is properly labelled. Reporting it with
  the unlabelled inputs fails the run.

A strong run lists both under "Checked and fine".

## Other observations a strong run may add (not required)

- Input borders `#d0d7de` on white are 1.4:1, failing the 3:1 non-text
  contrast rule for form field boundaries (`styles.css:73`).
- Close control is 14px text with no padding — below the 24x24 target size.
- `cart.items[0]` only: carts with more items show one product (partial
  state/content question for the product owner).
- No visible focus styles defined for any control (moot until they are
  buttons, then check the browser default isn't suppressed).
- The backdrop does not hide the background from assistive tech (`inert`).

## What a correct run concludes

Do not ship. Issues 1 and 4 (double charge) are P0: keyboard users cannot
pay or close, and anyone can be charged twice. Issues 2, 3, 7 and probably
5/8 are P1. Each finding has file:line and a concrete fix, both decoys are
left alone (ideally listed as checked and fine), and the report says the
review was static and lists what needs a browser/screen reader (tab walk,
announcement of the error, real viewport rendering). Source files are not
modified.
