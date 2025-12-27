"""Demonstration of Campaign Mechanics v0.1

This script shows how CampaignState tracks pressure across multiple scenes
and influences future scene setup without modifying engine internals.

Usage:
    python examples/campaign_mechanics_demo.py
"""

import sys
from pathlib import Path

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from spar_engine.engine import generate_event
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext, ScenePhase, RarityMode
from spar_engine.rng import TraceRNG
from spar_engine.content import load_pack
from spar_campaign import (
    CampaignState,
    CampaignDelta,
    apply_campaign_delta,
    decay_campaign_state,
    get_campaign_influence,
    record_severity_high_water_mark,
)


def run_campaign_demo():
    """Run a 6-scene campaign demonstrating long-term pressure tracking."""
    
    print("=" * 80)
    print("SPAR Campaign Mechanics v0.1 - Demonstration")
    print("=" * 80)
    print()
    
    # Initialize states
    campaign_state = CampaignState.default()
    engine_state = EngineState.default()
    rng = TraceRNG(seed=42)
    
    # Load content pack
    entries = load_pack("data/core_complications.json")
    
    # Define a sequence of scenes (approach → engage → aftermath cycle)
    scenes: list[tuple[str, ScenePhase, str, RarityMode]] = [
        ("Scene 1", "approach", "confined", "normal"),
        ("Scene 2", "engage", "confined", "normal"),
        ("Scene 3", "aftermath", "confined", "normal"),
        ("Scene 4", "approach", "populated", "normal"),
        ("Scene 5", "engage", "populated", "spiky"),  # Escalation
        ("Scene 6", "aftermath", "populated", "normal"),
    ]
    
    base_tags = [
        "hazard", "reinforcements", "time_pressure", "social_friction",
        "visibility", "mystic", "attrition", "terrain", "positioning",
        "opportunity", "information"
    ]
    
    for scene_num, (scene_name, phase, env, rarity) in enumerate(scenes, 1):
        print(f"\n{'─' * 80}")
        print(f"SCENE {scene_num}: {scene_name} ({phase}, {env}, {rarity} mode)")
        print(f"{'─' * 80}")
        
        # Show current campaign state
        print(f"\n[Campaign State Before Scene]")
        print(f"  Campaign Pressure: {campaign_state.campaign_pressure}")
        print(f"  Heat: {campaign_state.heat}")
        print(f"  Scars: {sorted(campaign_state.scars) if campaign_state.scars else 'None'}")
        print(f"  Total Scenes: {campaign_state.total_scenes_run}")
        
        # Get campaign influence on scene setup
        influence = get_campaign_influence(campaign_state)
        
        if influence["notes"]:
            print(f"\n[Campaign Influence]")
            for note in influence["notes"]:
                print(f"  • {note}")
            if influence["include_tags"]:
                print(f"  Include tags: {influence['include_tags']}")
            if influence["exclude_tags"]:
                print(f"  Exclude tags: {influence['exclude_tags']}")
            if influence["rarity_bias"]:
                print(f"  Rarity bias: {influence['rarity_bias']}")
        
        # Build scene context
        context = SceneContext(
            scene_id=f"demo_scene_{scene_num}",
            scene_phase=phase,
            environment=[env],
            tone=["gritty"],
            constraints=Constraints(
                confinement=0.7 if env == "confined" else 0.4,
                connectivity=0.3 if env == "confined" else 0.7,
                visibility=0.6,
            ),
        )
        
        # Apply campaign influence to tag selection
        # Note: In real use, exclude_tags would be applied more selectively
        # For this demo, we only apply include_tags to avoid content exhaustion
        scene_tags = base_tags.copy()
        for tag in influence.get("include_tags", []):
            if tag not in scene_tags:
                scene_tags.append(tag)
        
        # Exclude tags commented out for demo to prevent content exhaustion
        # In production, you'd handle this more carefully based on content availability
        # for tag in influence.get("exclude_tags", []):
        #     if tag in scene_tags:
        #         scene_tags.remove(tag)
        
        # Override rarity if campaign suggests it
        scene_rarity = influence.get("rarity_bias") or rarity
        
        selection = SelectionContext(
            enabled_packs=["data/core_complications.json"],
            include_tags=scene_tags,
            exclude_tags=[],
            factions_present=[],
            rarity_mode=scene_rarity,
        )
        
        # Generate complication
        event = generate_event(
            scene=context,
            state=engine_state,
            selection=selection,
            entries=entries,
            rng=rng,
        )
        
        # Show scene outcome
        print(f"\n[Scene Outcome]")
        print(f"  Event: {event.title} ({event.event_id})")
        print(f"  Severity: {event.severity}")
        if event.cutoff_applied:
            print(f"  Cutoff: {event.cutoff_resolution} (original: {event.original_severity})")
        print(f"  Tags: {event.tags}")
        print(f"  Effect Vector:")
        ev_dict = {
            "threat": event.effect_vector.threat,
            "cost": event.effect_vector.cost,
            "heat": event.effect_vector.heat,
            "time_pressure": event.effect_vector.time_pressure,
            "information": event.effect_vector.information,
            "opportunity": event.effect_vector.opportunity,
        }
        for k, v in ev_dict.items():
            if v > 0:
                print(f"    {k}: {v}")
        
        # Update engine state
        from spar_engine.state import apply_state_delta, tick_state
        engine_state = apply_state_delta(engine_state, event.state_delta)
        
        # Tick cooldowns between scenes (like harness batch runs)
        engine_state = tick_state(engine_state, ticks=2)
        
        # Derive campaign delta from scene outcome
        campaign_delta = CampaignDelta.from_scene_outcome(
            severity=event.severity,
            cutoff_applied=event.cutoff_applied,
            tags=event.tags,
            effect_vector_dict=ev_dict,
        )
        
        # Apply campaign delta
        campaign_state = apply_campaign_delta(campaign_state, campaign_delta)
        campaign_state = record_severity_high_water_mark(campaign_state, event.severity)
        
        print(f"\n[Campaign Delta Applied]")
        print(f"  Pressure +{campaign_delta.campaign_pressure_add}")
        print(f"  Heat +{campaign_delta.heat_add}")
        
        # Aftermath scenes trigger decay (consequences settling)
        if phase == "aftermath":
            print(f"\n[Aftermath Decay Applied]")
            print(f"  Pressure -3, Heat -2 (consequences settling)")
            campaign_state = decay_campaign_state(
                campaign_state,
                pressure_decay=3,
                heat_decay=2,
            )
        
        print(f"\n[Campaign State After Scene]")
        print(f"  Campaign Pressure: {campaign_state.campaign_pressure}")
        print(f"  Heat: {campaign_state.heat}")
        print(f"  Highest Severity Seen: {campaign_state.highest_severity_seen}")
    
    # Final summary
    print(f"\n\n{'═' * 80}")
    print("CAMPAIGN SUMMARY")
    print(f"{'═' * 80}")
    print(f"Total Scenes: {campaign_state.total_scenes_run}")
    print(f"Final Campaign Pressure: {campaign_state.campaign_pressure}")
    print(f"Final Heat: {campaign_state.heat}")
    print(f"Peak Severity: {campaign_state.highest_severity_seen}")
    print(f"Cutoffs Triggered: {campaign_state.total_cutoffs_seen}")
    print(f"Scars Acquired: {sorted(campaign_state.scars) if campaign_state.scars else 'None'}")
    
    print(f"\n[Observations]")
    print(f"• Campaign pressure accumulated from high-severity scenes")
    print(f"• Heat tracked from visibility and social friction")
    print(f"• Aftermath scenes applied decay (pressure release)")
    print(f"• Campaign state influenced scene setup tags dynamically")
    print(f"• Engine internals remained unchanged")
    print()


if __name__ == "__main__":
    run_campaign_demo()
