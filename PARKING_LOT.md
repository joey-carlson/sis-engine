# SPAR Tool Parking Lot

A running list of deferred ideas and improvements.

## Engine (Deferred)

- **State aging for `recent_event_ids`**: add tick-based eviction/aging policy (distinct from the bounded list). Consider a per-ID TTL or decay by tick/scene.
- **Pack versioning + pack metadata header**: support pack-level metadata (schema version, pack id, pack version, author, tags, notes) and enforce schema validation on load.

