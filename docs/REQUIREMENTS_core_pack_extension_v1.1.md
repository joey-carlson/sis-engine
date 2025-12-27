# Core Complications Pack Extension v1.1 - Requirements

**Date**: 2025-12-26  
**Status**: In Progress  
**Goal**: Expand core_complications.json from 35 to 60-80 entries

## Objective

Increase content density to reduce repetition and improve perceived system intelligence without adding new mechanics, tags, or complexity.

## Scope

**What This Is:**
- Content-only expansion
- Richer phrasing of existing situation types
- Better phase distribution (especially Aftermath)
- More texture, not more knobs

**What This Is Not:**
- New mechanics
- New tags or effect vectors
- Genre-specific content
- Filler entries that don't create tension

## Target Distribution

**Current State (35 entries):**
- Approach: ~10 entries
- Engage: ~15 entries
- Aftermath: ~15 entries (recently expanded)

**Target State (60-80 entries):**
- Approach: 15-20 entries (+5-10)
- Engage: 25 entries (+10)
- Aftermath: 25-30 entries (+10-15)

Aftermath gets disproportionate attention because it's still the thinnest phase and needs the most variety.

## Content Authoring Guidelines v1.0

### 1. Every Entry Is a Situation, Not a Fact

❌ Bad: "A patrol approaches."  
✅ Good: "A patrol is approaching sooner than expected, and avoiding them will require leaving something behind."

The entry should force a choice or reveal a tradeoff.

### 2. Always Imply Consequences

Every entry should answer:
- What happens if the PCs act?
- What happens if they don't?

This can be implicit in the phrasing.

### 3. Prefer Pressure Over Damage

Good entries:
- Increase tension
- Limit options
- Expose tradeoffs

Avoid:
- Pure HP loss
- Binary success/failure
- Deterministic outcomes

### 4. Tags Are Signals, Not Labels

Tags reflect **why this matters**, not **what it is**.

Examples:
- `visibility` → someone notices, exposure increases
- `obligation` → someone expects repayment
- `scarcity` → future options shrink

Don't over-tag. 2-4 tags per entry is ideal.

### 5. Write for Reuse

Avoid:
- Specific names ("Duke Varen")
- Fixed factions ("The Empire")
- Unique artifacts ("The Crystal of Souls")

Instead:
- Describe roles: "local authority," "rival crew," "desperate supplier"
- Let campaign context supply specificity

### 6. Tone Before Genre

Write entries so they work for:
- Fantasy (magic, medieval)
- Sci-fi (tech, space)
- Noir (urban, corruption)
- Modern (contemporary)
- Horror (dread, isolation)

Tone comes from phrasing and rhythm, not nouns.

Example: "Someone with their own agenda moves to complicate yours"
- Works in any setting
- Creates immediate tension
- Scales with context

### 7. Severity Reflects Instability, Not Importance

**High severity (7-10):**
- Compresses decision time
- Risks cascading fallout
- Forces immediate response

**Medium severity (4-6):**
- Complicates existing plans
- Introduces new pressures
- Requires adjustment

**Low severity (1-3):**
- Adds texture
- Shifts positioning
- Seeds future complications

Severity is **operational pressure**, not narrative importance.

### 8. Immediate Choices Should Be Meaningful

Good choices:
- Both have clear costs
- Neither is obviously "correct"
- Context determines which matters

Bad choices:
- One is clearly superior
- Both lead to same outcome
- Disconnected from situation

### 9. Test: "Would This Feel Repetitive Twice?"

Good entries scale with context:
- "Someone interferes" reads differently when it's a rival faction vs neutral party
- "Routes change" matters more when you're hunted vs exploring

Bad entries resolve too cleanly:
- "You find a hidden passage" (one-time discovery)
- "The boss appears" (only works once)

### 10. Sensory Details Over Exposition

❌ "The enemy is getting closer and you're running out of time."  
✅ "Boots echo closer, your breathing gets loud, timing slips."

Show pressure through sensory details, not explanation.

## Existing Tag Vocabulary (Do Not Expand)

```
hazard, reinforcements, time_pressure, social_friction, visibility, 
mystic, mystic_flux, attrition, terrain, positioning, opportunity, 
information, threat, cost, heat, obligation, consequence
```

All new entries must use these existing tags only.

## Existing Effect Vectors (Do Not Expand)

```
threat, cost, heat, time_pressure, position_shift, information, opportunity
```

All new entries must use these existing effect vectors only.

## Quality Bar

Each new entry must:
1. Force a choice or reveal a tradeoff
2. Work across multiple genres/settings
3. Scale with campaign context (factions, scars, pressure)
4. Use sensory details to convey pressure
5. Imply consequences without spelling them out
6. Follow existing tag/effect/severity conventions exactly

## Anti-Patterns to Avoid

❌ **Generic obstacles**: "A door is locked"  
✅ **Situations with stakes**: "A sealed door, but forcing it will be loud"

❌ **Binary success**: "Make a skill check"  
✅ **Pressure choices**: "Fast and noticed, or slow and vulnerable"

❌ **Filler content**: "You see something interesting"  
✅ **Immediate tension**: "Someone else saw it too, and they're moving"

❌ **Over-explanation**: "This is dangerous because..."  
✅ **Sensory pressure**: "Metal groans, dust shifts, timing matters"

## Testing Criteria

Before considering Phase 1 complete:
- [ ] 60-80 total entries in core_complications.json
- [ ] Aftermath phase has 25-30 entries (vs current 15)
- [ ] All new entries follow authoring guidelines
- [ ] No new tags, vectors, or mechanics introduced
- [ ] All tests still passing (no engine changes)
- [ ] Entries feel varied when generated in 50+ event batches
- [ ] Setting-neutral tone preserved throughout

## Next Phase Gate

Only proceed to Phase 2 (Loot Generator) when:
- Core pack feels dense enough that repetition is rare
- Aftermath phase feels as rich as Engage
- Events chain naturally into resource stress
- Content quality remains consistent at scale

## References

- Current pack: `data/core_complications.json`
- Content design notes: `data/aftermath_expansion_design.md`
- Content authoring guidelines: This document, Section "Content Authoring Guidelines v1.0"
