# Content Pack Templates

**Version:** 1.0  
**Purpose:** Help users create high-quality custom content packs

These templates show **recommended patterns, not hard limits**. Use them as starting points and adapt to your needs.

---

## What is a Content Pack?

Content packs add **situations, not rules**.

Each pack contributes new narrative problems the generator can draw from, using the same tags and mechanics as the core system. **Packs change the voice of play, not how the engine works.**

You don't need to understand the engine to write a pack.

---

## Pack Structure (New in v1.0)

Content packs use an **object format with metadata** at the top level:

```json
{
  "name": "My Custom Pack",
  "generator_type": "event",
  "description": "Brief description of pack's theme",
  "entries": [
    { ... entry 1 ... },
    { ... entry 2 ... }
  ]
}
```

**Legacy format (array) is still supported** for backward compatibility, but new packs should use the object format.

### Pack Metadata Fields

**`name`** (string, required)  
Display name for the pack. Used in campaign UI and diagnostics.

**`generator_type`** (string, required)  
Specifies which generator(s) can use this pack:
- `"event"` - Standard complications (approach/engage/aftermath)
- `"loot"` - Resource gains with consequences
- `"rumor"` - Future: rumor/reputation content
- `"npc"` - Future: NPC encounter content

**Important:** Set the correct generator_type to ensure your pack appears in the right context. Event packs won't be used by the loot generator, and vice versa.

**`description`** (string, required)  
1-2 sentence description of the pack's theme or focus. Shows in campaign UI to help GMs understand the pack's content.

**`entries`** (array, required)  
Array of situation/event entries. See "Field Reference" section below for entry structure.

---

## Available Templates

### Template A: Minimal Pack (`minimal_pack_template.json`)
**For:** Quick manual authoring  
**Generator Type:** Event (modify for loot/rumor/npc as needed)  
**Contains:** 3-5 example entries with inline guidance  
**Best for:** GMs who just want to add custom situations for their campaign

### Template B: Thematic Pack (`thematic_pack_template.json`)
**For:** Creating coherent thematic voices  
**Generator Type:** Event (shows event pack best practices)  
**Contains:** 10 entries showing "Urban Decay" theme with phase balance  
**Best for:** Authors creating setting-specific content (frontier, political intrigue, etc.)

### Template C: LLM-Assisted Pack (`llm_assisted_pack_template.json`)
**For:** Using LLMs safely  
**Generator Type:** Event (includes loot pack prompting guidance)  
**Contains:** Same as thematic + explicit prompting guidance for event and loot packs  
**Best for:** Authors who want to use AI assistance without breaking the system

---

## Pack Metadata vs Entry Fields

Content packs now have **two levels of structure**:
1. **Pack metadata** (top-level: name, generator_type, description)
2. **Entry fields** (inside the entries array)

The sections below describe **entry fields only**. Pack metadata is covered in "Pack Structure" above.

---

## Entry Field Reference

### Required Entry Fields

**`event_id`** (string)  
Unique identifier for this entry. Use format: `yourpack_phase_descriptor_01`

**`title`** (string)  
Short situation title (3-6 words). Focus on the complication, not the resolution.

**`tags`** (array of strings)  
Tags from the allowed vocabulary only. See "Allowed Tags" section below.

**`allowed_environments`** (array of strings)  
Where this situation can occur: `confined`, `populated`, `open`, `derelict`, `industrial`, `sea`, `planar`

**`allowed_scene_phases`** (array of strings)  
When this situation can occur: `approach`, `engage`, `aftermath`

**`severity_band`** (array of 2 integers)  
`[min, max]` severity range (1-10). **Severity measures instability, not importance.**
- 1-3: Minor complications
- 4-6: Moderate pressure
- 7-10: High stakes

**`weight`** (float)  
Selection probability modifier (0.5 = rare, 1.0 = normal, 1.5 = common)

**`cooldown`** (object)  
```json
{
  "event": 2,           // This specific event can't repeat for N turns
  "tags": {
    "hazard": 2,        // Tag cooldowns prevent similar situations
    "time_pressure": 1
  }
}
```

**`effect_vector_template`** (object)  
Numeric impact ranges `[min, max]` for each dimension. Common vectors:
- `threat` - danger level
- `cost` - resource/effort expenditure
- `heat` - attention/exposure
- `time_pressure` - urgency increase
- `position_shift` - tactical repositioning
- `information` - knowledge gained/lost
- `opportunity` - advantage/option creation

**`fiction`** (object)  
```json
{
  "prompt": "What happens - focus on consequences not resolution",
  "sensory": ["what they see", "what they hear"],
  "immediate_choice": [
    "Option that accepts the cost",
    "Option that changes the situation"
  ]
}
```

### Optional Fields

**`_template_notes`** (string)  
Non-runtime field for your own notes. Engine ignores fields starting with `_`.

**`_theme_guidance`**, **`_llm_prompt_guidance`**, etc.  
Any field starting with `_` is ignored by the engine - use for documentation.

---

## Allowed Tags

**Use only these tags** (from core pack vocabulary):

**Complications:**
- `hazard` - environmental dangers
- `reinforcements` - incoming forces/help
- `time_pressure` - urgency/deadlines
- `social_friction` - interpersonal/political complications
- `visibility` - exposure/observation
- `attrition` - wear/fatigue/depletion
- `terrain` - physical space complications
- `positioning` - tactical placement
- `mystic` - supernatural/unexplained elements

**Opportunities:**
- `opportunity` - advantages/openings
- `information` - knowledge/intel
- `cost` - resource decisions

**Outcomes:**
- `consequence` - lasting effects
- `obligation` - debts/commitments
- `heat` - attention/exposure (also vector)
- `threat` - danger (also vector)

**Special:**
- `mystic_flux` - supernatural instability (use with `mystic`)

Do not invent new tags. Work within the existing vocabulary.

---

## Writing Good Entries

### Do ✓
- **Present situations** - "Smoke fills the space"
- **Imply consequences** - "exits become unclear"
- **Force choices** - "push through or find another route"
- **Use neutral language** - "someone moves to block you"
- **Think reusable** - works in multiple campaigns

### Don't ✗
- **Resolve situations** - "you defeat the enemy"
- **Include mechanics** - "roll DEX check"
- **Name things** - "The Orc Chieftain"
- **Use genre nouns** - "photon torpedoes", "mana crystals"
- **Dump lore** - multi-paragraph backstories

### Severity Guidelines

Severity measures **instability**, not importance:

- **Low (1-3):** Inconvenience, minor complication, easily managed
- **Medium (4-6):** Pressure, costs require decisions, changes trajectory
- **High (7-10):** Crisis, forces major adaptation, lasting impact

High severity ≠ "this is important narratively"  
High severity = "this destabilizes the current situation significantly"

---

## Phase Balance

Good packs distribute entries across phases:

**Approach** (20-30%): Information gathering, positioning, preparation  
**Engage** (40-60%): Active complications, immediate threats, contested resources  
**Aftermath** (20-30%): Consequences, revelations, lingering effects

This isn't a hard rule - adjust for your theme. But avoid:
- All-engage packs (no breathing room)
- All-aftermath packs (no immediate pressure)

---

## Using LLMs Safely

**LLMs are best used as writing assistants, not system designers.**

### Safe Usage Pattern

1. **Give the LLM constraints explicitly** (see Template C)
2. **Review every entry** - LLMs will try to invent mechanics
3. **Remove:**
   - New tags
   - Resolution text
   - Genre-specific nouns
   - Mechanical instructions
4. **Verify tone consistency** across entries

### Example Prompt (from Template C)

"Generate 10 narrative situation entries for a tabletop RPG event generator. Each entry must be a situation that forces a choice and implies consequences. Use only these tags: [list]. Use only these environments: [list]. Do not invent new mechanics, tags, or rules. Do not include genre-specific nouns. Focus on consequences not resolution. Use neutral phrasing."

### Common LLM Mistakes

❌ **Inventing tags:** `"magic_surge"`, `"critical_hit"`  
✓ **Use existing:** `"mystic"`, `"threat"`

❌ **Genre-locked:** "The dragon appears"  
✓ **Neutral:** "A massive presence blocks the route"

❌ **Resolution:** "You win the fight"  
✓ **Situation:** "The fight turns in your favor, but at cost"

❌ **Mechanics:** "Roll initiative"  
✓ **Fiction:** "Timing becomes critical"

---

## Anti-Patterns to Avoid

### Urgency Creep
Don't make every entry high-severity or high-urgency. Players need breathing room.

**Bad pack:** 12 entries, all severity 7-10, all have `time_pressure`  
**Good pack:** Mix of 1-4 (complications), 4-7 (pressure), 7-10 (crisis)

### Genre Lock
Don't tie situations to specific settings unless the pack is explicitly genre-bound.

**Bad:** "The spaceship's reactor overloads"  
**Good:** "A critical power system becomes unstable"

### Resolution Text
Don't tell players what happens - present the choice and imply consequences.

**Bad:** "You fight the guards and escape"  
**Good:** "Guards move to block the exit, time to decide"

### Mechanical Instructions
Don't include game system instructions or stat blocks.

**Bad:** "Make a DC 15 Athletics check"  
**Good:** "The climb is more difficult than it appeared"

---

## Testing Your Pack

1. **Place your JSON file in** `data/` directory
2. **Enable it** in a campaign's Content Packs section
3. **Run a test batch** in Event Generator (50 events recommended)
4. **Check diagnostics** for:
   - Tag diversity (not clustering on one tag)
   - Severity distribution (mix of low/medium/high)
   - Cutoff rate (should be 20-40%, not 0% or 80%+)

---

## Quick Start Guide

### Option 1: Manual Authoring (Fast)
1. Copy `minimal_pack_template.json`
2. Rename it (e.g., `my_campaign_pack.json`)
3. Edit the 3 example entries
4. Add more entries using the same structure
5. Save to `data/` directory
6. Enable in your campaign

### Option 2: Thematic Pack (Best Practice)
1. Copy `thematic_pack_template.json`
2. Define your theme in `_theme_guidance` field
3. Write 8-12 entries maintaining tone consistency
4. Balance across approach/engage/aftermath phases
5. Test and refine

### Option 3: LLM-Assisted (Guardrailed)
1. Copy `llm_assisted_pack_template.json`
2. Use the suggested prompt with your LLM
3. **Review every entry carefully**
4. Remove genre-specific nouns
5. Verify tags/environments/phases are from allowed lists
6. Test for tone consistency

---

## Support & Resources

**Available Tags:** See "Allowed Tags" section above  
**Example Pack:** `data/core_complications.json` (reference implementation)  
**Phase Meanings:**
- Approach: Before the main event
- Engage: During the main event  
- Aftermath: After the main event

**Questions?** Test your pack with Event Generator diagnostics to validate behavior.

---

**Remember:** Content packs grow the ecosystem. Focus on situations that:
- Force interesting choices
- Imply consequences
- Work across multiple campaigns
- Maintain tone consistency

Good luck creating!
