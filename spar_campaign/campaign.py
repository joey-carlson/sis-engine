"""Campaign mechanics operations for long-term pressure management.

Version History:
- v0.1 (2025-12-25): Initial implementation

This module provides pure functions for managing campaign state across
multiple scenes. It handles pressure accumulation, decay, and translation
of campaign state into scene setup influences.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set

from .models import CampaignState, CampaignDelta


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
    
    # Union scars (irreversible)
    new_scars = state.scars | delta.scars_add
    
    # Track highest severity seen
    new_highest = state.highest_severity_seen
    
    # Increment counters
    new_scenes = state.total_scenes_run + delta.scenes_increment
    new_cutoffs = state.total_cutoffs_seen + (1 if delta.campaign_pressure_add >= 2 else 0)
    
    return CampaignState(
        campaign_pressure=new_pressure,
        heat=new_heat,
        scars=new_scars,
        total_scenes_run=new_scenes,
        total_cutoffs_seen=new_cutoffs,
        highest_severity_seen=new_highest,
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
        campaign_pressure=new_pressure,
        heat=new_heat,
        scars=state.scars,  # Unchanged
        total_scenes_run=state.total_scenes_run,
        total_cutoffs_seen=state.total_cutoffs_seen,
        highest_severity_seen=state.highest_severity_seen,
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
    
    # Specific scars might enable/disable certain content
    if "resources_depleted" in state.scars:
        include_tags.append("attrition")
        notes.append("Resources depleted: supply pressure continues")
    
    if "known_to_authorities" in state.scars:
        include_tags.append("social_friction")
        notes.append("Known to authorities: heightened scrutiny")
    
    return {
        "include_tags": include_tags,
        "exclude_tags": exclude_tags,
        "rarity_bias": rarity_bias,
        "notes": notes,
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
            campaign_pressure=state.campaign_pressure,
            heat=state.heat,
            scars=state.scars,
            total_scenes_run=state.total_scenes_run,
            total_cutoffs_seen=state.total_cutoffs_seen,
            highest_severity_seen=severity,
        )
    return state
