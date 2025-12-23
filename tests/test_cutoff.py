from spar_engine.cutoff import apply_cutoff

def test_cutoff_applies_and_converts():
    sev, applied, res, orig = apply_cutoff(sampled_severity=9, cap=6, phase="approach")
    assert sev == 6
    assert applied is True
    assert res in ("omen","clock_tick","downshift","hook","reroll")
    assert orig == 9

def test_cutoff_noop_when_under_cap():
    sev, applied, res, orig = apply_cutoff(sampled_severity=5, cap=6, phase="engage")
    assert sev == 5
    assert applied is False
    assert res == "none"
    assert orig is None
