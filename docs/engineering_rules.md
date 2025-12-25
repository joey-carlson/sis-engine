# SPAR Tool Engineering Rules v0.1

## Status
Draft v0.1  
Applies to all architecture, engine, UI, testing, and QA work for the SPAR procedural tooling project.

This document serves the same role as a ClineRules file: it defines how work is designed, implemented, tested, documented, and evolved over time. These rules are binding unless explicitly revised and versioned.

---

## 00 – General Operating Principles

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
