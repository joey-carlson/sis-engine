<!--
Version History:
- v0.1 (2025-12-28): Initial requirements for Event Patterns + Variants system
-->

# Event Patterns with Authored Variants v0.1

**Status:** Requirements  
**Target:** Event Generator v2.0  
**Dependencies:** Voice Profiles v0.1 (design), SOC Foundation (Rule 00)  
**Last Updated:** 2025-12-28

---

## Problem Statement

**GM Use Case:**
> "I want to generate 25-50 events for campaign planning, select 5-8 for upcoming sessions, and keep the rest as backup. I need variety without duplicates, and the batch must follow the SOC curve."

**Current Limitation:**
- Core complications pack: 107 entries
- At batch size 50, statistical probability of seeing same event multiple times
- Cooldowns help but aren't designed for large planning batches
- Content growth by raw addition (200+ entries) creates maintenance burden

**Design Constraint:**
> Multiplicative variety through structure, not linear volume growth.

---

## Solution Architecture

### Event Patterns with Authored Variants

**Core Concept:**
- **Pattern:** Semantic root concept (e.g., "Authority Intervenes")
- **Variant:** Fully authored execution of that pattern (e.g., "soft intervention", "public intervention")

**NOT Mad Libs:**
- Each variant is complete prose with its own tags/severity/fiction
- No runtime text assembly
- No sentence splicing or adjective swaps

**Multiplicative Effect:**
- 30 patterns × 3 variants = 90 distinct outcomes
- 120 entries (current) can feel like 400+ with patterns

---

## Design Requirements

### 1. Pattern Structure (Content Schema)

**Pattern Definition:**
```json
{
  "pattern_id": "authority_intervenes",
  "pattern_name": "Authority Intervenes",
  "description": "Officials insert themselves into the situation",
  "variants": [
    {
      "variant_id": "soft_intervention",
      "event_id": "authority_intervenes_soft",
      "title": "Questions and Permits",
      "tags": ["social_friction", "time_pressure", "information"],
      "severity_band": [1, 3],
      "weight": 1.0,
      "fiction_prompt": "...",
      "fiction_sensory": ["..."],
      "fiction_choices": ["..."],
      "spiral_emphasis": ["obligation", "attention"]
    },
    {
      "variant_id": "public_intervention",
      "event_id": "authority_intervenes_public",
      "title": "Public Attention",
      "tags": ["visibility", "heat", "social_friction"],
      "severity_band": [3, 5],
      "weight": 1.0,
      "fiction_prompt": "...",
      "spiral_emphasis": ["attention", "reputation"]
    },
    // ... more variants
  ]
}
```

**Key Properties:**
- `pattern_id`: Groups related variants
- `variant_id`: Unique within pattern
- `event_id`: Globally unique (pattern_variant format)
- `spiral_emphasis`: NEW field - which Pressure Spirals this variant feeds
- All existing ContentEntry fields preserved

### 2. Backward Compatibility

**Migration Path:**
- Existing events without patterns continue to work
- Treated as "pattern with single variant" implicitly
- No breaking changes to v1.0 content format
- Pattern-based content is additive enhancement

**Generator Behavior:**
- If `pattern_id` absent → traditional event
- If `pattern_id` present → pattern-aware selection

### 3. Batch Diversity Constraints (SOC-Safe)

**Applied at batch generation time, NOT to underlying probabilities:**

**Uniqueness Rules:**
```python
# Hard constraint
- No duplicate variant IDs in single batch

# Soft constraint (configurable)
- Max 2 variants from same pattern per batch (default)
- Can be adjusted based on batch size
```

**Representation Targets (Advisory):**
```python
# For batch size 25-50, aim for:
- Severity spread: 60% low (1-3), 30% mid (4-6), 10% high (7-10)
- Spiral coverage: Each Spiral type appears at least 15% of batch
- Phase balance: If multi-phase, each phase >= 20% of batch
```

**SOC Validation:**
- Global severity distribution unchanged
- Batch constraints only remove local redundancy
- "Shaping sample for human use, not changing physics"

### 4. Batch Variety Analytics (Mandatory UI Component)

**Location:** Event Generator tab, after batch generation

**UI Pattern:**
```
[Event Results: 50 generated]

▼ Batch Analysis (click to expand)

Severity Distribution:
  Low (1-3):     32 events (64%)  [SOC target: 60-70%]
  Medium (4-6):  14 events (28%)  [SOC target: 25-35%]
  High (7-10):    4 events (8%)   [SOC target: 5-10%]
  ✓ SOC curve maintained

Pattern Diversity:
  Distinct patterns: 28 of 50 events (56%)
  Variants per pattern: 1.79 average
  ✓ High variety (target: >50%)

Spiral Coverage:
  Attention:     14 events (28%)
  Obligation:    16 events (32%)
  Dependency:    12 events (24%)
  Reputation:     8 events (16%)
  ✓ Balanced representation

Phase Balance:
  Approach:      18 events (36%)
  Engage:        20 events (40%)
  Aftermath:     12 events (24%)

Uniqueness:
  ✓ No duplicate variants
  ✓ Pattern cap respected (max 2/pattern)
```

**Collapsed by Default:**
- Doesn't clutter normal generation workflow
- Expandable for GM planning, content authoring, diagnostics

**Read-Only:**
- No knobs or sliders
- Pure observability
- Builds trust through transparency

---

## Schema Changes

### ContentEntry Enhancement (Backward Compatible)

```python
@dataclass(frozen=True)
class ContentEntry:
    event_id: str  # Globally unique
    title: str
    tags: List[str]
    # ... existing fields ...
    
    # NEW fields (optional, backward compatible)
    pattern_id: Optional[str] = None           # Groups related variants
    variant_id: Optional[str] = None           # Unique within pattern
    spiral_emphasis: List[str] = field(default_factory=list)  # Pressure Spiral types
```

**Spiral Emphasis Values:**
- `"attention"`, `"obligation"`, `"dependency"`, `"reputation"`
- Connects to Voice Profiles (but usable without them)
- Content authors can tag which Spirals each variant feeds

### Pattern Metadata (Optional, for Analytics)

```python
@dataclass(frozen=True)
class EventPattern:
    """Metadata for an event pattern (grouping only, not required for generation)."""
    pattern_id: str
    pattern_name: str
    description: str
    variant_count: int
```

**Used For:**
- Batch analytics display
- Content pack validation
- Pattern coverage reports

**Not Used For:**
- Generation logic (variants are independent entries)
- Filtering or weighting

---

## Implementation Phases

### Phase 1: Schema + Model Updates

**Files:**
- `spar_engine/models.py` - Add pattern_id, variant_id, spiral_emphasis fields
- `spar_engine/content.py` - Pattern-aware loading (optional parsing)

**Changes:**
- Extend ContentEntry dataclass (frozen, backward compatible)
- Add validation for pattern/variant relationships
- Update pack loading to accept new fields

**Tests:**
- Content loading with patterns
- Backward compatibility with v1.0 packs
- Validation of pattern/variant uniqueness

### Phase 2: Batch Diversity Logic

**Files:**
- `streamlit_harness/app.py` - Enhance run_batch() function

**Changes:**
- Track variant IDs during batch generation
- Enforce no-duplicate-variants rule
- Apply soft pattern cap (configurable)
- Add Spiral/severity/phase representation checks

**Implementation Pattern:**
```python
def run_batch_with_diversity(
    count: int,
    # ... existing params ...
    max_variants_per_pattern: int = 2,
    enforce_diversity: bool = True
) -> List[EngineEvent]:
    """Generate batch with diversity constraints.
    
    Applies batch-level uniqueness without changing SOC probabilities.
    """
    seen_variant_ids = set()
    pattern_counts = {}
    results = []
    
    for i in range(count):
        # Generate using existing SOC logic
        event = generate_event(...)
        
        # Check diversity constraints
        if enforce_diversity:
            # Skip if duplicate variant
            if event.variant_id in seen_variant_ids:
                continue  # Regenerate
            
            # Check pattern cap
            if event.pattern_id:
                if pattern_counts.get(event.pattern_id, 0) >= max_variants_per_pattern:
                    continue  # Regenerate
        
        # Accept event
        seen_variant_ids.add(event.variant_id or event.event_id)
        if event.pattern_id:
            pattern_counts[event.pattern_id] = pattern_counts.get(event.pattern_id, 0) + 1
        results.append(event)
    
    return results
```

**SOC Safety:**
- Rejection sampling only (no probability manipulation)
- SOC distribution over full run remains unchanged
- Only local redundancy removed

**Tests:**
- No duplicates in batch
- Pattern cap enforcement
- SOC distribution maintained across multiple batches
- Variety metrics meet targets

### Phase 3: Batch Analytics UI

**Files:**
- `streamlit_harness/app.py` - Add analytics panel after batch display

**UI Implementation:**
```python
with st.expander("📊 Batch Analysis", expanded=False):
    # Severity distribution (reuse existing diagnostics)
    show_severity_histogram(events)
    
    # NEW: Pattern diversity metrics
    st.subheader("Pattern Diversity")
    pattern_stats = compute_pattern_diversity(events)
    st.metric("Distinct Patterns", pattern_stats["distinct_patterns"])
    st.metric("Variants per Pattern", f"{pattern_stats['avg_variants']:.2f}")
    
    # NEW: Spiral coverage
    st.subheader("Spiral Coverage")
    spiral_counts = compute_spiral_coverage(events)
    for spiral, count in spiral_counts.items():
        pct = (count / len(events)) * 100
        st.metric(spiral.title(), f"{count} events ({pct:.0f}%)")
    
    # NEW: Phase balance
    st.subheader("Phase Balance")
    phase_counts = compute_phase_balance(events)
    # ... display phase distribution
    
    # NEW: Uniqueness confirmation
    st.subheader("Uniqueness")
    if has_duplicates(events):
        st.warning("⚠️ Duplicate variants detected")
    else:
        st.success("✓ No duplicate variants")
```

**Collapsed by Default:**
- Normal GM workflow: just see events
- Planning workflow: expand to verify variety
- Content authoring: expand to check coverage

**Tests:**
- Analytics calculations accurate
- UI renders without errors
- Metrics update correctly per batch

### Phase 4: Content Refactoring (Iterative)

**Process:**
1. Identify high-value events that naturally have variants
2. Refactor into pattern + 2-4 variants
3. Each variant fully authored (complete ContentEntry)
4. Tag with spiral_emphasis
5. Test in batch generation

**Target Coverage:**
- Start with 10-15 patterns (30-50 variants)
- Focus on events that currently feel "samey"
- Prioritize high-frequency tags (social_friction, visibility, reinforcements)

**Quality Gates:**
- Each variant must feel distinct
- Variants must serve different Spirals or phases
- No Mad Libs or forced variation
- If variant feels artificial, keep as single event

---

## SOC Compliance Validation

**Rule 00 Checklist:**

✅ **Pressure accumulates implicitly**
- Patterns don't add pressure, just structure existing events

✅ **Release remains uneven**
- SOC severity sampling unchanged
- Variants selected using same weighted_choice
- Heavy-tail distribution preserved

✅ **Big outcomes feel earned**
- Patterns don't trigger guaranteed results
- Variants still subject to severity bands and cutoffs
- Critical events still rare and emergent

✅ **No explicit tuning knobs**
- Pattern cap is internal constraint, not GM dial
- Batch diversity is automatic, not configurable
- Analytics are read-only observability

✅ **Non-local effects preserved**
- Variants can feed different Spirals
- Consequence cascades still non-linear
- Campaign context still advisory

**Critical Tests:**
- "Does this add pressure or explain pressure?" → **Explains** (structures existing variety)
- "Does this bias inputs or control outputs?" → **Biases inputs** (variant selection)
- "Is this reshaping surface or changing gravity?" → **Reshaping surface**

---

## Integration with Existing Systems

### With Voice Profiles (Synergistic)

**Voice Profiles + Patterns:**
- Voice Profile biases tag selection
- Patterns provide multiple variants with different tags
- Result: Profile influences which variants are likely, not which patterns exist

**Example:**
- Pattern: "Authority Intervenes"
- Variants: soft (obligation), public (attention), covert (dependency), delegated (reputation)
- Voice Profile "Transactional" → slightly favors "soft" and "delegated" variants
- All variants remain possible, just probability-shifted

### With Campaign Context

**Campaign Context + Patterns:**
- Pressure/heat influence severity sampling
- Faction presence influences tag selection
- Patterns provide variants aligned with different faction types

**Example:**
- High heat → favors high-severity variants
- Faction present + Attention Spiral → favors visibility-tagged variants
- Pattern provides the options, context selects among them

### With Content Packs

**Multi-Pack + Patterns:**
- Patterns can span multiple packs
- Some packs might provide additional variants for core patterns
- Pack discovery remains unchanged

**Example:**
- Core pack: "Authority Intervenes" with 3 variants
- Urban Intrigue pack: Adds 2 more variants for same pattern
- Combined: 5 variants for richer urban campaigns

---

## Content Authoring Guidelines

### Pattern Identification

**Good Candidates for Patterns:**
- Events that logically have multiple execution modes
- Situations where tone/scope/Spiral emphasis varies
- High-frequency outcomes that currently feel repetitive

**Bad Candidates:**
- Unique, one-off dramatic moments
- Events with very specific prerequisites
- Situations that don't naturally vary

### Variant Creation Rules

**Each Variant Must:**
1. Stand alone as complete event
2. Share pattern's semantic root
3. Serve distinct Spiral emphasis
4. Have different severity band or tag focus
5. Feel intentionally authored, not mechanically derived

**Quality Test:**
> "Could I use these two variants in the same session and have them feel like different events?"

If yes → good pattern. If no → keep as single event.

### Spiral Emphasis Tagging

**Guidelines:**
- Tag 1-2 primary Spirals per variant
- Attention: visibility, heat, reinforcements
- Obligation: cost, opportunity, social_friction
- Dependency: attrition, terrain, hazard
- Reputation: consequence, information, social_friction

**Example:**
```json
{
  "variant_id": "covert_intervention",
  "spiral_emphasis": ["dependency", "attention"],
  "tags": ["information", "visibility", "positioning"]
}
```

---

## Batch Diversity Specification

### Hard Constraints (Always Enforced)

**No Duplicate Variants:**
- Same variant_id cannot appear twice in single batch
- Applies regardless of batch size

**Implementation:**
- Track seen_variant_ids during generation
- Skip and regenerate if duplicate detected
- Max retry attempts: 3× batch size (prevents infinite loops)

### Soft Constraints (Configurable Defaults)

**Pattern Cap:**
- Default: Max 2 variants per pattern per batch
- Rationale: Prevents "all Authority Intervenes, different flavors"
- Adjustable based on batch size:
  - Batch 10-25: max 1 variant/pattern
  - Batch 25-50: max 2 variants/pattern
  - Batch 50+: max 3 variants/pattern

**Representation Targets (Advisory):**
```python
DIVERSITY_TARGETS = {
    "severity": {
        "low": (0.60, 0.70),   # 60-70% of batch
        "mid": (0.25, 0.35),   # 25-35% of batch
        "high": (0.05, 0.10),  # 5-10% of batch
    },
    "spiral": {
        "min_per_spiral": 0.15,  # Each Spiral >= 15% of batch
    },
    "phase": {
        "min_per_phase": 0.20,   # Each phase >= 20% if multi-phase
    }
}
```

**Enforcement Strategy:**
- Check representation after every 10 events
- If target missed, temporarily boost underrepresented categories
- Boost is subtle (1.1-1.2× multiplier, not hard filter)
- SOC distribution still governs majority of selections

---

## Analytics Specification

### Batch Analysis Panel (Expandable)

**Location:** Event Generator tab, after event cards  
**Default State:** Collapsed  
**Access:** One-click expand

**Sections:**

**1. SOC Distribution (Existing, Enhanced)**
- Severity histogram with target bands overlaid
- Pass/fail indicator for SOC curve adherence

**2. Pattern Diversity (NEW)**
```
Distinct Patterns: 28 of 50 events (56%)
Variants per Pattern: 1.79 average
Pattern Cap: 2 variants/pattern (0 violations)

Status: ✓ High variety (target: >50%)
```

**3. Spiral Coverage (NEW)**
```
Attention Spiral:    14 events (28%)
Obligation Spiral:   16 events (32%)
Dependency Spiral:   12 events (24%)
Reputation Spiral:    8 events (16%)

Status: ✓ Balanced (each >= 15%)
```

**4. Phase Balance (NEW)**
```
Approach:   18 events (36%)
Engage:     20 events (40%)
Aftermath:  12 events (24%)

Status: ✓ Balanced (each >= 20%)
```

**5. Uniqueness Confirmation (NEW)**
```
✓ No duplicate variants
✓ Pattern cap respected
✓ Ready for GM curation
```

### Diagnostic vs Planning Mode

**Diagnostic Mode (Current):**
- Shows weights, probabilities, cutoff rates
- Developer/designer focused
- Helps tune content

**Planning Mode (NEW - This Feature):**
- Shows variety, coverage, uniqueness
- GM focused
- Builds confidence for planning workflow

**Both Valid:**
- Not replacing diagnostics
- Adding GM-relevant analytics
- Different audiences, different information

---

## Implementation Checklist

### Phase 1: Data Model & Schema
- [ ] Add pattern_id, variant_id, spiral_emphasis to ContentEntry
- [ ] Update content loader to parse pattern structure
- [ ] Add EventPattern metadata class (optional)
- [ ] Ensure backward compatibility with v1.0 format
- [ ] Unit tests for schema validation

### Phase 2: Batch Diversity Logic
- [ ] Implement uniqueness tracking in run_batch()
- [ ] Add pattern cap enforcement
- [ ] Add representation target boosting (subtle)
- [ ] Add retry logic with fallback
- [ ] Integration tests for diversity constraints

### Phase 3: Analytics UI
- [ ] Create batch_analytics.py helper module
- [ ] Implement pattern diversity calculation
- [ ] Implement Spiral coverage calculation
- [ ] Implement phase balance calculation
- [ ] Add expandable analytics panel to UI
- [ ] Tests for analytics calculations

### Phase 4: Content Refactoring
- [ ] Audit existing events for pattern candidates
- [ ] Refactor 10-15 high-value events into patterns
- [ ] Author 2-4 variants per pattern (30-50 new variants)
- [ ] Tag with spiral_emphasis
- [ ] Validate batch generation with patterns
- [ ] Update content pack templates/README

---

## Success Metrics

**Functional:**
- ✅ Batch of 50 generates with 0 duplicate variants
- ✅ Pattern diversity >50% (at least 25 distinct patterns)
- ✅ SOC curve maintained (measured via existing tests)
- ✅ Each Spiral represented >=15% of batch

**Subjective:**
- ✅ GM reports: "50-event batch feels varied and usable"
- ✅ Content authors: "Variants feel intentional, not procedural"
- ✅ Playtests: "Events don't feel samey across sessions"

**Performance:**
- ✅ Batch generation <5 seconds for 50 events
- ✅ No infinite loops or retry exhaustion

---

## Non-Goals (Explicit)

**This Feature Does NOT:**
- Introduce Mad Libs or procedural text assembly
- Change SOC severity sampling
- Add GM-facing configuration knobs
- Require rewriting existing v1.0 content
- Make patterns mandatory (backward compatible)
- Alter cutoff behavior
- Expose pattern structure to GM during play (internal only)

---

## Risks & Mitigations

### Risk 1: Variants Feel Forced
**Mitigation:** Quality gate - if variant doesn't feel distinct, keep as single event

### Risk 2: Pattern Cap Too Restrictive
**Mitigation:** Start conservative (max 2), adjust based on real batch testing

### Risk 3: Retry Logic Infinite Loops
**Mitigation:** Hard cap on retry attempts (3× batch size), graceful degradation

### Risk 4: Analytics Clutter UI
**Mitigation:** Collapsed by default, one-click expand, clean visual hierarchy

### Risk 5: Breaking SOC Distribution
**Mitigation:** Run distribution sanity tests before/after, maintain 191/191 passing

---

## Future Extensions (Parked)

### Consequence Overlays (v0.2)
- Authored consequence paths that don't rewrite prose
- Selected based on campaign context or Voice Profile
- Integrates with patterns naturally

### Cross-Pack Pattern Expansion (v0.3)
- Packs can contribute variants to existing patterns
- Enables community content to extend core patterns
- Requires provenance tracking

### Pattern-Aware Cooldowns (v0.4)
- Cooldown entire pattern vs individual variants
- Prevents "pattern fatigue" in long campaigns
- Needs playtesting to validate value

---

## References

**Related Documents:**
- `docs/engineering_rules.md` Rule 00 - SOC Foundation
- `docs/DESIGN_voice_profiles_v0.1.md` - Spiral emphasis integration
- `docs/ARCH_campaign_integration.md` - Campaign context patterns
- `docs/templates/README.md` - Content authoring guidelines

**Code Locations:**
- `spar_engine/models.py` - ContentEntry with pattern fields
- `spar_engine/content.py` - Pattern-aware loading
- `streamlit_harness/app.py` - Batch diversity + analytics

---

**Requirements Version:** v0.1 (Draft)  
**Next Step:** Designer review, then implementation  
**Maintainer:** SPAR Tool Engine Team
