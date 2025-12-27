"""Loot Generator - Narrative Resource Shock System

Loot in SPAR represents resource shocks with narrative consequences, not item catalogs.
Each "loot" is a situation that relieves immediate pressure while creating new obligations,
attention, or vulnerability.

Uses the same SOC foundation as event generation.
"""

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
    """Roll randomized effects from entry template. Shared with event generator."""
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


def _derive_loot_state_delta(
    scene: SceneContext,
    state: EngineState,
    entry: ContentEntry,
    severity: int
) -> StateDelta:
    """Derive state changes from loot acquisition.
    
    Loot impacts:
    - Attention (heat clock) if valuable or visible
    - Obligation if from contested or borrowed sources
    - Tag cooldowns to prevent loot spam
    """
    clocks: Dict[str, int] = {}

    # Loot can increase heat if visible or contested
    if "visibility" in entry.tags or "obligation" in entry.tags:
        clocks["heat"] = 1 if severity >= 5 else 0

    # Track recent loot to prevent repetition
    recent_add = [entry.event_id]
    
    # Apply tag cooldowns
    tag_sets: Dict[str, int] = {}
    for tag, cd in (entry.cooldown_tags or {}).items():
        tag_sets[tag] = max(tag_sets.get(tag, 0), int(cd))

    return StateDelta(
        clocks=clocks,
        recent_event_ids_add=recent_add,
        tag_cooldowns_set=tag_sets,
        flags_set={},
    )


def _apply_loot_cutoff_fiction(fiction: Fiction, resolution: str) -> Fiction:
    """Apply cutoff resolution overlays to loot fiction.
    
    Loot cutoffs represent moderated windfalls or complicated gains.
    """
    if resolution == "none":
        return fiction
    
    if resolution == "omen":
        prompt = "Omen of Wealth: " + (fiction.prompt or "You sense valuable resources nearby, but claiming them will draw attention.")
        choices = fiction.immediate_choice or ["Investigate the opportunity", "Note it for later"]
        return Fiction(prompt=prompt, sensory=fiction.sensory, immediate_choice=choices)
    
    if resolution == "clock_tick":
        prompt = "Contested Resource: " + (fiction.prompt or "Multiple parties move toward the same resource.")
        choices = fiction.immediate_choice or ["Act fast to secure it", "Let others reveal themselves first"]
        return Fiction(prompt=prompt, sensory=fiction.sensory, immediate_choice=choices)
    
    if resolution == "downshift":
        prompt = "Modest Gain: " + (fiction.prompt or "The resource is present but less valuable than hoped.")
        choices = fiction.immediate_choice or ["Take what's available", "Invest time finding more"]
        return Fiction(prompt=prompt, sensory=fiction.sensory, immediate_choice=choices)
    
    return fiction


def generate_loot(
    scene: SceneContext,
    state: EngineState,
    selection: SelectionContext,
    entries: Sequence[ContentEntry],
    rng: TraceRNG,
) -> EngineEvent:
    """Generate one narrative resource shock (loot situation).
    
    Loot represents resource discoveries that:
    - Relieve immediate pressure temporarily
    - Create new obligations, attention, or vulnerability
    - Feel like narrative events, not reward tables
    
    Uses identical SOC pipeline to event generation:
    - Campaign state informs severity sampling
    - Cutoff converts extreme values to story beats
    - Output integrates with Prep Queue → Canon flow
    
    Contract guarantees:
    - System-agnostic outputs
    - Deterministic with seed
    - Severity respects cap (cutoff converts)
    - No auto-application (staged for GM review)
    """
    constraints = scene.constraints.clamped()

    # Filter loot entries (reuses event filtering)
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
        raise ValueError("No loot entries available after filtering/cooldowns. Broaden tags or add loot content.")

    # SOC sampling (same as events)
    alpha = compute_alpha(selection.rarity_mode, constraints)
    sampled = sample_severity(rng, alpha=alpha, lo=1, hi=10)

    # Apply cutoff (same as events)
    cap = compute_severity_cap(
        scene.party_band,
        scene.scene_phase,
        constraints,
        state,
        rarity_mode=selection.rarity_mode,
    )
    severity, cutoff_applied, resolution, original = apply_cutoff(sampled, cap, scene.scene_phase)

    # Select entry matching severity band
    band_compatible = [e for e in candidates if e.severity_band[0] <= severity <= e.severity_band[1]]
    pool = band_compatible if band_compatible else candidates

    # Adaptive weighting (same as events)
    recent = list(state.recent_event_ids or [])
    recency_index = {eid: i for i, eid in enumerate(recent)}
    weights = []
    for e in pool:
        w = float(e.weight)
        if e.event_id in recency_index:
            i = recency_index[e.event_id]
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
            w = w / penalty
        weights.append(w)

    entry = rng.weighted_choice(pool, weights, label="loot_entry")

    # Roll effects
    ev = _roll_effect_vector(entry, rng)
    
    # Build fiction
    fiction = Fiction(
        prompt=entry.fiction_prompt,
        sensory=list(entry.fiction_sensory),
        immediate_choice=list(entry.fiction_choices),
    )
    fiction = _apply_loot_cutoff_fiction(fiction, resolution)

    # Derive state changes
    delta = _derive_loot_state_delta(scene, state, entry, severity)

    # Loot followups (potential complications from acquisition)
    followups = []
    if cutoff_applied and resolution == "omen":
        followups.append({"tag": "wealth_omen", "in": "aftermath"})
    if cutoff_applied and resolution == "clock_tick":
        followups.append({"tag": "contested_resource", "in": "immediate"})

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
