"""SPAR Campaign Mechanics Layer v0.1

Optional campaign-level state tracking that sits above the SPAR Engine.
Tracks long-term pressure, attention, and consequences across multiple scenes.

Key exports:
    - CampaignState: Campaign-level state model
    - CampaignDelta: Changes from scene outcomes
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
from .models import CampaignDelta, CampaignState

__all__ = [
    "CampaignState",
    "CampaignDelta",
    "apply_campaign_delta",
    "decay_campaign_state",
    "get_campaign_influence",
    "record_severity_high_water_mark",
]
