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
