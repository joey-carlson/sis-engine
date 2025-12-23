# Changelog

## 0.1.x – Streamlit Harness v0.1 Prototype Added

- Refactored Streamlit harness session state into a single HarnessState dataclass to prevent rerun scoping regressions.

- Clamped clocks in state application to a configurable range (default 0–12).
- Added adaptive weighting to reduce sticky outcomes (penalize recently used event_ids).
- Cutoff cap is now influenced by rarity mode (spiky lowers cap), harness diagnostics show cutoff resolution breakdown.

- Added Scenario Runner tab (multi-run suites) with downloadable Markdown/JSON debug reports for tuning.

- Harness batch runs tick cooldowns between generated events by default to avoid exhausting the content pool.

- Added a debug-first Streamlit harness (`streamlit_harness/app.py`) to exercise the engine and visualize diagnostics (severity distribution, cutoff rate, tag/event frequencies).
- Kept engine core UI-agnostic, harness is a separate layer that calls into `spar_engine`.
- Updated README with Streamlit harness install/run instructions.
- Added `/docs/KEY_DOCS.md` to help collaborators find the governing docs.
- Packaging hygiene: removed `.git` and `.DS_Store` from the distributed zip artifact.

All notable changes to this project are documented here.

