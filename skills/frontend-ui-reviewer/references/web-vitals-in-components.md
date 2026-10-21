# Core Web Vitals causes in component code

What to look for in a component diff, by metric. Thresholds (75th
percentile of real users): LCP under 2.5s, INP under 200ms, CLS under 0.1.

## CLS — layout shift

| Cause in code | Fix |
|---|---|
| `<img>` with no `width`/`height` and no CSS `aspect-ratio` | Set intrinsic `width` and `height` attributes (CSS can still scale it), or `aspect-ratio` on the container |
| Embeds, iframes, ads, maps with no reserved box | Reserve the space with `min-height` or `aspect-ratio` |
| Content inserted above existing content after load (banners, "new" badges) | Reserve the slot, or insert below the fold / in an overlay |
| Loading state smaller than the loaded content | Skeleton with the same dimensions |
| Web fonts swapping with very different metrics | `font-display: optional`, or `size-adjust` on the fallback face |

```jsx
<img src={product.imageUrl} alt={product.name} width={120} height={120} />
```

## LCP — largest contentful paint

- Hero or product image lazy-loaded (`loading="lazy"` on the LCP image
  delays it). Above-the-fold: eager, and `fetchpriority="high"` for the main
  one.
- Large images served at full resolution to small screens: use `srcset` /
  `sizes` or the framework image component (`next/image`, `@nuxt/image`).
- Render-blocking work: big synchronous scripts or CSS in the head, data
  fetched client-side after a JS bundle that could have been rendered on the
  server.
- Below-the-fold images without `loading="lazy"` compete for bandwidth with
  the LCP image.

## INP and bundle weight

**Whole-library imports for a single helper:**

| Import | Approx. cost (min+gzip) | Replacement |
|---|---|---|
| `import _ from 'lodash'` | ~25 KB | Native (`String.prototype.trim`, `Array.prototype.map`, `structuredClone`), or `lodash-es/debounce` |
| `import moment from 'moment'` | ~70 KB with locales | `Intl.DateTimeFormat`, `Date` arithmetic, or `date-fns` / `dayjs` per-function imports |
| Full icon packs (`import * as Icons`) | varies, often 100 KB+ | Import individual icons |

Every KB of JS is parse and execute time on a mid-range phone, which delays
the first interaction and every interaction that waits on the main thread.

**Render cost on hot paths:**

- Expensive computation in render on every keystroke (sorting or filtering
  large lists, formatting thousands of rows): `useMemo`, or move it out of
  the render path.
- Inline objects or functions passed to memoized children, defeating
  `React.memo` — only a finding if the child is expensive and actually
  re-renders often; don't flag it by reflex.
- Long lists without virtualization (hundreds of rows with images).
- Synchronous handlers that do heavy work before the UI can update; yield
  or defer non-urgent work (`startTransition`, `requestIdleCallback`).
- Code that only a modal or rarely used route needs, bundled into the main
  entry: `React.lazy` / dynamic `import()`.

## How to verify

- Bundle: `npx vite-bundle-visualizer`, `source-map-explorer`, or
  `webpack-bundle-analyzer`; compare before and after.
- CLS / LCP: Lighthouse or the Performance panel with CPU throttling
  (4x) and a "Fast 4G" network profile; the Layout Shift track shows which
  element moved.
- INP: the Performance panel's Interactions track while doing the real
  interaction.

If none can run, state the finding from the code and list the measurement
under "Needs manual or browser verification".

## Severity guide

- **P1:** shifts or delays a primary action (a Pay button that jumps as an
  image loads; LCP image lazy-loaded on a landing page).
- **P2:** measurable bloat or shift with no direct task failure — a 70 KB
  date library for one date, an unsized thumbnail.
- **P3:** micro-optimizations without evidence of a hot path.
