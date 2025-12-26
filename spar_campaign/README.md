# SPAR Campaign Mechanics v0.1

**Optional campaign-level state tracking layer**

---

## Purpose

This module provides campaign-scale state management that operates above the SPAR Engine, tracking pressure and consequences across multiple scenes without modifying engine internals.

**Design principle**: Scene mechanics create pressure. Campaign mechanics remember it.

---

## Quick Start

```python
from spar_campaign import (
    CampaignState,
    CampaignDelta,
    apply_campaign_delta,
    decay_campaign_state,
    get_campaign_influence,
)

# Initialize campaign state
campaign_state = CampaignState.default()

# After each scene...
# 1. Derive delta from scene outcome
delta = CampaignDelta.from_scene_outcome(
    severity=event.severity,
    cutoff_applied=event.cutoff_applied,
    tags=event.tags,
    effect_vector_dict=ev_dict,
)

# 2. Apply to campaign state
campaign_state = apply_campaign_delta(campaign_state, delta)

# 3. Get influence for next scene
influence = get_campaign_influence(campaign_state)

# 4. Apply decay at narrative moments (aftermath, downtime)
if phase == "aftermath":
    campaign_state = decay_campaign_state(campaign_state)
```

---

## What's Tracked

### Campaign Pressure (int)
- Accumulates from high-severity scenes (>5) and cutoffs
- Represents unresolved tension at campaign scale
- Default cap: 30

### Heat (int)
- Accumulates from visibility, social friction, reinforcements
- Represents external attention and response
- Default cap: 20

### Scars (Set[str])
- Permanent consequences (explicit only in v0.1)
- Examples: "resources_depleted", "known_to_authorities"
- No decay (irreversible)

---

## How It Influences Scenes

Campaign state provides **hints** for scene setup (does not override engine):

**High Pressure (≥20)**:
- Suggests: time_pressure, reinforcements tags
- Suggests: spiky rarity mode

**High Heat (≥15)**:
- Suggests: social_friction, visibility tags

**Low Pressure + Heat (<5)**:
- Suggests: exclude time_pressure tag
- Indicates breathing room for recovery

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

Run the demonstration script to see campaign mechanics in action:

```bash
python examples/campaign_mechanics_demo.py
```

This shows:
- 6-scene campaign (2 full approach/engage/aftermath cycles)
- Heat accumulation across scenes
- Aftermath decay (partial release)
- Dynamic tag influence based on campaign state
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

## Future (v0.2+)

Potential enhancements (not in v0.1):
- Streamlit UI integration
- Campaign scenario schema support
- Faction standing trackers
- Auto-scar triggers
- Resource depletion mechanics
- Campaign-level cutoffs/gates

All future work must preserve:
- Optional nature
- Pure functional design
- Engine separation
- Determinism

---

## Related Documents

- `docs/REQUIREMENTS_campaign_mechanics_v0.1.md` - Complete design and rationale
- `docs/contract.md` - SPAR Engine v0.1 Contract (unchanged)
- `docs/engineering_rules.md` - Implementation standards
- `examples/campaign_mechanics_demo.py` - Working demonstration

---

**Version**: 0.1  
**Last Updated**: 2025-12-25
