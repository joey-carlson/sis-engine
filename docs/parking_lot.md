# SPAR Tool Parking Lot (Post-v1.0)

_Last updated: 2025-12-26_

This is the single source of truth for **deferred** work. Everything here is optional and additive; it is not required for v1.0 to function.

## How to use this list
- **Next up** items are the best ROI and lowest risk.
- **Later** items are valuable but should wait until there is real user demand.
- **Deep R&D** items are experiments; only pursue if we have a specific pain to solve.
- When an item is unparked, it should move into a dated implementation plan and be removed from this list.

---

## Next up (highest ROI, lowest risk)

### 1) Thematic content packs (Events + Loot)
**Why now:** The engine is stable; perceived intelligence now scales with content breadth.  
**What:** Produce 2–4 high-quality packs with distinct voices (setting-neutral), plus campaign-specific packs when needed.
- Events: Urban Intrigue, Frontier Survival, Horror Pressure, Institutional/Political
- Loot: Salvage & Black Market is done; next: Patronage/Institutional Rewards; Smuggler’s Cache; Relic Curios
**Notes:** No new mechanics. Packs only.

### 2) Pack authoring ergonomics and quality gates
**Why now:** Community packs will drift without guardrails.  
**What:** Lightweight tooling and docs (no heavy UI) to keep packs consistent.
- Pack lint/validator (schema + tag vocabulary + phase coverage checks)
- Pack “smoke test” runner (small batch generation + sanity metrics)
- Pack provenance display (show which pack an output came from)
- Optional: “pack cookbook” examples (short, practical)

### 3) Source list import (deep) for external datasets
**Why now:** You’ve proven metadata-only sources; next step is real mapping from spreadsheets/CSVs into packs.  
**What:** Import/mapping pipeline with review step (no silent commits).
- Supported inputs: CSV/XLSX/JSON
- Mapping profiles per source (column → fields/tags/severity bands)
- Normalization rules (dedupe, tag hygiene)
- Output: generated pack(s) with provenance + version stamp
**Non-goals:** live syncing, web scraping, hosted parsing.

---

## Later (valuable, but wait for demand)

### 4) Campaign story web view (read-only)
**Why:** Exports are clean; web view is presentation-layer value.  
**What:** Render story-facing campaign history and sessions as a browsable timeline.
- Filters: factions, scars, threads
- “Player-safe” view toggle (hides GM private notes)
- Static export (HTML) or lightweight local server
**Non-goals:** editing in the web view (v1.x).

### 5) Canon Summary curation heuristics tuning
**Why:** Canon is now GM-authored; heuristics can help but must not overwrite.  
**What:** Better deterministic suggestions + optional prompts.
- Suggest 1–3 candidate canon bullets per session
- Provide templates by campaign tone
- Never auto-append; always GM review

### 6) Cross-system adapters
**Why:** Broadens adoption; not required for core value.  
**What:** Map outputs into system-specific forms as optional overlays.
- D&D 5e complications adapter
- GURPS complications adapter
- VtM complications adapter
**Notes:** Prefer presets + vocabulary + content packs, not engine forks.

### 7) Docx/PDF exports
**Why:** Nice-to-have for publishing workflows.  
**What:** Add DOCX export for story-facing campaign history and sessions (Markdown remains canonical).

### 8) Multi-GM / shared-world operations
**Why:** Only needed for living-campaign play at scale.  
**What:** Merge session packets, coordinator review, conflict resolution tooling.
- Session packet signing/versioning
- Merge UI for competing edits
- Canon publishing workflow

---

## Deep R&D (only if there is a concrete pain)

### 9) Alternative SOC sampling modes
**Why:** Experimental. Only pursue if the current SOC feel isn’t matching table experience.
- Tension pool / burst release modes
- Multi-modal severity distributions
- Context-aware alpha variations beyond current knobs

### 10) Advanced cutoff behaviors
- New conversion modes (beyond omen/clock_tick/downshift) only if needed
- Phase-sensitive cutoff families

### 11) Advanced diagnostics UI
**Why:** Current diagnostics are adequate; enhance only if contributors need it.
- Distribution visualizer dashboards
- State tracker graphs
- Parameter “what-if” simulator

### 12) API / plugin architecture
**Why:** Adds maintenance burden.  
**What:** Only if you need integrations (web app, mobile, external tools).
- REST API
- Plugin/connector model for packs/adapters

---

## Done and locked (for reference)
These are explicitly **not parked** and should not be revisited without a versioned proposal:
- Story vs system data contract and exports
- Campaign Manager loop (Prep Queue → Session Draft → Commit)
- Campaign history import (structured + natural + unstructured fallbacks)
- Faction CRUD and faction influence on generator context
- Multi-generator pack typing and discovery
- Loot generator v1.0 diagnostics + thematic pack baseline
- Event generator UI simplification and Diagnostics reframe
