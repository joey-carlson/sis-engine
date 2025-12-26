# Key Docs

This project is governed by a small set of documents. If you are new to the repo, start here.

## Core governance

1. **SPAR Tool Engineering Rules v0.1**  
   Process rules for architecture, implementation, testing, and versioning.

2. **SPAR Engine v0.1 Contract (Encounter Complications)**  
   Authoritative interface/behavior contract for the engine core.

## Tooling

3. **Streamlit Harness Requirements & Architecture** (`/docs/Streamlit_Harness_Requirements_Architecture.md`)
   Defines the debug-first harness used to tune and validate engine behavior. Version history tracked in file header.

## Campaign System

4. **Campaign Play Guide** (`/docs/PLAY_GUIDE_campaigns.md`)
   User-facing guide for campaign management, session finalization, and history import.

5. **Campaign Integration Architecture** (`/docs/ARCH_campaign_integration.md`)
   Technical architecture for campaign state management, data flows, and integration patterns.

## Context

6. **Project Context & Status**  
   Narrative context, key decisions, and current status for collaborators.

## Data Directories

7. **campaigns/** - Campaign persistent state (organized by campaign name)
   Each campaign has its own subdirectory containing:
   - `campaign_<id>.json` - Main campaign file (state, ledger, canon)
   - `campaign_<id>_import_overrides.json` - Parser classification overrides
   
   Structure: `campaigns/<Normalized_Campaign_Name>/campaign_*.json`
   
   Directory names are programmatically generated via `normalize_campaign_name_to_dir()`:
   - Removes special characters
   - Replaces spaces/hyphens with underscores
   - Example: "Spelljammer" → `campaigns/Spelljammer/`
   - Example: "City of Fog" → `campaigns/City_of_Fog/`
   
   **Note:** campaigns/ is version controlled for cross-deployment testing (local + Streamlit Cloud).

## Repo-level tracking

8. **CHANGELOG.md**  
   Chronological changes (append newest at top).

9. **PARKING_LOT.md**  
   Deferred ideas and future work items.
