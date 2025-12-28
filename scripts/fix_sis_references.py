#!/usr/bin/env python3
"""
Systematically correct SPAR→SiS system references across documentation.

This script corrects references where SPAR is used to describe the system
itself, not the SPAR campaign setting. It preserves legitimate setting references.
"""

import re
from pathlib import Path
from typing import List, Tuple

# Files to process with their specific patterns
CORRECTIONS = [
    # READMEs
    ("spar_campaign/README.md", [
        (r"# SPAR Campaign Mechanics", "# SiS Campaign Mechanics"),
        (r"above the SPAR Engine", "above the SiS Engine"),
        (r"SPAR Engine operates", "SiS Engine operates"),
        (r"- `docs/contract\.md` - SPAR Engine", "- `docs/contract.md` - SiS Engine"),
    ]),
    
    # Requirements docs
    ("docs/REQUIREMENTS_campaign_mechanics_v0.1.md", [
        (r"core SPAR Engine behavior", "core SiS Engine behavior"),
        (r"The SPAR Engine operates", "The SiS Engine operates"),
        (r"│  SPAR Engine    │", "│  SiS Engine     │"),
        (r"- `docs/contract\.md` - SPAR Engine", "- `docs/contract.md` - SiS Engine"),
    ]),
    
    ("docs/REQUIREMENTS_campaign_mechanics_v0.2.md", [
        (r"- `docs/contract\.md` - SPAR Engine", "- `docs/contract.md` - SiS Engine"),
    ]),
    
    ("docs/REQUIREMENTS_event_patterns_v0.1.md", [
        (r"\*\*Maintainer:\*\* SPAR Tool Engine Team", "**Maintainer:** SiS Tool Engine Team"),
    ]),
    
    # Implementation summaries
    ("docs/IMPLEMENTATION_SUMMARY_one_loot_table_v1.0.md", [
        (r"into SPAR's consequence-driven loot format", "into SiS's consequence-driven loot format"),
        (r"Add SPAR consequence-driven tags", "Add SiS consequence-driven tags"),
        (r"Rarity → SPAR Mapping", "Rarity → SiS Mapping"),
        (r"into SPAR situations", "into SiS situations"),
        (r"Balances SPAR's narrative", "Balances SiS's narrative"),
        (r"matches SPAR format", "matches SiS format"),
        (r"Preserves SPAR consequence-driven", "Preserves SiS consequence-driven"),
        (r"maintaining SPAR's narrative", "maintaining SiS's narrative"),
    ]),
    
    # Validation and analysis files
    ("docs/CAMPAIGN_RHYTHM_VALIDATION_ANALYSIS.md", [
        (r"whether SPAR naturally creates", "whether SiS naturally creates"),
        (r"\*\*Does SPAR feel like", "**Does SiS feel like"),
        (r"  - SPAR ↔ D&D adapter", "  - SiS ↔ D&D adapter"),
    ]),
    
    ("run_campaign_validation.py", [
        (r'lines\.append\("This analysis validates whether SPAR naturally', 
         'lines.append("This analysis validates whether SiS naturally'),
        (r'"  - SPAR ↔ D&D adapter', '"  - SiS ↔ D&D adapter'),
    ]),
    
    ("docs/CAMPAIGN_RHYTHM_RUNNER_DESIGN.md", [
        (r"for determining SPAR's next design", "for determining SiS's next design"),
    ]),
    
    # Examples
    ("examples/campaign_mechanics_demo.py", [
        (r'print\("SPAR Campaign Mechanics', 'print("SiS Campaign Mechanics'),
    ]),
    
    ("examples/campaign_mechanics_v0.2_demo.py", [
        (r'print\("SPAR Campaign Mechanics', 'print("SiS Campaign Mechanics'),
    ]),
    
    # Scripts
    ("scripts/convert_one_loot_table.py", [
        (r"Convert One Loot Table CSV to SPAR loot pack", "Convert One Loot Table CSV to SiS loot pack"),
        (r"# Rarity mapping to SPAR parameters", "# Rarity mapping to SiS parameters"),
        (r'"""Generate SPAR-style fiction', '"""Generate SiS-style fiction'),
        (r'"""Generate SPAR sensory details', '"""Generate SiS sensory details'),
        (r'"""Generate SPAR immediate choice', '"""Generate SiS immediate choice'),
        (r'print\(f"Converting {csv_path} to SPAR format', 'print(f"Converting {csv_path} to SiS format'),
        (r'to SPAR consequence-driven format', 'to SiS consequence-driven format'),
    ]),
    
    # DATA files
    ("data/one_loot_table.json", [
        (r'to SPAR consequence-driven format', 'to SiS consequence-driven format'),
    ]),
    
    # Test history files
    ("tests/test_history_parser_spelljammer.py", [
        (r'# Spelljammer Campaign History for SPAR Import', '# Spelljammer Campaign History for SiS Import'),
    ]),
    
    ("campaigns/Spelljammer/campaign_20251225_170643.json", [
        (r'for SPAR Import', 'for SiS Import'),
    ]),
    
    # Design docs
    ("docs/DESIGN_voice_profiles_v0.1.md", [
        (r"### Two Meanings of \"Spiral\" in SPAR", "### Two Meanings of \"Spiral\" in SiS"),
        (r"## Alignment with SPAR Tool Engineering", "## Alignment with SiS Tool Engineering"),
        (r"\*\*Maintainer:\*\* SPAR Tool Engine Team", "**Maintainer:** SiS Tool Engine Team"),
    ]),
    
    # Other implementation docs
    ("docs/GPT_CLINE_WORKFLOW.md", [
        (r"for the SPAR Tool Engine project", "for the SiS Tool Engine project"),
    ]),
    
    ("docs/project_context.md", [
        (r"# SPAR Procedural Engine", "# SiS Procedural Engine"),
        (r"> \*\*SPAR is the engine", "> **SiS is the engine"),
        (r"### 4\.1 SPAR Engine v0\.1 Contract", "### 4.1 SiS Engine v0.1 Contract"),
        (r"### 4\.2 SPAR Tool Engineering", "### 4.2 SiS Tool Engineering"),
        (r"- No system adapters \(D&D mapping, SPAR-native mapping\)", "- No system adapters (D&D mapping, setting-specific mapping)"),
    ]),
    
    # DATA_CONTRACT
    ("docs/DATA_CONTRACT_story_vs_system_v0.1.md", [
        (r"- Does it require understanding SPAR's implementation", "- Does it require understanding SiS's implementation"),
        (r"SPAR is a tool that generates", "SiS is a tool that generates"),
        (r"without needing to explain SPAR's internal mechanics", "without needing to explain SiS's internal mechanics"),
    ]),
    
    # Streamlit harness docs
    ("docs/Streamlit_Harness_Requirements_Architecture.md", [
        (r"Build a \*\*debug-first Streamlit harness\*\* for the SPAR Engine", 
         "Build a **debug-first Streamlit harness** for the SiS Engine"),
    ]),
    
    # Scenario docs
    ("scenarios/scenario_template.json", [
        (r'SPAR Engine validation scenarios', 'SiS Engine validation scenarios'),
    ]),
    
    # CHANGELOG (only system references, preserve SPAR setting references)
    ("CHANGELOG.md", [
        (r"SPAR Tool Engine v1\.0", "SiS Tool Engine v1.0"),
        (r"- Aligns SPAR positioning as truly genre-agnostic", "- Positions SPAR correctly as one campaign setting among many"),
    ]),
]


def fix_file(filepath: str, patterns: List[Tuple[str, str]]) -> bool:
    """Apply regex replacements to a file. Returns True if changes made."""
    path = Path(filepath)
    if not path.exists():
        print(f"⚠️  Skipping {filepath} (not found)")
        return False
    
    content = path.read_text()
    original = content
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        path.write_text(content)
        print(f"✅ Fixed {filepath}")
        return True
    else:
        print(f"   {filepath} (no changes)")
        return False


def main():
    print("Fixing SiS/SPAR system references...")
    print("=" * 80)
    
    changed_files = []
    for filepath, patterns in CORRECTIONS:
        if fix_file(filepath, patterns):
            changed_files.append(filepath)
    
    print("=" * 80)
    print(f"\nFixed {len(changed_files)} files:")
    for f in changed_files:
        print(f"  - {f}")
    
    print("\nDone! Review changes with: git diff")


if __name__ == "__main__":
    main()
