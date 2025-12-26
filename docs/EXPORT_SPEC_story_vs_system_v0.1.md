# Export Specification: Story vs System Views (v0.1)

**Version**: 0.1  
**Created**: 2025-12-26  
**Status**: Template Specification  
**Depends On**: DATA_CONTRACT_story_vs_system_v0.1.md

## Purpose

This specification defines the structure and content of campaign and session exports following the story-facing vs system-facing separation established in the data contract.

Two export modes:
1. **Story Export** (default): Narrative-focused, GM/player readable, resembles natural campaign notes
2. **System Export** (optional): Diagnostic-focused, structured metrics, for tuning/debugging

## Design Goals

### Story Export Goals
- Feel like a campaign bible, not a log file
- Readable months/years later without SPAR knowledge
- Suitable for sharing with players or publishing
- Pass the "read-aloud test" (could be read at the table)
- Resemble high-quality GM notes (Spelljammer manual style)

### System Export Goals
- Preserve full reproducibility
- Enable deterministic replay
- Support balance tuning and diagnostics
- Document all operational decisions
- Track generator health metrics

---

## Campaign Story Export (Default)

### File Naming
**Pattern**: `<campaign_name>_campaign_history_<YYYYMMDD>.md`  
**Example**: `space_opera_campaign_history_20251226.md`

### Document Structure

```markdown
# <Campaign Name>

*Campaign story exported: <YYYY-MM-DD HH:MM>*

## Campaign Overview

<Short narrative introduction derived from first 2-3 canon bullets>
<Establishes premise, tone, core conflict>
<Optional: Key factions, major locations, central mystery>
<Max 3-5 sentences or 2-3 bullets>

## Canon Summary

*Current state of the world*

- <Canon bullet 1>
- <Canon bullet 2>
- <Canon bullet 3>
...
- <Canon bullet N> (typically 8-15 bullets)

## Session Log

### Session <N> — <Date>

**What Happened:**

- <Event bullet 1>
- <Event bullet 2>
...

**Manual Entries & Notable Moments:**

#### <Manual Entry Title>

<Description text in paragraph or bullet form>

*GM Notes: <Optional context, player reactions, table notes>*

**Session Notes:**

<Optional freeform GM observations about the session>

**Notable Outcomes:**

- <Narrative description of scar/faction change, e.g., "Station security now actively hunting the crew">
- <Major losses/gains in narrative terms>

**Unresolved Threads:**

- <Thread 1 if explicitly flagged>
- <Thread 2 if explicitly flagged>

---

### Session <N+1> — <Date>

<Repeat structure>

---

## Open Threads

*Unresolved hooks and unanswered questions*

- <Thread 1>
- <Thread 2>
...
```

### Section Rules

#### Campaign Overview
- **Source**: First 2-3 canon_summary bullets
- **Max Length**: 3-5 sentences or 2-3 bullets
- **Purpose**: Orient reader to campaign premise
- **Tone**: Narrative, engaging
- **Optional**: Can be omitted if canon_summary too sparse

#### Canon Summary
- **Source**: campaign.canon_summary (all bullets)
- **Header**: "Current state of the world" subtitle
- **Format**: Clean bullet list, no nesting
- **Exclusions**: No event lists, no session titles, no metrics
- **Guideline**: 8-15 bullets optimal

#### Session Log - Header
- **Format**: `### Session <N> — <Date>`
- **Date Format**: YYYY-MM-DD only (no time)
- **Disambiguation**: If session_id present and duplicate session_number, append time: `Session 5 — 2025-12-26 (144410)`
- **Session Title**: Not included by default (derived from bullets if needed)

#### Session Log - What Happened
- **Source**: entry.what_happened (all bullets)
- **Format**: Bullet list
- **No Truncation**: Show all bullets, not just first N
- **No Collapse**: All bullets visible, not hidden in expanders

#### Session Log - Manual Entries
- **Condition**: Only if manual_entries present
- **Format**: 
  - Level 4 heading (`####`) for each entry title
  - Description as prose paragraph
  - GM Notes in italic if present
  - No severity numbers
  - No tags
  - No state deltas
- **Purpose**: Highlight GM-authored moments/NPCs/items

#### Session Log - Session Notes
- **Condition**: Only if session_notes present and non-empty
- **Format**: Prose paragraph or bullet list
- **Purpose**: GM reflection, table atmosphere, meta notes

#### Session Log - Notable Outcomes
- **Condition**: Only if scars created OR faction shifts occurred
- **Format**: Bullet list in narrative prose
- **Examples**:
  - ✅ "Crew now wanted by Station Authority"
  - ✅ "Medical supplies depleted, 2-week recovery needed"
  - ❌ "attention: +3, disposition: -1"
- **Source**: Derive from deltas.rumor_spread, faction_attention_change, new scars
- **Transformation**: Convert system flags to narrative descriptions

#### Session Log - Unresolved Threads
- **Condition**: Only if session has explicitly flagged threads
- **Format**: Bullet list
- **Note**: Not yet implemented in ledger schema (future)

#### Open Threads
- **Condition**: Only if campaign has open_threads (future field)
- **Format**: Clean bullet list
- **Purpose**: Track hooks to pay off
- **Note**: Not yet implemented in ledger schema

### Explicit Exclusions

The following MUST NOT appear in Campaign Story Export:
- `metadata.severity_avg`
- `metadata.cutoff_rate`
- `metadata.top_tags`
- `metadata.scenario_name`
- `metadata.prep_item_ids`
- `deltas.pressure_change` (numeric)
- `deltas.heat_change` (numeric)
- `active_sources` / `active_source_ids`
- `session_id` (except for disambiguation in header)
- `manual_entries[].severity`
- `manual_entries[].tags`
- `manual_entries[].pressure_delta`
- `manual_entries[].heat_delta`

If present in ledger, they are silently omitted from story export.

---

## Session Story Export (Default)

### File Naming
**Pattern**: `<campaign_name>_session_<NNN>_<YYYYMMDD>.md`  
**Example**: `space_opera_session_005_20251226.md`

### Document Structure

```markdown
# <Campaign Name> — Session <N>

*Session date: <YYYY-MM-DD>*

## What Happened

- <Event bullet 1>
- <Event bullet 2>
...

## Manual Entries & Notable Moments

### <Manual Entry Title>

**Description**: <Entry description>

<If tags present and narratively relevant, mention in prose>

<If factions/scars related, mention in prose>

**GM Notes**: <Optional GM context>

---

### <Manual Entry 2 Title>

<Repeat structure>

## Session Notes

<Optional freeform GM observations>

## Notable Outcomes

- <Narrative description of consequences>
- <Scars, faction shifts, losses, gains in prose>
```

### Section Rules

#### Header
- **Format**: `# <Campaign Name> — Session <N>`
- **Subheader**: `*Session date: <YYYY-MM-DD>*`
- **No Disambiguation**: Single session export doesn't need time suffix

#### What Happened
- **Source**: entry.what_happened (all bullets)
- **Format**: Bullet list, no nesting
- **No Truncation**: All bullets visible

#### Manual Entries
- **Condition**: Only if manual_entries present
- **Format**:
  - Level 3 heading (`###`) for each entry
  - **Description**: label followed by prose
  - Optional narrative mentions of tags/factions/scars if relevant
  - **GM Notes**: label with italic text
- **Exclusions**: No severity numbers, no state deltas as numbers

#### Session Notes
- **Condition**: Only if session_notes present
- **Format**: Prose or bullets
- **Purpose**: Context, reflection, player reactions

#### Notable Outcomes
- **Condition**: Only if outcomes exist (scars, faction changes, major consequences)
- **Format**: Bullet list in narrative prose
- **Transformation**: System flags → narrative descriptions

### Explicit Exclusions

The following MUST NOT appear in Session Story Export:
- All system-facing fields from data contract
- Severity in any form
- Numeric deltas
- Internal tags (unless narratively contextualized)
- Source metadata
- Prep item IDs
- Diagnostic statistics

---

## Campaign System Export (Optional)

### File Naming
**Pattern**: `<campaign_name>_system_<YYYYMMDD>.json`  
**Example**: `space_opera_system_20251226.json`

### Document Structure

```json
{
  "export_type": "system_diagnostic",
  "export_date": "<ISO timestamp>",
  "campaign_id": "<campaign_id>",
  "campaign_name": "<name>",
  
  "campaign_state": {
    // Full CampaignState JSON
  },
  
  "ledger": [
    // Full ledger entries with all system fields
  ],
  
  "prep_queue": [
    // Full prep queue
  ],
  
  "diagnostics": {
    "total_sessions": <N>,
    "peak_severity": <N>,
    "severity_distribution": {},
    "tag_frequency": {},
    "source_usage": {}
  }
}
```

### Purpose
- Full data preservation
- Deterministic replay capability
- Analytics and tuning
- Debug investigations

### When to Use
- Cross-session data analysis
- Balance tuning workflows
- Bug reproduction
- Advanced users only

---

## Narrative Transformation Rules

### Faction Changes
**System**: `deltas.faction_attention_change: true`  
**Story**: `"<Faction name> now actively seeking the crew"`

**System**: `FactionState.attention: 15, disposition: -1`  
**Story**: `"<Faction name> hostile and aware"`

### Scars
**System**: `Scar(category="resource", severity="medium", ...)`  
**Story**: `"Medical supplies depleted, recovery needed"`

**System**: `Scar(category="reputation", severity="high", ...)`  
**Story**: `"Known across the sector as fugitives"`

### Pressure/Heat
**System**: `pressure_change: +3, campaign_pressure: 12`  
**Story**: Campaign now in volatile band → omit or mention in context: `"Tensions escalating rapidly"`

**System**: `heat_change: +2, heat: 15`  
**Story**: Campaign now in hunted band → omit or mention in context: `"Multiple factions tracking crew movements"`

### Rumor Spread
**System**: `deltas.rumor_spread: true`  
**Story**: `"Word of the incident spreading"`

### Tags to Narrative
**System**: `tags: ["hazard", "visibility", "positioning"]`  
**Story**: Optionally mention in context: `"Poor visibility and dangerous terrain"`

**Default**: Omit tags entirely from story exports

---

## File Naming Specification

### Campaign Story Export
- **Pattern**: `<campaign_name>_campaign_history_<YYYYMMDD>.md`
- **Normalization**: Replace spaces with underscores, lowercase
- **Example**: "City of Fog" → `city_of_fog_campaign_history_20251226.md`
- **Location**: `campaigns/` directory or user-specified

### Session Story Export
- **Pattern**: `<campaign_name>_session_<NNN>_<YYYYMMDD>.md`
- **Session Number**: Zero-padded to 3 digits
- **Example**: Session 5 → `space_opera_session_005_20251226.md`
- **Location**: `campaigns/` directory or user-specified

### Campaign System Export
- **Pattern**: `<campaign_name>_system_<YYYYMMDD>.json`
- **Example**: `space_opera_system_20251226.json`
- **Location**: `campaigns/` directory or user-specified

---

## Implementation Priorities

### Phase 1 (Current)
- ✅ Story exports implemented with most story-facing fields
- ✅ System fields mostly excluded
- ⚠️ Some system leakage remains (tags, severity in manual entries)

### Phase 2 (Next)
- Remove remaining system field leakage from story exports
- Implement narrative transformation for Notable Outcomes
- Clean up session headers (disambiguation, no empty sections)

### Phase 3 (Future)
- Campaign Overview auto-generation from canon
- Open Threads tracking and export
- Web view templates (HTML output)
- Player-facing export variant (reduced spoilers)

---

## Examples

### Current Export (Mixed)
```markdown
### Session 5 — 2025-12-26

**What Happened:**
- Manual Test 02

**Manual Entries & GM Notes:**

#### Manual Test 02

**Description**: Manual Test 02

**Tags**: manual_test

**Severity**: 1/10

**GM Notes**: Manual Test 02

*Entry Impact: Pressure: +1 | Heat: -1*

**State Changes:**
- Pressure: +1
- Heat: -1
```

**Issues**: Tags, Severity, Entry Impact are system-facing

### Target Story Export (Pure)
```markdown
### Session 5 — 2025-12-26

**What Happened:**
- Crew negotiated tense standoff with station security
- Intelligence gathered about rival gang operations
- New alliance formed with unexpected NPC

**Manual Entries & Notable Moments:**

#### Unexpected Alliance

**Description**: Station security chief (NPC: Chen) offered crew intel in exchange for silence about departmental corruption. Players debated the moral implications for 20 minutes before accepting the deal.

**GM Notes**: This could become a major faction relationship. Chen might be recurring ally or future liability depending on player choices.

**Session Notes:**

Players were very engaged with moral choices tonight. The negotiation scene was entirely improvised - not from generator. High energy throughout.

**Notable Outcomes:**

- Station Security faction now aware of crew presence
- Crew gained actionable intelligence on rival gang movements
```

**Improvements**: No severity numbers, no numeric deltas, narrative faction changes, GM voice preserved

---

## Migration Path

### Existing Exports (v1 - Mixed)
- Contain both story and system fields
- Usable but cluttered
- Manually filter when reviewing

### Target Exports (v2 - Story)
- Story fields only by default
- Clean narrative focus
- Optional system appendix if requested

### Backward Compatibility
- Old exports remain valid
- New exports follow v0.1 spec
- Tool doesn't break old files

---

## Template Examples

### Minimal Session (No Manual Entries)

```markdown
### Session 3 — 2025-12-26

**What Happened:**
- Crew ambushed during cargo transfer
- Escaped through maintenance shafts
- Lost half the stolen goods in the chaos

**Notable Outcomes:**
- Rival gang now aware of crew's involvement
- Cargo bay access codes compromised
```

### Rich Session (With Manual Entries)

```markdown
### Session 8 — 2025-12-30

**What Happened:**
- Infiltrated restricted sector using forged credentials
- Discovered hidden research lab
- NPC scientist offered to defect in exchange for protection
- Security lockdown triggered during extraction

**Manual Entries & Notable Moments:**

#### The Defector

**Description**: Dr. Yuki Tanaka, lead researcher on Project Veil, approached crew during lab infiltration. Revealed corporation's illegal experiments and offered to share data in exchange for safe passage off-station. Crew agreed despite risks.

**GM Notes**: Tanaka becomes recurring NPC. Has critical intel but also makes crew targets for corporate security. Players immediately liked the character.

#### Project Veil Discovery

**Description**: Lab contained evidence of dimensional research with military applications. Crew recovered partial data logs and physical samples. Full implications still unclear.

**GM Notes**: This is the campaign's central mystery payoff. Players don't know full scope yet.

**Session Notes:**

Best session so far. Players loved the spy thriller atmosphere. The decision to help Tanaka was unanimous but they're worried about consequences. Spent 30 minutes planning extraction route - very tactical thinking.

**Notable Outcomes:**
- Dr. Tanaka joins crew as passenger/ally (new NPC)
- Corporation security actively hunting crew (heat escalation)
- Crew possesses classified research data (major intel asset)
- Lab location compromised, can't return
```

### Session With State Changes But No Manual Entries

```markdown
### Session 4 — 2025-12-28

**What Happened:**
- Tracked rival gang to abandoned warehouse district
- Set ambush at chokepoint
- Gang retreated after brief firefight
- Secured territory temporarily

**Notable Outcomes:**
- Rival gang now cautious of crew's capabilities
- Warehouse district under crew control (temporary)
```

### Session With No Outcomes

```markdown
### Session 2 — 2025-12-24

**What Happened:**
- Crew regrouped at safehouse
- Planned next moves and reviewed intel
- Restocked supplies and repaired equipment

**Session Notes:**

Quiet session focused on planning and character moments. No major plot developments but good downtime roleplay.
```

---

## System Export Specification (Optional)

### Current Implementation
System export is the full campaign JSON file. This is sufficient for v0.1.

### Future Enhancement (If Needed)
If we create a dedicated system export, it should:
- Include all ledger entries with full metadata
- Include CampaignState with all numeric fields
- Include prep_queue with full prep item data
- Add diagnostics section:
  ```json
  "diagnostics": {
    "session_count": 12,
    "peak_severity": 8,
    "severity_histogram": {...},
    "tag_frequency": {...},
    "source_distribution": {...},
    "cutoff_rate_avg": 0.18
  }
  ```

For now, the campaign JSON serves this purpose.

---

## Notable Outcomes Transformation Guide

### When to Include
Include "Notable Outcomes" section if any of:
- New scars created
- Faction attention/disposition changed
- Major asset gained/lost (explicit in manual entry)
- Rumor spread flag set

### How to Transform

#### Scar Creation
```python
# System
scar = Scar(
    scar_id="known_to_authorities",
    category="reputation",
    severity="high",
    notes="Station security has crew biometrics"
)

# Story
"Crew now flagged in station security systems"
```

#### Faction Attention Change
```python
# System
deltas["faction_attention_change"] = True
# + specific faction in manual entry

# Story
"<Faction name> now actively tracking crew movements"
```

#### Rumor Spread
```python
# System  
deltas["rumor_spread"] = True

# Story
"Word of the incident spreading through local channels"
```

### Fallback
If outcomes unclear from structured data, omit section entirely rather than inventing prose.

---

## Implementation Notes

### Current Export Code Location
- Campaign history export: `streamlit_harness/campaign_ui.py` ~line 550
- Session export: `streamlit_harness/campaign_ui.py` ~line 670

### Required Changes for v0.1 Spec Compliance

1. **Remove system field leakage**:
   - Remove Tags, Severity, Entry Impact from manual entries
   - Remove numeric pressure/heat from State Changes
   - Remove Metadata section entirely

2. **Add Notable Outcomes**:
   - New section after Session Notes
   - Transform scars/faction changes to narrative prose
   - Omit if no outcomes

3. **Improve session headers**:
   - Use session_id for disambiguation
   - Skip empty State Changes sections (already implemented)

4. **Optional Campaign Overview**:
   - Derive from first 2-3 canon bullets
   - Add before Canon Summary section

### Minimal Changes
Most story-facing structure already correct. Main work is:
- Removing system fields
- Adding outcome transformations
- Polishing headers

---

## Versioning

**v0.1 (2025-12-26)**: Initial export specification  
- Campaign Story Export structure defined
- Session Story Export structure defined  
- System Export deferred to JSON
- Explicit exclusion lists
- Narrative transformation guidelines

**Future versions** may:
- Add web view templates (HTML)
- Define player-facing export variant
- Add docx export specification
- Specify API response formats

---

## References

- **Data Contract**: `docs/DATA_CONTRACT_story_vs_system_v0.1.md`
- **Campaign UI**: `streamlit_harness/campaign_ui.py`
- **Export Implementation**: Campaign history ~line 550, Session export ~line 670

---

## Acceptance Criteria for Implementation (Task 3)

When implementing this spec:

1. ✅ Campaign story export contains no severity numbers
2. ✅ Session story export contains no tags or deltas in manual entries  
3. ✅ Empty State Changes sections omitted
4. ✅ Session headers disambiguate duplicate session_numbers
5. ✅ Notable Outcomes transforms system flags to narrative prose
6. ✅ All story-facing fields from data contract appear
7. ✅ All system-facing fields from data contract excluded
8. ✅ Export passes "read-aloud test" (sounds natural)
9. ✅ File naming follows specification exactly
10. ✅ Exports work with both old ledger entries (no session_id) and new ones

---

## Out of Scope

The following are NOT part of export specification:

- Canon Summary curation logic (separate task)
- Generator output richness (separate task)
- Web view design (separate task)
- Player-facing vs GM-facing variants (future)
- Multi-format support (PDF, docx, etc.) (future)
- Export automation/scheduling (future)
