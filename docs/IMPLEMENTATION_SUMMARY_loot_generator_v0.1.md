# Implementation Summary: Loot Generator v0.1

**Date:** 2025-12-26  
**Status:** Complete  
**Version:** 0.1

---

## Overview

Implemented Loot Generator as a narrative resource shock system using the same SOC foundation as event generation. Loot represents resource discoveries that relieve pressure temporarily while creating new obligations, attention, or vulnerability.

**Core Philosophy:** *"You gained something — now the world reacts."*

---

## What Was Implemented

### 1. Loot Generation Engine (`spar_engine/loot.py`)

**Function:** `generate_loot(scene, state, selection, entries, rng) -> EngineEvent`

**Pipeline (Identical to Event Generator):**
```
Campaign State
   ↓
Distribution (heavy-tail SOC)
   ↓
Cutoff / Constraint
   ↓
Outcome (Loot Situation)
```

**Key Features:**
- Reuses 100% of SOC infrastructure (filtering, severity sampling, cutoff, adaptive weighting)
- No new models or types (uses `ContentEntry` → `EngineEvent`)
- Deterministic with seed
- Respects cooldowns and recent ID tracking
- Integrates with existing campaign state

**Loot-Specific Cutoff Overlays:**
- **Omen:** "Omen of Wealth: You sense valuable resources nearby..."
- **Clock Tick:** "Contested Resource: Multiple parties move toward the same resource..."
- **Downshift:** "Modest Gain: The resource is present but less valuable than hoped..."

### 2. Core Loot Content Pack (`data/core_loot_situations.json`)

**Contains:** 15 narrative resource shock situations

**Design Principles:**
- Every entry implies **tradeoffs, not just gains**
- Emphasis on **opportunity + consequence** vectors
- Negative cost values (pressure relief)
- Obligation/visibility/social_friction tags (world reacts)

**Example Situations:**
- "Concealed Stockpile" - supplies that ease shortages but draw attention when moved
- "Artifact of Interest" - unknown relic that powerful factions will want
- "Sudden Windfall" - gain that creates expectations
- "Leverage Material" - evidence that gives power but makes you a target

**Tag Distribution:**
- Primary: `opportunity` (all entries)
- Consequence: `obligation`, `visibility`, `social_friction`
- Impact: `information`, `positioning`, `cost`, `time_pressure`

### 3. UI Integration (`streamlit_harness/app.py`)

**Generator Type Selector:**
```
⚔️ Event | 💰 Loot
```
Located in sidebar for context-aware control hiding.

**Behavior:**
- Radio button switches between event/loot generation
- Loot automatically loads `data/core_loot_situations.json`
- Falls back to event pack if loot pack unavailable

**Domain-Correct Controls:**

**When Generator = Event (shown):**
- Scene Setup (preset, phase)
- Constraint sliders (in Advanced)
- Tick mechanics (in Advanced)
- Filters, rarity, diagnostics

**When Generator = Loot (hidden):**
- ❌ Scene Setup (not tactical positioning)
- ❌ Constraint sliders (not movement physics)
- ✓ Rarity mode (SOC applies)
- ✓ Filters (tag filtering valid)
- ✓ Diagnostics (same analysis)

**Loot Context Strip:**
Appears when Generator = Loot, derived from campaign state:
- **No campaign:** "Standalone loot generation..."
- **With campaign:** "Resource shock influenced by campaign state..."
- **With factions:** Adds "Current interests: [Faction1], [Faction2]"
- **High pressure/heat:** Adds "Acquisition likely to be noticed or contested"

**Internal Loot Defaults (Stable):**
- Phase: "aftermath" (not user-configurable)
- Environment: "derelict" (neutral)
- Constraints: neutral (0.5, 0.5, 0.5)
- Scene ID: "loot_harness"

**Prep Queue Integration:**
- Loot → Prep Queue (same as events)
- Can mix loot and events in same queue
- Commit via Finalize Session workflow
- Same 50-item cap applies

---

## Design Constraints Met

### Constraint: Loot is Not Items ✓
Every loot situation presents **tradeoffs and consequences**, not stat blocks:
- "Moving it will be noticed"
- "But their source will be missed"
- "Using it will create enemies or debts"
- "Their silence isn't free"

### Constraint: No New Mechanics ✓
- Uses existing SOC pipeline
- Uses existing models (`ContentEntry`, `EngineEvent`)
- Uses existing vectors (opportunity, heat, cost, etc.)
- Uses existing tags (no new vocabulary)
- Integrates with existing Prep Queue → Canon flow

### Constraint: No Inventory System ✓
Loot never:
- Tracks quantities
- Creates equipment lists
- Manages currency
- Auto-applies to character sheets
- Requires new UI panels

### Constraint: System-Agnostic ✓
All loot situations use neutral language:
- "Tools or gear that enable new approaches"
- "Fungible resources that ease immediate needs"
- "Permission to move through contested ground"

No genre-specific nouns or game system references.

---

## Technical Architecture

### Shared Generator Pattern

Both generators follow identical structure:
1. **Filter** candidates by environment/phase/tags/cooldowns
2. **Sample** severity using SOC (alpha parameter)
3. **Apply** cutoff based on cap
4. **Select** entry matching severity band
5. **Weight** by recency (adaptive anti-repetition)
6. **Roll** effects from template
7. **Derive** state delta
8. **Return** `EngineEvent`

**Code Reuse:** ~95% of loot.py logic mirrors engine.py patterns

### State Integration

Loot affects campaign state through:
- **Heat clock** (if visible/obligated, severity ≥ 5)
- **Recent IDs** (prevents immediate repetition)
- **Tag cooldowns** (prevents loot spam)
- **Followups** (contested resources, wealth omens)

No loot-specific state fields needed.

---

## Testing

### Automated Tests (13 new tests)
```
✓ test_loot_pack_loads - Verify pack loads
✓ test_loot_generation_basic - Valid output structure
✓ test_loot_soc_pipeline - SOC severity distribution
✓ test_loot_cutoff_mechanics - Cutoff system works
✓ test_loot_state_delta - State changes valid
✓ test_loot_cooldowns - Cooldown mechanics work
✓ test_loot_deterministic - Same seed = same output
✓ test_loot_effects_have_opportunity - Opportunity emphasis
✓ test_loot_negative_cost - Pressure relief present
✓ test_loot_consequence_tags - Consequence tags included
✓ test_loot_no_content_error - Graceful content exhaustion
✓ test_loot_adaptive_weighting - Recency penalties work
✓ test_loot_followups - Cutoff followups generate
```

### Full Suite Results
**184/184 tests passing** (171 original + 13 loot)

### Manual Testing Verified
- Loot generator accessible via radio button
- Loads loot pack on demand
- Generates loot situations with consequences
- Mixes with events in unified prep queue
- Commits through same finalization flow
- Diagnostics show loot distribution

---

## Files Modified

**New Files:**
- `spar_engine/loot.py` - Loot generation engine
- `data/core_loot_situations.json` - Core loot content pack (15 situations)
- `tests/test_loot_generation.py` - Comprehensive test coverage

**Modified Files:**
- `streamlit_harness/app.py` - Added generator type selector and routing

**No Changes To:**
- Campaign mechanics
- Story/system data contract
- Export templates
- Existing event generator
- Core engine math

---

## Content Quality

### Relief + Consequence Pattern

Every loot situation follows the formula:
**Immediate Relief + Future Tension**

Examples:
- Medical supplies (cost: -2) BUT "their source will be missed" (heat risk)
- Liquid assets (opportunity: +5) BUT "spending creates patterns" (visibility)
- Witness cooperation (heat: -2) BUT "their silence isn't free" (obligation)

### Negative Vectors (Pressure Relief)

7 entries have negative cost ranges:
- Medical Supplies: cost [-2, -1]
- Sudden Windfall: cost [-2, -1]
- Specialized Equipment: cost [-1, 0]
- Temporary Shelter: cost [-1, 0]
- Liquid Assets: cost [-2, -1]
- Patron's Interest: cost [-2, -1]
- Safe Passage: cost [-1, 0]
- Witness Cooperation: heat [-2, -1] (only negative heat!)

This enables actual pressure reduction, not just new problems.

---

## User Journey

### Discovery
1. User navigates to Event Generator
2. Sees "⚔️ Event | 💰 Loot" radio selector
3. Clicks "💰 Loot"

### Generation
4. Clicks "Generate 1" or "Generate 10"
5. Loot pack loads automatically
6. Loot situations appear with:
   - Opportunity-focused effects
   - Consequence warnings in fiction
   - Tradeoff choices

### Integration
7. Loot appears in same event list
8. Can mix loot and events
9. Send to Prep Queue (same workflow)
10. Commit via Finalize Session

### Outcome
11. Loot provides resource relief
12. But creates obligations/attention/vulnerability
13. World reacts to acquisition

---

## Design Philosophy Achieved

### "Resource Shock, Not Reward Table" ✓
- No stat blocks
- No equipment lists
- No genre-specific items
- Every gain has narrative cost

### "Situations, Not Outcomes" ✓
Loot presents choices:
- "Take it all now and risk attention" vs "Take only what you can carry quietly"
- "Accept the patronage" vs "Maintain independence"
- "Use it immediately" vs "Hold for critical moment"

### "Consequences Compound" ✓
Tags explicitly encode future complications:
- `obligation` - debts owed
- `visibility` - attention drawn
- `social_friction` - relationships strained
- `heat` - exposure increased

---

## SOC Fidelity

Loot respects all SOC principles:
- **Heavy-tail distribution** (spiky mode produces variance)
- **Cutoff conversion** (extreme values → story beats)
- **Adaptive weighting** (prevents repetition)
- **State-dependent** (cooldowns, recency, campaign context)
- **Deterministic** (same seed = same output)

No shortcuts or exceptions.

---

## Acceptance Criteria

All criteria met:
- ✅ Loot generates using SOC logic
- ✅ Output feels narrative, not mechanical
- ✅ Campaign context and faction influence apply
- ✅ Loot stages and commits like events
- ✅ No new mechanics or knobs introduced
- ✅ Existing workflows unchanged
- ✅ All tests pass (184/184)

---

## Out of Scope (Achieved)

Successfully avoided:
- ❌ Item stats
- ❌ Equipment lists
- ❌ Currency tracking
- ❌ Automatic loot application
- ❌ Market simulation
- ❌ Genre-specific loot vocab
- ❌ Player-facing inventories

---

## Future Considerations

**Thematic Loot Packs** (Post-v0.1):
- Frontier survival loot
- Urban intrigue loot
- Political leverage loot

**Loot → Event Chaining** (Post-v0.1):
- "You took the relic" → "Factions hunt for it"
- "You called in the favor" → "They expect reciprocation"

**Campaign-Specific Loot** (Post-v0.1):
- Faction-tied resources
- Scar-related opportunities

All future work remains additive.

---

## Lessons Learned

1. **Shared infrastructure pays dividends** - 95% code reuse from event generator
2. **Same models work** - No need for `LootEvent` or `LootEntry` types
3. **Consequences > rewards** - "Relief + tension" formula works narratively
4. **Negative vectors essential** - Actual pressure reduction requires negative cost/heat
5. **Prep Queue unifies** - Events and loot mixing naturally in same queue proves the design

---

## Metrics

**Code Added:**
- `spar_engine/loot.py`: 230 lines
- `data/core_loot_situations.json`: 15 entries
- `tests/test_loot_generation.py`: 13 tests
- `streamlit_harness/app.py`: ~20 lines modified

**Code Reused:**
- SOC sampling: 100%
- Cutoff system: 100%
- Filtering logic: 100%
- State delta: 100%
- Adaptive weighting: 100%

**Test Coverage:**
- 184/184 tests passing
- +13 loot-specific tests
- 0 regressions

---

## Next Steps

Loot Generator v0.1 is production-ready.

**Roadmap Options:**
1. Thematic loot packs (extend ecosystem)
2. System adapters (D&D, GURPS integration)
3. Advanced campaign mechanics

All depend on v0.1 foundation established here.

---

## Designer Intent

**Mission: "Make resource discoveries feel like problems you want."**

✅ Achieved. Loot creates immediate relief and future tension simultaneously. The "resource shock" framing prevents inventory bloat while maintaining narrative pressure.

The decision to reuse `EngineEvent` and `ContentEntry` was correct - loot is just another situation type, not a separate system.
