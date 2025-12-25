# SPAR Tool Parking Lot

A running list of deferred ideas and improvements.

## Engine (Deferred)

- **State aging for `recent_event_ids`**: add tick-based eviction/aging policy (distinct from the bounded list). Consider a per-ID TTL or decay by tick/scene.
- **Pack versioning + pack metadata header**: support pack-level metadata (schema version, pack id, pack version, author, tags, notes) and enforce schema validation on load.

## Streamlit Harness - JSON Scenario System (Deferred)

- **Directory browser UI**: Visual directory/file selection widget for scenario result output paths (currently text input only)
- **Sea preset support**: Add "sea" environment to preset options and scene_preset_values() function
- **Full JSON schema validation**: Validate field types, value ranges, and enum constraints (currently only validates required fields exist)
- **Scenario editor**: In-app JSON editing and creation interface for building scenarios without external editor
- **Scenario comparison**: Side-by-side result comparison UI for analyzing multiple scenario runs

## Campaign Mechanics Layer (Explicitly Deferred)

**Status**: Parked pending content richness stabilization

Campaign rhythm validation confirmed core engine creates sufficient multi-scene rhythms through severity variance and state memory. Clock plateau identified as future campaign-mechanics concern, NOT engine defect.

Deferred mechanics that belong to optional campaign layer:
- **Long-term clocks**: Campaign-scale pressure indicators (beyond scene-level tension/heat)
- **Clock decay rules**: Phase-specific clock reduction (e.g., aftermath decay)
- **Faction pressure**: Multi-faction tension tracking and consequences
- **Scars/Heat/Reputation**: Persistent campaign-level consequences
- **Arc-scale consequences**: Long-form narrative state tracking
- **Meta-pacing rules**: Campaign rhythm modifiers

**Design Intent**: These belong to an explicit campaign mechanics system layered on top of the stable core engine, not integrated into engine logic. Preserves engine simplicity, interpretability, and flexibility for different campaign styles.

## SPAR ↔ D&D Adapter Formalization (Explicitly Deferred)

**Status**: Parked pending content richness and campaign mechanics

Integration and publication-facing work:
- **Mechanical mappings**: How SPAR outputs map to D&D complications
- **DC/Damage translation**: SPAR severity → D&D difficulty/damage
- **System-specific consequences**: SPAR state → D&D mechanical effects
- **Adapter documentation**: Usage examples and integration guides
- **SPAR mechanics formalization**: Reverse mapping (D&D → SPAR inputs)

**Design Intent**: Requires stable content library and optional campaign layer before formalization makes sense.
