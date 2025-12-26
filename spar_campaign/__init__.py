"""SPAR Campaign Mechanics Layer v0.2

Optional campaign-level state tracking that sits above the SPAR Engine.
Tracks long-term pressure, attention, and consequences across multiple scenes.

Version History:
- v0.2 (2025-12-25): Added structured scars, faction tracking, long-arc bands
- v0.1 (2025-12-25): Initial implementation

Key exports:
    - CampaignState: Campaign-level state model (v0.2)
    - CampaignDelta: Changes from scene outcomes
    - Scar: Structured scar model (v0.2)
    - FactionState: Faction tracking model (v0.2)
    - apply_campaign_delta: Apply delta to campaign state
    - decay_campaign_state: Apply time-based decay
    - get_campaign_influence: Get scene setup hints from campaign state
"""

from .campaign import (
    apply_campaign_delta,
    decay_campaign_state,
    get_campaign_influence,
    record_severity_high_water_mark,
)
from .models import CampaignDelta, CampaignState, FactionState, Scar

__all__ = [
    "CampaignState",
    "CampaignDelta",
    "Scar",
    "FactionState",
    "apply_campaign_delta",
    "decay_campaign_state",
    "get_campaign_influence",
    "record_severity_high_water_mark",
]
