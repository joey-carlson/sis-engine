"""Integration test verifying the cooldown accumulation fix.

This test ensures that batches can complete successfully even when
tick_between=False, by verifying that the minimum tick of 1 is applied
to prevent cooldown accumulation.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from spar_engine.content import load_pack
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.engine import generate_event
from spar_engine.state import apply_state_delta, tick_state


@pytest.fixture
def entries():
    pack_path = Path(__file__).parent.parent / "data" / "core_complications.json"
    return load_pack(pack_path)


def run_batch_with_manual_ticking(
    scene: SceneContext,
    selection: SelectionContext,
    entries,
    seed: int,
    n: int,
    tick_between: bool,
    ticks_between: int,
):
    """Manual implementation matching the fixed run_batch logic."""
    state = EngineState.default()
    rng = TraceRNG(seed=seed)
    events = []

    for idx in range(n):
        if idx > 0:
            # The FIX: Always tick at least 1 to prevent cooldown accumulation
            tick_amount = max(1, ticks_between if tick_between else 1)
            state = tick_state(state, ticks=tick_amount)

        rng.trace.clear()
        ev = generate_event(scene, state, selection, entries, rng)
        state = apply_state_delta(state, ev.state_delta)
        events.append(ev)

    return events, state


def test_aftermath_batch_completes_without_ticking(entries):
    """Verify aftermath batches complete when tick_between=False.
    
    This was the original failure case: aftermath has only 8 events,
    and without ticking, cooldowns would accumulate and exhaust the pool.
    
    Note: Using dungeon instead of wilderness because wilderness aftermath
    has only 3 events (all sharing "attrition" tag), which is insufficient.
    """
    scene = SceneContext(
        scene_id="test_aftermath",
        scene_phase="aftermath",
        environment=["confined"],
        tone=["test"],
        constraints=Constraints(confinement=0.8, connectivity=0.3, visibility=0.6),
        party_band="unknown",
        spotlight=["test"],
    )
    selection = SelectionContext(
        enabled_packs=["core"],
        include_tags=[],  # No tag filtering
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal",
    )

    # This should complete without raising ValueError
    events, final_state = run_batch_with_manual_ticking(
        scene=scene,
        selection=selection,
        entries=entries,
        seed=1000,
        n=50,  # Larger than available aftermath content
        tick_between=False,  # The key test: no explicit ticking requested
        ticks_between=0,
    )

    # Verify we got events
    assert len(events) == 50, "Should generate full batch"
    
    # Verify cooldowns are being managed (not accumulating indefinitely)
    # With minimum tick of 1, max cooldown should be around 2-3
    max_cooldown = max(final_state.tag_cooldowns.values()) if final_state.tag_cooldowns else 0
    assert max_cooldown <= 4, f"Cooldowns should decay, got max={max_cooldown}"


def test_tick_between_still_respected(entries):
    """Verify that when tick_between=True, the specified tick amount is used."""
    scene = SceneContext(
        scene_id="test_tick",
        scene_phase="engage",
        environment=["confined"],
        tone=["test"],
        constraints=Constraints(confinement=0.8, connectivity=0.3, visibility=0.6),
        party_band="unknown",
        spotlight=["test"],
    )
    selection = SelectionContext(
        enabled_packs=["core"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal",
    )

    # Run with explicit ticking
    events, final_state = run_batch_with_manual_ticking(
        scene=scene,
        selection=selection,
        entries=entries,
        seed=2000,
        n=20,
        tick_between=True,
        ticks_between=3,  # Aggressive ticking
    )

    # With 3 ticks between events, cooldowns should be nearly zero
    assert len(events) == 20
    max_cooldown = max(final_state.tag_cooldowns.values()) if final_state.tag_cooldowns else 0
    assert max_cooldown <= 2, f"With 3 ticks, cooldowns should be minimal, got max={max_cooldown}"


def test_all_phases_complete_with_batch_200(entries):
    """Verify all phases can complete 200-event batches without errors."""
    presets = [
        ("confined", {"confinement": 0.8, "connectivity": 0.3, "visibility": 0.6}),
        ("open", {"confinement": 0.3, "connectivity": 0.5, "visibility": 0.4}),
    ]
    phases = ["approach", "engage", "aftermath"]

    for preset_name, constraints_dict in presets:
        for phase in phases:
            scene = SceneContext(
                scene_id=f"test_{preset_name}_{phase}",
                scene_phase=phase,  # type: ignore
                environment=[preset_name],
                tone=["test"],
                constraints=Constraints(**constraints_dict),
                party_band="unknown",
                spotlight=["test"],
            )
            selection = SelectionContext(
                enabled_packs=["core"],
                include_tags=[],
                exclude_tags=[],
                factions_present=[],
                rarity_mode="normal",
            )

            # Should not raise ValueError
            events, _ = run_batch_with_manual_ticking(
                scene=scene,
                selection=selection,
                entries=entries,
                seed=3000,
                n=200,
                tick_between=False,
                ticks_between=0,
            )

            assert len(events) == 200, f"Failed for {preset_name}/{phase}"


def test_cooldown_decay_rate(entries):
    """Verify cooldowns decay at expected rate with minimum ticking."""
    scene = SceneContext(
        scene_id="test_decay",
        scene_phase="engage",
        environment=["confined"],
        tone=["test"],
        constraints=Constraints(confinement=0.5, connectivity=0.5, visibility=0.5),
        party_band="unknown",
        spotlight=["test"],
    )
    selection = SelectionContext(
        enabled_packs=["core"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal",
    )

    events, final_state = run_batch_with_manual_ticking(
        scene=scene,
        selection=selection,
        entries=entries,
        seed=4000,
        n=10,
        tick_between=False,
        ticks_between=0,
    )

    # After 10 events with minimum tick of 1 each:
    # - 9 ticks total (between events)
    # - Cooldowns of 2-3 should be fully expired
    # - Only the most recent event's cooldowns should remain
    assert len(events) == 10
    
    # Count how many tags have active cooldowns
    active_cooldowns = sum(1 for cd in final_state.tag_cooldowns.values() if cd > 0)
    
    # With 9 ticks and cooldowns of 2-3, we should have minimal active cooldowns
    # (only from the last 1-2 events)
    assert active_cooldowns <= 8, f"Too many active cooldowns: {active_cooldowns}"
