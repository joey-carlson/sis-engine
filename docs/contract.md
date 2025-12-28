# SiS Engine v0.1 Contract
## Encounter Complications Engine

**Status:** Draft v0.1

**Purpose**  
This document defines the system-agnostic contract for the SiS (Spirals in Spirals) Engine, focused on generating encounter complications. It serves as the foundational architecture and requirements reference for all SiS-powered tooling. Game systems (D&D, GURPS, SPAR, etc.) act purely as adapters layered on top of this engine.

The core design principle is **material independence with macro-constraint control**: the engine operates on state, distributions, and cutoffs without embedding any system-specific mechanics.

---

## 1. Design Goals

- **System-agnostic output**: No hardcoded DCs, damage, or stat references.
- **Low GM overhead**: GMs configure intent and tone, not probability math.
- **Stateful behavior**: Pressure accumulates and releases in bursts.
- **Safe by default**: Finite-size cutoffs prevent campaign-breaking results.
- **Composable**: Content packs and adapters are modular.

---

## 2. Engine Inputs

### 2.1 Scene Context
```json
{
  "scene_id": "string",
  "scene_phase": "approach|engage|aftermath",
  "environment": ["confined","populated","open","sea","derelict","industrial","planar"],
  "tone": ["gritty","heroic","weird","noir","gonzo"],
  "constraints": {
    "confinement": 0.0,
    "connectivity": 0.0,
    "visibility": 0.0
  },
  "party_band": "low|mid|high|unknown",
  "spotlight": ["combat","social","exploration","stealth","mystic"]
}
```

**Constraint sliders**
- **Confinement**: Physical or tactical restriction, difficulty of disengagement.
- **Connectivity**: Availability of buffers, allies, exits, or parallel paths.
- **Visibility**: Degree to which actions propagate attention or consequences.

These parameters define the effective "morphology" of the scene and drive distribution shape and cutoffs.

---

### 2.2 Engine State
```json
{
  "clocks": {
    "tension": 0,
    "heat": 0,
    "attrition": 0,
    "mystic_flux": 0
  },
  "cooldowns": {
    "recent_event_ids": [],
    "tag_cooldowns": {}
  },
  "flags": {
    "alarm_raised": false,
    "reinforcements_possible": true,
    "exit_available": true
  }
}
```

- Clocks default to a 0–12 range.
- Cooldowns prevent repetition and encourage cascading consequences.
- Flags constrain or unlock specific content paths.

---

### 2.3 Content Selection
```json
{
  "enabled_packs": [],
  "include_tags": [],
  "exclude_tags": [],
  "factions_present": [],
  "rarity_mode": "calm|normal|spiky"
}
```

Content is filtered entirely through tags and scene compatibility.

---

## 3. Engine Outputs

### 3.1 Core Output Object
```json
{
  "event_id": "string",
  "title": "string",
  "tags": [],
  "severity": 1,
  "cutoff_applied": false,
  "cutoff_resolution": "none|omen|hook|clock_tick|downshift|reroll",
  "effect_vector": {
    "threat": 0,
    "cost": 0,
    "heat": 0,
    "time_pressure": 0,
    "position_shift": 0,
    "information": 0,
    "opportunity": 0
  },
  "fiction": {
    "prompt": "string",
    "sensory": [],
    "immediate_choice": []
  },
  "state_delta": {
    "clocks": {},
    "cooldowns": {},
    "flags": {}
  },
  "followups": []
}
```

### 3.2 Severity Scale

Severity is an integer from **1–10**:

- **1–2**: Texture and friction
- **3–4**: Meaningful complication
- **5–6**: Serious complication requiring adaptation
- **7–8**: Major escalation or pivot
- **9–10**: Local crisis or campaign-significant threat (usually gated)

---

## 4. Engine Behavior

### 4.1 Trigger Modes

- **Pressure Trigger (default)**: Roll when tension crosses thresholds or on GM demand.
- **Turn Timer**: Roll every N rounds or turns.
- **Action Trigger**: Roll on flagged player actions (noise, failure, pursuit, etc.).

---

### 4.2 Severity Distribution

v0.1 supports two modes:

1. **Truncated Heavy-Tail (default)**  
   Produces many low-severity events and few high-severity events, with an enforced cap.

2. **Tension Pool**  
   Pressure accumulates as discrete units and releases in bursts, reducing tension afterward.

Distribution parameters are derived automatically from constraints and rarity mode.

---

### 4.3 Cutoff Policy

If sampled severity exceeds the scene cap:

- **Omen**: Foreshadow the larger threat
- **Hook**: Convert to a lead or opportunity
- **Clock Tick**: Advance a relevant clock
- **Downshift**: Reduce severity to the cap
- **Reroll**: One reroll, then downshift

Default by phase:
- *Approach*: Omen
- *Engage*: Clock Tick
- *Aftermath*: Downshift

---

## 5. Content Entry Schema
```json
{
  "event_id": "string",
  "title": "string",
  "tags": [],
  "allowed_environments": [],
  "allowed_scene_phases": [],
  "severity_band": [2,6],
  "weight": 1.0,
  "cooldown": {},
  "effect_vector_template": {},
  "fiction": {}
}
```

Entries define *what* can happen, not *how often*.

---

## 6. Adapter Hints (Optional)
```json
{
  "adapter_hints": {
    "difficulty_hint": "easy|standard|hard",
    "scale_hint": "single|area|scene",
    "duration_hint": "instant|short|scene"
  }
}
```

Adapters may ignore these entirely.

---

## 7. Acceptance Criteria

- Distribution sanity: majority low severity, rare high severity after cutoff
- No event repetition inside cooldown window
- Severity above cap never manifests directly

---

## 8. Versioning

This document uses semantic versioning. All changes append to version history rather than overwriting prior decisions.
