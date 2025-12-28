"""Tests for multi-pack integration with Campaign model.

Tests campaign-level content pack selection and loading.
"""

import json
from pathlib import Path
import tempfile

import pytest

from streamlit_harness.campaign_ui import Campaign, discover_content_packs
from spar_campaign import CampaignState


def test_campaign_default_has_core_pack():
    """New campaigns default to core event pack and One Loot Table."""
    campaign = Campaign(
        campaign_id="test_123",
        name="Test Campaign",
        created="2025-01-01T00:00:00",
        last_played="2025-01-01T00:00:00",
    )
    
    # Multi-generator pack system v1.0: defaults to core_complications + one_loot_table
    assert campaign.enabled_content_packs == ["data/core_complications.json", "data/one_loot_table.json"]
    assert len(campaign.enabled_content_packs) == 2


def test_campaign_serialization_includes_packs():
    """Campaign serialization includes enabled_content_packs field."""
    campaign = Campaign(
        campaign_id="test_123",
        name="Test Campaign",
        created="2025-01-01T00:00:00",
        last_played="2025-01-01T00:00:00",
        enabled_content_packs=["data/core_complications.json", "data/pack2.json"],
    )
    
    data = campaign.to_dict()
    
    assert "enabled_content_packs" in data
    assert data["enabled_content_packs"] == ["data/core_complications.json", "data/pack2.json"]


def test_campaign_deserialization_backward_compatible():
    """Campaign deserialization handles missing enabled_content_packs (backward compatibility)."""
    # Old format without enabled_content_packs
    data = {
        "campaign_id": "test_123",
        "name": "Test Campaign",
        "created": "2025-01-01T00:00:00",
        "last_played": "2025-01-01T00:00:00",
        "canon_summary": [],
        "campaign_state": None,
        "ledger": [],
        "sources": [],
        "prep_queue": [],
        # No enabled_content_packs field
    }
    
    campaign = Campaign.from_dict(data)
    
    # Should default to core pack
    assert campaign.enabled_content_packs == ["data/core_complications.json"]
    assert len(campaign.enabled_content_packs) == 1


def test_campaign_roundtrip_preserves_packs():
    """Campaign roundtrip serialization preserves enabled_content_packs."""
    original = Campaign(
        campaign_id="test_123",
        name="Test Campaign",
        created="2025-01-01T00:00:00",
        last_played="2025-01-01T00:00:00",
        enabled_content_packs=["data/core_complications.json", "data/urban.json"],
    )
    
    # Serialize and deserialize
    data = original.to_dict()
    restored = Campaign.from_dict(data)
    
    assert restored.enabled_content_packs == ["data/core_complications.json", "data/urban.json"]


def test_discover_content_packs_returns_core():
    """Pack discovery returns at least the core packs (event and loot)."""
    packs = discover_content_packs()
    
    # Should find both core packs
    assert len(packs) >= 2
    
    # Core packs sorted first
    assert packs[0]["path"] == "data/core_complications.json"
    assert packs[0]["name"] == "Core Complications"
    assert packs[0]["generator_type"] == "event"
    assert packs[0]["is_core"] is True
    assert packs[0]["entry_count"] > 0
    
    assert packs[1]["path"] == "data/core_loot_situations.json"
    assert packs[1]["name"] == "Core Loot Situations"
    assert packs[1]["generator_type"] == "loot"
    assert packs[1]["is_core"] is True
    assert packs[1]["entry_count"] > 0


def test_discover_content_packs_structure():
    """Pack discovery returns properly structured pack metadata with generator_type."""
    packs = discover_content_packs()
    core_pack = packs[0]
    
    # Verify all required fields present (multi-generator pack system v1.0)
    assert "path" in core_pack
    assert "name" in core_pack
    assert "description" in core_pack
    assert "generator_type" in core_pack
    assert "entry_count" in core_pack
    assert "is_core" in core_pack
    
    # Verify types
    assert isinstance(core_pack["path"], str)
    assert isinstance(core_pack["name"], str)
    assert isinstance(core_pack["description"], str)
    assert isinstance(core_pack["generator_type"], str)
    assert isinstance(core_pack["entry_count"], int)
    assert isinstance(core_pack["is_core"], bool)
    
    # Verify generator_type is valid
    assert core_pack["generator_type"] in ["event", "loot", "rumor", "npc"]


def test_campaign_with_multiple_packs():
    """Campaign can have multiple packs enabled."""
    campaign = Campaign(
        campaign_id="test_123",
        name="Multi-Pack Campaign",
        created="2025-01-01T00:00:00",
        last_played="2025-01-01T00:00:00",
        enabled_content_packs=[
            "data/core_complications.json",
            "data/pack2.json",
            "data/pack3.json",
        ],
    )
    
    assert len(campaign.enabled_content_packs) == 3
    assert "data/core_complications.json" in campaign.enabled_content_packs


def test_campaign_can_toggle_packs():
    """Campaign pack list can be modified."""
    campaign = Campaign(
        campaign_id="test_123",
        name="Test Campaign",
        created="2025-01-01T00:00:00",
        last_played="2025-01-01T00:00:00",
        enabled_content_packs=["data/core_complications.json"],
    )
    
    # Add a pack
    campaign.enabled_content_packs.append("data/urban.json")
    assert len(campaign.enabled_content_packs) == 2
    
    # Remove a pack
    campaign.enabled_content_packs.remove("data/urban.json")
    assert len(campaign.enabled_content_packs) == 1


def test_campaign_save_load_with_packs(tmp_path):
    """Campaign save/load roundtrip preserves pack configuration."""
    # Create campaign with custom packs
    campaign = Campaign(
        campaign_id="test_save_load",
        name="Test Campaign",
        created="2025-01-01T00:00:00",
        last_played="2025-01-01T00:00:00",
        campaign_state=CampaignState.default(),
        enabled_content_packs=["data/core_complications.json", "data/custom.json"],
    )
    
    # Save to temp file
    save_path = tmp_path / "test_campaign.json"
    save_path.write_text(json.dumps(campaign.to_dict(), indent=2))
    
    # Load back
    data = json.loads(save_path.read_text())
    loaded = Campaign.from_dict(data)
    
    assert loaded.enabled_content_packs == ["data/core_complications.json", "data/custom.json"]
    assert loaded.campaign_id == "test_save_load"
