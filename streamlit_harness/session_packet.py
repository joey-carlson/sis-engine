"""Session Packet for Generator → Campaign integration.

Version History:
- v0.1 (2025-12-25): Initial session packet implementation

Provides Session Packet data model for transporting generator run results
into Campaign Manager finalization wizard.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionPacket:
    """Session packet derived from generator run results.
    
    Transports run metadata and suggested deltas from Event Generator
    to Campaign Manager finalization wizard. GM reviews and commits.
    
    This is advisory data - never auto-commits to campaign state.
    """
    
    # Run metadata
    scenario_name: str
    preset: str
    phase: str
    rarity_mode: str
    seed: int
    batch_size: int
    
    # Run statistics
    severity_avg: float
    cutoff_rate: float
    top_tags: List[tuple[str, int]]  # (tag, count)
    top_events: List[Dict[str, Any]]  # Event dicts
    
    # Suggested campaign deltas
    suggested_pressure_delta: int
    suggested_heat_delta: int
    suggested_faction_updates: Dict[str, int]  # {faction_id: attention_delta}
    candidate_scars: List[Dict[str, str]]  # {scar_id, category, severity, notes}
    
    # Explanatory notes
    notes: List[str] = field(default_factory=list)
    
    @staticmethod
    def from_run_result(
        scenario_name: str,
        preset: str,
        phase: str,
        rarity_mode: str,
        seed: int,
        batch_size: int,
        events: List[Dict[str, Any]],
        summary: Dict[str, Any],
    ) -> "SessionPacket":
        """Derive session packet from generator run results.
        
        Applies heuristics to suggest campaign deltas based on:
        - Severity distribution
        - Tag frequencies
        - Event patterns
        """
        # Extract statistics
        severity_avg = summary.get("severity_avg", 0)
        cutoff_rate = summary.get("cutoff_rate", 0)
        top_tags = summary.get("top_tags", [])[:10]
        
        # Select notable events (top 5 by severity)
        sorted_events = sorted(events, key=lambda e: e.get("severity", 0), reverse=True)
        top_events = sorted_events[:5]
        
        # Suggest pressure delta
        # High severity average or cutoffs → pressure increase
        pressure_delta = 0
        if severity_avg >= 6:
            pressure_delta += 2
        elif severity_avg >= 5:
            pressure_delta += 1
        
        if cutoff_rate >= 0.15:  # 15%+ cutoffs
            pressure_delta += 2
        elif cutoff_rate >= 0.10:
            pressure_delta += 1
        
        # Suggest heat delta
        # Visibility/social tags → heat increase
        heat_delta = 0
        for tag, count in top_tags:
            if tag in ["visibility", "social_friction", "reinforcements"]:
                heat_delta += 1
        
        # Cap suggested deltas (advisory)
        pressure_delta = min(pressure_delta, 5)
        heat_delta = min(heat_delta, 5)
        
        # Suggest faction updates (if high visibility/social tags)
        faction_updates = {}
        visibility_count = sum(count for tag, count in top_tags if tag == "visibility")
        social_count = sum(count for tag, count in top_tags if tag == "social_friction")
        
        if visibility_count + social_count >= batch_size * 0.3:  # 30%+ visibility
            # Suggest generic faction attention increase
            # GM will select which factions in wizard
            faction_updates["__suggested__"] = 2
        
        # Suggest candidate scars (high severity or specific tags)
        candidate_scars = []
        
        if severity_avg >= 7:
            candidate_scars.append({
                "scar_id": "high_intensity_engagement",
                "category": "physical",
                "severity": "medium",
                "notes": f"Severe engagement (avg severity {severity_avg:.1f})",
            })
        
        # Check for attrition/resource tags
        attrition_count = sum(count for tag, count in top_tags if tag == "attrition")
        if attrition_count >= 3:
            candidate_scars.append({
                "scar_id": "resources_strained",
                "category": "resource",
                "severity": "low",
                "notes": f"Multiple attrition events ({attrition_count})",
            })
        
        # Generate explanatory notes
        notes = []
        if pressure_delta > 0:
            notes.append(f"Pressure +{pressure_delta}: High severity average ({severity_avg:.1f})")
        if heat_delta > 0:
            notes.append(f"Heat +{heat_delta}: Visibility/social friction prominent")
        if faction_updates:
            notes.append("Faction attention suggested: Select factions to update")
        if candidate_scars:
            notes.append(f"Scar candidates: {len(candidate_scars)} suggested based on intensity")
        
        return SessionPacket(
            scenario_name=scenario_name,
            preset=preset,
            phase=phase,
            rarity_mode=rarity_mode,
            seed=seed,
            batch_size=batch_size,
            severity_avg=severity_avg,
            cutoff_rate=cutoff_rate,
            top_tags=top_tags,
            top_events=top_events,
            suggested_pressure_delta=pressure_delta,
            suggested_heat_delta=heat_delta,
            suggested_faction_updates=faction_updates,
            candidate_scars=candidate_scars,
            notes=notes,
        )
