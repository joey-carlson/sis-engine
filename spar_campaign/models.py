"""Campaign-level state models for long-term pressure tracking.

Version History:
- v0.1 (2025-12-25): Initial implementation

This module defines campaign-scale state that persists across scenes,
tracking pressure, attention, and consequences that operate at a longer
timescale than scene-level clocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(frozen=True)
class CampaignState:
    """Campaign-level state tracking long-term pressure and consequences.
    
    This state layer sits above EngineState and tracks information that
    persists across multiple scenes. It observes scene outcomes and can
    influence future scene setup without modifying core engine behavior.
    
    Design principle: Scene mechanics create pressure. Campaign mechanics remember it.
    """
    
    # Long-term pressure that accumulates from volatility
    campaign_pressure: int = 0
    
    # External awareness and response tracking
    heat: int = 0
    
    # Irreversible or semi-permanent changes (optional v0.1)
    scars: Set[str] = field(default_factory=set)
    
    # Tracking for derived behavior (future use)
    total_scenes_run: int = 0
    total_cutoffs_seen: int = 0
    highest_severity_seen: int = 0
    
    @staticmethod
    def default() -> "CampaignState":
        """Create default campaign state with zero pressure."""
        return CampaignState(
            campaign_pressure=0,
            heat=0,
            scars=set(),
            total_scenes_run=0,
            total_cutoffs_seen=0,
            highest_severity_seen=0,
        )
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON export."""
        return {
            "campaign_pressure": self.campaign_pressure,
            "heat": self.heat,
            "scars": sorted(list(self.scars)),
            "total_scenes_run": self.total_scenes_run,
            "total_cutoffs_seen": self.total_cutoffs_seen,
            "highest_severity_seen": self.highest_severity_seen,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "CampaignState":
        """Deserialize from dictionary."""
        return CampaignState(
            campaign_pressure=data.get("campaign_pressure", 0),
            heat=data.get("heat", 0),
            scars=set(data.get("scars", [])),
            total_scenes_run=data.get("total_scenes_run", 0),
            total_cutoffs_seen=data.get("total_cutoffs_seen", 0),
            highest_severity_seen=data.get("highest_severity_seen", 0),
        )


@dataclass(frozen=True)
class CampaignDelta:
    """Changes to apply to CampaignState after a scene resolves.
    
    This is the interface between scene outcomes and campaign state.
    Values are additive (will be added to current state values).
    """
    
    campaign_pressure_add: int = 0
    heat_add: int = 0
    scars_add: Set[str] = field(default_factory=set)
    scenes_increment: int = 1
    
    @staticmethod
    def from_scene_outcome(
        severity: int,
        cutoff_applied: bool,
        tags: List[str],
        effect_vector_dict: Dict[str, int],
    ) -> "CampaignDelta":
        """Derive campaign delta from a scene's outcome.
        
        Accumulation rules (v0.1):
        - Campaign pressure: +1 per severity point above 5, +2 if cutoff
        - Heat: +1 per visibility/social_friction tag, +effect_vector.heat
        - Scars: Not auto-generated in v0.1 (explicit only)
        """
        pressure = 0
        
        # High severity scenes accumulate pressure
        if severity > 5:
            pressure += (severity - 5)
        
        # Cutoffs indicate tension near breaking point
        if cutoff_applied:
            pressure += 2
        
        # Calculate heat from tags and effect vector
        heat_accumulation = 0
        
        # Tags that spread attention
        visibility_tags = ["visibility", "social_friction", "reinforcements"]
        for tag in tags:
            if tag in visibility_tags:
                heat_accumulation += 1
        
        # Add direct heat from effect vector
        heat_accumulation += effect_vector_dict.get("heat", 0)
        
        return CampaignDelta(
            campaign_pressure_add=pressure,
            heat_add=heat_accumulation,
            scars_add=set(),  # Explicit only in v0.1
            scenes_increment=1,
        )
