from __future__ import annotations

from typing import Dict, Sequence

from .content import filter_entries
from .cutoff import apply_cutoff
from .models import (
    ContentEntry,
    EffectVector,
    EngineEvent,
    EngineState,
    Fiction,
    SceneContext,
    SelectionContext,
    StateDelta,
)
from .rng import TraceRNG
from .severity import compute_alpha, compute_severity_cap, sample_severity


def _roll_effect_vector(entry: ContentEntry, rng: TraceRNG) -> EffectVector:
    t = entry.effect_vector_template or {}

    def r(key: str) -> int:
        lo, hi = t.get(key, (0, 0))
        if lo == hi:
            return int(lo)
        return int(rng.randint(int(lo), int(hi), label=f"effect:{key}"))

    return EffectVector(
        threat=r("threat"),
        cost=r("cost"),
        heat=r("heat"),
        time_pressure=r("time_pressure"),
        position_shift=r("position_shift"),
        information=r("information"),
        opportunity=r("opportunity"),
    )


def _derive_state_delta(scene: SceneContext, state: EngineState, entry: ContentEntry, severity: int) -> StateDelta:
    clocks: Dict[str, int] = {}

    if scene.scene_phase == "engage":
        clocks["tension"] = 1 if severity >= 3 else 0
    elif scene.scene_phase == "approach":
        clocks["tension"] = 1 if severity >= 5 else 0
    else:
        clocks["tension"] = 0

    if "reinforcements" in entry.tags or "visibility" in entry.tags:
        clocks["heat"] = 1 if severity >= 4 else 0

    recent_add = [entry.event_id]
    tag_sets: Dict[str, int] = {}
    for tag, cd in (entry.cooldown_tags or {}).items():
        tag_sets[tag] = max(tag_sets.get(tag, 0), int(cd))

    return StateDelta(
        clocks=clocks,
        recent_event_ids_add=recent_add,
        tag_cooldowns_set=tag_sets,
        flags_set={},
    )


def _apply_cutoff_fiction_overlay(fiction: Fiction, resolution: str) -> Fiction:
    if resolution == "none":
        return fiction
    if resolution == "omen":
        prompt = "Omen: " + (fiction.prompt or "You notice signs of a larger threat gathering momentum.")
        choices = fiction.immediate_choice or ["Investigate the sign", "Ignore it and press on"]
        return Fiction(prompt=prompt, sensory=fiction.sensory, immediate_choice=choices)
    if resolution == "clock_tick":
        prompt = "Escalation: " + (fiction.prompt or "Pressure rises, something shifts in the background.")
        choices = fiction.immediate_choice or ["Push to end this now", "Reposition and reduce exposure"]
        return Fiction(prompt=prompt, sensory=fiction.sensory, immediate_choice=choices)
    if resolution == "downshift":
        prompt = "Narrow Escape: " + (fiction.prompt or "The worst of it doesn’t land, but you feel the near miss.")
        choices = fiction.immediate_choice or ["Capitalize on the moment", "Recover and stabilize"]
        return Fiction(prompt=prompt, sensory=fiction.sensory, immediate_choice=choices)
    return fiction


def generate_event(
    scene: SceneContext,
    state: EngineState,
    selection: SelectionContext,
    entries: Sequence[ContentEntry],
    rng: TraceRNG,
) -> EngineEvent:
    """Generate one encounter complication event.

    Contract guarantees:
    - system-agnostic outputs
    - deterministic with seed
    - severity never exceeds cap (cutoff converts)
    """
    constraints = scene.constraints.clamped()

    candidates = filter_entries(
        entries=entries,
        environment=scene.environment,
        phase=scene.scene_phase,
        include_tags=selection.include_tags,
        exclude_tags=selection.exclude_tags,
        recent_event_ids=state.recent_event_ids,
        tag_cooldowns=state.tag_cooldowns,
    )
    if not candidates:
        raise ValueError("No content entries available after filtering/cooldowns. Broaden tags or add content.")

    alpha = compute_alpha(selection.rarity_mode, constraints)
    sampled = sample_severity(rng, alpha=alpha, lo=1, hi=10)

    cap = compute_severity_cap(
        scene.party_band,
        scene.scene_phase,
        constraints,
        state,
        rarity_mode=selection.rarity_mode,
    )
    severity, cutoff_applied, resolution, original = apply_cutoff(sampled, cap, scene.scene_phase)

    band_compatible = [e for e in candidates if e.severity_band[0] <= severity <= e.severity_band[1]]
    pool = band_compatible if band_compatible else candidates

    # Adaptive weighting (v0.2): reduce "sticky" outcomes without hard-banning them.
    recent = list(state.recent_event_ids or [])
    recency_index = {eid: i for i, eid in enumerate(recent)}  # 0 = most recent
    weights = []
    for e in pool:
        w = float(e.weight)
        if e.event_id in recency_index:
            i = recency_index[e.event_id]
            # Tiered penalty based on recency position
            # Stronger penalties for very recent, gentler for older
            if i == 0:
                penalty = 10.0  # just occurred
            elif i == 1:
                penalty = 6.0
            elif i == 2:
                penalty = 4.0
            elif i <= 4:
                penalty = 3.0
            elif i <= 6:
                penalty = 2.0
            else:
                penalty = 1.5  # old but still in window
            w = w / penalty
        weights.append(w)

    entry = rng.weighted_choice(pool, weights, label="content_entry")

    ev = _roll_effect_vector(entry, rng)
    fiction = Fiction(
        prompt=entry.fiction_prompt,
        sensory=list(entry.fiction_sensory),
        immediate_choice=list(entry.fiction_choices),
    )
    fiction = _apply_cutoff_fiction_overlay(fiction, resolution)

    delta = _derive_state_delta(scene, state, entry, severity)

    followups = []
    if cutoff_applied and resolution == "omen":
        followups.append({"tag": "omen_followup", "in": "aftermath"})
    if cutoff_applied and resolution == "clock_tick":
        followups.append({"tag": "pressure_aftershock", "in": "1-2 turns"})

    return EngineEvent(
        event_id=entry.event_id,
        title=entry.title,
        tags=list(entry.tags),
        severity=severity,
        cutoff_applied=cutoff_applied,
        cutoff_resolution=resolution,
        original_severity=original,
        effect_vector=ev,
        fiction=fiction,
        state_delta=delta,
        followups=followups,
        rng_trace=list(rng.trace),
    )
