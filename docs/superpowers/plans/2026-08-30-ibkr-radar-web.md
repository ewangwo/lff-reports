# IBKR Radar Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a public-safe GitHub Pages dashboard that refreshes its latest internet-derived market snapshot and computes the A/B/C review signals without exposing private IBKR data.

**Architecture:** A Python collector creates a versioned public JSON snapshot from price and SEC sources. A React/Vite frontend loads that snapshot without browser caching and renders the approved table-led dashboard. GitHub Actions refreshes data and build artifacts; private TWS data remains outside the public repository.

**Tech Stack:** Python 3.12, pytest, React 19, TypeScript, Vite, Vitest, Testing Library, Recharts, GitHub Actions, GitHub Pages.

---

### Task 1: Metric and signal engine

**Files:**
- Create: `scripts/radar_data/metrics.py`
- Create: `scripts/radar_data/models.py`
- Test: `tests/radar_data/test_metrics.py`

- [ ] Write failing tests for SMA200, empirical percentile, relative volume, insufficient samples, ETF PE exclusion, negative EPS, and A/B/C signal classification.
- [ ] Run `python -m pytest tests/radar_data/test_metrics.py -v` and confirm failures are caused by missing modules.
- [ ] Implement immutable dataclasses and pure calculation functions with explicit missing-data results.
- [ ] Re-run the test file and confirm all metric tests pass.

### Task 2: Public market and SEC collector

**Files:**
- Create: `scripts/radar_data/providers.py`
- Create: `scripts/radar_data/collector.py`
- Create: `scripts/radar_data/universe.py`
- Create: `scripts/update_ibkr_radar.py`
- Test: `tests/radar_data/test_collector.py`
- Test fixture: `tests/radar_data/fixtures/`

- [ ] Write failing provider/collector tests using local Yahoo and SEC fixtures.
- [ ] Verify the tests fail before production code exists.
- [ ] Implement bounded HTTP fetches, source timestamps, SEC filing summaries, public-universe collection, and atomic snapshot replacement.
- [ ] Confirm failed upstream requests retain the last good snapshot and emit a data-health error.
- [ ] Run collector tests and a bounded live smoke collection for two public symbols.

### Task 3: React dashboard behavior

**Files:**
- Create: `radar-app/package.json`
- Create: `radar-app/vite.config.ts`
- Create: `radar-app/src/types.ts`
- Create: `radar-app/src/lib/signals.ts`
- Create: `radar-app/src/lib/api.ts`
- Create: `radar-app/src/lib/signals.test.ts`
- Create: `radar-app/src/App.test.tsx`

- [ ] Install pinned frontend dependencies.
- [ ] Write failing tests for A/B/C labels, no-store snapshot loading, filters, selection, and stale-data display.
- [ ] Run Vitest and confirm expected failures.
- [ ] Implement the data contracts, signal helpers, API loader, and state behavior.
- [ ] Re-run Vitest until all behavior tests pass.

### Task 4: Approved visual implementation

**Files:**
- Create: `radar-app/src/App.tsx`
- Create: `radar-app/src/styles.css`
- Create: `radar-app/src/components/SignalTable.tsx`
- Create: `radar-app/src/components/EventRail.tsx`
- Create: `radar-app/src/components/DetailPanel.tsx`
- Create: `radar-app/src/components/DataHealth.tsx`
- Create: `radar-app/src/main.tsx`
- Create: `radar-app/index.html`

- [ ] Extract palette, typography, spacing, table density, borders, states, and responsive rules from the accepted concept.
- [ ] Implement the dark table-led desktop dashboard without trading controls or private metrics.
- [ ] Add keyboard-accessible filters, sorting, row selection, refresh, and responsive stacking.
- [ ] Verify desktop and mobile rendering in a browser and correct overflow, typography, and state issues.

### Task 5: GitHub Pages build and refresh automation

**Files:**
- Create: `.github/workflows/update-ibkr-radar.yml`
- Create: `radar-app/scripts/copy-build.mjs`
- Modify: `index.html`
- Generate: `tools/ibkr-radar/`
- Generate: `data/ibkr-radar/public-snapshot.json`

- [ ] Add a workflow with manual and scheduled triggers, bounded collection, tests, build, and Pages artifact update.
- [ ] Ensure the workflow has only contents write permission and no broker or trading secrets.
- [ ] Build into `tools/ibkr-radar/` with the correct GitHub Pages base path.
- [ ] Add a public-safe index entry without account facts.
- [ ] Run a repository privacy scan for account numbers, private holdings, credentials, order identifiers, and API keys.

### Task 6: Verification and deployment

**Files:**
- Modify: `README.md` if present, otherwise create `tools/ibkr-radar/README.md`

- [ ] Run the full Python and frontend test suites.
- [ ] Run the production build and inspect generated paths.
- [ ] Serve the Pages tree locally and test refresh, filters, selection, data health, desktop, and mobile.
- [ ] Compare browser screenshots against the accepted concept and record at least five visual checks.
- [ ] Commit the feature branch, push it, merge only after verification, then push `main`.
- [ ] Verify the live GitHub Pages URL and report any propagation delay.
