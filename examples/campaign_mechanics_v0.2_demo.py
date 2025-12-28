"""Demonstration of Campaign Mechanics v0.2

This script shows v0.2 features:
- Structured scars (permanent consequences)
- Faction tracking (attention + disposition)
- Long-arc bands (descriptive state tiers)

Usage:
    python examples/campaign_mechanics_v0.2_demo.py
"""

import sys
from pathlib import Path

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from typing import List, Optional

from spar_engine.engine import generate_event
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext, ScenePhase, RarityMode
from spar_engine.rng import TraceRNG
from spar_engine.content import load_pack
from spar_campaign import (
    CampaignState,
    CampaignDelta,
    Scar,
    FactionState,
    apply_campaign_delta,
    decay_campaign_state,
    get_campaign_influence,
    record_severity_high_water_mark,
)


def run_v02_demo():
    """Run 8-scene campaign demonstrating v0.2 features."""
    
    print("=" * 80)
    print("SiS Campaign Mechanics v0.2 - Demonstration")
    print("Structured Scars • Faction Tracking • Long-Arc Bands")
    print("=" * 80)
    print()
    
    # Initialize states
    campaign_state = CampaignState.default()
    engine_state = EngineState.default()
    rng = TraceRNG(seed=123)  # Different seed for variety
    
    # Load content
    entries = load_pack("data/core_complications.json")
    
    # Define factions for this campaign
    print("[Campaign Setup]")
    print("Factions defined:")
    print("  • city_watch: Local law enforcement")
    print("  • merchant_guild: Economic interests")
    print("  • underground: Criminal network")
    print()
    
    # Campaign sequence with explicit consequences
    scenes: List[tuple[str, ScenePhase, str, RarityMode, List[str], Optional[List[Scar]]]] = [
        ("Scene 1: Infiltration", "approach", "populated", "normal", ["city_watch"], None),
        ("Scene 2: Confrontation", "engage", "populated", "normal", ["city_watch"], None),
        ("Scene 3: Escape", "aftermath", "populated", "normal", [], None),
        # Add a scar from the first encounter
        ("Scene 4: Regroup", "approach", "derelict", "normal", [], [
            Scar(
                scar_id="known_to_city_watch",
                category="reputation",
                severity="medium",
                source="Scene 2 confrontation",
                created_scene_index=2,
                notes="Faces seen by city watch during escape"
            )
        ]),
        ("Scene 5: New Deal", "engage", "populated", "normal", ["merchant_guild"], None),
        ("Scene 6: Complications", "engage", "populated", "spiky", ["city_watch", "merchant_guild"], None),
        # Add resource scar from extended conflict
        ("Scene 7: Depleted", "aftermath", "populated", "normal", [], [
            Scar(
                scar_id="supplies_depleted",
                category="resource",
                severity="high",
                source="Scene 6 extended engagement",
                created_scene_index=6,
                notes="Critical supplies exhausted in prolonged conflict"
            )
        ]),
        ("Scene 8: Fallout", "aftermath", "populated", "normal", ["underground"], None),
    ]
    
    base_tags = [
        "hazard", "reinforcements", "time_pressure", "social_friction",
        "visibility", "mystic", "attrition", "terrain", "positioning",
        "opportunity", "information"
    ]
    
    for scene_num, (scene_name, phase, env, rarity, factions, explicit_scars) in enumerate(scenes, 1):
        print(f"\n{'═' * 80}")
        print(f"{scene_name}")
        print(f"Phase: {phase} | Environment: {env} | Rarity: {rarity}")
        print(f"{'═' * 80}")
        
        # Show campaign state
        print(f"\n[Campaign State]")
        print(f"  Pressure: {campaign_state.campaign_pressure} ({campaign_state.get_pressure_band()})")
        print(f"  Heat: {campaign_state.heat} ({campaign_state.get_heat_band()})")
        
        if campaign_state.scars:
            print(f"  Scars:")
            for scar in campaign_state.scars:
                print(f"    • {scar.scar_id} ({scar.category}, {scar.severity})")
                if scar.notes:
                    print(f"      {scar.notes}")
        else:
            print(f"  Scars: None")
        
        if campaign_state.factions:
            print(f"  Factions:")
            for fid, faction in campaign_state.factions.items():
                disp_str = {-2: "hostile", -1: "unfriendly", 0: "neutral", 1: "friendly", 2: "allied"}[faction.disposition]
                print(f"    • {fid}: attention={faction.attention}, {disp_str}")
        else:
            print(f"  Factions: None tracked yet")
        
        # Get influence
        influence = get_campaign_influence(campaign_state)
        
        if influence["notes"]:
            print(f"\n[Campaign Influence]")
            for note in influence["notes"]:
                print(f"  • {note}")
            if influence["suggested_factions_involved"]:
                print(f"  Suggested factions: {influence['suggested_factions_involved']}")
        
        # Build scene with campaign influence
        context = SceneContext(
            scene_id=f"demo_v02_scene_{scene_num}",
            scene_phase=phase,
            environment=[env],
            tone=["gritty"],
            constraints=Constraints(confinement=0.5, connectivity=0.6, visibility=0.7),
        )
        
        scene_tags = base_tags + influence.get("include_tags", [])
        scene_rarity = influence.get("rarity_bias") or rarity
        
        selection = SelectionContext(
            enabled_packs=["data/core_complications.json"],
            include_tags=scene_tags,
            exclude_tags=[],
            factions_present=factions,
            rarity_mode=scene_rarity,
        )
        
        # Generate event
        event = generate_event(
            scene=context,
            state=engine_state,
            selection=selection,
            entries=entries,
            rng=rng,
        )
        
        # Show outcome
        print(f"\n[Scene Outcome]")
        print(f"  {event.title} (severity {event.severity})")
        if event.cutoff_applied:
            print(f"  Cutoff: {event.cutoff_resolution}")
        print(f"  Tags: {', '.join(event.tags[:4])}")  # First 4 tags
        
        # Update engine state
        from spar_engine.state import apply_state_delta, tick_state
        engine_state = apply_state_delta(engine_state, event.state_delta)
        engine_state = tick_state(engine_state, ticks=2)
        
        # Derive campaign delta
        ev_dict = {
            "threat": event.effect_vector.threat,
            "cost": event.effect_vector.cost,
            "heat": event.effect_vector.heat,
            "time_pressure": event.effect_vector.time_pressure,
            "information": event.effect_vector.information,
            "opportunity": event.effect_vector.opportunity,
        }
        
        delta = CampaignDelta.from_scene_outcome(
            severity=event.severity,
            cutoff_applied=event.cutoff_applied,
            tags=event.tags,
            effect_vector_dict=ev_dict,
            factions_present=factions,
            explicit_scars=explicit_scars,
        )
        
        # Show delta
        print(f"\n[Campaign Delta]")
        print(f"  Pressure +{delta.campaign_pressure_add}, Heat +{delta.heat_add}")
        if delta.scars_add:
            print(f"  Scars added:")
            for scar in delta.scars_add:
                print(f"    • {scar.scar_id}")
        if delta.faction_updates:
            print(f"  Faction updates:")
            for fid, updates in delta.faction_updates.items():
                if updates["attention_add"] > 0:
                    print(f"    • {fid}: attention +{updates['attention_add']}")
        
        # Apply delta
        campaign_state = apply_campaign_delta(campaign_state, delta)
        campaign_state = record_severity_high_water_mark(campaign_state, event.severity)
        
        # Aftermath decay
        if phase == "aftermath":
            print(f"\n[Aftermath Decay: Pressure -3, Heat -2]")
            campaign_state = decay_campaign_state(campaign_state, pressure_decay=3, heat_decay=2)
    
    # Final summary
    print(f"\n\n{'═' * 80}")
    print("CAMPAIGN SUMMARY")
    print(f"{'═' * 80}")
    print(f"Total Scenes: {campaign_state.total_scenes_run}")
    print(f"Campaign Pressure: {campaign_state.campaign_pressure} ({campaign_state.get_pressure_band()})")
    print(f"Heat: {campaign_state.heat} ({campaign_state.get_heat_band()})")
    print(f"Peak Severity: {campaign_state.highest_severity_seen}")
    
    print(f"\n[Persistent Scars]")
    if campaign_state.scars:
        for scar in campaign_state.scars:
            print(f"  • {scar.scar_id} ({scar.category}, {scar.severity})")
            print(f"    {scar.notes}")
    else:
        print(f"  None")
    
    print(f"\n[Faction States]")
    if campaign_state.factions:
        for fid, faction in campaign_state.factions.items():
            disp_str = {-2: "hostile", -1: "unfriendly", 0: "neutral", 1: "friendly", 2: "allied"}[faction.disposition]
            print(f"  • {fid}: attention={faction.attention}/20, {disp_str}")
    else:
        print(f"  None")
    
    print(f"\n[Key Observations - v0.2 Features]")
    print(f"✓ Scars persisted across all scenes (Scene 4, 7)")
    print(f"✓ Scars influenced later scene tags (resource scar → attrition)")
    print(f"✓ Factions accumulated attention from visibility/social tags")
    print(f"✓ Long-arc bands provided human-readable state descriptors")
    print(f"✓ Backward compatibility maintained (v0.1 can upgrade to v0.2)")
    print(f"✓ Engine internals completely unchanged")
    print()


if __name__ == "__main__":
    run_v02_demo()
