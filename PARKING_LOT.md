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

## Campaign Mechanics Layer - Future Enhancements (v0.2+)

**Status**: v0.1 COMPLETE and LOCKED (see `spar_campaign/` module)

Campaign Mechanics v0.1 successfully implements:
- Campaign pressure and heat tracking
- Scene outcome observation
- Non-invasive scene setup influence
- Explicit decay mechanics

Potential future enhancements (deferred until v0.1 validated in play):
- **Faction standing trackers**: Multi-faction tension and diplomacy state
- **Auto-scar triggers**: Automatic scar generation from significant events
- **Resource depletion mechanics**: Campaign-scale supply tracking
- **Richer influence rules**: More sophisticated scene setup hints
- **UI integration**: Streamlit harness campaign state display
- **Scenario schema support**: Campaign state in JSON scenarios
- **Campaign-level cutoffs**: Optional hard gates based on campaign state

**Design Intent**: All future work must preserve optional nature, pure functional design, and engine separation.

## Source List Import (External Content Feeds) - Deferred

**Context:**
As SPAR content grows, manually maintaining large content packs becomes inefficient. We've already reviewed community-scale datasets (e.g., large spreadsheet-based loot tables), which demonstrate both the value and pitfalls of external content sources.

**Idea:**
Introduce a future capability to treat a large external file (spreadsheet, CSV, JSON, etc.) as a source list that can be imported, transformed, or referenced as a content feed for event/scenario generation.

**High-level goals:**
- Allow pointing at a large external dataset as an input source
- Map source rows/entries into SPAR-compatible content entries
- Preserve engine/content separation (source is not engine logic)
- Enable large-scale content reuse without hand-curation

**Non-goals (for now):**
- No importer UX design yet
- No live syncing or hot-reload assumptions
- No schema locking beyond SPAR's internal content format
- No community submission pipeline yet

**Design considerations (future):**
- Clear separation between canonical content packs and imported sources
- Strong tag normalization and hygiene
- Validation layer to prevent low-quality or inconsistent imports
- Ability to selectively enable/disable source subsets

**Prerequisites before implementation:**
- Campaign Mechanics v0.1 validated in play
- At least one full thematic content pack completed
- Clear decisions on content ownership and curation workflow

---

## SPAR ↔ D&D Adapter Formalization (Explicitly Deferred)

**Status**: Parked pending content richness and campaign mechanics validation

Integration and publication-facing work:
- **Mechanical mappings**: How SPAR outputs map to D&D complications
- **DC/Damage translation**: SPAR severity → D&D difficulty/damage
- **System-specific consequences**: SPAR state → D&D mechanical effects
- **Adapter documentation**: Usage examples and integration guides
- **SPAR mechanics formalization**: Reverse mapping (D&D → SPAR inputs)

**Design Intent**: Requires stable content library and optional campaign layer before formalization makes sense.
