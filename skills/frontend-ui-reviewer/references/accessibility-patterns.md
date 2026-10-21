# Accessibility patterns and fixes

Concrete patterns for the findings that come up most in component review.
Each section: how to spot it, who it hurts, the fix, how to verify.

## Button vs link vs clickable div

**Spot it:** `onClick` on `div`, `span`, `li`, `img`, `td`, or an `<a>` with
no `href` used as a button.

**Who it hurts:** keyboard users can't reach it (no tab stop) or activate it
(no Enter/Space); screen readers announce it as text or not at all; voice
control users can't say "click Pay" because it has no role.

**Rule:** it changes the URL → `<a href>`. It does something on this page →
`<button type="button">` (or `type="submit"` inside a form).

```jsx
// Before
<div className="pay-button" onClick={pay}>Pay</div>

// After
<button type="submit" className="pay-button">Pay</button>
```

Patching a div with `role="button" tabIndex={0}` also requires an
`onKeyDown` for Enter and Space, a disabled state via `aria-disabled`, and
form-submission wiring by hand. Prefer the native element; reset its styles
with `appearance: none; border: 0; font: inherit;`.

**Verify:** Tab reaches it, focus ring is visible, Enter and Space both
activate it, the accessibility tree shows role `button` with the text name.

## Visible focus

`outline: none` or `outline: 0` with no replacement leaves keyboard users
guessing where they are. Fix with `:focus-visible`:

```css
.btn:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }
```

The indicator needs 3:1 contrast against the adjacent background.

## Labels and accessible names

**Placeholder is not a label.** It disappears on input, is usually low
contrast, and many screen reader / browser combinations don't announce it
as the field's name.

```jsx
<label htmlFor="card-number">Card number</label>
<input id="card-number" name="cc-number" autoComplete="cc-number" inputMode="numeric" />
```

If the design truly has no visible label, use `aria-label`, and say in the
review that a visible label is still better for users with cognitive or
memory impairments. Icon-only buttons need a name: `aria-label="Close"` on
the `<button>`, `aria-hidden="true"` on the icon inside it.

**Correct patterns not to flag:**

- `<label htmlFor="x">` paired with `<input id="x">` — labelled.
- `<label><input type="checkbox" /> Remember me</label>` — labelled by
  wrapping.
- A decorative image with `alt=""` (with or without `aria-hidden="true"`)
  next to text that already carries the meaning — correctly hidden.

## Alt text

- Meaningful image (product photo, chart, logo that links home): `alt`
  describes what it conveys — `alt="Blue ceramic mug, 350 ml"`.
- Decorative (icon beside text that says the same thing, background
  flourish): `alt=""`. Not missing `alt` — a missing attribute makes screen
  readers read the file name.
- Image that is the only content of a link or button: `alt` names the
  destination or action, not the picture.

## Dialogs and modals

A dialog must:

1. Have `role="dialog"` (or use `<dialog>`), `aria-modal="true"`, and a name
   via `aria-labelledby` pointing at its heading.
2. Move focus inside on open — to the first field, or to the heading with
   `tabIndex={-1}` if the content needs reading first.
3. Trap Tab and Shift+Tab inside while open.
4. Close on Escape.
5. Return focus to the element that opened it on close.
6. Hide the background from assistive tech (`inert` on the page root, or
   `aria-hidden="true"` on siblings) and stop background scroll.

Native `<dialog>` with `showModal()` gives 1, 3 (in current browsers), 4
and 6. You still restore focus yourself:

```jsx
function Modal({ open, onClose, titleId, children }) {
  const ref = useRef(null);
  const returnTo = useRef(null);
  useEffect(() => {
    const dlg = ref.current;
    if (open) { returnTo.current = document.activeElement; dlg.showModal(); }
    else if (dlg.open) { dlg.close(); returnTo.current?.focus(); }
  }, [open]);
  return (
    <dialog ref={ref} aria-labelledby={titleId} onCancel={(e) => { e.preventDefault(); onClose(); }}>
      {children}
    </dialog>
  );
}
```

Without `<dialog>`, use a maintained trap (`focus-trap-react`, Radix
`Dialog`, Headless UI `Dialog`) rather than writing one.

**Verify:** open with the keyboard, Tab cycles inside only, Escape closes,
focus lands back on the trigger.

## Announcing async changes

Content that appears without focus moving (an error after submit, "Saved",
a cart count) is silent to screen readers unless announced:

```jsx
<p role="alert">{error}</p>               // assertive, for errors
<p role="status" aria-live="polite">{msg}</p>  // polite, for success/progress
```

The live region must exist in the DOM before its text changes; mounting an
element with text already inside is announced inconsistently. Render the
container always and change its contents. For form errors, moving focus to
an error summary or the first invalid field also works.

## ARIA misuse

- `role="button"` with no key handler or tab stop — name without behavior.
- `aria-label` on a `div` or `span` with no role — ignored by most screen
  readers.
- `aria-hidden="true"` on something focusable — keyboard focus lands on an
  element screen readers say doesn't exist.
- `aria-expanded`, `aria-selected` and similar set once and never updated.
- Redundant roles (`<button role="button">`) are harmless noise; don't rank
  them above P3.

The first rule of ARIA: use the native element if one exists.

## Contrast (WCAG 2.x AA)

- Normal text: 4.5:1. Large text (24px, or 18.66px bold): 3:1.
- Non-text UI (input borders, focus rings, icons that carry meaning): 3:1
  against adjacent colors.
- Disabled controls are exempt, but must still look disabled.

Reference ratios against white `#ffffff`:

| Color | Ratio | Passes normal text? |
|---|---|---|
| `#aaaaaa` | 2.3:1 | no |
| `#999999` | 2.8:1 | no |
| `#767676` | 4.5:1 | yes (the lightest gray that does) |
| `#57606a` | 6.4:1 | yes |
| `#d0d7de` | 1.4:1 | no, and fails 3:1 as an input border |

Compute others with the WCAG relative-luminance formula or any contrast
checker; always quote both colors and the ratio in the finding.

## Touch targets

WCAG 2.2 AA (2.5.8) requires 24x24 CSS px minimum or enough spacing;
44x44 is the comfortable size for primary actions. A 14px text "Close" with
no padding is usually below both.

## Severity guide for a11y findings

- **P0:** a primary task cannot be completed by keyboard or screen reader
  (pay, submit, close a modal that blocks the page).
- **P1:** a task is possible but a group is seriously impeded — unlabeled
  required fields, no focus management in a dialog, errors not announced,
  body text failing contrast.
- **P2:** secondary content or controls affected, workarounds exist.
- **P3:** redundant ARIA, heading level nits, improvements beyond AA.
