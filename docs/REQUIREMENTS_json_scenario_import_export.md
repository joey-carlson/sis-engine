# Requirements: JSON Scenario Import/Export System

<!--
Version History:
- v1.0 (2025-12-25): Initial requirements definition
-->

**Status**: Approved for implementation  
**Date**: December 2025

## Objective

Enable JSON-based scenario definition, import, execution, and result export in the Streamlit harness to support:
- Automated validation workflows
- Reproducible test scenarios
- Phase weighting analysis
- Scenario library management

## User Requirements

### Primary Workflow
1. Define scenario parameters in JSON format
2. Import scenario JSON (file upload or library)
3. Execute scenario with specified parameters
4. Export results to user-specified file path

### Secondary Features
- Built-in scenario library for common validation tasks
- **Save as Template**: Export current hardcoded suite UI settings as JSON scenario
  - Unified save/export UX (same as report saves)
  - Working directory display for path clarity
  - Specify save path with cross-session persistence (survives app restarts)
  - Descriptive default filenames with timestamps
  - Includes all parameters: presets, phases, modes, batch size, seed, tags, ticks
  - Enables ad-hoc scenario creation without manual JSON editing
  - Uses shared save_report_to_path() backend (no code duplication)
- **Unified Save/Export UX**: All three save/export operations use consistent interface
  - Save Report (Markdown)
  - Save Report (JSON)
  - Save as Template (JSON)
  - Each displays working directory, accepts path specification, persists paths across all sessions
- **Cross-Session Persistence**: User-specified file paths stored in `.streamlit_harness_config.json`
  - Paths remembered across app restarts and browser sessions
  - Config file excluded from git (personal preferences)
  - Automatic fallback to sensible defaults if config missing
- Maintain existing hardcoded suite functionality
- Backward compatibility with current UI

## JSON Schema

### Scenario Definition Format

```json
{
  "schema_version": "1.0",
  "name": "Scenario Name",
  "description": "Brief description of validation purpose",
  "output_basename": "clean_filename_base",
  "presets": ["dungeon", "city", "wilderness", "ruins"],
  "phases": ["approach", "engage", "aftermath"],
  "rarity_modes": ["normal"],
  "batch_size": 200,
  "base_seed": 1000,
  "include_tags": "",
  "exclude_tags": "",
  "tick_between": true,
  "ticks_between": 1,
  "verbose": false
}
```

### Required Fields (Validation Level 1)
- `name` (string)
- `presets` (array of strings)
- `phases` (array of strings)
- `rarity_modes` (array of strings)
- `batch_size` (integer)
- `base_seed` (integer)

### Optional Fields
- `schema_version` (string, default: "1.0") - Future-proofs format evolution
- `output_basename` (string, optional) - Clean basename for output files (avoids messy path handling when saving multiple formats)
- `description` (string, default: "")
- `include_tags` (string CSV, default: "")
- `exclude_tags` (string CSV, default: "")
- `tick_between` (boolean, default: true)
- `ticks_between` (integer, default: 1)
- `verbose` (boolean, default: false)

### Design Notes
- **schema_version**: Added per designer feedback to avoid future pain when extending the format. Currently "1.0", future scenarios can validate compatibility.
- **output_basename**: Added per designer feedback to provide consistent basename when generating multiple output files (JSON + markdown summaries). If omitted, system auto-generates from scenario name.

## UI Components

### Scenarios Tab Enhancements

**Import Section** (new):
- File uploader: "Upload scenario JSON"
- Dropdown: "Or select from library"
- Display: Loaded scenario details
- Validation: Show errors for invalid JSON

**Configuration Section** (existing):
- Keep current suite dropdown for hardcoded suites
- Keep existing manual controls

**Export Section** (unified):
- Working directory display: Shows Path.cwd() for path context
- Text input: "Save results to path" (full file path, persists in session)
- Buttons: 
  - "Run and Save Scenario" (scenario execution with auto-save)
  - "Save Report (Markdown)" (manual export current results)
  - "Save Report (JSON)" (manual export current results)
  - "Save as Template" (export current UI settings as scenario JSON)
- All save operations use unified save_report_to_path() backend
- All path inputs persist across sessions via st.session_state
- Status: Success/error feedback for all operations

**Results Section** (existing):
- Summary table
- Download buttons (markdown/JSON)

## Implementation Details

### File Structure
```
scenarios/
├── phase_validation_scenario_a.json
├── phase_validation_scenario_b.json
└── README.md
```

### Core Functions

1. **load_scenario_json(file_or_path) -> Dict**
   - Parse JSON
   - Validate required fields
   - Return scenario dict or raise error

2. **save_report_to_path(report: Dict, path: str) -> bool**
   - Write JSON to specified path
   - Create parent directories if needed
   - Return success/failure

3. **get_builtin_scenarios() -> List[Dict]**
   - Scan scenarios/ directory
   - Load and return scenario metadata
   - Cache results

### Execution Flow

**Scenario Execution**:
```
Import JSON → Validate → Display preview → User specifies output path 
→ Click "Run and save scenario" → Execute suite → Save to path → Show success/error
```

**Report Export**:
```
Run hardcoded suite → Generate results → Specify save path 
→ Click "Save Report (Markdown/JSON)" → Save to path → Show success/error
```

**Template Creation**:
```
Configure UI settings → Specify template save path 
→ Click "Save as Template" → Export settings as JSON → Show success/error
```

All operations share the same UX pattern:
1. Working directory displayed above path input
2. Path specification with cross-session persistence (survives app restarts)
3. Descriptive default filenames with timestamps
4. Success/error feedback

### Persistence Implementation
- Paths stored in `.streamlit_harness_config.json` in project root
- File loaded on app startup, saved whenever paths change
- Config file excluded from git via `.gitignore`
- Ensures user preferences persist across all sessions (browser restarts, terminal restarts, etc.)

## Built-in Scenarios (Initial)

### Scenario A: Phase Weighting Validation - Normal
- All presets × All phases × Normal mode
- Batch size: 200
- Purpose: Validate phase differentiation

### Scenario B: Phase Weighting Validation - Spiky
- All presets × All phases × Spiky mode  
- Batch size: 200
- Same seed as Scenario A
- Purpose: Compare rarity mode impact on phases

## Parking Lot Items

### Deferred to Future Iterations
1. **Directory browser UI**: Visual directory selection for output path
2. **Sea preset support**: Add sea environment to preset options
3. **Full JSON validation**: Validate field types and value ranges
4. **Scenario editor**: In-app JSON editing and creation
5. **Scenario comparison**: Side-by-side result comparison UI

## Acceptance Criteria

- ✅ Can load scenario JSON from file upload
- ✅ Can select scenarios from built-in library
- ✅ Required field validation works
- ✅ Results save to user-specified file path
- ✅ Existing suite functionality unchanged
- ✅ Error messages clear and actionable
- ✅ All three save/export operations use unified UX
- ✅ All file paths persist across all sessions (app restarts, browser sessions)
- ✅ Paths stored in `.streamlit_harness_config.json` (excluded from git)
- ✅ Working directory displayed for all save operations
- ✅ Descriptive default filenames generated for all exports

## Technical Constraints

- No engine logic changes
- No changes to result data format
- Maintain determinism (same scenario + seed = same results)
- Handle file I/O errors gracefully

## Files to Modify

1. `streamlit_harness/app.py` - Main implementation
2. `scenarios/` - New directory with built-in scenarios
3. `scenarios/README.md` - Scenario library documentation
4. `PARKING_LOT.md` - Add deferred features
5. `docs/` - This requirements document

## Expected Outcome

Users can define validation scenarios in JSON, import them into the harness, execute them with one click, and have results automatically saved to a specified location - enabling automated validation workflows and reproducible testing.
