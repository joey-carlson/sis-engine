from spar_engine.content import load_pack, filter_entries

def test_exclude_tags_filters_out_entries():
    entries = load_pack("data/core_complications_v0_1.json")
    out = filter_entries(
        entries=entries,
        environment=["dungeon"],
        phase="engage",
        include_tags=["hazard","reinforcements","time_pressure","social_friction","visibility"],
        exclude_tags=["mystic"],
        recent_event_ids=[],
        tag_cooldowns={},
    )
    assert all("mystic" not in e.tags for e in out)

def test_recent_event_id_blocks_repeat():
    entries = load_pack("data/core_complications_v0_1.json")
    some = entries[0].event_id
    out = filter_entries(
        entries=entries,
        environment=["dungeon"],
        phase="engage",
        include_tags=["hazard","reinforcements","time_pressure","social_friction","visibility","mystic"],
        exclude_tags=[],
        recent_event_ids=[some],
        tag_cooldowns={},
    )
    assert all(e.event_id != some for e in out)
