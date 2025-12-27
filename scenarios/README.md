# Scenario Library

This directory contains predefined scenario definitions for the Streamlit harness.

## Purpose

Scenario JSON files enable:
- Reproducible validation workflows
- Automated testing
- Consistent comparison across runs
- Documentation of validation parameters

## Scenario Format

```json
{
  "name": "Scenario Name",
  "description": "Purpose and context",
  "presets": ["confined", "populated", "open", "derelict"],
  "phases": ["approach", "engage", "aftermath"],
  "rarity_modes": ["normal"],
  "batch_size": 200,
  "base_seed": 1000,
  "include_tags": "",
  "exclude_tags": "",
  "tick_between": true,
  "ticks_between": 2,
  "verbose": false
}
```

## Required Fields
- `name`, `presets`, `phases`, `rarity_modes`, `batch_size`, `base_seed`

## Built-in Scenarios

### phase_validation_scenario_a.json
**Purpose**: Validate phase differentiation in Normal mode  
**Runs**: 4 presets × 3 phases × 1 mode = 12 runs  
**Batch**: 200 events each  
**Seed**: 1000

### phase_validation_scenario_b.json
**Purpose**: Validate phase differentiation in Spiky mode  
**Runs**: 4 presets × 3 phases × 1 mode = 12 runs  
**Batch**: 200 events each  
**Seed**: 1000 (same as A for direct comparison)

## Usage

### Running Existing Scenarios
1. Open Streamlit harness "Scenarios" tab
2. Import scenario JSON:
   - **Option A**: Upload JSON file using file uploader
   - **Option B**: Select from built-in library dropdown
3. Review displayed scenario details
4. Working directory shown for context (e.g., `/Users/name/project`)
5. Specify output file path in text input (defaults to descriptive name with timestamp)
6. Click "Run and Save Scenario"
7. Results automatically saved as JSON with success/error feedback
8. Output path persists in session for next save operation

### Exporting Results Manually
After running any suite (hardcoded or scenario):
1. View results in summary table
2. Working directory shown for context
3. Choose format:
   - **Markdown**: Specify path, click "Save Report (Markdown)"
   - **JSON**: Specify path, click "Save Report (JSON)"
4. File saved to specified path with success/error feedback
5. Paths persist in session for convenience

### Creating New Scenarios

**Method 1: From Template**
1. Copy `scenarios/scenario_template.json`
2. Modify fields as needed
3. Save to scenarios/ directory
4. Scenario automatically appears in library dropdown

**Method 2: Export from UI**
1. Configure hardcoded suite settings in Streamlit harness:
   - Select presets, phases, rarity modes
   - Adjust batch size, seed, tags, ticks
2. Working directory shown for context
3. Specify template save path in text input (defaults to descriptive name with timestamp)
4. Click "Save as Template"
5. Template file created with all current UI settings
6. Success/error feedback displayed
7. Import template in future sessions to reproduce exact configuration

### Unified Save/Export UX
All save/export operations follow the same pattern:
- **Working Directory Display**: Shows current working directory above path input for clarity
- **Path Specification**: Text input for full file path (relative or absolute)
- **Cross-Session Persistence**: Specified paths remembered across ALL sessions (app restarts, browser sessions)
  - Paths stored in `.streamlit_harness_config.json` (excluded from git)
  - Automatic load on app startup, save on path changes
  - Personal preferences survive terminal/browser restarts
- **Descriptive Defaults**: Auto-generated filenames with timestamps and context
  - Results: `{output_basename}_{YYYYMMDD_HHMMSS}.json`
  - Templates: `scenario_template_{YYYYMMDD_HHMMSS}.json`
  - Reports: `report_markdown_{YYYYMMDD_HHMMSS}.md` or `report_json_{YYYYMMDD_HHMMSS}.json`
- **Success/Error Feedback**: Clear confirmation or error messages for all operations
- **Shared Backend**: All operations use save_report_to_path() function (no code duplication)

### File Naming Examples
- Scenario results: `phase_validation_normal_20251225_132042.json`
- Custom template: `scenario_template_20251225_140815.json`
- Markdown report: `report_markdown_20251225_152330.md`
- JSON report: `report_json_20251225_152330.json`

Timestamps prevent accidental overwrites and clearly identify when exports were created.
