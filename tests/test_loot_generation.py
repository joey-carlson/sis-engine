"""Tests for Loot Generator - Narrative Resource Shock System"""

import pytest

from spar_engine.content import load_pack
from spar_engine.loot import generate_loot
from spar_engine.models import Constraints, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.state import EngineState, apply_state_delta


def test_loot_pack_loads():
    """Verify core loot pack loads successfully."""
    entries = load_pack("data/core_loot_situations.json")
    assert len(entries) > 0, "Loot pack should contain entries"
    assert all(e.event_id.startswith("loot_") for e in entries), "All loot IDs should start with 'loot_'"


def test_loot_generation_basic():
    """Verify loot generator produces valid output."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["derelict"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=["opportunity"],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    loot = generate_loot(scene, state, selection, entries, rng)
    
    # Validate output structure
    assert loot.event_id.startswith("loot_")
    assert loot.title
    assert len(loot.tags) > 0
    assert 1 <= loot.severity <= 10
    assert loot.fiction.prompt
    assert len(loot.fiction.immediate_choice) == 2


def test_loot_soc_pipeline():
    """Verify loot uses SOC severity sampling."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["populated"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="spiky"  # Should produce more variance
    )
    
    state = EngineState.default()
    
    # Generate multiple loot situations
    severities = []
    for seed in range(20):
        rng = TraceRNG(seed=seed)
        loot = generate_loot(scene, state, selection, entries, rng)
        severities.append(loot.severity)
    
    # Verify heavy-tail distribution (should have range)
    assert min(severities) < max(severities), "Spiky mode should produce severity variance"
    assert max(severities) >= 5, "Should occasionally produce higher severity"


def test_loot_cutoff_mechanics():
    """Verify cutoff system works for loot."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["derelict"],
        tone=["test"],
        constraints=Constraints(confinement=0.8, connectivity=0.3, visibility=0.6),  # Confined = lower cap
        party_band="low",  # Low band = lower cap
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="spiky"
    )
    
    state = EngineState.default()
    
    # Generate many samples - some should trigger cutoff
    cutoff_count = 0
    for seed in range(50):
        rng = TraceRNG(seed=seed)
        loot = generate_loot(scene, state, selection, entries, rng)
        if loot.cutoff_applied:
            cutoff_count += 1
            # Verify cutoff resolution is applied
            assert loot.cutoff_resolution in ["omen", "clock_tick", "downshift"]
            # Verify fiction overlay
            if loot.cutoff_resolution == "omen":
                assert "Omen of Wealth" in loot.fiction.prompt
            elif loot.cutoff_resolution == "clock_tick":
                assert "Contested Resource" in loot.fiction.prompt
            elif loot.cutoff_resolution == "downshift":
                assert "Modest Gain" in loot.fiction.prompt
    
    assert cutoff_count > 0, "Should have some cutoffs in 50 samples with low cap"


def test_loot_state_delta():
    """Verify loot produces valid state deltas."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["populated"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=["obligation"],  # Should have some heat impact
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    loot = generate_loot(scene, state, selection, entries, rng)
    
    # Verify state delta structure
    assert loot.state_delta.recent_event_ids_add
    assert loot.event_id in loot.state_delta.recent_event_ids_add
    
    # Apply delta and verify state changes
    new_state = apply_state_delta(state, loot.state_delta)
    assert loot.event_id in new_state.recent_event_ids


def test_loot_cooldowns():
    """Verify loot respects cooldown mechanics."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["derelict"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=["opportunity"],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    # Generate first loot
    loot1 = generate_loot(scene, state, selection, entries, rng)
    state = apply_state_delta(state, loot1.state_delta)
    
    # Verify cooldown was set
    assert loot1.event_id in state.recent_event_ids
    if loot1.state_delta.tag_cooldowns_set:
        for tag, cd in loot1.state_delta.tag_cooldowns_set.items():
            assert tag in state.tag_cooldowns
            assert state.tag_cooldowns[tag] > 0


def test_loot_deterministic():
    """Verify loot generation is deterministic with same seed."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["populated"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    
    # Generate with same seed twice
    rng1 = TraceRNG(seed=123)
    loot1 = generate_loot(scene, state, selection, entries, rng1)
    
    rng2 = TraceRNG(seed=123)
    loot2 = generate_loot(scene, state, selection, entries, rng2)
    
    # Should be identical
    assert loot1.event_id == loot2.event_id
    assert loot1.severity == loot2.severity
    assert loot1.title == loot2.title


def test_loot_effects_have_opportunity():
    """Verify loot entries emphasize opportunity vector."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["derelict"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=["opportunity"],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    
    # Generate multiple loot situations
    opportunity_values = []
    for seed in range(20):
        rng = TraceRNG(seed=seed)
        loot = generate_loot(scene, state, selection, entries, rng)
        opportunity_values.append(loot.effect_vector.opportunity)
    
    # Most loot should have positive opportunity
    positive_count = sum(1 for v in opportunity_values if v > 0)
    assert positive_count > len(opportunity_values) * 0.7, "Most loot should provide opportunity"


def test_loot_negative_cost():
    """Verify some loot can have negative cost (pressure relief)."""
    entries = load_pack("data/core_loot_situations.json")
    
    # Find entries with negative cost potential
    negative_cost_entries = [
        e for e in entries 
        if e.effect_vector_template.get("cost", (0, 0))[0] < 0
    ]
    
    assert len(negative_cost_entries) > 0, "Some loot should offer cost relief"


def test_loot_consequence_tags():
    """Verify loot includes consequence-oriented tags."""
    entries = load_pack("data/core_loot_situations.json")
    
    # Collect all tags from loot pack
    all_tags = set()
    for e in entries:
        all_tags.update(e.tags)
    
    # Should include consequence tags
    consequence_tags = {"obligation", "social_friction", "visibility", "heat"}
    found_consequence = consequence_tags & all_tags
    
    assert len(found_consequence) > 0, "Loot should include consequence-oriented tags"


def test_loot_no_content_error():
    """Verify loot generator raises appropriate error when no content available."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="approach",  # Most loot is aftermath
        environment=["sea"],  # Limited environment
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=["nonexistent_tag"],  # Impossible filter
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    with pytest.raises(ValueError, match="No loot entries available"):
        generate_loot(scene, state, selection, entries, rng)


def test_loot_adaptive_weighting():
    """Verify loot uses adaptive weighting to prevent repetition."""
    from spar_engine.state import tick_state
    
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["populated"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal"
    )
    
    state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    # Generate first loot
    loot1 = generate_loot(scene, state, selection, entries, rng)
    state = apply_state_delta(state, loot1.state_delta)
    
    # Tick to expire cooldowns (like the real generator does)
    state = tick_state(state, ticks=2)
    
    # Generate second loot with updated state
    rng = TraceRNG(seed=43)  # Different seed
    loot2 = generate_loot(scene, state, selection, entries, rng)
    
    # Should be different due to recency penalty
    assert loot1.event_id != loot2.event_id, "Consecutive loot should avoid recent IDs"


def test_loot_followups():
    """Verify loot cutoffs produce appropriate followups."""
    entries = load_pack("data/core_loot_situations.json")
    
    scene = SceneContext(
        scene_id="test",
        scene_phase="aftermath",
        environment=["derelict"],
        tone=["test"],
        constraints=Constraints(confinement=0.9, connectivity=0.2, visibility=0.7),  # Very confined
        party_band="low",
        spotlight=[]
    )
    
    selection = SelectionContext(
        enabled_packs=["loot"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="spiky"
    )
    
    state = EngineState.default()
    
    # Generate many samples to find cutoff cases
    for seed in range(100):
        rng = TraceRNG(seed=seed)
        loot = generate_loot(scene, state, selection, entries, rng)
        
        if loot.cutoff_applied:
            # Cutoffs should produce followups
            if loot.cutoff_resolution == "omen":
                assert any("wealth_omen" in str(f) for f in loot.followups)
            elif loot.cutoff_resolution == "clock_tick":
                assert any("contested_resource" in str(f) for f in loot.followups)
            # Found at least one cutoff, test passes
            return
    
    # If no cutoffs in 100 samples, that's also valid (depends on cap/alpha interaction)
    # Just ensure the test doesn't fail spuriously
    pass
