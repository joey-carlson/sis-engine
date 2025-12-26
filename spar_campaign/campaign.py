"""Campaign mechanics operations for long-term pressure management.

Version History:
- v0.2 (2025-12-25): Extended for structured scars and faction tracking
- v0.1 (2025-12-25): Initial implementation

This module provides pure functions for managing campaign state across
multiple scenes. It handles pressure accumulation, decay, and translation
of campaign state into scene setup influences.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set

from .models import CampaignState, CampaignDelta, FactionState, Scar


def apply_campaign_delta(
    state: CampaignState,
    delta: CampaignDelta,
    *,
    pressure_cap: int = 30,
    heat_cap: int = 20,
) -> CampaignState:
    """Apply a CampaignDelta to CampaignState (pure function).
    
    Args:
        state: Current campaign state
        delta: Changes from scene outcome
        pressure_cap: Maximum campaign pressure (prevents runaway)
        heat_cap: Maximum heat/attention (prevents runaway)
    
    Returns:
        New campaign state with delta applied and caps enforced
    """
    # Add pressure, cap to prevent runaway
    new_pressure = min(
        state.campaign_pressure + delta.campaign_pressure_add,
        pressure_cap
    )
    
    # Add heat, cap to prevent runaway
    new_heat = min(
        state.heat + delta.heat_add,
        heat_cap
    )
    
    # Add new scars (irreversible, no duplicates by scar_id)
    existing_scar_ids = {s.scar_id for s in state.scars}
    new_scars = list(state.scars)
    for scar in delta.scars_add:
        if scar.scar_id not in existing_scar_ids:
            new_scars.append(scar)
    
    # Update factions
    new_factions = dict(state.factions)
    for faction_id, updates in delta.faction_updates.items():
        if faction_id in new_factions:
            # Update existing faction
            old_faction = new_factions[faction_id]
            new_attention = min(
                old_faction.attention + updates.get("attention_add", 0),
                20  # faction attention cap
            )
            new_disposition = max(-2, min(2,
                old_faction.disposition + updates.get("disposition_add", 0)
            ))
            new_factions[faction_id] = FactionState(
                faction_id=faction_id,
                attention=new_attention,
                disposition=new_disposition,
                notes=old_faction.notes,
            )
        else:
            # Create new faction
            new_factions[faction_id] = FactionState(
                faction_id=faction_id,
                attention=updates.get("attention_add", 0),
                disposition=updates.get("disposition_add", 0),
                notes=None,
            )
    
    # Track highest severity seen
    new_highest = state.highest_severity_seen
    
    # Increment counters
    new_scenes = state.total_scenes_run + delta.scenes_increment
    new_cutoffs = state.total_cutoffs_seen + (1 if delta.campaign_pressure_add >= 2 else 0)
    
    return CampaignState(
        version="0.2",
        campaign_pressure=new_pressure,
        heat=new_heat,
        scars=new_scars,
        factions=new_factions,
        total_scenes_run=new_scenes,
        total_cutoffs_seen=new_cutoffs,
        highest_severity_seen=new_highest,
        _legacy_scars=state._legacy_scars,  # Preserve legacy
    )


def decay_campaign_state(
    state: CampaignState,
    *,
    pressure_decay: int = 1,
    heat_decay: int = 1,
) -> CampaignState:
    """Apply time-based decay to campaign state (pure function).
    
    Use this between scenes or at narrative downtime moments to
    represent pressure release, cooling attention, etc.
    
    Args:
        state: Current campaign state
        pressure_decay: Amount to reduce campaign_pressure
        heat_decay: Amount to reduce heat
    
    Returns:
        New state with decay applied
    
    Note: Scars are permanent and do not decay.
    """
    new_pressure = max(0, state.campaign_pressure - pressure_decay)
    new_heat = max(0, state.heat - heat_decay)
    
    return CampaignState(
        version="0.2",
        campaign_pressure=new_pressure,
        heat=new_heat,
        scars=state.scars,  # Unchanged
        factions=state.factions,  # Unchanged
        total_scenes_run=state.total_scenes_run,
        total_cutoffs_seen=state.total_cutoffs_seen,
        highest_severity_seen=state.highest_severity_seen,
        _legacy_scars=state._legacy_scars,
    )


def get_campaign_influence(state: CampaignState) -> Dict[str, Any]:
    """Translate campaign state into scene setup influence.
    
    This function provides hints for scene setup without modifying
    engine internals. The calling code decides how to apply these hints.
    
    Returns dictionary with:
        - include_tags: Tags to add to scene selection
        - exclude_tags: Tags to suppress
        - rarity_bias: Suggested shift to rarity mode (if any)
        - notes: Human-readable explanation
    
    Design principle: Campaign state suggests, scene setup decides.
    """
    include_tags: List[str] = []
    exclude_tags: List[str] = []
    rarity_bias: str | None = None
    notes: List[str] = []
    
    # High campaign pressure suggests more volatility
    if state.campaign_pressure >= 20:
        include_tags.append("time_pressure")
        include_tags.append("reinforcements")
        rarity_bias = "spiky"
        notes.append("Very high campaign pressure: volatile conditions likely")
    elif state.campaign_pressure >= 10:
        include_tags.append("time_pressure")
        notes.append("Elevated campaign pressure: situation remains tense")
    
    # High heat means attention and response
    if state.heat >= 15:
        include_tags.append("social_friction")
        include_tags.append("visibility")
        notes.append("High heat: authorities and factions are aware")
    elif state.heat >= 8:
        include_tags.append("visibility")
        notes.append("Moderate heat: attention is building")
    
    # Low pressure + low heat might allow breathing room
    if state.campaign_pressure < 5 and state.heat < 5:
        exclude_tags.append("time_pressure")
        notes.append("Low pressure: opportunity for recovery")
    
    # Specific scars might enable/disable certain content (v0.2)
    for scar in state.scars:
        if scar.category == "resource":
            include_tags.append("attrition")
            notes.append(f"Scar: {scar.scar_id} - supply pressure continues")
        
        if scar.category in ["social", "political", "reputation"]:
            include_tags.append("social_friction")
            notes.append(f"Scar: {scar.scar_id} - social complications likely")
    
    # v0.1 legacy scar support
    if "resources_depleted" in state._legacy_scars:
        include_tags.append("attrition")
        notes.append("Resources depleted: supply pressure continues")
    
    if "known_to_authorities" in state._legacy_scars:
        include_tags.append("social_friction")
        notes.append("Known to authorities: heightened scrutiny")
    
    # Faction influence (v0.2)
    high_attention_factions = [
        fid for fid, f in state.factions.items() if f.attention >= 10
    ]
    hostile_factions = [
        fid for fid, f in state.factions.items() if f.disposition <= -1
    ]
    
    if high_attention_factions:
        include_tags.append("reinforcements")
        notes.append(f"High faction attention: {', '.join(high_attention_factions)}")
    
    if hostile_factions:
        include_tags.append("social_friction")
        notes.append(f"Hostile factions: {', '.join(hostile_factions)}")
    
    # Add pressure and heat band descriptors
    pressure_band = state.get_pressure_band()
    heat_band = state.get_heat_band()
    
    if pressure_band != "stable" or heat_band != "quiet":
        notes.append(f"Campaign state: {pressure_band} pressure, {heat_band} heat")
    
    # Suggest factions that might be involved based on state
    suggested_factions = []
    for fid, faction in state.factions.items():
        if faction.attention >= 5:
            suggested_factions.append(fid)
    
    return {
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
        "rarity_bias": rarity_bias,
        "notes": notes,
        "suggested_factions_involved": suggested_factions,
        "pressure_band": pressure_band,
        "heat_band": heat_band,
    }


def record_severity_high_water_mark(
    state: CampaignState,
    severity: int,
) -> CampaignState:
    """Update highest severity seen if this scene exceeds it.
    
    Helper function to track campaign volatility peak.
    """
    if severity > state.highest_severity_seen:
        return CampaignState(
            version="0.2",
            campaign_pressure=state.campaign_pressure,
            heat=state.heat,
            scars=state.scars,
            factions=state.factions,
            total_scenes_run=state.total_scenes_run,
            total_cutoffs_seen=state.total_cutoffs_seen,
            highest_severity_seen=severity,
            _legacy_scars=state._legacy_scars,
        )
    return state
