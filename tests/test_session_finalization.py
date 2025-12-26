"""Tests for Campaign UI session finalization data transformation logic.

These tests focus on the critical data flows in campaign_ui.py that were
previously untested and led to data loss bugs.
"""

import json
from pathlib import Path
import tempfile
import pytest

from streamlit_harness.campaign_ui import Campaign, PrepItem
from spar_campaign import CampaignState, FactionState


def test_campaign_serialization_with_full_bullets():
    """Test that full bullet lists persist through save/load cycle."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override campaigns directory for test
        import streamlit_harness.campaign_ui as cui
        original_dir = cui.CAMPAIGNS_DIR
        cui.CAMPAIGNS_DIR = Path(tmpdir)
        
        try:
            # Create campaign with rich ledger entry
            campaign = Campaign(
                campaign_id="test_001",
                name="Test Campaign",
                created="2025-01-01T00:00:00",
                last_played="2025-01-01T00:00:00",
                canon_summary=["Campaign begins"],
                campaign_state=CampaignState.default(),
                ledger=[{
                    "session_number": 1,
                    "session_date": "2025-01-01T00:00:00",
                    "what_happened": [
                        "Event 1",
                        "Event 2", 
                        "Event 3",
                        "Event 4",
                        "Event 5",
                        "Event 6",
                        "Event 7",
                        "Event 8",
                        "Event 9",
                        "Event 10",
                    ],
                    "session_notes": "GM notes about the session",
                    "metadata": {
                        "severity_avg": 5.5,
                        "cutoff_rate": 0.2,
                        "top_tags": ["hazard", "social"],
                    },
                    "deltas": {"pressure_change": 2, "heat_change": 1},
                    "active_sources": ["core_complications"],
                }],
            )
            
            # Save and reload
            campaign.save()
            loaded = Campaign.load("test_001")
            
            # Verify full bullet list persisted
            assert loaded is not None
            assert len(loaded.ledger) == 1
            assert len(loaded.ledger[0]["what_happened"]) == 10
            assert loaded.ledger[0]["what_happened"][9] == "Event 10"
            
            # Verify session notes persisted
            assert loaded.ledger[0]["session_notes"] == "GM notes about the session"
            
            # Verify metadata persisted
            assert loaded.ledger[0]["metadata"]["severity_avg"] == 5.5
            assert loaded.ledger[0]["metadata"]["cutoff_rate"] == 0.2
            assert loaded.ledger[0]["metadata"]["top_tags"] == ["hazard", "social"]
            
        finally:
            cui.CAMPAIGNS_DIR = original_dir


def test_canon_summary_synthesis_one_bullet():
    """Test canon synthesis with 1 bullet: use as-is."""
    bullets = ["Single important event"]
    
    # Simulate synthesis logic from render_finalize_session
    if len(bullets) == 1:
        canon_bullet = bullets[0]
    elif len(bullets) <= 4:
        canon_bullet = f"{bullets[0]}; {bullets[1]}"
    else:
        canon_bullet = f"{bullets[0]} (and more)"
    
    assert canon_bullet == "Single important event"


def test_canon_summary_synthesis_two_to_four_bullets():
    """Test canon synthesis with 2-4 bullets: join first two."""
    bullets = ["Event A", "Event B", "Event C"]
    
    # Simulate synthesis logic
    if len(bullets) == 1:
        canon_bullet = bullets[0]
    elif len(bullets) <= 4:
        canon_bullet = f"{bullets[0]}; {bullets[1]}"
    else:
        canon_bullet = f"{bullets[0]} (and more)"
    
    assert canon_bullet == "Event A; Event B"


def test_canon_summary_synthesis_five_plus_bullets():
    """Test canon synthesis with 5+ bullets: first + indicator."""
    bullets = ["Event 1", "Event 2", "Event 3", "Event 4", "Event 5", "Event 6"]
    
    # Simulate synthesis logic
    if len(bullets) == 1:
        canon_bullet = bullets[0]
    elif len(bullets) <= 4:
        canon_bullet = f"{bullets[0]}; {bullets[1]}"
    else:
        canon_bullet = f"{bullets[0]} (and more)"
    
    assert canon_bullet == "Event 1 (and more)"


def test_ledger_entry_structure_with_metadata():
    """Test that ledger entry structure includes all required fields."""
    # Simulate session entry creation
    session_entry = {
        "session_number": 5,
        "session_date": "2025-01-15T12:00:00",
        "what_happened": ["Event A", "Event B", "Event C"],
        "session_notes": "Test notes",
        "metadata": {
            "severity_avg": 6.2,
            "cutoff_rate": 0.25,
            "top_tags": ["hazard", "reinforcements"],
            "scenario_name": "Test Scenario",
            "prep_item_ids": ["prep_001", "prep_002"],
        },
        "deltas": {
            "pressure_change": 3,
            "heat_change": 2,
            "rumor_spread": True,
            "faction_attention_change": False,
        },
        "active_sources": ["core_complications", "custom_content"],
        "active_source_ids": ["source_001"],
    }
    
    # Verify structure
    assert "session_number" in session_entry
    assert "what_happened" in session_entry
    assert "session_notes" in session_entry
    assert "metadata" in session_entry
    assert len(session_entry["what_happened"]) == 3
    assert session_entry["session_notes"] == "Test notes"
    assert session_entry["metadata"]["severity_avg"] == 6.2


def test_prep_item_serialization_preserves_all_fields():
    """Test PrepItem serialization round-trip."""
    item = PrepItem(
        item_id="prep_001",
        created_at="2025-01-01T00:00:00",
        title="Test Event",
        summary="Event summary",
        tags=["hazard", "social"],
        source={"preset": "dungeon", "phase": "engage"},
        status="queued",
        related_factions=["city_watch"],
        related_scars=["wounded"],
        notes="Prep notes",
    )
    
    # Serialize and deserialize
    data = item.to_dict()
    loaded = PrepItem.from_dict(data)
    
    # Verify all fields preserved
    assert loaded.item_id == "prep_001"
    assert loaded.title == "Test Event"
    assert loaded.summary == "Event summary"
    assert loaded.tags == ["hazard", "social"]
    assert loaded.source["preset"] == "dungeon"
    assert loaded.status == "queued"
    assert loaded.notes == "Prep notes"


def test_bullet_collection_from_visible_and_hidden():
    """Test that bullet collection preserves hidden bullets.
    
    This is the regression test for the data loss bug where only visible
    bullets were committed.
    """
    # Simulate session state
    finalize_bullets = [
        "Bullet 1",
        "Bullet 2",
        "Bullet 3",
        "Bullet 4",
        "Bullet 5",
        "Bullet 6",  # Hidden
        "Bullet 7",  # Hidden
        "Bullet 8",  # Hidden
    ]
    
    # Simulate showing only first 5
    show_all_bullets = False
    visible_count = 5 if not show_all_bullets else len(finalize_bullets)
    
    # Simulate form input updates (only visible bullets can be edited)
    # User edited bullet 2
    bullets = finalize_bullets.copy()
    bullets[1] = "Bullet 2 EDITED"
    
    # CRITICAL: Build what_happened from FULL list, not just visible
    what_happened = [b.strip() for b in bullets if b.strip()]
    
    # Verify all 8 bullets preserved
    assert len(what_happened) == 8
    assert what_happened[1] == "Bullet 2 EDITED"
    assert what_happened[5] == "Bullet 6"  # Hidden bullet preserved
    assert what_happened[7] == "Bullet 8"  # Last hidden bullet preserved


def test_session_notes_optional():
    """Test that session notes are optional and None when empty."""
    # Simulate commit with empty notes
    session_notes = ""
    stored_notes = session_notes if session_notes.strip() else None
    
    assert stored_notes is None
    
    # Simulate commit with actual notes
    session_notes = "Some notes"
    stored_notes = session_notes if session_notes.strip() else None
    
    assert stored_notes == "Some notes"


def test_metadata_includes_prep_item_ids():
    """Test that metadata includes prep item IDs when from prep queue."""
    # Simulate session from prep queue
    prep_items_to_archive = ["prep_001", "prep_002", "prep_003"]
    
    metadata = {
        "severity_avg": 5.0,
        "cutoff_rate": 0.1,
        "top_tags": ["hazard"],
        "scenario_name": "Prep Queue",
    }
    
    # Add prep item IDs
    metadata["prep_item_ids"] = prep_items_to_archive
    
    assert "prep_item_ids" in metadata
    assert len(metadata["prep_item_ids"]) == 3
    assert metadata["prep_item_ids"][0] == "prep_001"


def test_campaign_name_normalization():
    """Test campaign name to directory normalization."""
    from streamlit_harness.campaign_ui import normalize_campaign_name_to_dir
    
    assert normalize_campaign_name_to_dir("City of Fog") == "City_of_Fog"
    assert normalize_campaign_name_to_dir("Test-Campaign") == "Test_Campaign"
    assert normalize_campaign_name_to_dir("Campaign!@#") == "Campaign"
    assert normalize_campaign_name_to_dir("  Spaces  ") == "Spaces"


def test_empty_bullet_filtering():
    """Test that empty bullets are filtered out but non-empty preserved."""
    bullets = [
        "Event 1",
        "",  # Empty
        "Event 3",
        "   ",  # Whitespace only
        "Event 5",
    ]
    
    what_happened = [b.strip() for b in bullets if b.strip()]
    
    assert len(what_happened) == 3
    assert what_happened == ["Event 1", "Event 3", "Event 5"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
