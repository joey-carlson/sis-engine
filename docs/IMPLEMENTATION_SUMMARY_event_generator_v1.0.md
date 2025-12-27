# Event Generator UI v1.0 - Reorganization Summary

**Date**: 2025-12-26  
**Status**: ✅ Implemented  
**Commit**: Pending

## Problem Statement

The Event Generator UI was cognitively overloaded, serving too many personas simultaneously:
- **GM Users**: Need simple scene setup and generation
- **Engine Developers**: Need constraint sliders, tick mechanics, state debugging
- **Scenario Analysts**: Need batch controls, seed management, tag filtering

This resulted in 15+ sidebar controls with no clear hierarchy, requiring scrolling to access basic GM functions and mixing technical controls with game-facing controls.

## Solution: 3-Layer Progressive Disclosure

### Layer 1: Primary GM Controls (Always Visible)
**Goal**: GM can generate events without understanding engine internals

**Controls**:
- Campaign Context selector
- Scene Setup: Preset, Phase, Rarity Mode
- 🏷️ Filters (collapsed expander)
  - Include tags (CSV)
  - Exclude tags (CSV)

**Design Constraints Applied**:
1. Seed moved OUT of primary layer (it's a debugging tool, not GM control)
2. Tags behind collapsed "Filters" expander (powerful but not default-visible)
3. Campaign context + faction spotlight remain primary visible guidance

### Layer 2: Context & Influence
**Location**: Main content area (not sidebar)

**Elements**:
- Campaign Context Strip (campaign name, faction focus, pressure/heat bands)
- Expandable faction influence details
- One-click disable for context

### Layer 3: Advanced Settings (Collapsed Expander)
**Goal**: Engine developers and power users have full access to internals

**Controls** (all hidden by default):
- **Seed**: RNG seed for reproducible generation
- **Batch count**: 10/50/200 selection
- **Scene Constraints**: Confinement, Connectivity, Visibility sliders
- **Tick Mechanics**: Tick mode, ticks, tick between events, ticks between events
- **Technical Identifiers**: Scene ID, party band
- **Content Pack**: Pack path, load button, tag vocabulary
- **State Debugging**: Reset button, state JSON viewer

## Key Improvements

1. **Default View Fits on One Screen**: No scrolling required for normal GM use
2. **Clear Separation**: GM controls vs engine developer diagnostics
3. **Progressive Disclosure**: Advanced features accessible but not in the way
4. **Preserve Functionality**: All original controls present, just reorganized

## Tab-Conditional Behavior

**Events Tab**: Shows reorganized sidebar with 3-layer hierarchy  
**Scenarios Tab**: Sidebar NOT shown (scenarios have their own inline controls)

This prevents control duplication and reduces cognitive load - each tab shows only relevant controls.

## User Experience Flow

**Typical GM Session** (without opening any expanders):
1. Select campaign from dropdown (or choose "No Campaign")
2. Choose scene setup (preset/phase/rarity) - 3 dropdowns
3. Click "Generate 1" or "Generate N" button
4. Review generated events

**Advanced User Session** (when needed):
1. Expand 🏷️ Filters to customize tag inclusion/exclusion
2. Expand 🔧 Advanced Settings to:
   - Set specific seed for reproducibility
   - Adjust batch size
   - Fine-tune scene constraints
   - Configure tick mechanics
   - Debug state

## Implementation Notes

- Sidebar rendering unchanged for Scenarios tab (no Event Generator controls shown)
- All variable defaults initialized before sidebar to prevent undefined errors
- Campaign context merging still works for tag defaults
- Generate buttons use batch size from Advanced Settings but remain in primary view
- Seed defaults to 42, user can change in Advanced Settings for reproducibility

## Validation

✓ Default sidebar fits on standard screen without scrolling  
✓ GM controls are non-technical and game-focused  
✓ All original functionality preserved in Advanced Settings  
✓ Tags customizable but not dominating first screen  
✓ Seed removed from primary GM view  
✓ Campaign context provides visible guidance

## Next Steps

- Monitor GM feedback on new hierarchy
- Consider adding "Generate Again" button that auto-increments seed behind scenes
- Potential future: Move batch size to Generate button itself ("Generate 1/10/50")
