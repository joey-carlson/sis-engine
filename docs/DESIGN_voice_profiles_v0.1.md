<!--
Version History:
- v0.1 (2025-12-28): Initial design specification for Voice Profiles as Spiral-native system
-->

# Voice Profiles: Spiral-Native Pressure Routing

**Version:** v0.1 (Draft)  
**Status:** Design + Scaffold Only  
**Target:** Loot Generator v1.1 (Events later)  
**Last Updated:** 2025-12-28

## Overview

Voice Profiles are campaign-level presets that bias which **Spiral pressure types** dominate when content is generated. They add narrative flavor and intent without introducing new mechanics or configuration surfaces.

**Core Principle:** Spirals are the organizing abstraction. Voice Profiles route pressure through different Spiral types, creating distinct campaign feels.

---

## What Are Spirals? (Disambiguation)

### Two Meanings of "Spiral" in SPAR

1. **Spiral of Revelation™** (SPAR RPG Core Framework)
   - The 8-step narrative structure: Awakening → Catalyst → Threshold → Confrontation → Abyss → Epiphany → Ascent → Transformation
   - Campaign-arc level storytelling tool
   - Trademarked concept from SPAR RPG

2. **Pressure Spirals** (Tool Engine Concept - THIS DOCUMENT)
   - Types of narrative pressure that accumulate and route through campaigns
   - Examples: Attention Spiral, Obligation Spiral, Dependency Spiral, Reputation Spiral
   - The "shape" of how consequences compound

**This document addresses Pressure Spirals (#2), not the Spiral of Revelation framework (#1).**

---

## Design Requirements

From Designer specification:

1. **Spiral-native:** Each profile emphasizes a Spiral pressure type
2. **Presets, not knobs:** Named options only (e.g., "Transactional", "Volatile")
3. **No engine changes:** Data models and documentation only
4. **Advisory only:** Like Campaign Context (suggests, never enforces)
5. **Campaign-level:** Applied at campaign creation/settings, not per-roll
6. **Zero GM cognitive load:** Named presets with clear intent

---

## Spiral Pressure Types

### Attention Spiral
**Pressure Pattern:** Visibility accumulates → more eyes watching → harder to operate quietly

**Manifests As:**
- Heat clock acceleration
- Visibility tag frequency
- Reinforcement likelihood
- Social friction from being known

**Campaign Feel:** "Every move is watched. Every mistake is recorded."

**Tag Bias Intent:**
- Increase: `visibility`, `heat`, `reinforcements`, `social_friction`
- Thematic: Being seen compounds; secrets become impossible

---

### Obligation Spiral
**Pressure Pattern:** Debts accumulate → creditors call in favors → autonomy erodes

**Manifests As:**
- Cost vector emphasis
- Social friction from expectations
- Time pressure from deadlines
- Opportunity tied to strings attached

**Campaign Feel:** "Nothing is free. Every gain comes with interest."

**Tag Bias Intent:**
- Increase: `cost`, `obligation` (via effect_vector), `social_friction`, `time_pressure`
- Thematic: Every resource borrowed becomes leverage against you

---

### Dependency Spiral
**Pressure Pattern:** Reliance on systems → systems fail → cascade vulnerability

**Manifests As:**
- Attrition acceleration
- Terrain/hazard complications
- Resource scarcity
- Gear failure frequency

**Campaign Feel:** "The infrastructure is crumbling. Nothing stays reliable."

**Tag Bias Intent:**
- Increase: `attrition`, `terrain`, `hazard`, `consequence`
- Thematic: Systems you depend on betray you

---

### Reputation Spiral
**Pressure Pattern:** Actions define identity → identity constrains options → prior choices haunt

**Manifests As:**
- Social friction dominance
- Information spread
- Faction disposition volatility
- Consequence emphasis

**Campaign Feel:** "The world remembers. Your past is always present."

**Tag Bias Intent:**
- Increase: `social_friction`, `information`, `consequence`, `visibility`
- Thematic: Every action reshapes how the world sees you

---

## Voice Profile Presets

### Transactional
**Spiral Emphasis:** Obligation (primary), Attention (secondary)  
**Campaign Intent:** "Everything has a price. Everyone keeps a ledger."

**Routing:**
- Obligation Spiral: 60%
- Attention Spiral: 30%
- Other: 10%

**Tag Bias (Advisory):**
- Heavy: `cost`, `obligation`, `opportunity`
- Moderate: `visibility`, `social_friction`
- Light: `information`

**Use Cases:**
- Noir detective campaigns
- Underworld/smuggler arcs
- Political intrigue
- Resource scarcity settings

---

### Volatile
**Spiral Emphasis:** Attention (primary), Dependency (secondary)  
**Campaign Intent:** "The world is watching. Nothing holds together."

**Routing:**
- Attention Spiral: 50%
- Dependency Spiral: 35%
- Other: 15%

**Tag Bias (Advisory):**
- Heavy: `visibility`, `heat`, `reinforcements`
- Moderate: `hazard`, `attrition`, `terrain`
- Light: `social_friction`

**Use Cases:**
- High-stakes heists
- Surveillance/espionage
- Collapsing infrastructure
- Hot pursuit scenarios

---

### Stabilizing
**Spiral Emphasis:** Reputation (primary), Obligation (secondary)  
**Campaign Intent:** "Build legitimacy. Manage consequences. Play the long game."

**Routing:**
- Reputation Spiral: 55%
- Obligation Spiral: 30%
- Other: 15%

**Tag Bias (Advisory):**
- Heavy: `social_friction`, `consequence`, `information`
- Moderate: `cost`, `opportunity`
- Light: `visibility`

**Use Cases:**
- Rebuilding campaigns
- Faction diplomacy
- Institutional reform
- Legacy-building arcs

---

### Erosion
**Spiral Emphasis:** Dependency (primary), Reputation (secondary)  
**Campaign Intent:** "Systems fail. Trust crumbles. Survive."

**Routing:**
- Dependency Spiral: 60%
- Reputation Spiral: 25%
- Other: 15%

**Tag Bias (Advisory):**
- Heavy: `attrition`, `terrain`, `hazard`, `consequence`
- Moderate: `cost`, `social_friction`
- Light: `opportunity`

**Use Cases:**
- Post-apocalyptic survival
- Decay/horror campaigns
- Collapsing civilization
- Resource depletion arcs

---

## Proposed Data Structure

### VoiceProfile Model (Immutable)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Literal

SpiralType = Literal["attention", "obligation", "dependency", "reputation"]

@dataclass(frozen=True)
class SpiralWeight:
    """Weight for a specific Spiral pressure type."""
    spiral_type: SpiralType
    weight: float  # 0.0-1.0, must sum to 1.0 across profile
    
@dataclass(frozen=True)  
class TagBias:
    """Advisory tag emphasis levels."""
    heavy: List[str]      # Strong emphasis
    moderate: List[str]   # Moderate emphasis
    light: List[str]      # Subtle emphasis

@dataclass(frozen=True)
class VoiceProfile:
    """Campaign-level preset for Spiral pressure routing.
    
    Voice Profiles are advisory, like Campaign Context. They suggest
    tag biases and Spiral emphasis but never hard-filter content.
    """
    profile_id: str           # e.g., "transactional"
    display_name: str         # e.g., "Transactional"
    description: str          # One-liner campaign intent
    spiral_weights: List[SpiralWeight]  # Distribution across Spiral types
    tag_bias: TagBias         # Advisory tag emphasis
    use_cases: List[str]      # Example campaign types
```

### Example: Transactional Profile

```python
VoiceProfile(
    profile_id="transactional",
    display_name="Transactional",
    description="Everything has a price. Everyone keeps a ledger.",
    spiral_weights=[
        SpiralWeight(spiral_type="obligation", weight=0.60),
        SpiralWeight(spiral_type="attention", weight=0.30),
        SpiralWeight(spiral_type="dependency", weight=0.05),
        SpiralWeight(spiral_type="reputation", weight=0.05),
    ],
    tag_bias=TagBias(
        heavy=["cost", "obligation", "opportunity"],
        moderate=["visibility", "social_friction"],
        light=["information"],
    ),
    use_cases=[
        "Noir detective campaigns",
        "Underworld/smuggler arcs", 
        "Political intrigue",
        "Resource scarcity settings",
    ],
)
```

---

## Integration Approach (Future)

### Loot Generator v1.1 Target

**No Engine Changes Required:**
- Voice Profile stored in CampaignState (optional field)
- Campaign Context computation reads profile
- Tag bias weights fed into existing selection logic
- Uses current adaptive weighting system

**Advisory Flow:**
```
VoiceProfile → ContextBundle → tag_bias_weights → weighted_choice()
                                                      ↓
                                                (existing engine)
```

**Key Design Decision:** Profile biases tags during selection, NOT severity sampling. SOC math remains untouched.

### Where It Lives

**Data Model Location:**
- `spar_campaign/models.py` - VoiceProfile dataclass
- `spar_campaign/campaign.py` - Profile application logic (pure function)

**Integration Location:**
- `streamlit_harness/campaign_context.py` - ContextBundle computation
- `streamlit_harness/campaign_ui.py` - Profile selection UI (future)

**Content Location:**
- `data/voice_profiles.json` - Profile definitions (future)

### Bias Weight Specification (Designer-Level Tuning)

**Magnitude Philosophy:**
- Bias weights must be **subtle but perceptible**
- Target: Noticeable over 1-2 sessions, not per-roll
- Range: 5-15% per tag level
- Compound effect when entries have multiple biased tags

**Approved Weight Multipliers:**

```python
# Tag bias multipliers (applied to entry base weight during selection)
BIAS_MULTIPLIERS = {
    "heavy": 1.15,    # 15% boost - strongest emphasis
    "moderate": 1.10, # 10% boost - noticeable accent
    "light": 1.05,    # 5% boost - subtle nudge
}
```

**Compounding Example:**
```
Entry with tags ["opportunity", "visibility", "cost"]
Profile: Transactional (heavy: opportunity/cost, moderate: visibility)

Base weight: 1.0
Voice weight: 1.0 × 1.15 (opportunity) × 1.15 (cost) × 1.10 (visibility)
            = 1.0 × 1.46 = 1.46

Result: 46% more likely to be selected than unbiased entry
```

**Rationale:**
- Single heavy tag: 15% boost (barely noticeable)
- Two heavy tags: 32% boost (starting to feel thematic)
- Three heavy tags: 52% boost (clearly emphasized)
- Variety preserved: unbiased entries still selected ~40% of time

**Anti-Pattern Guard:**
If >70% of generated results share the same tags, bias is too strong. Reduce multipliers.

### Integration Pattern (Future Implementation)

```python
# In campaign_context.py (future)
def compute_context_bundle(
    state: CampaignState,
    voice_profile: Optional[VoiceProfile] = None
) -> ContextBundle:
    # Existing severity weights from pressure
    severity_weights = calculate_severity_weights(state.pressure)
    
    # NEW: Tag bias from voice profile (subtle multipliers)
    tag_bias_weights = {}
    if voice_profile:
        for tag in voice_profile.tag_bias.heavy:
            tag_bias_weights[tag] = 1.15  # 15% boost
        for tag in voice_profile.tag_bias.moderate:
            tag_bias_weights[tag] = 1.10  # 10% boost
        for tag in voice_profile.tag_bias.light:
            tag_bias_weights[tag] = 1.05  # 5% boost
    
    return ContextBundle(
        # ... existing fields ...
        tag_bias_weights=tag_bias_weights,  # NEW field
    )
```

**No Generator Changes:**
- Loot generator already uses weighted_choice
- Tag bias weights apply during entry selection
- Falls back gracefully if profile absent
- Maintains deterministic behavior with seeds

---

## Mapping Examples

### Transactional → Loot Selection

**Spiral Routing:**
- 60% Obligation → Emphasize cost/strings-attached
- 30% Attention → Resources draw eyes
- 10% Other → Variety

**Tag Bias Application (Subtle Multipliers):**
```
Available loot entries after filtering: 10

Entry A: tags=["opportunity", "visibility"]
  Base weight: 1.0
  Voice weight: 1.0 × 1.15 (opportunity=heavy) × 1.10 (visibility=moderate)
             = 1.0 × 1.265 = 1.27
  
Entry B: tags=["information", "cost"]
  Base weight: 1.0
  Voice weight: 1.0 × 1.05 (information=light) × 1.15 (cost=heavy)
             = 1.0 × 1.208 = 1.21
  
Entry C: tags=["hazard", "terrain"]
  Base weight: 1.0
  Voice weight: 1.0 × 1.0 (no bias) = 1.0

Weighted selection slightly favors A > B > C
```

**Result:** Transactional campaigns see ~27% more opportunity-with-visibility loot, ~21% more cost-information loot. Hazards still appear but less frequently. Over 5-10 rolls, the Transactional feel emerges without dominating.

---

### Erosion → Event Selection

**Spiral Routing:**
- 60% Dependency → Systems fail
- 25% Reputation → Actions echo
- 15% Other

**Tag Bias Application (Subtle Multipliers):**
```
Available event entries: 15

"Gear Failure" [attrition, hazard]
  Base weight: 1.0
  Voice weight: 1.0 × 1.15 (attrition=heavy) × 1.15 (hazard=heavy)
             = 1.0 × 1.32 = 1.32
  
"Rival Interferes" [social_friction, reinforcements]
  Base weight: 1.0
  Voice weight: 1.0 × 1.10 (social_friction=moderate) × 1.0 (no bias)
             = 1.0 × 1.10 = 1.10
  
"Sudden Opening" [opportunity, positioning]
  Base weight: 1.0
  Voice weight: 1.0 × 1.05 (opportunity=light) × 1.0 (no bias)
             = 1.0 × 1.05 = 1.05

Weighted selection slightly favors Gear Failure > Rival > Opening
```

**Result:** Erosion campaigns see ~32% more system-failure events, ~10% more social complications. Opportunities still occur but less frequently. The campaign feels brittle and unreliable without monotony.

---

## Non-Goals (Explicit)

**This Design Phase Does NOT Include:**
- UI implementation
- Tuning logic or weight calculation
- New tags or mechanics
- Changes to existing content packs
- Modifications to SOC sampling
- Generator code changes
- Test implementation

**This Is:**
- Data structure proposal
- Conceptual framework
- Integration approach documentation
- Mapping examples for future implementation

---

## Integration with Existing Systems

### Relation to Campaign Context (Existing)

**Campaign Context (v1.0):**
- Derives severity weights from pressure
- Tracks recent events for cooldowns
- Includes faction dispositions

**Voice Profiles (Proposed):**
- Adds tag bias weights
- Routes Spiral pressure emphasis
- Complements (doesn't replace) context

**Combined Effect:**
```
Campaign → Context Bundle → Generator
          ↓
    Severity Weights (from pressure)
    Recent Events (for cooldowns)
    Faction Influence (existing)
    Tag Bias (from Voice Profile) ← NEW
```

### Relation to Rarity Mode (Existing)

**Rarity Mode:** Controls severity distribution shape (calm/normal/spiky)  
**Voice Profile:** Controls tag emphasis and Spiral routing

**Orthogonal Concepts:**
- Rarity = "How extreme are outcomes?"
- Voice = "What kind of pressure dominates?"

**Example:**
- Spiky + Transactional = Extreme obligations and costs
- Calm + Erosion = Gentle but relentless decay
- Normal + Volatile = Balanced but highly visible

---

## Alignment with SPAR Tool Engineering Rules

**Rule 00 - General Principles:**
✅ Design before implementation (this document)  
✅ Simple, inspectable system (presets, not knobs)  
✅ Alternatives considered (see rejected approaches below)

**Rule 01 - Documentation & Versioning:**
✅ Architecture separate from implementation  
✅ Version in header (v0.1), not filename  
✅ Historical decisions preserved

**Rule 02 - Core Engine Design:**
✅ System-agnostic (Spirals work for any RPG)  
✅ No mechanics, only situation emphasis  
✅ Advisory pattern maintained

**Rule 04 - Content & Adapters:**
✅ Profiles bias selection, not distributions  
✅ Content packs unchanged  
✅ Cutoff logic untouched

**Rule 08 - Collaboration Contract:**
✅ Flags risks: Tag bias could feel "samey" if over-tuned  
✅ Tradeoff: Flavor vs. variety must be balanced in implementation

---

## Rejected Approaches

### Approach 1: Per-Generator Configuration
**Why Rejected:** Violates "presets not knobs" requirement. Too much GM cognitive load.

### Approach 2: Content Pack Variants
**Why Rejected:** Explosion of content maintenance. Profiles should work across packs.

### Approach 3: Hard Filtering by Spiral Type
**Why Rejected:** Too restrictive. Advisory bias maintains variety while suggesting emphasis.

### Approach 4: Effect Vector Manipulation
**Why Rejected:** Changes generator behavior. Profiles should only influence selection.

---

## Implementation Checklist (Future Work)

When this design is approved and implementation begins:

### Phase 1: Data Models
- [ ] Add VoiceProfile, SpiralWeight, TagBias to `spar_campaign/models.py`
- [ ] Add `voice_profile: Optional[VoiceProfile]` to CampaignState
- [ ] Add serialization (to_dict/from_dict) for persistence
- [ ] Add migration logic for existing campaigns (default to None)

### Phase 2: Profile Definitions
- [ ] Create `data/voice_profiles.json` with 4 initial profiles
- [ ] Document profile selection guidance for GMs
- [ ] Add profiles to content pack templates/README

### Phase 3: Context Integration
- [ ] Add `tag_bias_weights: Dict[str, float]` to ContextBundle
- [ ] Update `compute_context_bundle()` to derive tag bias from profile
- [ ] Ensure graceful fallback when profile=None

### Phase 4: Generator Integration (Loot First)
- [ ] Modify weighted_choice in loot generator to apply tag bias
- [ ] Preserve deterministic behavior with seeds
- [ ] Add RNG trace entries for tag bias application
- [ ] Validate no SOC/cutoff changes

### Phase 5: Testing
- [ ] Unit tests for VoiceProfile model
- [ ] Tests for tag bias weight calculation
- [ ] Integration tests for loot generation with profiles
- [ ] Distribution sanity tests (variety preservation)

### Phase 6: UI (Optional)
- [ ] Add voice profile selector to campaign creation
- [ ] Add profile info display in dashboard
- [ ] Add profile override/disable in generator tab

---

## Designer Decisions (Locked for v0.1)

**From Designer Review 2025-12-28:**

1. **Spiral Type Coverage:** ✅ **4 Spiral types LOCKED**
   - Attention, Obligation, Dependency, Reputation are orthogonal and complete
   - Cover social, structural, informational, and identity pressure
   - Do not add more until real play exposes missing pressure vector

2. **Profile Count:** ✅ **4 presets LOCKED**
   - Transactional, Volatile, Stabilizing, Erosion provide wide tonal range
   - More than 4 increases choice anxiety
   - Add new presets only when real campaign can't be expressed with existing

3. **Tag Vocabulary Extension:** ❌ **NO new tags for v0.1 or v1.x**
   - Existing tags provide sufficient expressive power
   - Profiles must work by biasing existing tags only
   - Adding tags would fragment content and undermine backward compatibility
   - If Spiral can't be expressed, it's content phrasing issue not schema issue

4. **Event Generator Timing:** ✅ **Separately - Loot first, Events later**
   - Loot Generator v1.1: Introduce Voice Profiles
   - Event Generator: Follow after observing Loot in play
   - Learn tuning lessons from Loot before applying to Events

5. **Content Pack Interaction:** 🚫 **Not for v0.1 - Future consideration**
   - Packs express Spiral affinity implicitly via tags/phrasing
   - No explicit Spiral metadata on packs yet
   - Keeps authors focused on writing good situations
   - Revisit in v2.x if packs consistently fight selected profiles

---

## References

**Related Documents:**
- `docs/engineering_rules.md` - Design standards
- `docs/ARCH_campaign_integration.md` - Campaign integration patterns
- `docs/DATA_CONTRACT_story_vs_system_v0.1.md` - Story/system separation
- `SPAR RPG/SPAR_CoreRules_Section_4_Spiral_of_Revelation_v2.0.docx` - Spiral of Revelation framework

**Code Locations (Future):**
- `spar_campaign/models.py` - VoiceProfile dataclass
- `streamlit_harness/campaign_context.py` - Profile → tag bias logic
- `data/voice_profiles.json` - Profile definitions

---

**Design Version:** v0.1 (Draft)  
**Next Step:** Designer review and approval before implementation  
**Maintainer:** SPAR Tool Engine Team
