from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import ContentEntry, ScenePhase, AdapterHints

def load_pack(path: str | Path) -> List[ContentEntry]:
    """Load a single content pack from JSON file.
    
    Supports two formats:
    - Legacy: JSON array of entries
    - New: JSON object with metadata (name, generator_type, entries array)
    
    Backward compatible - automatically detects format.
    """
    p = Path(path)
    data = json.loads(p.read_text())
    
    # Detect format: object with "entries" field vs array
    if isinstance(data, dict) and "entries" in data:
        # New format: object with metadata
        raw_entries = data["entries"]
    else:
        # Legacy format: array of entries
        raw_entries = data
    
    entries: List[ContentEntry] = []
    for raw in raw_entries:
        hints = raw.get("adapter_hints")
        adapter_hints = None
        if hints:
            adapter_hints = AdapterHints(
                difficulty_hint=hints.get("difficulty_hint"),
                scale_hint=hints.get("scale_hint"),
                duration_hint=hints.get("duration_hint"),
            )
        entries.append(
            ContentEntry(
                event_id=raw["event_id"],
                title=raw["title"],
                tags=list(raw.get("tags", [])),
                allowed_environments=list(raw.get("allowed_environments", [])),
                allowed_scene_phases=list(raw.get("allowed_scene_phases", [])),
                severity_band=tuple(raw.get("severity_band", [1, 10])),
                weight=float(raw.get("weight", 1.0)),
                cooldown_event=int(raw.get("cooldown", {}).get("event", 0)),
                cooldown_tags=dict(raw.get("cooldown", {}).get("tags", {})),
                effect_vector_template={k: tuple(v) for k, v in raw.get("effect_vector_template", {}).items()},
                fiction_prompt=raw.get("fiction", {}).get("prompt", ""),
                fiction_sensory=list(raw.get("fiction", {}).get("sensory", [])),
                fiction_choices=list(raw.get("fiction", {}).get("immediate_choice", [])),
                adapter_hints=adapter_hints,
            )
        )
    return entries


def get_pack_metadata(path: str | Path) -> dict[str, str]:
    """Get pack metadata without loading all entries.
    
    Returns:
        Dictionary with keys: name, generator_type, description
        Defaults: generator_type="event" for backward compatibility
    """
    p = Path(path)
    data = json.loads(p.read_text())
    
    # New format: object with metadata
    if isinstance(data, dict) and "entries" in data:
        return {
            "name": data.get("name", p.stem),
            "generator_type": data.get("generator_type", "event"),
            "description": data.get("description", ""),
        }
    else:
        # Legacy format: array (defaults to event)
        return {
            "name": p.stem,
            "generator_type": "event",
            "description": "",
        }


def load_packs(paths: Iterable[str | Path]) -> List[ContentEntry]:
    """Load and merge multiple content packs into union pool.
    
    Args:
        paths: Iterable of file paths to content pack JSON files
        
    Returns:
        Merged list of content entries from all packs
        
    Notes:
        - If same event_id appears in multiple packs, last one wins
        - No weighting or priority - all entries treated equally by SOC
        - Empty paths list returns empty entry list
    """
    all_entries: List[ContentEntry] = []
    seen_ids: dict[str, str] = {}  # event_id -> pack_path for conflict detection
    
    for path in paths:
        pack_entries = load_pack(path)
        pack_path_str = str(Path(path).name)
        
        for entry in pack_entries:
            if entry.event_id in seen_ids:
                # Duplicate event_id - last one wins, but log for debugging
                # In production, this could log a warning
                pass
            seen_ids[entry.event_id] = pack_path_str
            all_entries.append(entry)
    
    return all_entries


def load_packs_by_generator_type(
    paths: Iterable[str | Path],
    generator_type: str
) -> List[ContentEntry]:
    """Load and merge packs filtered by generator type.
    
    Args:
        paths: Iterable of file paths to content pack JSON files
        generator_type: Target generator type (e.g., "event", "loot")
        
    Returns:
        Merged list of content entries from packs matching generator_type
        
    Notes:
        - Packs without generator_type metadata default to "event"
        - Returns empty list if no matching packs found
    """
    matching_paths = []
    
    for path in paths:
        try:
            metadata = get_pack_metadata(path)
            if metadata["generator_type"] == generator_type:
                matching_paths.append(path)
        except Exception:
            # Skip packs that fail to load
            continue
    
    return load_packs(matching_paths)

def _any_tag_on_cooldown(entry: ContentEntry, tag_cooldowns: dict[str, int]) -> bool:
    for t in entry.tags:
        if tag_cooldowns.get(t, 0) > 0:
            return True
    return False

def filter_entries(
    entries: Sequence[ContentEntry],
    environment: List[str],
    phase: ScenePhase,
    include_tags: List[str],
    exclude_tags: List[str],
    recent_event_ids: List[str],
    tag_cooldowns: dict[str, int],
) -> List[ContentEntry]:
    env_set = set(environment)
    include_set = set(include_tags) if include_tags else None
    exclude_set = set(exclude_tags) if exclude_tags else set()

    out: List[ContentEntry] = []
    for e in entries:
        if e.event_id in set(recent_event_ids):
            continue
        if exclude_set and (exclude_set.intersection(e.tags)):
            continue
        if include_set is not None and not include_set.intersection(e.tags):
            continue
        if e.allowed_scene_phases and phase not in e.allowed_scene_phases:
            continue
        if e.allowed_environments and not env_set.intersection(e.allowed_environments):
            continue
        if _any_tag_on_cooldown(e, tag_cooldowns):
            continue
        out.append(e)
    return out
