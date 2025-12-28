# Data Contract: Story-Facing vs System-Facing (v0.1)

**Version**: 0.1  
**Created**: 2025-12-26  
**Status**: Foundation Document  

## Purpose

This contract defines which campaign and session data fields serve **narrative purposes** (GM/player readable) versus **system purposes** (internal metrics, reproducibility, tuning).

Establishing this separation prevents:
- Debug dumps appearing in story exports
- Operational metrics cluttering narrative records
- Conflation of "what happened" with "how the simulation processed it"

This contract enables multiple "views" over the same underlying truth:
- **Story View**: Campaign history for GMs and players
- **System View**: Diagnostics and tuning data
- **Ledger**: Stores both, exports choose a lens

## Design Principle

**Test**: If you'd feel weird reading it out loud to your gaming group, it's not story-facing.

---

## Story-Facing Data

### Definition
Data that serves narrative memory and campaign continuity.

### Purpose
- Remember what happened
- Understand what is true now
- Track unresolved narrative threads
- Support GM prep and player recap

### Characteristics
- Human language prose
- Curated and edited
- Interpretable months/years later
- Independent of simulation internals
- Can be read aloud without explanation

### Fields and Components

#### Canon Summary
- **Field**: `canon_summary` (List[str])
- **Content**: 8-12 curated bullets describing current world state
- **Update Trigger**: Opt-in during session finalization
- **Example**: `"The station's security grid was compromised during the heist"`

#### Session Narrative
- **Field**: `what_happened` (List[str])
- **Content**: N event/outcome bullets per session
- **Update Trigger**: GM entry during finalization
- **Example**: `"Crew infiltrated cargo bay under cover of maintenance shift"`

#### Manual Entries
- **Fields**: `manual_entries[].title`, `.description`, `.notes`
- **Content**: GM-authored events, improvisations, notable moments
- **Format**: Structured but narrative (not metrics)
- **Example**: 
  ```
  Title: "Unexpected Alliance"
  Description: "Station chief offered intel in exchange for crew's silence"
  Notes: "Player diplomacy roll was critical success"
  ```

#### Session Notes
- **Field**: `session_notes` (Optional[str])
- **Content**: Freeform GM observations, context, table atmosphere
- **Example**: `"Players were very engaged with the moral dilemma here"`

#### Open Threads
- **Field**: Not yet implemented in ledger (future)
- **Content**: Unresolved plot hooks, unanswered questions
- **Example**: `"Who tipped off the rival crew about the heist?"`

#### Narrative Consequences
- **Expressed As**: Prose descriptions of faction/scar outcomes
- **Not As**: Numeric deltas or flag states
- **Example**: `"Mercenary Guild now actively seeking the crew"` (not "attention: +2")

### Excluded from Story-Facing
- Severity numbers
- Cutoff flags/resolutions
- RNG seeds
- Statistical summaries
- Internal tags (unless narratively meaningful)
- Pressure/heat as numbers (bands OK: "volatile", "hunted")
- Distribution parameters

---

## System-Facing Data

### Definition
Data that serves simulation operation, reproducibility, and tuning.

### Purpose
- Drive future generation
- Track pressure and attention
- Maintain determinism and testability
- Enable balance tuning
- Support debugging diagnostics

### Characteristics
- Structured
- Numeric
- Diagnostic
- Often ephemeral (severity) or persistent (seeds)
- Requires domain knowledge to interpret

### Fields and Components

#### Severity
- **Field**: `metadata.severity_avg`, `manual_entries[].severity`
- **Content**: Event intensity measure (1-10 scale)
- **Purpose**: Drives pressure increases, cutoff risk, generator bias
- **Lifecycle**: Important when it happens, then fades
- **Storage**: Keep in JSON for diagnostics, hide from story exports
- **Example**: `severity_avg: 6.2` (drives mechanics, not shown to GM as story)

#### Cutoff Tracking
- **Field**: `metadata.cutoff_rate`
- **Content**: Percentage of events that were cutoff-resolved
- **Purpose**: System health metric, balance verification
- **Example**: `cutoff_rate: 0.25`

#### Pressure & Heat Deltas
- **Fields**: `deltas.pressure_change`, `deltas.heat_change`
- **Content**: Numeric state adjustments
- **Purpose**: Campaign state tracking, bands drive generator
- **Note**: Bands ("volatile", "hunted") can be story-relevant, raw numbers are not
- **Example**: `pressure_change: +3` (system), `"campaign now volatile"` (story)

#### Tags
- **Field**: `metadata.top_tags`, `manual_entries[].tags`
- **Content**: Internal classification tokens
- **Purpose**: Generator filtering, pattern analysis
- **Visibility**: Diagnostic view only, not story exports
- **Example**: `["hazard", "reinforcements", "positioning"]`

#### Source Metadata
- **Fields**: `metadata.scenario_name`, `.seed`, `active_sources[]`
- **Content**: Which content packs, presets, RNG seeds generated events
- **Purpose**: Reproducibility, content attribution
- **Example**: `scenario_name: "Event Generator", seed: 42`

#### Prep Item References
- **Field**: `metadata.prep_item_ids[]`
- **Content**: IDs of prep items used in session
- **Purpose**: Track prep → canon flow, archive management
- **Example**: `["prep_20251226_001439680017_0"]`

#### Determinism Keys
- **Fields**: `session_id`, `entry_id`
- **Content**: Unique identifiers for ledger stability
- **Purpose**: Prevent duplicates, enable stable references
- **Example**: `session_id: "session_20251226_144410"`

#### Peak Severity Tracking
- **Field**: `campaign_state.highest_severity_seen`
- **Content**: Highest session severity encountered
- **Purpose**: Campaign intensity tracking, dashboard metric
- **Example**: `highest_severity_seen: 8`

#### Generator Diagnostics
- **Fields**: Future — scenario validation results, distribution checks
- **Content**: Test pass/fail, distribution verification, engine health
- **Purpose**: Tuning, regression detection

### Excluded from System-Facing
- Prose descriptions
- GM observations
- Player reactions
- Narrative interpretation
- Canon summary bullets

---

## Separation Rules

### Rule 1: Ledger Stores Both
The campaign ledger (JSON) contains both story-facing and system-facing fields. This enables:
- Full reproducibility (system data preserved)
- Rich exports (story data available)
- Multiple views (choose lens per export)

### Rule 2: Default Exports Choose Story Lens
Campaign history exports and web story views should default to story-facing data only.

System data available via:
- Diagnostic exports (opt-in)
- Collapsed "Session Statistics" appendices
- Separate analytics reports

### Rule 3: Editing Happens Story-Side
The Finalize Session workflow primarily edits story-facing fields:
- What Happened bullets (GM review)
- Manual entry text (GM curation)
- Session notes (GM reflection)
- Canon Summary updates (opt-in)

System-facing fields auto-generated or minimally adjusted (pressure/heat sliders).

### Rule 4: System Data Never Required for Story
A campaign history export must be readable and useful even if:
- Severity metadata missing
- Source attributions unknown
- Tags absent
- Deltas zero

Story quality depends on GM curation, not system completeness.

### Rule 5: Story Data Never Required for System
The engine and campaign mechanics must function even if:
- Canon Summary empty or stub
- Session notes absent
- Manual entries not provided

System quality depends on operational metrics, not narrative richness.

### Rule 6: System-Facing Never Leaks Into Narrative
System-facing data should never appear in narrative exports unless explicitly requested via diagnostic mode or collapsed appendices.

---

## Example Ledger Entry

### Complete Entry (Stores Both)

```json
{
  "session_id": "session_20251226_144410",
  "session_number": 5,
  "session_date": "2025-12-26T14:44:10.134035",
  
  // STORY-FACING DATA
  "what_happened": [
    "Crew infiltrated cargo bay during shift change",
    "Security chief confronted them but offered deal",
    "Intel acquired about rival gang's next move"
  ],
  "session_notes": "Players were very engaged with moral choices. The deal with security chief was improvised.",
  "manual_entries": [
    {
      "entry_id": "manual_20251226_144229285468",
      "title": "Unexpected Alliance",
      "description": "Station security chief (NPC: Chen) offered crew intel in exchange for silence about corruption. Players debated for 20 minutes before accepting.",
      "notes": "This could become major faction relationship later"
    }
  ],
  
  // SYSTEM-FACING DATA
  "metadata": {
    "severity_avg": 6.2,
    "cutoff_rate": 0.15,
    "top_tags": ["social", "information", "faction_shift"],
    "scenario_name": "Event Generator",
    "prep_item_ids": ["prep_20251226_020750023892_0"]
  },
  "deltas": {
    "pressure_change": 2,
    "heat_change": -1,
    "rumor_spread": false,
    "faction_attention_change": true
  },
  "active_sources": ["core_complications"],
  "active_source_ids": ["source_builtin_001"]
}
```

### Story Export (Narrative Lens)

```markdown
### Session 5 — 2025-12-26

**What Happened:**
- Crew infiltrated cargo bay during shift change
- Security chief confronted them but offered deal
- Intel acquired about rival gang's next move

**Manual Entries & GM Notes:**

#### Unexpected Alliance

**Description**: Station security chief (NPC: Chen) offered crew intel in exchange for silence about corruption. Players debated for 20 minutes before accepting.

**GM Notes**: This could become major faction relationship later

**Session Notes:**

Players were very engaged with moral choices. The deal with security chief was improvised.
```

### System Export (Diagnostic Lens, Opt-In)

```markdown
### Session 5 — Diagnostics

**System Metadata:**
- Severity Avg: 6.2
- Cutoff Rate: 15%
- Top Tags: social, information, faction_shift
- Scenario: Event Generator
- Sources: core_complications

**State Deltas:**
- Pressure: +2 (now volatile band)
- Heat: -1 (remains hunted band)
- Faction attention increased

**Reproducibility:**
- Session ID: session_20251226_144410
- Prep Items Used: 1
```

---

## Migration Notes

### Existing Campaigns
- Old ledger entries without `session_id`: Auto-generate on first load or leave as legacy
- Sessions without story/system separation: Treat all fields as "both" until re-exported
- Canon summaries with pollution: Manual cleanup recommended (tool can't infer intent)

### Future Sessions
- All new sessions get `session_id`
- Story fields populated during Finalize Session
- System fields auto-filled from generator output
- Exports apply appropriate lens

---

## Versioning

**v0.1 (2025-12-26)**: Initial contract definition  
- Story-facing: canon_summary, what_happened, manual_entries, session_notes
- System-facing: severity, cutoff_rate, tags, deltas, sources, IDs
- Rules: ledger stores both, exports choose lens, editing is story-side

**Future versions** may:
- Add open_threads to story-facing
- Define web view data structure
- Specify API contract for external consumers
- Add faction/scar narrative descriptions to story-facing

---

## Implementation Guidance

### For Export Code
When generating campaign/session exports:

1. Check export type (story vs diagnostic)
2. Filter fields by contract definition
3. Format story fields as prose
4. Collapse or omit system fields in story view
5. For diagnostic view, include full system context

### For UI Code
When building Finalize Session form:

1. Story fields get text inputs, editors
2. System fields get numeric sliders, checkboxes
3. Story section comes first (primary workflow)
4. System section collapsed or "Advanced"
5. Helpful labels distinguish purposes

### For Future Features
When adding new ledger fields:

1. Classify as story OR system OR both
2. Document in this contract
3. Update export logic accordingly
4. Test that separation is maintained

---

## Relationship to Severity

### Critical Clarification
**Severity is fundamentally system-facing**.

### What Severity Is
- Momentary pressure signal
- Input to simulation (drives pressure, cutoff risk, future generation)
- Intensity of situational instability
- **Not** narrative importance or story quality

### What Severity Is Not
- Story quality measure
- Plot significance rating
- Player enjoyment metric
- Canon-worthiness indicator

### Where Severity Appears
- **System exports**: Full numeric data
- **JSON ledger**: Preserved for reproducibility
- **Diagnostic views**: With other metrics
- **Session Statistics**: Collapsed appendix only

### Where Severity Does NOT Appear
- Canon Summary bullets
- "What Happened" narrative
- Default campaign history exports
- Player-facing recaps
- Web story views

### Severity's Effects (Story-Visible Outcomes)
High severity events **may** create story-visible consequences:
- Scars (mechanical lasting effects)
- Faction attention shifts
- Pressure band changes (stable → volatile)
- Heat band changes (quiet → hunted)

But the severity number itself remains internal.

**Example of Correct Usage**:
- ❌ Don't export: "Event severity: 8/10"
- ✅ Do export: "Security compromised, emergency lockdowns in effect" (the consequence)

---

## Classification Test

### Story-Facing Test
Answer YES to all:
- Can a GM read it months later and remember/understand?
- Would it make sense read aloud at the table?
- Does it describe the fiction, not the process?
- Is it independent of how SPAR works internally?

### System-Facing Test
Answer YES to any:
- Does it feed engine calculations?
- Is it needed for deterministic replay?
- Would changing it alter future generation?
- Does it require understanding SiS's implementation?

If a field serves both, store in ledger but choose appropriate lens for each export type.

---

## Complete Field Classification

### Story-Facing Fields
| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `canon_summary` | List[str] | Current world state | "Station defenses compromised" |
| `what_happened` | List[str] | Session events | "Crew escaped via maintenance tunnels" |
| `manual_entries[].title` | str | Event label | "Unexpected Betrayal" |
| `manual_entries[].description` | str | Event narrative | "NPC Chen revealed their true allegiance" |
| `manual_entries[].notes` | Optional[str] | GM context | "This surprised everyone at the table" |
| `session_notes` | Optional[str] | Session observations | "Great session, players loved the twist" |

### System-Facing Fields
| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `session_id` | str | Unique identifier | "session_20251226_144410" |
| `metadata.severity_avg` | float | Intensity metric | 6.2 |
| `metadata.cutoff_rate` | float | Resolution metric | 0.15 |
| `metadata.top_tags` | List[str] | Classification | ["social", "information"] |
| `metadata.scenario_name` | str | Generator source | "Event Generator" |
| `metadata.prep_item_ids` | List[str] | Prep tracking | ["prep_001"] |
| `deltas.pressure_change` | int | State adjustment | +2 |
| `deltas.heat_change` | int | State adjustment | -1 |
| `deltas.rumor_spread` | bool | Flag | true |
| `deltas.faction_attention_change` | bool | Flag | true |
| `active_sources` | List[str] | Content attribution | ["core_complications"] |
| `active_source_ids` | List[str] | Source IDs | ["source_001"] |
| `manual_entries[].severity` | Optional[int] | Intensity | 7 |
| `manual_entries[].tags` | List[str] | Classification | ["combat", "surprise"] |
| `manual_entries[].pressure_delta` | Optional[int] | State impact | +1 |
| `manual_entries[].heat_delta` | Optional[int] | State impact | -1 |

### Hybrid Fields (Context-Dependent)
| Field | Story Use | System Use |
|-------|-----------|------------|
| `session_number` | Display label | Ordering (with session_id) |
| `session_date` | Timestamp for GM | Chronological ordering |
| `manual_entries[].related_factions` | Can be narrative | Can be system tracking |
| `manual_entries[].related_scars` | Can be narrative | Can be system tracking |

---

## Maintenance

This contract should be updated when:
- New ledger fields added
- Export types change
- Separation violations discovered
- Community feedback identifies edge cases

All updates should:
- Increment version number
- Document rationale
- Update examples
- Verify no export code contradicts contract

---

## References

- **Campaign UI**: `streamlit_harness/campaign_ui.py`
- **Session Packet**: `streamlit_harness/session_packet.py` 
- **Export Logic**: Campaign history and session markdown generation
- **Campaign State**: `spar_campaign/models.py` (CampaignState structure)

---

## Future Work (Out of Scope for v0.1)

1. **Web Story View**: HTML/Markdown template optimized for reading, not diagnosis
2. **Narrative Faction Descriptions**: Replace "attention: 15/20" with "actively hunting the crew"
3. **Open Threads Tracking**: Explicit ledger field for unresolved hooks
4. **Canon Curation Heuristics**: Smarter synthesis from session bullets
5. **Generator Lexicon Integration**: Campaign-specific terminology in generated content

---

## Appendix: Philosophy

### Why This Matters

Games create two parallel records:
1. **The Story**: What fictionally happened in the world
2. **The Process**: How the game mechanics resolved it

SiS is a tool that generates The Process (events, complications, pressure).  
The GM and players create The Story (how they responded, what it meant).

The ledger must store both because:
- Process enables reproducibility and tuning
- Story enables memory and continuity

But exports must choose because:
- GMs don't think in severity numbers when remembering sessions
- Debug output isn't campaign lore
- Mixing layers makes neither useful

### The Read-Aloud Test

If you can't read something aloud at your game table without needing to explain SiS's internal mechanics, it's system-facing.

**System-facing**: "Severity 7.2, cutoff rate 0.3, pressure +4"  
**Story-facing**: "The ambush forced a desperate retreat. Guards are now actively searching."

### Separation Enables Multiple Views

Once separated, you can create:
- **GM Story Export**: Clean narrative for long-term campaign record
- **Player Recap**: Simplified "what happened" without GM secrets
- **Web Campaign Page**: Beautiful story presentation
- **Diagnostic Dashboard**: Full system metrics for tuning
- **Reproducibility Log**: All seeds/sources/IDs for deterministic replay

All from the same underlying ledger, just choosing different lenses.

---

## Parking Lot Items (Post-Contract)

These depend on this contract being established:

1. **Campaign story web view design**: Story-facing rendering layer for web presentation
2. **Canon Summary curation heuristics**: Post-separation quality improvements
3. **Generator richness pass**: Campaign lexicon → generator output specificity
4. **Faction narrative descriptions**: Replace metrics with prose in exports
5. **Open threads system**: Explicit tracking of unresolved hooks
