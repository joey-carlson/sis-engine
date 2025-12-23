from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple

ScenePhase = Literal["approach", "engage", "aftermath"]
RarityMode = Literal["calm", "normal", "spiky"]
PartyBand = Literal["low", "mid", "high", "unknown"]

CutoffResolution = Literal["none", "omen", "hook", "clock_tick", "downshift", "reroll"]

@dataclass(frozen=True)
class Constraints:
    confinement: float
    connectivity: float
    visibility: float

    def clamped(self) -> "Constraints":
        def c(x: float) -> float:
            return max(0.0, min(1.0, x))
        return Constraints(c(self.confinement), c(self.connectivity), c(self.visibility))

@dataclass(frozen=True)
class SceneContext:
    scene_id: str
    scene_phase: ScenePhase
    environment: List[str]
    tone: List[str]
    constraints: Constraints
    party_band: PartyBand = "unknown"
    spotlight: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class EngineState:
    clocks: Dict[str, int] = field(default_factory=dict)
    recent_event_ids: List[str] = field(default_factory=list)
    tag_cooldowns: Dict[str, int] = field(default_factory=dict)
    flags: Dict[str, bool] = field(default_factory=dict)

    @staticmethod
    def default() -> "EngineState":
        return EngineState(
            clocks={"tension": 0, "heat": 0, "attrition": 0, "mystic_flux": 0},
            recent_event_ids=[],
            tag_cooldowns={},
            flags={"alarm_raised": False, "reinforcements_possible": True, "exit_available": True},
        )

@dataclass(frozen=True)
class SelectionContext:
    enabled_packs: List[str]
    include_tags: List[str]
    exclude_tags: List[str]
    factions_present: List[str]
    rarity_mode: RarityMode = "normal"

@dataclass(frozen=True)
class EffectVector:
    threat: int = 0
    cost: int = 0
    heat: int = 0
    time_pressure: int = 0
    position_shift: int = 0
    information: int = 0
    opportunity: int = 0

@dataclass(frozen=True)
class Fiction:
    prompt: str
    sensory: List[str] = field(default_factory=list)
    immediate_choice: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class StateDelta:
    clocks: Dict[str, int] = field(default_factory=dict)
    recent_event_ids_add: List[str] = field(default_factory=list)
    tag_cooldowns_set: Dict[str, int] = field(default_factory=dict)
    flags_set: Dict[str, bool] = field(default_factory=dict)

@dataclass(frozen=True)
class AdapterHints:
    difficulty_hint: Optional[Literal["easy", "standard", "hard"]] = None
    scale_hint: Optional[Literal["single", "area", "scene"]] = None
    duration_hint: Optional[Literal["instant", "short", "scene"]] = None

@dataclass(frozen=True)
class ContentEntry:
    event_id: str
    title: str
    tags: List[str]
    allowed_environments: List[str]
    allowed_scene_phases: List[ScenePhase]
    severity_band: Tuple[int, int]  # inclusive
    weight: float = 1.0
    cooldown_event: int = 0
    cooldown_tags: Dict[str, int] = field(default_factory=dict)
    effect_vector_template: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    fiction_prompt: str = ""
    fiction_sensory: List[str] = field(default_factory=list)
    fiction_choices: List[str] = field(default_factory=list)
    adapter_hints: Optional[AdapterHints] = None

@dataclass(frozen=True)
class EngineEvent:
    event_id: str
    title: str
    tags: List[str]
    severity: int
    cutoff_applied: bool
    cutoff_resolution: CutoffResolution
    original_severity: Optional[int]
    effect_vector: EffectVector
    fiction: Fiction
    state_delta: StateDelta
    followups: List[Dict[str, str]] = field(default_factory=list)
    rng_trace: List[Dict[str, str]] = field(default_factory=list)
