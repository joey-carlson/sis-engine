"""Analysis of open severity band distribution issue."""

from pathlib import Path
from collections import Counter

from spar_engine.content import filter_entries, load_pack
from spar_engine.models import Constraints, EngineState, SceneContext, SelectionContext
from spar_engine.rng import TraceRNG
from spar_engine.severity import compute_alpha, sample_severity


def analyze_open_severity_distribution():
    """Analyze what events are available at different severity levels."""
    entries = load_pack("data/core_complications.json")
    
    # Get open engage events
    constraints = Constraints(confinement=0.3, connectivity=0.6, visibility=0.4)
    state = EngineState.default()
    
    candidates = filter_entries(
        entries=entries,
        environment=["open"],
        phase="engage",
        include_tags=[],
        exclude_tags=[],
        recent_event_ids=[],
        tag_cooldowns={},
    )
    
    print(f"Wilderness engage: {len(candidates)} total events")
    
    # Analyze severity band coverage
    severity_coverage = {}
    for sev in range(1, 11):
        compatible = [e for e in candidates if e.severity_band[0] <= sev <= e.severity_band[1]]
        severity_coverage[sev] = compatible
        print(f"\nSeverity {sev}: {len(compatible)} events available")
        for e in compatible:
            print(f"  {e.event_id} (band {e.severity_band}, weight {e.weight})")
    
    # Sample severity distribution
    print(f"\n--- Severity Sampling Distribution (Normal mode) ---")
    alpha = compute_alpha("normal", constraints)
    print(f"Alpha: {alpha:.2f}")
    
    rng = TraceRNG(seed=42)
    severity_samples = []
    for _ in range(1000):
        sev = sample_severity(rng, alpha=alpha, lo=1, hi=10)
        severity_samples.append(sev)
        rng.trace.clear()
    
    sev_freq = Counter(severity_samples)
    print("\nSeverity frequency (1000 samples):")
    for sev in sorted(sev_freq.keys()):
        pct = (sev_freq[sev] / 1000) * 100
        available = len(severity_coverage[sev])
        print(f"  Sev {sev}: {sev_freq[sev]:3d} ({pct:5.1f}%) -> {available} events available")
    
    # Calculate expected selection bias
    print(f"\n--- Expected Selection Pressure ---")
    low_sev_pct = sum(sev_freq[s] for s in [1, 2]) / 1000 * 100
    low_sev_events = len(severity_coverage[1])
    print(f"Low severity (1-2): {low_sev_pct:.1f}% of samples")
    print(f"Events that can handle sev 1-2: {low_sev_events}")
    print(f"Expected avg appearances per low-sev event: {low_sev_pct * 2:.1f} times in 200-event batch")
    
    print(f"\nConclusion:")
    print(f"  terrain_fog_01, terrain_thorns_01, time_misread_01 are the ONLY")
    print(f"  events with severity_band starting at 1.")
    print(f"  They must absorb ALL severity=1 samples (~{sev_freq[1]} in 1000).")
    print(f"  This creates structural dominance independent of adaptive weighting.")


if __name__ == "__main__":
    analyze_open_severity_distribution()
