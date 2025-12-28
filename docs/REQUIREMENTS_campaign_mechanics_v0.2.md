<!--
Version History:
- v0.2 (2025-12-25): Structured scars, faction tracking, long-arc bands
-->

# Campaign Mechanics Layer v0.2 - Requirements & Design

**Status**: Draft v0.2  
**Date**: 2025-12-25  
**Type**: Feature Extension

---

## 1. Overview

### Objective
Extend Campaign Mechanics from v0.1 (short-term memory) to v0.2 (long-arc consequences) by adding:
- Structured scars (permanent consequences)
- Faction tracking (attention + disposition)
- Long-arc bands (descriptive state tiers)

### Design Principle
> Scene outcomes echo forward. Campaign mechanics remember what can't be undone.

### Changes from v0.1
- Scars: `Set[str]` → `List[Scar]` (structured objects)
- Added: `factions: Dict[str, FactionState]`
- Added: `get_pressure_band()` and `get_heat_band()` methods
- Enhanced: `get_campaign_influence()` with faction/scar awareness
- Maintained: Backward compatibility for v0.1 saves

---

## 2. New Models (v0.2)

### 2.1 Scar (Structured)

```python
@dataclass(frozen=True)
class Scar:
    scar_id: str
    category: ScarCategory  # physical, social, political, resource, reputation, environment
    severity: ScarSeverity  # low, medium, high
    source: Optional[str]
    created_scene_index: Optional[int]
    notes: Optional[str]
```

**Design notes:**
- Permanent (no decay in v0.2)
- Explicit creation only (no auto-generation)
- Influences scene setup via category
- Human-readable with notes field

**Category influence:**
- `resource` → suggests attrition tag
- `social/political/reputation` → suggests social_friction tag
- `physical` → future content hooks
- `environment` → terrain/hazard hooks

### 2.2 FactionState

```python
@dataclass(frozen=True)
class FactionState:
    faction_id: str
    attention: int  # 0-20 cap
    disposition: int  # -2 (hostile) to +2 (allied)
    notes: Optional[str]
```

**Accumulation rules:**
- Attention +1 per visibility/social_friction tag (if faction present)
- Attention +1 for reinforcements tag
- Attention +1 if effect_vector.heat ≥ 2
- Disposition changes: Explicit only (no auto-adjustment)

**Influence:**
- Attention ≥10 → suggests reinforcements tag
- Disposition ≤-1 → suggests social_friction tag
- Attention ≥5 → faction suggested as involved

**Design notes:**
- Factions observe and remember (don't act yet)
- Cap prevents runaway attention (20 max)
- Disposition stays neutral by default
- No faction AI or auto-triggers

### 2.3 Long-Arc Bands (Descriptive)

**Pressure Bands:**
- 0-4: stable
- 5-9: strained
- 10-19: volatile
- 20+: critical

**Heat Bands:**
- 0-3: quiet
- 4-7: noticed
- 8-14: hunted
- 15+: exposed

**Purpose:** Informational only. Provides human-readable state summary without changing behavior.

---

## 3. CampaignState v0.2

### Schema

```python
@dataclass(frozen=True)
class CampaignState:
    version: str = "0.2"
    campaign_pressure: int = 0
    heat: int = 0
    scars: List[Scar] = []
    factions: Dict[str, FactionState] = {}
    total_scenes_run: int = 0
    total_cutoffs_seen: int = 0
    highest_severity_seen: int = 0
    _legacy_scars: Set[str] = set()  # v0.1 compatibility
```

### Backward Compatibility

**v0.1 → v0.2 upgrade:**
- String scars stored in `_legacy_scars`
- Legacy scars still influence scene setup
- Version field auto-upgrades to "0.2"
- All v0.1 saves loadable

### Serialization

```python
# v0.2 format
{
  "version": "0.2",
  "campaign_pressure": 2,
  "heat": 12,
  "scars": [
    {
      "scar_id": "known_to_city_watch",
      "category": "reputation",
      "severity": "medium",
      "source": "Scene 2 confrontation",
      "created_scene_index": 2,
      "notes": "Faces seen during escape"
    }
  ],
  "factions": {
    "city_watch": {
      "faction_id": "city_watch",
      "attention": 2,
      "disposition": 0,
      "notes": null
    }
  }
}
```

---

## 4. Integration Pattern (v0.2)

### Typical Usage

```python
# Scene setup
influence = get_campaign_influence(campaign_state)

# Returns:
{
  "include_tags": ["social_friction", "attrition"],
  "exclude_tags": [],
  "rarity_bias": None,
  "notes": [
    "Scar: known_to_city_watch - social complications likely",
    "Scar: supplies_depleted - supply pressure continues"
  ],
  "suggested_factions_involved": ["city_watch"],
  "pressure_band": "stable",
  "heat_band": "hunted"
}

# Generate scene with explicit scars/factions
delta = CampaignDelta.from_scene_outcome(
    severity=event.severity,
    cutoff_applied=event.cutoff_applied,
    tags=event.tags,
    effect_vector_dict=ev_dict,
    factions_present=["city_watch", "merchant_guild"],
    explicit_scars=[Scar(...)] if adding_scar else None,
)

# Apply and update
campaign_state = apply_campaign_delta(campaign_state, delta)
```

---

## 5. Demo Results (Seed 123, 8 Scenes)

### Scar Persistence
- Scene 4: Added "known_to_city_watch" (reputation, medium)
- Scene 7: Added "supplies_depleted" (resource, high)
- Both persisted through remaining scenes
- Scene 5+ influenced by reputation scar (added social_friction)
- Scene 7+ influenced by resource scar (added attrition)

### Faction Tracking
- city_watch: attention 0→1→2 (from visibility/social tags)
- merchant_guild: attention 0→1 (Scene 5)
- underground: attention 0→2 (Scene 8, high visibility)
- All dispositions stayed neutral (no explicit changes)

### Long-Arc Bands
- Pressure: "stable" throughout (0-2 range)
- Heat: "quiet" → "noticed" → "hunted" (0→12)
- Bands changed at appropriate thresholds
- Human-readable state summary provided

### Key Validations
✅ Scars persist across scenes  
✅ Scars influence future scene setup  
✅ Factions accumulate attention correctly  
✅ Disposition stays neutral without explicit change  
✅ Bands provide readable state descriptors  
✅ v0.1 compatibility maintained  
✅ Engine internals unchanged  

---

## 6. Acceptance Criteria

- [x] Structured Scar model with category/severity/notes
- [x] Scars persist across scenes (no auto-decay)
- [x] Scars influence scene setup tags
- [x] FactionState tracks attention and disposition
- [x] Factions accumulate attention from scene outcomes
- [x] Disposition changes explicit only (no auto)
- [x] Long-arc bands provide descriptive tiers
- [x] Bands are derived (not stored state)
- [x] Backward compatibility for v0.1 saves
- [x] Demo script shows all v0.2 features
- [x] Engine internals unchanged
- [x] Deterministic behavior preserved

**Status**: ✅ All acceptance criteria met

---

## 7. Non-Invasive Integration (Verified)

### Campaign Mechanics v0.2 NEVER:
- ❌ Modifies spar_engine/*.py files
- ❌ Overrides severity sampling
- ❌ Alters cutoff logic
- ❌ Forces specific outcomes
- ❌ Auto-triggers faction actions

### Campaign Mechanics v0.2 MAY:
- ✅ Suggest tags based on scars/factions
- ✅ Suggest rarity_mode based on pressure
- ✅ Provide human-readable notes
- ✅ Track attention/disposition passively
- ✅ Add explicit scars from delta

---

## 8. Future Extensions (v0.3+)

### Not in v0.2 (Deferred)
- Scar remediation mechanics
- Faction AI or actions
- Auto-scar triggers
- Disposition auto-adjustment
- Campaign victory/failure states
- Faction diplomacy trees

### Design Constraints for Future
- Must preserve optional nature
- Must maintain pure functional design
- Must keep engine separation
- Must stay legible and inspectable

---

## 9. Comparison: v0.1 vs v0.2

| Feature | v0.1 | v0.2 |
|---------|------|------|
| Pressure tracking | ✅ | ✅ |
| Heat tracking | ✅ | ✅ |
| Scars | String set | Structured objects |
| Factions | ❌ | ✅ Attention + disposition |
| Long-arc bands | ❌ | ✅ Descriptive tiers |
| Backward compat | N/A | ✅ Loads v0.1 saves |
| Serialization | Basic | Full with version |

---

## 10. Testing Strategy

### v0.2 Testing
- **Gist test**: v0.2 demo script serves as comprehensive gist test
- **Integration**: Validates scar persistence, faction tracking, bands
- **Compatibility**: Demo shows v0.1 state can upgrade to v0.2

### Future Testing (v0.3+)
- Scar deduplication edge cases
- Faction cap enforcement
- Serialization roundtrip with all features
- Backward compatibility with multiple versions

---

## Related Documents

- `docs/REQUIREMENTS_campaign_mechanics_v0.1.md` - Original v0.1 design
- `docs/contract.md` - SiS Engine v0.1 Contract (unchanged)
- `docs/engineering_rules.md` - Implementation standards
- `examples/campaign_mechanics_v0.2_demo.py` - v0.2 demonstration
- `spar_campaign/` - Implementation modules

---

**Implementation Date**: 2025-12-25  
**Next Review**: After play validation of scars and factions
