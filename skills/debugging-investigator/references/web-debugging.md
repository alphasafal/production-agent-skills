# Web / Frontend Debugging

Evidence sources, in order of cost:

1. **Console errors and network tab** — the actual error, actual request/response
   payloads and status codes. Don't guess at what a request sent; read it.
2. **React/Vue/framework devtools** — component state and props at the moment
   of failure, not what you assume they are.
3. **Source maps / stack trace symbolication** — a minified stack trace is not
   evidence until it's mapped back to source.
4. **Repro in an isolated page/component** — strip the app shell away; render
   just the failing component with the same props/state.

## Common mechanisms worth checking as hypotheses

- **Stale closure**: an event handler or effect captured an old value because
  a dependency array is missing it.
- **Race between render and async data**: component reads state before a
  fetch/subscription resolves, or after unmount (check for missing cleanup).
- **Hydration mismatch**: server-rendered markup differs from first client
  render (common cause: `Date.now()`, `Math.random()`, locale-dependent
  formatting, or conditional rendering keyed on `typeof window`).
- **Event handler double-firing**: missing debouncing, or both a bubbling
  handler and a capturing handler attached.
- **CSS specificity / cascade**: a "broken layout" bug is often not a logic
  bug at all — check computed styles before touching component code.

## Evidence checklist before forming a hypothesis

- [ ] Exact error message and stack trace (symbolicated)
- [ ] Network request/response for any involved API call
- [ ] Browser + OS + viewport if the bug is rendering-related
- [ ] Whether it reproduces in an incognito window (rules out extensions/cache)
