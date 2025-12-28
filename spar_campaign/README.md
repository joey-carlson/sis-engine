# SiS Campaign Mechanics v0.2

**Optional campaign-level state tracking layer**

---

## Purpose

This module provides campaign-scale state management that operates above the SiS Engine, tracking pressure and consequences across multiple scenes without modifying engine internals.

**Design principles**:
- v0.1: "Scene mechanics create pressure. Campaign mechanics remember it."
- v0.2: "Scene outcomes echo forward. Campaign mechanics remember what can't be undone."

---

## Quick Start (v0.2)

```python
from spar_campaign import (
    CampaignState,
    CampaignDelta,
    Scar,
    FactionState,
    apply_campaign_delta,
    decay_campaign_state,
    get_campaign_influence,
)

# Initialize campaign state
campaign_state = CampaignState.default()

# After each scene...
# 1. Derive delta from scene outcome (with optional scars/factions)
delta = CampaignDelta.from_scene_outcome(
    severity=event.severity,
    cutoff_applied=event.cutoff_applied,
    tags=event.tags,
    effect_vector_dict=ev_dict,
    factions_present=["city_watch", "merchant_guild"],  # v0.2
    explicit_scars=[Scar(...)] if adding_scar else None,  # v0.2
)

# 2. Apply to campaign state
campaign_state = apply_campaign_delta(campaign_state, delta)

# 3. Get influence for next scene (now includes faction/scar hints)
influence = get_campaign_influence(campaign_state)
# Returns: include_tags, suggested_factions_involved, pressure_band, heat_band, etc.

# 4. Apply decay at narrative moments (aftermath, downtime)
if phase == "aftermath":
    campaign_state = decay_campaign_state(campaign_state)
```

---

## What's Tracked (v0.2)

### Campaign Pressure (int)
- Accumulates from high-severity scenes (>5) and cutoffs
- Represents unresolved tension at campaign scale
- Default cap: 30
- **Bands**: stable (0-4), strained (5-9), volatile (10-19), critical (20+)

### Heat (int)
- Accumulates from visibility, social friction, reinforcements
- Represents external attention and response
- Default cap: 20
- **Bands**: quiet (0-3), noticed (4-7), hunted (8-14), exposed (15+)

### Scars (List[Scar]) - v0.2 Enhanced
- **Structured objects** with category, severity, source, notes
- Categories: physical, social, political, resource, reputation, environment
- Severity: low, medium, high
- Permanent (no auto-decay)
- Influence scene setup based on category

### Factions (Dict[str, FactionState]) - v0.2 New
- Tracks external actors (authorities, rivals, organizations)
- **Attention** (0-20): How aware they are
- **Disposition** (-2 to +2): hostile/unfriendly/neutral/friendly/allied
- Accumulates from visibility/social tags when faction present
- Disposition changes explicit only (stays neutral by default)

---

## How It Influences Scenes (v0.2)

Campaign state provides **hints** for scene setup (does not override engine):

**Pressure-based (unchanged from v0.1)**:
- High (≥20): time_pressure, reinforcements, spiky mode
- Moderate (≥10): time_pressure
- Low (<5 + heat <5): exclude time_pressure

**Heat-based (unchanged from v0.1)**:
- High (≥15): social_friction, visibility
- Moderate (≥8): visibility

**Scar-based (v0.2 new)**:
- Resource scars → attrition tag
- Social/political/reputation scars → social_friction tag
- Provides human-readable notes explaining influence

**Faction-based (v0.2 new)**:
- Attention ≥10 → reinforcements tag
- Hostile disposition → social_friction tag
- Attention ≥5 → faction suggested as involved in scene
- Provides faction-specific notes

**Bands (v0.2 new)**:
- Returns: pressure_band, heat_band
- Informational descriptors for human readability
- Not used for rules/logic (descriptive only)

See `get_campaign_influence()` for complete logic.

---

## Architecture

### Pure Functional Design
- All operations are pure functions
- Immutable state (frozen dataclasses)
- Deterministic with explicit inputs
- No side effects or hidden state

### Separation of Concerns
```
CampaignState (this module)
    ↕ observes / suggests
EngineState (spar_engine)
```

Campaign layer NEVER:
- Modifies engine.py behavior
- Overrides severity or cutoff logic
- Directly alters EngineState

Campaign layer MAY:
- Suggest tags for SelectionContext
- Suggest rarity_mode changes
- Provide human-readable notes

---

## Files

- `models.py` - CampaignState and CampaignDelta dataclasses
- `campaign.py` - Pure functions for state management
- `__init__.py` - Package exports

---

## Demo

### v0.1 Demo (Basic Features)
```bash
python examples/campaign_mechanics_demo.py
```

Shows: Heat accumulation, aftermath decay, basic influence

### v0.2 Demo (Full Features)
```bash
python examples/campaign_mechanics_v0.2_demo.py
```

Shows:
- 8-scene campaign with explicit consequences
- Structured scars persisting and influencing scenes
- 3 factions tracking attention from scene outcomes
- Long-arc bands (stable/hunted) changing over time
- Backward compatibility (v0.1 → v0.2)
- Complete separation from engine internals

---

## Integration Example

```python
# Scene setup with campaign influence
influence = get_campaign_influence(campaign_state)

# Apply campaign hints to selection
tags = base_tags + influence["include_tags"]
tags = [t for t in tags if t not in influence["exclude_tags"]]
rarity_mode = influence.get("rarity_bias") or default_rarity

# Run scene normally (engine unchanged)
selection = SelectionContext(
    enabled_packs=["data/core_complications.json"],
    include_tags=tags,
    exclude_tags=[],
    factions_present=[],
    rarity_mode=rarity_mode,
)

event = generate_event(context, engine_state, selection, entries, rng)

# Update both states
engine_state = apply_state_delta(engine_state, event.state_delta)

delta = CampaignDelta.from_scene_outcome(...)
campaign_state = apply_campaign_delta(campaign_state, delta)
```

---

## Version History

### v0.2 (2025-12-25) - Current
- ✅ Structured scars (category, severity, source, notes)
- ✅ Faction tracking (attention, disposition)
- ✅ Long-arc bands (pressure/heat descriptors)
- ✅ Enhanced campaign influence
- ✅ Backward compatibility with v0.1

### v0.1 (2025-12-25) - Initial
- Campaign pressure tracking
- Heat tracking
- Basic string scars
- Scene setup influence
- Explicit decay

## Future (v0.3+)

Potential enhancements (not in v0.2):
- Scar remediation mechanics
- Faction AI or actions
- Auto-scar triggers
- Disposition auto-adjustment
- Streamlit UI integration
- Campaign scenario schema support

All future work must preserve:
- Optional nature
- Pure functional design
- Engine separation
- Determinism

---

## Related Documents

- `docs/REQUIREMENTS_campaign_mechanics_v0.2.md` - v0.2 design (current)
- `docs/REQUIREMENTS_campaign_mechanics_v0.1.md` - v0.1 design (foundation)
- `docs/contract.md` - SiS Engine v0.1 Contract (unchanged)
- `docs/engineering_rules.md` - Implementation standards
- `examples/campaign_mechanics_v0.2_demo.py` - v0.2 demonstration
- `examples/campaign_mechanics_demo.py` - v0.1 demonstration

---

**Version**: 0.2  
**Last Updated**: 2025-12-25
