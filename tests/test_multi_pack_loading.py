"""Tests for multi-pack content loading functionality."""

import json
from pathlib import Path
import pytest

from spar_engine.content import load_pack, load_packs


def test_load_packs_empty_list():
    """Empty pack list returns empty entry list."""
    entries = load_packs([])
    assert entries == []


def test_load_packs_single_pack():
    """Single pack loads correctly via load_packs()."""
    pack_path = Path(__file__).parent.parent / "data" / "core_complications.json"
    
    # Load via load_packs (new function)
    entries_multi = load_packs([pack_path])
    
    # Load via load_pack (original function)
    entries_single = load_pack(pack_path)
    
    # Should produce identical results
    assert len(entries_multi) == len(entries_single)
    assert [e.event_id for e in entries_multi] == [e.event_id for e in entries_single]


def test_load_packs_multiple_packs(tmp_path):
    """Multiple packs merge into union pool."""
    # Create two small test packs
    pack1 = [
        {
            "event_id": "test_01",
            "title": "Test Event 1",
            "tags": ["hazard"],
            "allowed_environments": ["confined"],
            "allowed_scene_phases": ["engage"],
            "severity_band": [1, 5],
            "weight": 1.0,
            "cooldown": {"event": 0, "tags": {}},
            "effect_vector_template": {"threat": [0, 2]},
            "fiction": {"prompt": "Test 1"}
        }
    ]
    
    pack2 = [
        {
            "event_id": "test_02",
            "title": "Test Event 2",
            "tags": ["social_friction"],
            "allowed_environments": ["populated"],
            "allowed_scene_phases": ["approach"],
            "severity_band": [2, 6],
            "weight": 0.8,
            "cooldown": {"event": 0, "tags": {}},
            "effect_vector_template": {"cost": [1, 3]},
            "fiction": {"prompt": "Test 2"}
        }
    ]
    
    # Write packs to temp files
    pack1_path = tmp_path / "pack1.json"
    pack2_path = tmp_path / "pack2.json"
    pack1_path.write_text(json.dumps(pack1))
    pack2_path.write_text(json.dumps(pack2))
    
    # Load both packs
    entries = load_packs([pack1_path, pack2_path])
    
    # Verify union
    assert len(entries) == 2
    assert entries[0].event_id == "test_01"
    assert entries[1].event_id == "test_02"


def test_load_packs_duplicate_event_ids(tmp_path):
    """Duplicate event_ids: last pack wins."""
    # Create two packs with same event_id but different content
    pack1 = [
        {
            "event_id": "duplicate_01",
            "title": "First Version",
            "tags": ["hazard"],
            "allowed_environments": ["confined"],
            "allowed_scene_phases": ["engage"],
            "severity_band": [1, 5],
            "weight": 1.0,
            "cooldown": {"event": 0, "tags": {}},
            "effect_vector_template": {},
            "fiction": {"prompt": "First"}
        }
    ]
    
    pack2 = [
        {
            "event_id": "duplicate_01",
            "title": "Second Version",
            "tags": ["social_friction"],
            "allowed_environments": ["populated"],
            "allowed_scene_phases": ["approach"],
            "severity_band": [2, 6],
            "weight": 0.8,
            "cooldown": {"event": 0, "tags": {}},
            "effect_vector_template": {},
            "fiction": {"prompt": "Second"}
        }
    ]
    
    pack1_path = tmp_path / "pack1.json"
    pack2_path = tmp_path / "pack2.json"
    pack1_path.write_text(json.dumps(pack1))
    pack2_path.write_text(json.dumps(pack2))
    
    # Load both - pack2 should win
    entries = load_packs([pack1_path, pack2_path])
    
    # Both entries present (no deduplication yet - that would be enhancement)
    assert len(entries) == 2
    # Last one (pack2) is at end
    assert entries[1].title == "Second Version"
    assert entries[1].fiction_prompt == "Second"


def test_load_packs_preserves_pack_order(tmp_path):
    """Pack load order is preserved in output."""
    pack1 = [{"event_id": "a", "title": "A", "tags": [], "severity_band": [1,5], "fiction": {}}]
    pack2 = [{"event_id": "b", "title": "B", "tags": [], "severity_band": [1,5], "fiction": {}}]
    pack3 = [{"event_id": "c", "title": "C", "tags": [], "severity_band": [1,5], "fiction": {}}]
    
    for i, pack_data in enumerate([pack1, pack2, pack3], 1):
        (tmp_path / f"pack{i}.json").write_text(json.dumps(pack_data))
    
    paths = [tmp_path / f"pack{i}.json" for i in [1, 2, 3]]
    entries = load_packs(paths)
    
    assert len(entries) == 3
    assert [e.event_id for e in entries] == ["a", "b", "c"]


def test_load_packs_maintains_entry_structure(tmp_path):
    """All ContentEntry fields preserved through multi-pack loading."""
    pack = [{
        "event_id": "full_test",
        "title": "Full Test",
        "tags": ["hazard", "visibility"],
        "allowed_environments": ["confined", "populated"],
        "allowed_scene_phases": ["engage", "aftermath"],
        "severity_band": [3, 8],
        "weight": 0.9,
        "cooldown": {"event": 2, "tags": {"hazard": 2, "visibility": 1}},
        "effect_vector_template": {"threat": [1, 3], "heat": [0, 2]},
        "fiction": {
            "prompt": "Test prompt",
            "sensory": ["sound", "sight"],
            "immediate_choice": ["Choice A", "Choice B"]
        }
    }]
    
    pack_path = tmp_path / "test.json"
    pack_path.write_text(json.dumps(pack))
    
    entries = load_packs([pack_path])
    entry = entries[0]
    
    assert entry.event_id == "full_test"
    assert entry.title == "Full Test"
    assert entry.tags == ["hazard", "visibility"]
    assert entry.allowed_environments == ["confined", "populated"]
    assert entry.allowed_scene_phases == ["engage", "aftermath"]
    assert entry.severity_band == (3, 8)
    assert entry.weight == 0.9
    assert entry.cooldown_event == 2
    assert entry.cooldown_tags == {"hazard": 2, "visibility": 1}
    assert entry.effect_vector_template == {"threat": (1, 3), "heat": (0, 2)}
    assert entry.fiction_prompt == "Test prompt"
    assert entry.fiction_sensory == ["sound", "sight"]
    assert entry.fiction_choices == ["Choice A", "Choice B"]
