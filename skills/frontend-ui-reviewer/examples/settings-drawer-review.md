# Worked example: reviewing a Vue account-settings drawer

**Prompt:** "Can you give the new settings drawer a once-over before
Thursday's release? It's `SettingsDrawer.vue` and `ToggleRow.vue`."

The app is Vue 3 + Vite. A Playwright setup exists in the repo, so the run
started the dev server, tabbed through the drawer and ran
`@axe-core/playwright` on it. Abridged `UI_REVIEW.md` output:

---

# UI review — SettingsDrawer

## Verdict

**Do not ship as-is; ship after the P0-P1 fixes.** 1 P0, 3 P1, 2 P2, 1 P3.

## Scope

- **Files:** `src/components/SettingsDrawer.vue`, `src/components/ToggleRow.vue`,
  `src/styles/tokens.css` (read for values).
- **Entry point:** the gear icon in `AppHeader.vue` sets `settingsOpen`.
- **Assumed users:** logged-in customers on desktop and mobile; keyboard and
  screen-reader users assumed present (not stated in the request).
- **Verification:** dev server + Playwright (Chromium) keyboard walk and
  axe run; viewports 1280px and 360px. No screen reader was available.

## Findings

| ID | Sev | Dimension | Title | Location | Affected users |
|---|---|---|---|---|---|
| U1 | P0 | a11y | Notification toggles are `span`s, unreachable by keyboard | `ToggleRow.vue:4` | Keyboard, switch-device, screen-reader users |
| U2 | P1 | a11y | Drawer doesn't trap focus or return it to the gear button | `SettingsDrawer.vue:12-30` | Keyboard and screen-reader users |
| U3 | P1 | states | Save failure is silent; spinner stops and nothing is shown | `SettingsDrawer.vue:58-66` | Everyone; worst on flaky mobile networks |
| U4 | P1 | a11y | Gear trigger is an icon-only button with no name | `AppHeader.vue:22` | Screen-reader and voice-control users |
| U5 | P2 | responsive | Drawer `width: 420px` covers and clips at 360px | `SettingsDrawer.vue:94` | Mobile users |
| U6 | P2 | consistency | Hard-coded `#2f6fed` and `14px` padding beside existing tokens | `SettingsDrawer.vue:97-103` | Future theming / dark mode |
| U7 | P3 | performance | `date-fns` imported as a namespace for one `format` call | `SettingsDrawer.vue:41` | Slow devices (minor) |

## Finding details

### U1 — P0 — Notification toggles unreachable by keyboard

- **Evidence:** `<span class="toggle" :class="{ on: modelValue }"
  @click="$emit('update:modelValue', !modelValue)"></span>`. No role, no
  `tabindex`, no key handler, no label association. In the Playwright walk,
  Tab went from "Display name" straight to "Save", skipping all four toggles.
  axe reported nothing for these spans — they have no role, so there was
  nothing for it to check.
- **Impact:** keyboard users can't change any notification preference;
  screen readers read the row label but announce no control.
- **Fix:**
  ```vue
  <button type="button" role="switch" :aria-checked="modelValue"
          :aria-labelledby="labelId" class="toggle" :class="{ on: modelValue }"
          @click="$emit('update:modelValue', !modelValue)" />
  ```
- **Verify:** Tab reaches each toggle, Space flips it, the accessibility
  tree shows `switch` with the row label as its name and the checked state.

### U2 — P1 — No focus trap or focus return

- **Evidence:** the drawer is a `div` rendered with `v-if`; there is no
  `role="dialog"`, no focus call on open, and no listener for Escape.
  Playwright: after opening, the first Tab went to the page behind the
  overlay; closing left focus on `<body>`.
- **Impact:** keyboard users end up behind the overlay and lose their place
  on close; screen-reader users aren't told a dialog opened.
- **Fix:** render inside `<dialog>` with `showModal()` and
  `aria-labelledby="settings-title"`, handle `cancel` to close on Escape,
  and store and restore `document.activeElement` on open/close (see the
  pattern in `references/accessibility-patterns.md`).

### U3 — P1 — Save failure is silent

- **Evidence:** `catch { saving.value = false }` — no error message is set
  and nothing is rendered for the failure path. With the network set to
  offline in Playwright, clicking Save showed the spinner for a moment and
  then went back to idle.
- **Impact:** users think their settings saved; the next session shows the
  old values.
- **Fix:** keep `error` state; render `<p role="alert">{{ error }}</p>` above
  the Save button; keep the edited values; keep Save enabled for retry.

### U4 — P1 — Gear trigger has no accessible name

- **Evidence:** `<button class="icon-btn" @click="open"><GearIcon /></button>`;
  axe: `button-name` violation.
- **Fix:** `aria-label="Settings"` on the button, `aria-hidden="true"` on
  the SVG.

### U5 — P2 — Fixed drawer width on mobile

- **Evidence:** `.drawer { width: 420px; }`; at 360px the Save button sits
  partly off-screen and the page scrolls horizontally.
- **Fix:** `width: min(420px, 100vw);` and full-height at small breakpoints.

### U6 — P2 — Hard-coded values beside tokens

- **Evidence:** `background: #2f6fed; padding: 14px;` while `tokens.css`
  defines `--color-primary: #2f6fed` and `--space-3: 12px`.
- **Fix:** use `var(--color-primary)` and `var(--space-3)`; the 2px
  difference from 14px is not a design decision anyone asked for.

### U7 — P3 — Namespace import of date-fns

- **Evidence:** `import * as dateFns from 'date-fns'` for
  `dateFns.format(updatedAt, 'PP')`. Vite tree-shakes most of it; the
  visualizer showed about 3 KB gzip added.
- **Fix:** `import { format } from 'date-fns'`, or `Intl.DateTimeFormat`.

## Checked and fine

- "Display name" and "Email" inputs have visible `<label for>` labels and
  `autocomplete="name"` / `"email"`.
- The avatar image has `width`/`height` and a meaningful `alt` ("Your
  profile photo"); the chevron icons are `aria-hidden="true"` beside text.
- Body text `#1f2328` on `#ffffff` (16:1) and secondary text `#57606a` on
  `#ffffff` (6.4:1) pass AA.
- Save button has a submitting state (`disabled` + "Saving...") that
  prevents double submit.
- Focus ring: tokens define `:focus-visible` outline at 3:1 against the
  drawer background.

## Needs manual or browser verification

- Screen-reader announcement of the new `role="alert"` and the switch
  states (no NVDA/VoiceOver available in this run).
- 200% zoom and text-spacing overrides.
- Dark mode, which loads a runtime theme the static check couldn't resolve.
