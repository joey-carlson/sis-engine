from __future__ import annotations

from typing import Dict, List

from .models import EngineState, StateDelta


def apply_state_delta(
    state: EngineState,
    delta: StateDelta,
    *,
    recent_max_len: int = 12,
    clock_min: int = 0,
    clock_max: int = 12,
) -> EngineState:
    """Apply a StateDelta to an EngineState (pure function).

    v0.1 policy:
    - clocks: add deltas (missing clocks treated as 0) and clamp to [clock_min, clock_max]
    - recent_event_ids: prepend new IDs, de-dupe, cap length
    - tag_cooldowns_set: set cooldowns to max(existing, set_value)
    - flags_set: overwrite keys provided
    """
    clocks: Dict[str, int] = dict(state.clocks)
    for k, v in (delta.clocks or {}).items():
        clocks[k] = int(clocks.get(k, 0) + int(v))
        clocks[k] = max(int(clock_min), min(int(clock_max), int(clocks[k])))

    combined = list(delta.recent_event_ids_add or []) + list(state.recent_event_ids or [])
    seen = set()
    recent: List[str] = []
    for eid in combined:
        if eid in seen:
            continue
        seen.add(eid)
        recent.append(eid)
        if len(recent) >= int(recent_max_len):
            break

    tag_cooldowns = dict(state.tag_cooldowns)
    for tag, cd in (delta.tag_cooldowns_set or {}).items():
        tag_cooldowns[tag] = max(int(tag_cooldowns.get(tag, 0)), int(cd))

    flags = dict(state.flags)
    for k, v in (delta.flags_set or {}).items():
        flags[k] = bool(v)

    return EngineState(
        clocks=clocks,
        recent_event_ids=recent,
        tag_cooldowns=tag_cooldowns,
        flags=flags,
    )


def tick_state(state: EngineState, ticks: int = 1) -> EngineState:
    """Advance time for stateful cooldowns (pure function).

    v0.2 policy:
    - decrement tag cooldown counters by `ticks` to min 0
    - age `recent_event_ids` by dropping oldest entries at a rate of 1 per 2 ticks
      (slower aging preserves adaptive weighting effectiveness)
    - clocks are NOT automatically decremented
    """
    t = max(0, int(ticks))
    if t == 0:
        return state

    tag_cooldowns: Dict[str, int] = {}
    for tag, cd in (state.tag_cooldowns or {}).items():
        n = max(0, int(cd) - t)
        if n > 0:
            tag_cooldowns[tag] = n

    recent = list(state.recent_event_ids or [])
    # Age recent_event_ids by dropping the oldest entries at a rate of 1 per tick
    drop = min(t, len(recent))
    if drop:
        recent = recent[:-drop]

    return EngineState(
        clocks=dict(state.clocks),
        recent_event_ids=recent,
        tag_cooldowns=tag_cooldowns,
        flags=dict(state.flags),
    )
