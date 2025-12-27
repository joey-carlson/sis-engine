#!/usr/bin/env python3
"""CLI runner for the SPAR Engine v0.1 (encounter complications).

This is a thin wrapper around `spar_engine.engine.generate_event`.

Examples (zsh):
  python3 engine.py --scene-phase engage --env confined --confinement 0.8 --connectivity 0.2 --visibility 0.7 --party-band mid --seed 42
  python3 engine.py --scene myscene --scene-phase approach --env city --tone noir --include-tags hazard,visibility --count 5
  python3 engine.py --event hazard_smoke_01 --scene-phase engage --env confined --count 1

Stateful run (persist across invocations):
  python3 engine.py --state-in state.json --state-out state.json --tick-mode turn --ticks 1
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional, Tuple

from spar_engine.content import load_pack
from spar_engine.engine import generate_event
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.state import apply_state_delta, tick_state


def _split_csv(v: str) -> List[str]:
    if not v:
        return []
    return [x.strip() for x in v.split(",") if x.strip()]


def _scene_preset(preset: str) -> Tuple[Constraints, str]:
    preset = (preset or "").strip().lower()
    if preset == "confined":
        return Constraints(confinement=0.8, connectivity=0.3, visibility=0.6), "confined"
    if preset == "populated":
        return Constraints(confinement=0.4, connectivity=0.8, visibility=0.7), "populated"
    if preset == "open":
        return Constraints(confinement=0.3, connectivity=0.5, visibility=0.4), "open"
    if preset == "derelict":
        return Constraints(confinement=0.6, connectivity=0.4, visibility=0.5), "derelict"
    return Constraints(confinement=0.5, connectivity=0.5, visibility=0.5), ""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="spar-engine",
        description="Run the SPAR Engine v0.1 (encounter complications) from the CLI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Scene inputs
    p.add_argument("--scene", default="cli", help="Scene identifier (arbitrary label).")
    p.add_argument("--scene-phase", choices=["approach", "engage", "aftermath"], default="engage")
    p.add_argument("--scene-preset", choices=["confined", "populated", "open", "derelict"], default=None,
                   help="Optional preset that sets morphology defaults and env if env not provided.")
    p.add_argument("--env", default="", help="Comma-separated environment tags, e.g. confined,derelict")
    p.add_argument("--tone", default="gritty", help="Comma-separated tone tags, e.g. gritty,noir")
    p.add_argument("--spotlight", default="combat", help="Comma-separated spotlight tags, e.g. combat,stealth")
    p.add_argument("--party-band", choices=["low", "mid", "high", "unknown"], default="unknown")

    # Morphology (0..1); if scene-preset is provided, these override the preset if explicitly set
    p.add_argument("--confinement", type=float, default=None)
    p.add_argument("--connectivity", type=float, default=None)
    p.add_argument("--visibility", type=float, default=None)

    # Selection / filtering
    p.add_argument("--rarity-mode", choices=["calm", "normal", "spiky"], default="normal")
    p.add_argument(
        "--include-tags",
        default="hazard,reinforcements,time_pressure,social_friction,visibility,mystic,attrition,terrain,positioning",
        help="Comma-separated tags; entry must match at least one.",
    )
    p.add_argument("--exclude-tags", default="", help="Comma-separated tags to exclude.")
    p.add_argument("--pack", default="data/core_complications.json", help="Path to a JSON content pack.")
    p.add_argument("--event-id", default="", help="Force a specific event_id (must exist in pack).")
    p.add_argument("--event", default="", help="Alias for --event-id.")

    # RNG / output
    p.add_argument("--seed", type=int, default=42, help="Seed for deterministic output.")
    p.add_argument("--count", type=int, default=1, help="Number of events to generate.")
    p.add_argument("--format", choices=["pretty", "jsonl"], default="pretty", help="Output format.")
    p.add_argument("--show-trace", action="store_true", help="Include RNG trace in output.")

    # Stateful runs
    p.add_argument("--state-in", default="", help="Path to read EngineState from (JSON).")
    p.add_argument("--state-out", default="", help="Path to write updated EngineState to (JSON).")
    p.add_argument("--tick-mode", choices=["none", "turn", "scene"], default="none",
                   help="Whether to decrement tag cooldowns before generating.")
    p.add_argument("--ticks", type=int, default=0, help="How many ticks to apply when tick-mode != none.")
    return p


def _load_state(path: str) -> EngineState:
    p = Path(path)
    raw = json.loads(p.read_text())
    return EngineState(
        clocks=dict(raw.get("clocks", {})),
        recent_event_ids=list(raw.get("recent_event_ids", [])),
        tag_cooldowns=dict(raw.get("tag_cooldowns", {})),
        flags=dict(raw.get("flags", {})),
    )


def _save_state(path: str, state: EngineState) -> None:
    p = Path(path)
    payload = asdict(state)
    p.write_text(json.dumps(payload, indent=2))


def main() -> int:
    args = build_parser().parse_args()

    entries = load_pack(Path(args.pack))

    preset_constraints, preset_env = _scene_preset(args.scene_preset) if args.scene_preset else (_scene_preset("")[0], "")
    env = _split_csv(args.env) if args.env else ([preset_env] if preset_env else ["confined"])
    tone = _split_csv(args.tone)
    spotlight = _split_csv(args.spotlight)

    # Morphology: preset defaults, overridden by explicit flags
    confinement = preset_constraints.confinement if args.confinement is None else float(args.confinement)
    connectivity = preset_constraints.connectivity if args.connectivity is None else float(args.connectivity)
    visibility = preset_constraints.visibility if args.visibility is None else float(args.visibility)

    scene = SceneContext(
        scene_id=args.scene,
        scene_phase=args.scene_phase,
        environment=env,
        tone=tone,
        constraints=Constraints(confinement=confinement, connectivity=connectivity, visibility=visibility),
        party_band=args.party_band,
        spotlight=spotlight,
    )

    selection = SelectionContext(
        enabled_packs=["core_complications_v0_1"],
        include_tags=_split_csv(args.include_tags),
        exclude_tags=_split_csv(args.exclude_tags),
        factions_present=[],
        rarity_mode=args.rarity_mode,
    )

    state = _load_state(args.state_in) if args.state_in else EngineState.default()

    if args.tick_mode != "none" and args.ticks > 0:
        state = tick_state(state, ticks=args.ticks)

    forced_id = (args.event_id or args.event or "").strip()
    if forced_id:
        if not any(e.event_id == forced_id for e in entries):
            raise SystemExit(f"--event-id/--event {forced_id!r} not found in pack {args.pack!r}")
        entries = [e for e in entries if e.event_id == forced_id]

    rng = TraceRNG(seed=args.seed)

    for i in range(args.count):
        rng.trace.clear()
        event = generate_event(scene, state, selection, entries, rng)

        # Apply delta for subsequent events in this same invocation (and for state-out)
        state = apply_state_delta(state, event.state_delta)

        payload = asdict(event)
        if not args.show_trace:
            payload.pop("rng_trace", None)

        if args.format == "jsonl":
            print(json.dumps(payload, ensure_ascii=False))
        else:
            print(f"== Event {i+1}/{args.count} ==")
            print(f"{event.title}  (id={event.event_id})")
            print(f"Severity: {event.severity}   Cutoff: {event.cutoff_applied} ({event.cutoff_resolution})")
            print(f"Tags: {', '.join(event.tags)}")
            print(f"Effects: {event.effect_vector}")
            if event.fiction.prompt:
                print()
                print(event.fiction.prompt)
            if event.fiction.immediate_choice:
                print("Choices:")
                for c in event.fiction.immediate_choice:
                    print(f" - {c}")
            print()

    if args.state_out:
        _save_state(args.state_out, state)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
