from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

from .models import CutoffResolution, ScenePhase

def default_cutoff_resolution_by_phase(phase: ScenePhase) -> CutoffResolution:
    if phase == "approach":
        return "omen"
    if phase == "engage":
        return "clock_tick"
    return "downshift"

def apply_cutoff(sampled_severity: int, cap: int, phase: ScenePhase) -> tuple[int, bool, CutoffResolution, int | None]:
    """Apply finite-size cutoff policy.

    Returns: (final_severity, cutoff_applied, resolution, original_severity_if_cut)
    """
    if sampled_severity <= cap:
        return sampled_severity, False, "none", None

    resolution = default_cutoff_resolution_by_phase(phase)
    # Contract requirement: severity above cap never manifests directly.
    final_sev = cap

    return final_sev, True, resolution, sampled_severity
