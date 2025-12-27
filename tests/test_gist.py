import pytest

from spar_engine.engine import generate_event
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.content import load_pack
from spar_engine.severity import compute_severity_cap

def test_gist_generate_events_deterministic_and_safe():
    entries = load_pack("data/core_complications.json")
    rng = TraceRNG(seed=123)

    scene = SceneContext(
        scene_id="gist",
        scene_phase="approach",
        environment=["confined"],
        tone=["gritty"],
        constraints=Constraints(confinement=0.8, connectivity=0.2, visibility=0.7),
        party_band="low",
        spotlight=["combat"],
    )
    state = EngineState.default()
    sel = SelectionContext(
        enabled_packs=["core_complications_v0_1"],
        include_tags=["hazard","reinforcements","time_pressure","social_friction","visibility"],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal",
    )

    cap = compute_severity_cap(scene.party_band, scene.scene_phase, scene.constraints, state)
    events = [generate_event(scene, state, sel, entries, rng) for _ in range(25)]

    # safety: severity never exceeds cap
    assert all(e.severity <= cap for e in events)

    # deterministic trace should exist
    assert all(isinstance(e.rng_trace, list) and len(e.rng_trace) > 0 for e in events)

    # outputs should be populated
    assert all(e.event_id and e.title and isinstance(e.tags, list) for e in events)
