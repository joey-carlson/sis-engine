"""Debug script to understand wilderness adaptive weighting behavior."""

from pathlib import Path

from spar_engine.content import filter_entries, load_pack
from spar_engine.engine import generate_event
from spar_engine.models import (
    Constraints,
    EngineState,
    SceneContext,
    SelectionContext,
)
from spar_engine.rng import TraceRNG
from spar_engine.severity import compute_alpha, compute_severity_cap, sample_severity
from spar_engine.state import apply_state_delta, tick_state


def debug_wilderness_selection():
    """Debug why terrain_fog_01 dominates wilderness batches."""
    entries = load_pack("data/core_complications.json")
    
    # Wilderness setup
    constraints = Constraints(confinement=0.3, connectivity=0.6, visibility=0.4)
    scene = SceneContext(
        scene_id="debug_wilderness",
        scene_phase="engage",
        environment=["open"],
        tone=["gritty"],
        constraints=constraints,
        party_band="mid",
        spotlight=["combat"],
    )
    
    selection = SelectionContext(
        enabled_packs=["core"],
        include_tags=[],
        exclude_tags=[],
        factions_present=[],
        rarity_mode="normal",
    )
    
    state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    # Run 30 events and track detailed selection info
    terrain_fog_selections = []
    
    for idx in range(30):
        if idx > 0:
            state = tick_state(state, ticks=2)
        
        # Get candidates after filtering
        candidates = filter_entries(
            entries=entries,
            environment=scene.environment,
            phase=scene.scene_phase,
            include_tags=selection.include_tags,
            exclude_tags=selection.exclude_tags,
            recent_event_ids=state.recent_event_ids,
            tag_cooldowns=state.tag_cooldowns,
        )
        
        # Sample severity
        alpha = compute_alpha(selection.rarity_mode, constraints)
        sampled_sev = sample_severity(rng, alpha=alpha, lo=1, hi=10)
        
        # Get cap
        cap = compute_severity_cap(
            scene.party_band,
            scene.scene_phase,
            constraints,
            state,
            rarity_mode=selection.rarity_mode,
        )
        
        # Filter by severity band
        band_compatible = [e for e in candidates if e.severity_band[0] <= sampled_sev <= e.severity_band[1]]
        pool = band_compatible if band_compatible else candidates
        
        # Check if terrain_fog_01 is in pool
        fog_in_pool = any(e.event_id == "terrain_fog_01" for e in pool)
        fog_in_recent = "terrain_fog_01" in (state.recent_event_ids or [])
        
        if fog_in_pool:
            fog_entry = next(e for e in pool if e.event_id == "terrain_fog_01")
            recency_index = {eid: i for i, eid in enumerate(state.recent_event_ids or [])}
            
            # Calculate terrain_fog_01's weight with penalty
            base_w = float(fog_entry.weight)
            if fog_entry.event_id in recency_index:
                i = recency_index[fog_entry.event_id]
                if i == 0:
                    penalty = 10.0
                elif i == 1:
                    penalty = 6.0
                elif i == 2:
                    penalty = 4.0
                elif i <= 4:
                    penalty = 3.0
                elif i <= 6:
                    penalty = 2.0
                else:
                    penalty = 1.5
                penalized_w = base_w / penalty
            else:
                penalized_w = base_w
                penalty = 1.0
        
        rng.trace.clear()
        event = generate_event(scene, state, selection, entries, rng)
        state = apply_state_delta(state, event.state_delta)
        
        if event.event_id == "terrain_fog_01":
            terrain_fog_selections.append({
                "idx": idx,
                "in_pool": fog_in_pool,
                "in_recent": fog_in_recent,
                "pool_size": len(pool),
                "candidates_size": len(candidates),
                "sampled_severity": sampled_sev,
                "severity_cap": cap,
                "recent_window": list(state.recent_event_ids[:5]) if state.recent_event_ids else [],
                "base_weight": base_w if fog_in_pool else None,
                "penalized_weight": penalized_w if fog_in_pool else None,
                "penalty_factor": penalty if fog_in_pool else None,
            })
    
    print(f"\nWilderness Debug (first 30 events):")
    print(f"terrain_fog_01 selected {len(terrain_fog_selections)} times")
    print(f"\nDetailed selection info:")
    for info in terrain_fog_selections[:10]:  # Show first 10
        print(f"\n  Event {info['idx']}:")
        print(f"    Pool size: {info['pool_size']} (from {info['candidates_size']} candidates)")
        print(f"    Sampled severity: {info['sampled_severity']}, Cap: {info['severity_cap']}")
        print(f"    In recent window: {info['in_recent']}")
        if info['in_recent']:
            print(f"    Weight: {info['base_weight']:.2f} -> {info['penalized_weight']:.3f} (penalty: /{info['penalty_factor']:.1f})")
        print(f"    Recent: {info['recent_window']}")


if __name__ == "__main__":
    debug_wilderness_selection()
