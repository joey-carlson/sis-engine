# SPAR Tool Engineering Rules v0.1

## Status
Draft v0.1  
Applies to all architecture, engine, UI, testing, and QA work for the SPAR procedural tooling project.

This document serves the same role as a ClineRules file: it defines how work is designed, implemented, tested, documented, and evolved over time. These rules are binding unless explicitly revised and versioned.

---

## 00 – Self-Organized Criticality (SOC) Foundation

**Core Philosophy:** SiS does not decide what happens. SiS decides when accumulated pressure can no longer be ignored.

SiS (Spirals in Spirals) is built on Self-Organized Criticality principles. This is not optional decoration—it is the load-bearing structure that makes procedural generation feel emergent rather than arbitrary.

### What SOC Means in SPAR Terms

Systems that:
1. **Accumulate pressure gradually** from player decisions and campaign state
2. **Release pressure in uneven bursts** (many small, few large outcomes)
3. **Self-organize without external tuning** (no GM-controlled escalation dials)
4. **Naturally settle near critical thresholds** (tension maintained, not eliminated)
5. **Produce non-linear effects** (small actions can trigger big releases; big actions might do little)

**Metaphor:** Sandpile. You don't decide when an avalanche happens. You just keep adding grains.

### SOC Compliance Checklist

Any new feature must satisfy these non-negotiable properties:

**1. Pressure accumulates implicitly**
- Builds from play decisions, not GM manual adjustment
- Emerges from campaign state (heat, faction attention, scars, dependency)
- Observable but not directly steerable

**2. Release is uneven (heavy-tailed distribution)**
- Many small outcomes, fewer medium ones, rare large ones
- Severity sampling must preserve power-law shape
- Tests must validate distribution properties

**3. Big outcomes feel earned, not triggered**
- No "boss fight at level 5" scheduling
- No deterministic milestone rewards
- Cutoffs fire rarely and convert to narrative beats
- Critical moments emerge from accumulated context

**4. No explicit tuning knobs exposed**
- Expose inputs (presets), not outcomes (sliders)
- Calm/Normal/Spiky are modes, not scalar dials
- Voice Profiles bias selection, they don't control results
- Campaign context is advisory, not deterministic

**5. Local actions have non-local effects**
- Small decisions can cascade unpredictably
- Loot relieves pressure locally while spiking it elsewhere
- Faction reactions delay across sessions
- Infrastructure dependencies create vulnerability chains

### SOC Violation Patterns (Red Flags)

Watch for these anti-patterns that would compromise SOC:
- ❌ Hard thresholds exposed to GMs for tuning
- ❌ Guaranteed "big moments" scheduling
- ❌ Linear progression systems (level gates, reward ladders)
- ❌ Mode switches that rewrite underlying math
- ❌ Content gating by player tier or campaign phase
- ❌ Deterministic milestone triggers

### The Critical Test

Before adding any new feature, ask:

**"Does this add pressure, or does it explain pressure?"**
- If it **explains** → probably SOC-safe (diagnostics, context, advisory bias)
- If it **controls** → suspect (hard thresholds, deterministic triggers, outcome dials)

**"Does this bias inputs, or control outputs?"**
- If it **biases inputs** → SOC-safe (Voice Profiles, campaign context)
- If it **controls outputs** → SOC violation (guaranteed outcomes, forced escalation)

### SOC in Practice (Current System Validation)

**Event Generator:** ✅ SOC-compliant
- Pressure from scene constraints + campaign state
- Heavy-tailed severity sampling
- Cutoffs for finite-size safety
- Many small events, rare critical ones

**Loot Generator:** ✅ SOC-compliant
- Pressure redistribution (relief ↔ obligation)
- Conservative baseline prevents runaway escalation
- Non-deterministic resource shocks
- No reward tables or linear progression

**Campaign System:** ✅ SOC-compliant
- Pressure/heat accumulate from play outcomes
- Faction attention emerges from visibility
- Scars persist without manual tracking
- Advisory pattern throughout (suggests, never enforces)

**Voice Profiles:** ✅ SOC-safe
- Bias which pressure channels fill first
- Don't control when/how pressure releases
- Subtle magnitude (5-15% range)
- "Reshaping surface, not changing gravity"

---

## 01 – General Operating Principles

- Design before implementation. Architecture and contracts come first.
- Prefer **simple, inspectable systems** over clever or opaque solutions.
- Always consider alternatives. If a better approach exists, surface it.
- Optimize for **maintainability, configurability, and debuggability** from day one.
- Changes should be **small, discrete, and versioned**.
- Do not silently rewrite previously approved architecture or contracts.
- Procedural generation must feel *intentional*, not arbitrary.

---

## 01 – Documentation & Versioning Rules

- Architecture, Requirements, and Implementation are **separate artifacts**.
- The SPAR Engine Contract is authoritative for engine behavior.
- Any change to engine behavior requires:
  - A version bump
  - A changelog entry
  - Explicit note of breaking vs non-breaking impact
- Historical decisions are never overwritten, only appended or superseded.
- Versioning uses semantic versioning:
  - v0.x = draft / exploratory
  - v1.x = stable / referenceable
  - v2.x+ = breaking revisions

### File Versioning Policy
- **Never use version numbers in filenames** (e.g., avoid `file_v2.md`, `data_v0_1.json`)
- Version information must be tracked in:
  - **File headers**: Use HTML comments for markdown, docstrings for Python
  - **Content pack metadata**: Use dedicated README files in data/ directories
  - **Project-level changes**: Use CHANGELOG.md
- Format for version history headers:
  ```html
  <!--
  Version History:
  - v2.0 (2025-12-25): Description of changes
  - v1.0 (2025-12-22): Initial version
  -->
  ```
- Rationale: Version numbers in filenames create file proliferation, complicate references, and obscure current state. Header versioning keeps repos clean and maintainable.

---

## 02 – Core SPAR Engine Design Rules

- The engine must remain **system-agnostic** at all times.
- No system-specific mechanics (DCs, damage, stats, XP, etc.) may appear in engine logic.
- Game systems (D&D, SPAR-native, others) are implemented **only as adapters**.
- Engine outputs:
  - severity
  - effect vectors
  - tags
  - fiction prompts
- Engine never dictates *solutions*, only *situations*.
- Cutoff logic (finite-size safety rails) is mandatory and non-optional.
- Randomness must be:
  - seedable
  - inspectable
  - reproducible in deterministic mode

---

## 03 – State, Distributions, and Cutoffs

- All state changes must be explicit and logged.
- No hidden global state.
- Pressure accumulation and release must be observable.
- Distribution parameters must be derived from:
  - scene constraints
  - rarity mode
  - engine state
- Power-law or heavy-tail behavior must always be paired with cutoffs.
- If severity exceeds cap, conversion rules apply (omen, hook, clock, downshift).

---

## 04 – Content & Adapters

- Content packs define *what can happen*, not probabilities.
- Weighting is handled by the engine, not authored tables.
- Content entries must be:
  - tagged
  - severity-banded
  - environment- and phase-aware
- Adapters are thin translation layers.
- Adapters may:
  - map severity to mechanics
  - interpret effect vectors
- Adapters may not:
  - alter engine distributions
  - bypass cutoff logic
  - mutate engine state directly

---

## 05 – Implementation Guidelines

- Prefer pure functions for engine logic.
- Separate concerns strictly:
  - engine core
  - state management
  - UI
  - adapters
- Avoid tight coupling between UI and engine.
- Configuration should live in data, not code.
- Code should be readable by a future maintainer who did not write it.

---

## 06 – Testing Philosophy

### Gist Tests
- Every major feature should have at least one **gist test**:
  - covers the full generation loop
  - validates core behavior quickly
  - prioritizes clarity over exhaustiveness

### Unit Tests
- Use Arrange / Act / Assert structure.
- Tests describe **behavior**, not implementation details.
- Distribution sanity tests are required:
  - severity bands
  - cutoff enforcement
  - repetition guards
- Deterministic test mode must be supported via seeded RNG.

---

## 07 – MVP Tooling Strategy

- MVP prioritizes **correctness and feel**, not polish.
- Streamlit is acceptable for v0.x prototyping.
- Engine logic must be UI-agnostic from day one.
- React is planned for later phases once behavior stabilizes.
- Debug views (histograms, state traces) are required, not optional.

---

## 08 – Collaboration Contract

- Push back when a request:
  - violates the engine contract
  - introduces system coupling
  - adds complexity without leverage
- Flag risks early and explicitly.
- The user is final arbiter of design decisions.
- Disagreements should surface tradeoffs, not stall progress.

---

## 09 – Revision Policy

- This document is living but versioned.
- Changes require:
  - explicit proposal
  - rationale
  - version increment
- Old rules remain readable for historical context.

---

## 10 – Guiding Principle

> The engine should create pressure, texture, and consequence.  
> Players create solutions.  
> Systems interpret outcomes.
