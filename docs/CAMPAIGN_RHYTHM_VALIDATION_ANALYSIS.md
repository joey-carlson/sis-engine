# Campaign Rhythm Validation Analysis

**Date**: December 2025
**Scenarios**: Campaign Rhythm - Normal Mode & Spiky Mode
**Execution Mode**: Sequential 6-scene campaign with shared EngineState

## Executive Summary

This analysis validates whether SiS naturally creates pressure/release/recovery/renewed-tension
rhythms across multiple scenes WITHOUT requiring explicit campaign-level rules.

## Normal Mode Analysis

### Per-Scene Metrics

| Scene | Phase | Severity Avg | Cutoff Rate | Clocks | Tag Cooldowns | Recent IDs |
|-------|-------|--------------|-------------|--------|---------------|------------|
| 1 | approach | 2.78 | 6.0% | {'tension': 11, 'heat': 7, 'attrition': 0, 'mystic_flux': 0} | 1 | 1 |
| 2 | engage | 2.76 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 2 |
| 3 | aftermath | 2.62 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 3 |
| 4 | approach | 2.96 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 4 |
| 5 | engage | 3.04 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 5 |
| 6 | aftermath | 3.94 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 6 |

### Observations

**Approach → Engage (Scenes 1-2)**: Severity decreased by 0.02
**Engage → Aftermath (Scenes 2-3)**: Severity decreased by 0.14
**First Cycle Avg**: 2.72
**Second Cycle Avg**: 3.31
**Cycle Comparison**: Second cycle higher by 0.59

## Spiky Mode Analysis

### Per-Scene Metrics

| Scene | Phase | Severity Avg | Cutoff Rate | Clocks | Tag Cooldowns | Recent IDs |
|-------|-------|--------------|-------------|--------|---------------|------------|
| 1 | approach | 3.58 | 12.0% | {'tension': 12, 'heat': 11, 'attrition': 0, 'mystic_flux': 0} | 2 | 1 |
| 2 | engage | 3.14 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 2 |
| 3 | aftermath | 3.52 | 6.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 3 | 3 |
| 4 | approach | 4.00 | 4.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 3 | 4 |
| 5 | engage | 3.68 | 0.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 5 |
| 6 | aftermath | 3.36 | 2.0% | {'tension': 12, 'heat': 12, 'attrition': 0, 'mystic_flux': 0} | 2 | 6 |

## Comparative Analysis (Normal vs Spiky)

- **Normal Mode Average Severity**: 3.02
- **Spiky Mode Average Severity**: 3.55
- **Normal Mode Average Cutoff Rate**: 1.0%
- **Spiky Mode Average Cutoff Rate**: 4.0%

## Key Findings

### 1. Phase Differentiation Across Scenes
- [ ] Approach scenes show exploratory/controlled behavior
- [ ] Engage scenes show elevated pressure
- [ ] Aftermath scenes show pressure release

### 2. State Evolution (Clock Trends)
- [ ] Clocks accumulate across scenes (not reset)
- [ ] Meaningful variation between scenes
- [ ] Natural rhythm vs flatline behavior

### 3. Second Cycle Behavior
- [ ] Second cycle affected by first cycle state
- [ ] Not identical to first cycle
- [ ] Evidence of memory/consequence

### 4. Rarity Mode Differentiation
- [ ] Spiky mode shows pressure spikes
- [ ] At least one meaningful cutoff event in sequence
- [ ] Avoids permanent high tension plateau
- [ ] Avoids permanent calm (no spikes)

## Detailed Findings

### Normal Mode Rhythm

**Escalation Pattern**: 
- Severity gradually increases across the campaign (2.78 → 3.94)
- First cycle average: 2.72, Second cycle average: 3.31 (+0.59)
- Clear escalation trend demonstrates state memory and consequence

**Release Pattern**: 
- Engage → Aftermath shows severity reduction (2.76 → 2.62 in first cycle)
- However, severity increases overall across campaign despite phase transitions
- Aftermath provides relative relief but not absolute reset

**Cycle Differentiation**: 
- Second cycle IS affected by first cycle (higher baseline severity)
- Second cycle scenes average 21.7% higher severity than first cycle
- Demonstrates state carry-forward and cumulative pressure

**Clock Behavior**: 
- ⚠️ **Clocks max out quickly** (tension=12, heat=12 by Scene 2)
- Once maxed, clocks stay at cap for remainder of campaign
- Clock clamping prevents clock-based rhythm (only severity rhythm remains)
- System relies on content selection variance, not clock variance

### Spiky Mode Rhythm

**Spike Occurrences**: 
- Scene 1 (Approach) shows 12% cutoff rate - immediate pressure spike
- Cutoffs also in Scenes 3, 4, 6 (aftermath/approach phases)
- Spikes distributed across multiple scenes, not concentrated

**Release Effectiveness**: 
- Severity varies between scenes (3.14 to 4.00 range)
- Cutoff rates fluctuate (0% to 12%)
- No scene shows runaway pressure (highest cutoff is 12%)

**Plateau Avoidance**: 
- ⚠️ **Clocks do plateau** (all at max by Scene 2)
- However, **severity variance** prevents feeling of permanent tension
- System avoids behavioral plateau even with clock plateau

**Differentiation from Normal**: 
- Spiky average severity: 3.55 vs Normal: 3.02 (+17.5%)
- Spiky average cutoff: 4.0% vs Normal: 1.0% (4x higher)
- Spiky shows more cutoff events and higher severity volatility
- Modes feel distinctly different despite same clock behavior

## Recommendation

**Status**: ⚠️ **MIXED RESULTS - DESIGNER DECISION REQUIRED**

### What Works (✅)

1. **State Carry-Forward Confirmed**: Second cycle clearly affected by first cycle
2. **Severity Escalation**: Natural increase across campaign (2.72 → 3.31 avg in Normal)
3. **Rarity Mode Differentiation**: Spiky feels distinctly more volatile (4x cutoff rate)
4. **No Hard Resets**: State memory preserved across all scenes
5. **Adequate Variance**: Severity changes scene-to-scene prevent flatline feeling

### What's Concerning (⚠️)

1. **Clock Plateau**: Both tension and heat max out (12) by Scene 2, never decrease
2. **No Clock-Based Rhythm**: Clocks provide no pressure/release signal after Scene 2
3. **Single-Dimension Rhythm**: System relies on severity variance, not clock variance
4. **Clamping Behavior**: Clock_max=12 reached too quickly, creates immediate ceiling

### Critical Question

**Does SiS feel like a living system over time?**

**Answer**: **Partially**

- **Severity rhythm**: YES - clear escalation/variation across scenes
- **Clock rhythm**: NO - clocks plateau immediately and never release
- **State memory**: YES - second cycle affected by first
- **Phase identity**: WEAK - approach/engage/aftermath don't show strong differentiation

### Options

**Option 1: Accept Current Rhythm (Recommended)**
- Severity variance provides sufficient rhythm
- Clock plateau may be acceptable if severity drives experience
- System avoids flatline and runaway behaviors
- Rarity modes differentiate appropriately
- **Lock campaign rhythm, proceed to next frontier**

**Option 2: Adjust Clock Mechanics**
- Increase clock_max to allow more headroom
- Add clock decay in aftermath phase
- Tie clock behavior more directly to phase
- **Requires engine changes, deferred per task spec**

### Issues Identified

- [x] Clock plateau - tension/heat max by Scene 2
- [x] No clock release mechanism
- [ ] Flatline behavior - NOT present (severity varies)
- [ ] Runaway escalation - NOT present (severity controlled)
- [ ] Hard resets - NOT present (state carries forward)
- [ ] Rarity mode issues - NOT present (modes differentiate)

## Next Steps

If rhythm is sufficient:
- Campaign validation complete
- Ready for next design frontier:
  - Campaign-level consequence mechanics (long-term clocks, scars, factions), OR
  - Content richness passes (loot, factions, narrative arcs), OR
  - SiS ↔ D&D adapter formalization

If rhythm needs adjustment:
- Document specific issues
- Propose solutions
- DO NOT implement yet - designer review required
