"""Import overrides for campaign history parsing.

Stores per-campaign GM corrections to entity classification.
Enables persistent promote/demote decisions across imports.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


CAMPAIGNS_DIR = Path("campaigns")


@dataclass
class ImportOverrides:
    """Per-campaign import classification overrides.
    
    Stores GM corrections to heuristic entity classification.
    Persists across imports to avoid repeated corrections.
    """
    
    campaign_id: str
    promoted_to_faction: Set[str] = field(default_factory=set)
    demoted_to_place: Set[str] = field(default_factory=set)
    demoted_to_artifact: Set[str] = field(default_factory=set)
    demoted_to_concept: Set[str] = field(default_factory=set)
    ignored: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        """Serialize to dict for JSON storage."""
        return {
            "campaign_id": self.campaign_id,
            "promoted_to_faction": list(self.promoted_to_faction),
            "demoted_to_place": list(self.demoted_to_place),
            "demoted_to_artifact": list(self.demoted_to_artifact),
            "demoted_to_concept": list(self.demoted_to_concept),
            "ignored": list(self.ignored),
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "ImportOverrides":
        """Deserialize from dict."""
        return ImportOverrides(
            campaign_id=data["campaign_id"],
            promoted_to_faction=set(data.get("promoted_to_faction", [])),
            demoted_to_place=set(data.get("demoted_to_place", [])),
            demoted_to_artifact=set(data.get("demoted_to_artifact", [])),
            demoted_to_concept=set(data.get("demoted_to_concept", [])),
            ignored=set(data.get("ignored", [])),
        )
    
    def get_path(self) -> Path:
        """Get filesystem path for this override file (searches subdirectories)."""
        # Search all subdirectories for the override file
        for subdir in CAMPAIGNS_DIR.iterdir():
            if subdir.is_dir():
                path = subdir / f"{self.campaign_id}_import_overrides.json"
                if path.exists():
                    return path
        
        # If not found, need to determine which subdirectory to use
        # Load the campaign to get its name
        for subdir in CAMPAIGNS_DIR.iterdir():
            if subdir.is_dir():
                campaign_path = subdir / f"{self.campaign_id}.json"
                if campaign_path.exists():
                    # Return path in this subdirectory
                    return subdir / f"{self.campaign_id}_import_overrides.json"
        
        # Fallback: use campaigns root (shouldn't happen in normal operation)
        return CAMPAIGNS_DIR / f"{self.campaign_id}_import_overrides.json"
    
    def save(self) -> None:
        """Save overrides to disk in subdirectory."""
        path = self.get_path()
        path.parent.mkdir(parents=True, exist_ok=True)  # Ensure subdirectory exists
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @staticmethod
    def load(campaign_id: str) -> "ImportOverrides":
        """Load overrides from disk (searches subdirectories), or create new if doesn't exist."""
        # Search all subdirectories for the override file
        for subdir in CAMPAIGNS_DIR.iterdir():
            if subdir.is_dir():
                path = subdir / f"{campaign_id}_import_overrides.json"
                if path.exists():
                    try:
                        data = json.loads(path.read_text())
                        return ImportOverrides.from_dict(data)
                    except Exception:
                        pass
        
        # Return empty overrides if not found
        return ImportOverrides(campaign_id=campaign_id)
    
    def apply_to_parsed(self, parsed: Dict) -> Dict:
        """Apply overrides to parsed history data.
        
        Moves entities between categories based on GM corrections.
        Returns modified parsed dict (non-destructive).
        """
        # Start with copy of original classifications
        factions = set(parsed.get("factions", []))
        entities = parsed.get("entities", {})
        places = set(entities.get("places", []))
        artifacts = set(entities.get("artifacts", []))
        concepts = set(entities.get("concepts", []))
        
        # Apply promotions to faction
        for name in self.promoted_to_faction:
            # Remove from other categories
            places.discard(name)
            artifacts.discard(name)
            concepts.discard(name)
            # Add to factions
            factions.add(name)
        
        # Apply demotions
        for name in self.demoted_to_place:
            factions.discard(name)
            places.add(name)
        
        for name in self.demoted_to_artifact:
            factions.discard(name)
            artifacts.add(name)
        
        for name in self.demoted_to_concept:
            factions.discard(name)
            concepts.add(name)
        
        # Apply ignored
        for name in self.ignored:
            factions.discard(name)
            places.discard(name)
            artifacts.discard(name)
            concepts.discard(name)
        
        # Return modified dict
        return {
            **parsed,
            "factions": sorted(factions),
            "entities": {
                "places": sorted(places),
                "artifacts": sorted(artifacts),
                "concepts": sorted(concepts),
            },
        }
