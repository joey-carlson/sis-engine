from spar_engine.models import EngineState, StateDelta
from spar_engine.state import apply_state_delta, tick_state

def test_apply_state_delta_updates_clocks_and_recent_ids():
    s = EngineState.default()
    d = StateDelta(clocks={"tension": 2}, recent_event_ids_add=["a","b"], tag_cooldowns_set={"hazard": 3}, flags_set={"alarm_raised": True})
    s2 = apply_state_delta(s, d)
    assert s2.clocks["tension"] == 2
    assert s2.recent_event_ids[0] == "a"
    assert "b" in s2.recent_event_ids
    assert s2.tag_cooldowns["hazard"] == 3
    assert s2.flags["alarm_raised"] is True

def test_tick_state_decrements_tag_cooldowns():
    s = EngineState.default()
    s = EngineState(clocks=s.clocks, recent_event_ids=s.recent_event_ids, tag_cooldowns={"hazard": 2, "x": 1}, flags=s.flags)
    s2 = tick_state(s, ticks=1)
    assert s2.tag_cooldowns["hazard"] == 1
    assert "x" not in s2.tag_cooldowns


def test_apply_state_delta_clamps_clocks():
    s = EngineState.default()
    d = StateDelta(clocks={"tension": 999}, recent_event_ids_add=[], tag_cooldowns_set={}, flags_set={})
    s2 = apply_state_delta(s, d, clock_min=0, clock_max=12)
    assert s2.clocks["tension"] == 12
