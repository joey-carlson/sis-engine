# Campaign Integration Flows B-D - Implementation Status

**Date**: 2025-12-25  
**Status**: Foundations Complete, UI Wiring In Progress

---

## Overview

This document tracks the implementation status of bidirectional Campaign ↔ Generator integration (Flows B-D).

---

## Flow A: Context → Generator ✅ COMPLETE

**Status**: Fully implemented (commit 5d3e57c)

**What's working:**
- Context Bundle computation from CampaignState v0.2
- Auto-apply when "Run Session" clicked
- Context Applied strip (View/Disable buttons)
- Tag pre-filling (merged with defaults)
- Context persistence across sessions

---

## Flow B: Generator → Campaign (Session Packet)

**Status**: ✅ COMPLETE (commit 501de42)

**Completed:**
- ✅ SessionPacket model (commit 365230c)
- ✅ from_run_result() derives suggestions
- ✅ Pressure/heat delta heuristics
- ✅ Faction update suggestions
- ✅ Candidate scars
- ✅ "Finalize Session" button in Event Generator (commit 501de42)
- ✅ Pre-fill finalize wizard from packet (commit 501de42)
- ✅ Session statistics display
- ✅ Packet cleared after commit

**How it works:**
1. Generate events in Event Generator (with campaign context)
2. Click "Finalize Session" button (appears after generation)
3. SessionPacket created from results
4. Wizard opens pre-filled (top 3 events, pressure/heat suggestions)
5. GM reviews, edits, commits
6. Campaign state updates

**Test:**
- Create campaign → Run Session → Generate events → Finalize Session
- Observe: Wizard pre-filled with event titles and suggested deltas

---

## Flow C: History → Existing Campaign

**Status**: Foundation complete, UI needed

**Completed (commit 365230c):**
- ✅ History parser (`streamlit_harness/history_parser.py`)
- ✅ detect_dates() - Multiple format support
- ✅ split_into_sessions() - Chunk by date markers
- ✅ extract_canon_summary() - Last N sentences
- ✅ extract_factions() - Named entity frequency
- ✅ parse_campaign_history() - Full pipeline with notes

**Remaining Work:**
- [ ] Add "Import History" button to Campaign Dashboard
- [ ] File upload widget (txt, md, paste)
- [ ] Parse Preview UI (sessions, canon, factions)
- [ ] Editable date fields for unknown dates
- [ ] Diff view (existing canon vs proposed)
- [ ] Commit button → merge into campaign

**Estimated effort**: 3-4 hours (UI + review flow)

---

## Flow D: History → New Campaign

**Status**: Parser ready, creation flow needed

**Completed**: Parser (commit 365230c)

**Remaining Work:**
- [ ] Wire "Import Campaign History" button (landing page)
- [ ] Reuse parse_campaign_history()
- [ ] Propose campaign name (from history)
- [ ] Show creation form pre-filled
- [ ] Create campaign → open dashboard

**Estimated effort**: 2 hours (reuses Flow C parser)

---

## Data Models

### SessionPacket
```python
@dataclass
class SessionPacket:
    scenario_name: str
    preset: str
    phase: str
    severity_avg: float
    cutoff_rate: float
    top_tags: List[tuple[str, int]]
    suggested_pressure_delta: int
    suggested_heat_delta: int
    suggested_faction_updates: Dict[str, int]
    candidate_scars: List[Dict[str, str]]
    notes: List[str]
```

### Parsed History
```python
{
    "sessions": [{"session_number": 1, "date": "2025-12-20", "content": "..."}],
    "canon_summary": ["Bullet 1", "Bullet 2", ...],
    "factions": ["City Watch", "Merchant Guild", ...],
    "notes": ["✓ Detected 3 sessions", ...]
}
```

---

## Integration Boundaries (Preserved)

**Session Packet:**
- ❌ Never auto-commits to campaign
- ✅ Advisory suggestions only
- ✅ GM reviews all before commit

**History Parser:**
- ❌ Never overwrites existing canon without review
- ✅ Shows diff view (before/after)
- ✅ GM edits dates/content before commit

**Context Bundle:**
- ❌ Never modifies campaign state
- ✅ Read-only derived object
- ✅ Visible and dismissible

---

## Next Steps

### Immediate (Flow B UI)
1. Add session_packet to last_batch in app.py
2. Wire "Finalize Session" button after runs
3. Pre-fill wizard from packet
4. Test suggested deltas flow

### Medium-term (Flows C & D UI)
5. Add "Import History" to dashboard
6. Implement parse preview UI
7. Wire landing page import button
8. Test date detection edge cases

### Documentation
9. Create docs/PLAY_GUIDE_campaigns.md
10. Create docs/ARCH_campaign_integration.md
11. Update KEY_DOCS.md

---

## Testing Checklist

- [ ] Flow B: Generate run → See finalize button → Wizard prefilled → Commit
- [ ] Flow C: Dashboard import → Upload → Preview → Edit dates → Commit
- [ ] Flow D: Landing import → Upload → Review proposal → Create campaign
- [ ] Edge cases: No dates detected, empty history, malformed input
- [ ] Multi-campaign: Context switching, no state leakage

---

## GitHub Sync

**Remote**: https://github.com/joey-carlson/spar-engine  
**Branch**: main  
**Commits ready to push**: 11 (f5d943f through 365230c)

Sync command:
```bash
git push origin main
```

---

**Status Summary**:
- Flow A: ✅ Complete (commit 5d3e57c)
- Flow B: ✅ Complete (commit 501de42)
- Flow C: 🟡 Parser complete, UI needed (~3-4 hours)
- Flow D: 🟡 Reuses parser, UI needed (~2 hours)

**Total Progress**: 70% complete (Flows A & B working, C & D need UI)
