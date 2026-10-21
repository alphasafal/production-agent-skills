---
name: frontend-ui-reviewer
description: >
  Reviews user-facing UI code (React, Vue, Svelte, HTML/CSS): traces keyboard
  and screen-reader paths, checks every UI state, responsive layout, Core Web
  Vitals, forms and design tokens, then ranks P0-P3 findings with fixes. Use
  when asked to review a component, screen, modal, dialog or form UI before
  it ships, do an accessibility or a11y check, WCAG contrast, keyboard
  or focus support, mobile layout, layout shift or bundle size, or when
  building frontend UI in a rush ("just make the form work, skip the a11y").
  Do not use for a backend or API diff with no UI (use production-code-review),
  or building and shipping a whole feature (use feature-to-production).
license: MIT
compatibility: Needs read access to the component, style and asset files. A browser, dev server or test runner (Playwright, Testing Library, axe) is optional and used for verification when present.
metadata:
  category: frontend
  composes_with:
    - production-code-review
    - feature-to-production
---

# Purpose

Catch the UI defects generic code review walks past: controls a keyboard
cannot reach, fields a screen reader cannot name, states nobody designed,
layouts that break at 390px, and markup that shifts or bloats the page. Each
finding names who it hurts and how to fix it, and the report says plainly
what was verified in a browser and what was only read.

# When to use

- A component, page, modal or form is about to ship and someone asks for a
  review, a "quick look", or "is this ready".
- Asked about accessibility, a11y, WCAG, contrast, keyboard or screen-reader
  support, mobile or responsive layout, layout shift, or bundle weight.
- Building UI yourself: run the workflow on your own output before handing
  it back, especially when the request says to skip the polish.
- As the UI pass inside `feature-to-production` or alongside
  `production-code-review` on a diff that touches JSX, templates or CSS.

# When NOT to use

- The diff has no user-facing surface (API handler, migration, worker) —
  use `production-code-review`.
- The task is building and shipping a whole feature end to end — use
  `feature-to-production`; it calls this skill for its UI stage.
- A conceptual question ("flexbox vs grid", "what is ARIA") with no code to
  review — answer it directly.
- Pure visual-design critique (palette, typography taste) with no defect —
  say so; this skill reports defects, not preferences.

# Required inputs

- The UI files: components, templates, styles, and the design-token file if
  one exists.
- Context: who uses it, the main devices or viewport widths, and the
  framework. If unstated, assume mobile and keyboard users exist and say so.
- Optional: a running dev server, Storybook, or test runner for verification.

# Workflow

1. **Scope.** List the files reviewed, the framework, and the entry point
   (what opens or renders this UI). Note whether a browser or test runner is
   available; that decides what step 9 can verify.
2. **Inventory interactive elements.** For every element with an event
   handler, record its tag. A `div`/`span` with `onClick` and no role,
   `tabIndex` and key handler is a keyboard dead end. Anything that navigates
   should be `<a href>`; anything that acts should be `<button>`.
3. **Trace the keyboard path.** Walk Tab order through the UI in source
   order: can every control be reached, is focus visible (no
   `outline: none` without a replacement), and does Enter/Space activate it?
   For dialogs: focus moves in on open, Tab is trapped inside, Escape closes,
   focus returns to the trigger on close, and the dialog has `role="dialog"`,
   `aria-modal` and an accessible name.
4. **Check names and semantics.** Every input has a `<label>` or
   `aria-label`/`aria-labelledby` — placeholder is not a label. Every
   meaningful image has `alt` text; decorative ones have `alt=""`. Headings
   are in order. ARIA is only added where native HTML can't do the job; an
   `aria-*` attribute that contradicts the element is a defect, not a fix.
5. **Enumerate UI states.** For each async action or data source, find the
   code for loading, empty, error, partial, and disabled/submitting. Missing
   submitting state means double-submit; an error path that resets state
   means the user retypes everything. Async results and errors must be
   announced (`role="alert"`, `aria-live`, or focus moved to the message).
6. **Check forms.** Errors are tied to their field (`aria-describedby`,
   `aria-invalid`), input survives a failed submit, the submit is a real
   `type="submit"` so Enter works, and fields carry `autocomplete`,
   `inputMode` and the right `type`.
7. **Check responsiveness and visuals.** Look for fixed pixel widths and
   heights on containers, missing `max-width`, horizontal overflow, touch
   targets under 24x24 CSS px (44x44 preferred), and text colors. Compute
   contrast for every text/background pair you can resolve: 4.5:1 for normal
   text, 3:1 for large text and UI component boundaries (WCAG AA).
8. **Check performance and consistency.** Images without `width`/`height`
   (or `aspect-ratio`) cause layout shift; below-the-fold images need
   `loading="lazy"`. Whole-library imports for one helper (`lodash`,
   `moment`) bloat the bundle. Look for expensive work in render on hot paths
   and inline objects that defeat memoization. Hard-coded colors and spacing
   next to existing tokens, and re-implemented components, are consistency
   findings.
9. **Verify.** If a browser or runner exists, tab through the UI, run axe
   (`@axe-core/playwright`, `jest-axe`, or the browser extension), and
   resize to 320px and 390px. Otherwise state exactly which checks were
   static, and list what needs a browser or a screen reader.
10. **Rank and write.** Rank P0-P3 by who is blocked and how badly, give
    each finding file:line, evidence, affected users and a concrete fix, then
    write `UI_REVIEW.md`. Do not edit source unless asked.

# Tool & resource guidance

- For dialogs, buttons vs links, labels, live regions and ARIA misuse, read
  `references/accessibility-patterns.md`; it has the fix code for each.
- For loading/empty/error/submitting states and form behavior, read
  `references/ui-states-and-forms.md`.
- For layout shift, bundle weight, render cost and lazy loading, read
  `references/web-vitals-in-components.md`.
- Grep for `onClick=` on non-button tags, `outline: none`, `placeholder=`,
  `<img`, hex colors, `px` widths and whole-library imports to seed the
  inventory, then read each hit in context.
- Resolve CSS variables to real values before computing contrast; a token
  name is not a color.

# Output contract

Write `UI_REVIEW.md` with these sections, in order:

- **Verdict** — ship / ship after P0-P1 fixes / do not ship, in one line,
  plus the count of findings by severity.
- **Scope** — files, framework, entry point, assumed users and viewports,
  and whether a browser or test runner was used.
- **Findings** — a table: ID, severity, dimension (a11y, states, responsive,
  performance, forms, consistency), title, file:line, affected users.
- **Finding details** — per finding: evidence (quoted code), user impact
  naming who is affected, the fix as code or a precise change, and how to
  verify it.
- **Checked and fine** — things that were examined and are correct, so the
  reader knows they were not skipped.
- **Needs manual or browser verification** — what static reading could not
  settle (screen-reader announcements, real contrast over images, zoom).

# Quality checks

- [ ] Every interactive element was inventoried and its keyboard path traced.
- [ ] Every finding has file:line, quoted evidence, affected users and a fix.
- [ ] Each async action was checked for loading, error, empty and
      submitting states, not only the success render.
- [ ] Contrast claims cite the two resolved colors and the ratio.
- [ ] Correct patterns (decorative `alt=""`, labelled checkbox) appear under
      "Checked and fine", not as findings.
- [ ] The verdict matches the severities: no "ship" with an open P0.
- [ ] Static-only checks are labelled as such.

# Red flags

Stop and correct course if any of these are true:

- You are about to approve and cannot list the Tab order through the UI.
- Every finding concerns the success render; no line mentions what the user
  sees while the request is in flight or after it fails.
- You called a control accessible because it has an `aria-*` attribute,
  without checking it has a role, a name and keyboard handling.
- A finding says "low contrast" with no colors or ratio.
- A finding is a preference (rounder corners, another font) filed as P1-P2.
- You flagged `alt=""` on a decorative image, or a `<label htmlFor>` pair,
  as missing accessibility.
- You wrote "verified" for something you only read.

# Common rationalizations

Excuses that come up for skipping this workflow, and why they don't hold:

| Rationalization | Reality |
|---|---|
| "It's an internal tool, accessibility doesn't matter." | Internal users include keyboard-only users, screen-reader users and people with injuries. Public-sector and enterprise buyers also audit internal tools. |
| "The design system handles that." | Only if the component uses it. A `div` styled to look like the system's button inherits none of its semantics or focus handling. Check the code in front of you. |
| "We'll add loading states later." | A missing submitting state on a payment button is a double charge today. States are part of the feature, not polish. |
| "It looks fine on my screen." | Your screen is wide, fast and mouse-driven. Most users are on a 390px phone, some on a slow network, some with no mouse. |
| "It has aria-label, so it's accessible." | A name on an element that can't take focus or respond to Enter is still unusable. ARIA describes behavior; it doesn't add it. |
| "axe passed, so we're done." | Automated checks catch roughly a third of WCAG issues. They can't tell you focus returns to the trigger or that an error is announced. |
| "The user said skip the a11y and just make it work." | Then keep the review short, not absent: a control the keyboard can't reach doesn't work. Flag P0s; defer P3s. |

# Edge cases

- **Component library in use** (MUI, Radix, Headless UI): check it is used
  as documented — a Radix `Dialog` without `Dialog.Title` still lacks a name.
- **Only a diff is available**: review the changed UI, read the parent and
  styles it depends on, and list unread context under manual verification.
- **Colors from variables you can't resolve** (theme at runtime): mark the
  contrast check as needing browser verification rather than guessing.
- **Canvas, maps, video or charts**: check the surrounding controls and
  text alternatives; note the inner widget as needing manual testing.
- **Server-rendered or no-JS HTML**: check that forms and links work before
  hydration; a `div onClick` does nothing until JS loads.
- **Asked to fix, not just review**: write the review first, then apply the
  fixes and re-run the keyboard trace and any automated check.

# References

- `references/accessibility-patterns.md` — dialog focus management, button
  vs link, labels, live regions, ARIA misuse, contrast, with fix code.
- `references/ui-states-and-forms.md` — the state checklist and form
  behavior, with fix code.
- `references/web-vitals-in-components.md` — CLS, LCP and INP causes in
  component code and their fixes.
- `examples/settings-drawer-review.md` — a full worked `UI_REVIEW.md` for a
  Vue account-settings drawer.
