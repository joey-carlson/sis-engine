from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from spar_engine.models import EngineState


@dataclass
class HarnessState:
    """Single source of truth for Streamlit harness session state.

    Store exactly one instance under `st.session_state["hs"]`.
    This prevents regressions where local variables (e.g., batch_n) go out of scope on rerun.
    """
    # Engine/session state
    engine_state: EngineState = field(default_factory=EngineState.default)
    events: List[Dict[str, Any]] = field(default_factory=list)       # newest-first
    last_batch: List[Dict[str, Any]] = field(default_factory=list)
    last_suite_report: Optional[Dict[str, Any]] = None

    # Content pack cache
    pack_entries: List[Any] = field(default_factory=list)
    tag_vocab: List[str] = field(default_factory=list)

    # UI settings
    batch_n: int = 50

    def reset(self) -> None:
        self.engine_state = EngineState.default()
        self.events = []
        self.last_batch = []
        self.last_suite_report = None
