from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple

@dataclass
class TraceRNG:
    """Seedable RNG with an inspectable trace.

    This wrapper is intentionally small and explicit:
    - no globals
    - deterministic with seed
    - records key random decisions for debugging and tests
    """
    seed: int | None = None
    _rng: random.Random = field(init=False, repr=False)
    trace: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def randint(self, a: int, b: int, label: str = "randint") -> int:
        v = self._rng.randint(a, b)
        self.trace.append({"op": label, "value": str(v), "range": f"{a}-{b}"})
        return v

    def random(self, label: str = "random") -> float:
        v = self._rng.random()
        self.trace.append({"op": label, "value": f"{v:.10f}"})
        return v

    def choice(self, seq: Sequence[Any], label: str = "choice") -> Any:
        if not seq:
            raise ValueError("choice() requires a non-empty sequence")
        idx = self._rng.randrange(len(seq))
        self.trace.append({"op": label, "index": str(idx), "len": str(len(seq))})
        return seq[idx]

    def weighted_choice(self, items: Sequence[Any], weights: Sequence[float], label: str = "weighted_choice") -> Any:
        if len(items) != len(weights):
            raise ValueError("items and weights must be same length")
        if not items:
            raise ValueError("weighted_choice requires non-empty items")
        total = float(sum(max(0.0, w) for w in weights))
        if total <= 0.0:
            # fall back to uniform choice if weights are degenerate
            self.trace.append({"op": label, "note": "degenerate_weights_uniform"})
            return self.choice(items, label=f"{label}:uniform")
        r = self._rng.random() * total
        upto = 0.0
        for i, w in enumerate(weights):
            w = max(0.0, float(w))
            upto += w
            if upto >= r:
                self.trace.append({"op": label, "index": str(i), "total": f"{total:.6f}"})
                return items[i]
        # numeric edge: return last
        self.trace.append({"op": label, "note": "fell_through_last"})
        return items[-1]
