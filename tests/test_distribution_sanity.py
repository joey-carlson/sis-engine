from collections import Counter

from spar_engine.engine import generate_event
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.content import load_pack

def test_distribution_sanity_normal_mode_majority_low():
    entries = load_pack("data/core_complications_v0_1.json")
    rng = TraceRNG(seed=999)

    scene = SceneContext(
        scene_id="dist",
        scene_phase="engage",
        environment=["dungeon"],
        tone=["gritty"],
        constraints=Constraints(confinement=0.7, connectivity=0.3, visibility=0.6),
        party_band="mid",
        spotlight=["combat"],
    )
    state = EngineState.default()
    sel = SelectionContext(
        enabled_packs=["core_complications_v0_1"],
        include_tags=["hazard","reinforcements","time_pressure","social_friction","visibility","mystic"],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal",
    )

    events = [generate_event(scene, state, sel, entries, rng) for _ in range(200)]
    buckets = Counter()
    for e in events:
        if e.severity <= 3:
            buckets["low"] += 1
        elif e.severity <= 6:
            buckets["mid"] += 1
        else:
            buckets["high"] += 1

    # Loose sanity checks (prototype): majority low, minority high.
    assert buckets["low"] >= 90
    assert buckets["high"] <= 40
