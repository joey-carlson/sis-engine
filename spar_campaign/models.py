"""Campaign-level state models for long-term pressure tracking.

Version History:
- v0.2 (2025-12-25): Added structured scars, faction tracking, long-arc bands
- v0.1 (2025-12-25): Initial implementation

This module defines campaign-scale state that persists across scenes,
tracking pressure, attention, and consequences that operate at a longer
timescale than scene-level clocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Set

# Type aliases for v0.2
ScarCategory = Literal["physical", "social", "political", "resource", "reputation", "environment"]
ScarSeverity = Literal["low", "medium", "high"]
PressureBand = Literal["stable", "strained", "volatile", "critical"]
HeatBand = Literal["quiet", "noticed", "hunted", "exposed"]


@dataclass(frozen=True)
class Scar:
    """Structured scar representing persistent campaign consequence.
    
    Scars are permanent or semi-permanent changes that echo forward
    through the campaign. They influence scene setup and provide
    narrative continuity.
    """
    
    scar_id: str
    category: ScarCategory
    severity: ScarSeverity
    source: Optional[str] = None
    created_scene_index: Optional[int] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "scar_id": self.scar_id,
            "category": self.category,
            "severity": self.severity,
            "source": self.source,
            "created_scene_index": self.created_scene_index,
            "notes": self.notes,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "Scar":
        """Deserialize from dictionary."""
        return Scar(
            scar_id=data["scar_id"],
            category=data["category"],
            severity=data["severity"],
            source=data.get("source"),
            created_scene_index=data.get("created_scene_index"),
            notes=data.get("notes"),
        )


@dataclass(frozen=True)
class FactionState:
    """Tracks a faction's attention and disposition toward the party.
    
    Factions are external actors (authorities, rivals, organizations)
    whose awareness and attitude evolves based on campaign events.
    
    v0.2: Factions observe and remember. They don't act yet.
    """
    
    faction_id: str
    attention: int = 0  # How aware they are (0-20 default cap)
    disposition: int = 0  # How they feel (-2 hostile, 0 neutral, +2 favorable)
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "faction_id": self.faction_id,
            "attention": self.attention,
            "disposition": self.disposition,
            "notes": self.notes,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "FactionState":
        """Deserialize from dictionary."""
        return FactionState(
            faction_id=data["faction_id"],
            attention=data.get("attention", 0),
            disposition=data.get("disposition", 0),
            notes=data.get("notes"),
        )


@dataclass(frozen=True)
class CampaignState:
    """Campaign-level state tracking long-term pressure and consequences.
    
    This state layer sits above EngineState and tracks information that
    persists across multiple scenes. It observes scene outcomes and can
    influence future scene setup without modifying core engine behavior.
    
    Design principle: Scene mechanics create pressure. Campaign mechanics remember it.
    
    Version History:
    - v0.2: Added structured scars, faction tracking, version field
    - v0.1: Initial pressure/heat/basic scars
    """
    
    # Schema version for backward compatibility
    version: str = "0.2"
    
    # Long-term pressure that accumulates from volatility
    campaign_pressure: int = 0
    
    # External awareness and response tracking
    heat: int = 0
    
    # Structured scars (v0.2) - permanent consequences
    scars: List[Scar] = field(default_factory=list)
    
    # Faction tracking (v0.2) - external actors
    factions: Dict[str, FactionState] = field(default_factory=dict)
    
    # Tracking for derived behavior
    total_scenes_run: int = 0
    total_cutoffs_seen: int = 0
    highest_severity_seen: int = 0
    
    # v0.1 compatibility: legacy scars (deprecated, use structured scars)
    _legacy_scars: Set[str] = field(default_factory=set)
    
    @staticmethod
    def default() -> "CampaignState":
        """Create default campaign state with zero pressure."""
        return CampaignState(
            version="0.2",
            campaign_pressure=0,
            heat=0,
            scars=[],
            factions={},
            total_scenes_run=0,
            total_cutoffs_seen=0,
            highest_severity_seen=0,
            _legacy_scars=set(),
        )
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary for JSON export."""
        return {
            "version": self.version,
            "campaign_pressure": self.campaign_pressure,
            "heat": self.heat,
            "scars": [s.to_dict() for s in self.scars],
            "factions": {fid: f.to_dict() for fid, f in self.factions.items()},
            "total_scenes_run": self.total_scenes_run,
            "total_cutoffs_seen": self.total_cutoffs_seen,
            "highest_severity_seen": self.highest_severity_seen,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "CampaignState":
        """Deserialize from dictionary with backward compatibility.
        
        Supports loading v0.1 state (string scars) and v0.2 state (structured).
        """
        version = data.get("version", "0.1")
        
        # Load scars with version compatibility
        scars_data = data.get("scars", [])
        if version == "0.1" or (scars_data and isinstance(scars_data[0], str)):
            # v0.1 format: list of strings, store in legacy field
            scars = []
            legacy_scars = set(scars_data)
        else:
            # v0.2 format: list of dicts
            scars = [Scar.from_dict(s) for s in scars_data]
            legacy_scars = set()
        
        # Load factions (v0.2 only)
        factions_data = data.get("factions", {})
        factions = {fid: FactionState.from_dict(f) for fid, f in factions_data.items()}
        
        return CampaignState(
            version="0.2",  # Always upgrade to current
            campaign_pressure=data.get("campaign_pressure", 0),
            heat=data.get("heat", 0),
            scars=scars,
            factions=factions,
            total_scenes_run=data.get("total_scenes_run", 0),
            total_cutoffs_seen=data.get("total_cutoffs_seen", 0),
            highest_severity_seen=data.get("highest_severity_seen", 0),
            _legacy_scars=legacy_scars,
        )
    
    def get_pressure_band(self) -> PressureBand:
        """Get descriptive band for current pressure level (informational only)."""
        if self.campaign_pressure >= 20:
            return "critical"
        elif self.campaign_pressure >= 10:
            return "volatile"
        elif self.campaign_pressure >= 5:
            return "strained"
        else:
            return "stable"
    
    def get_heat_band(self) -> HeatBand:
        """Get descriptive band for current heat level (informational only)."""
        if self.heat >= 15:
            return "exposed"
        elif self.heat >= 8:
            return "hunted"
        elif self.heat >= 4:
            return "noticed"
        else:
            return "quiet"


@dataclass(frozen=True)
class CampaignDelta:
    """Changes to apply to CampaignState after a scene resolves.
    
    This is the interface between scene outcomes and campaign state.
    Values are additive (will be added to current state values).
    
    Version History:
    - v0.2: Added structured scars, faction updates
    - v0.1: Basic pressure/heat/string scars
    """
    
    campaign_pressure_add: int = 0
    heat_add: int = 0
    
    # v0.2: Structured scars to add
    scars_add: List[Scar] = field(default_factory=list)
    
    # v0.2: Faction attention/disposition changes
    faction_updates: Dict[str, Dict[str, int]] = field(default_factory=dict)
    # Format: {"faction_id": {"attention_add": 1, "disposition_add": 0}}
    
    scenes_increment: int = 1
    
    # v0.1 compatibility
    _legacy_scars_add: Set[str] = field(default_factory=set)
    
    @staticmethod
    def from_scene_outcome(
        severity: int,
        cutoff_applied: bool,
        tags: List[str],
        effect_vector_dict: Dict[str, int],
        *,
        factions_present: Optional[List[str]] = None,
        explicit_scars: Optional[List[Scar]] = None,
    ) -> "CampaignDelta":
        """Derive campaign delta from a scene's outcome.
        
        Accumulation rules (v0.2):
        - Campaign pressure: +1 per severity point above 5, +2 if cutoff
        - Heat: +1 per visibility/social_friction tag, +effect_vector.heat
        - Scars: Explicit only (no auto-generation)
        - Factions: +1 attention per visibility/social_friction if faction present
        
        Args:
            severity: Scene severity
            cutoff_applied: Whether cutoff was triggered
            tags: Event tags
            effect_vector_dict: Effect vector as dict
            factions_present: Optional list of faction IDs relevant to scene
            explicit_scars: Optional list of scars to add
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
        
        # Calculate faction updates (v0.2)
        faction_updates: Dict[str, Dict[str, int]] = {}
        if factions_present:
            for faction_id in factions_present:
                attention_add = 0
                
                # Visibility and social friction draw faction attention
                if "visibility" in tags or "social_friction" in tags:
                    attention_add += 1
                
                # Reinforcements suggest faction response
                if "reinforcements" in tags:
                    attention_add += 1
                
                # High heat draws attention
                if effect_vector_dict.get("heat", 0) >= 2:
                    attention_add += 1
                
                if attention_add > 0:
                    faction_updates[faction_id] = {
                        "attention_add": attention_add,
                        "disposition_add": 0,  # Neutral by default
                    }
        
        return CampaignDelta(
            campaign_pressure_add=pressure,
            heat_add=heat_accumulation,
            scars_add=list(explicit_scars) if explicit_scars else [],
            faction_updates=faction_updates,
            scenes_increment=1,
            _legacy_scars_add=set(),
        )
