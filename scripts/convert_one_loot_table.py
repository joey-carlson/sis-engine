#!/usr/bin/env python3
"""
Convert One Loot Table CSV to SiS loot pack format.
Applies rarity-based conversion strategy with GM guidance.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any


# Rarity mapping to SiS parameters
RARITY_MAP = {
    "Mundane": {
        "severity_band": [1, 3],
        "weight": 1.0,
        "base_tags": ["opportunity"],
        "rarity_number": 1
    },
    "Common": {
        "severity_band": [1, 4],
        "weight": 1.0,
        "base_tags": ["opportunity"],
        "rarity_number": 2
    },
    "Uncommon": {
        "severity_band": [2, 5],
        "weight": 0.8,
        "base_tags": ["opportunity", "visibility"],
        "rarity_number": 3
    },
    "Rare": {
        "severity_band": [3, 6],
        "weight": 0.7,
        "base_tags": ["opportunity", "visibility", "social_friction"],
        "rarity_number": 4
    },
    "Very Rare": {
        "severity_band": [3, 7],
        "weight": 0.6,
        "base_tags": ["opportunity", "visibility", "social_friction", "obligation"],
        "rarity_number": 5
    },
    "Legendary": {
        "severity_band": [4, 8],
        "weight": 0.5,
        "base_tags": ["opportunity", "visibility", "social_friction", "obligation", "cost"],
        "rarity_number": 6
    }
}

# Category-specific tags and fiction elements
CATEGORY_ENHANCEMENTS = {
    "Weapon": {
        "additional_tags": ["threat"],
        "sensory_themes": ["lethal potential", "combat readiness", "weapon design"],
        "choice_pattern": "combat_utility"
    },
    "Armor": {
        "additional_tags": ["positioning"],
        "sensory_themes": ["protective design", "mobility trade-off", "defensive coverage"],
        "choice_pattern": "protection_burden"
    },
    "Potion": {
        "additional_tags": ["time_pressure"],
        "sensory_themes": ["liquid contents", "sealed container", "finite resource"],
        "choice_pattern": "consume_save"
    },
    "Book": {
        "additional_tags": ["information"],
        "sensory_themes": ["written knowledge", "preserved pages", "specialized content"],
        "choice_pattern": "study_trade"
    },
    "Ring": {
        "additional_tags": [],
        "sensory_themes": ["wearable design", "subtle presence", "personal item"],
        "choice_pattern": "keep_gift"
    },
    "Wondrous Item": {
        "additional_tags": ["cost"],
        "sensory_themes": ["unusual nature", "unclear purpose", "magical essence"],
        "choice_pattern": "use_examine"
    },
    "Treasure": {
        "additional_tags": [],
        "sensory_themes": ["valuable material", "portable wealth", "tradeable asset"],
        "choice_pattern": "keep_trade"
    },
    "Adventuring Gear": {
        "additional_tags": [],
        "sensory_themes": ["practical design", "functional utility", "worn from use"],
        "choice_pattern": "use_store"
    }
}


def sanitize_event_id(item_name: str, index: int) -> str:
    """Create clean event ID from item name."""
    # Remove special characters, convert to lowercase, replace spaces with underscores
    clean = re.sub(r'[^\w\s-]', '', item_name.lower())
    clean = re.sub(r'[-\s]+', '_', clean)
    return f"item_{clean[:40]}_{index:04d}"


def extract_d_and_d_mechanics(properties: str, requirements: str, category: str) -> str:
    """Extract D&D mechanical details for original_inspiration field."""
    parts = []
    if properties:
        parts.append(properties)
    if requirements:
        parts.append(f"Requires: {requirements}")
    
    result = " | ".join(filter(None, parts)) if parts else "See GM guidance"
    return f"{category}: {result}" if result != "See GM guidance" else result


def generate_fiction_prompt(item_name: str, description: str, rarity: str, category: str) -> str:
    """Generate SiS-style fiction prompt from D&D item."""
    # Extract narrative essence from description
    desc_lower = description.lower()
    
    # Rarity-based narrative framing
    if rarity in ["Mundane", "Common"]:
        return f"{description.rstrip('.')}. Functional and unremarkable."
    elif rarity == "Uncommon":
        return f"{description.rstrip('.')}. Distinctive enough to be remembered."
    elif rarity == "Rare":
        return f"{description.rstrip('.')}. Carries reputation and expectation."
    elif rarity in ["Very Rare", "Legendary"]:
        return f"{description.rstrip('.')}. Known by name and feared or coveted."
    
    return description


def generate_sensory_details(description: str, category: str, rarity: str) -> List[str]:
    """Generate SiS sensory details from item description."""
    sensory = []
    
    # Add category-specific sensory if available
    if category in CATEGORY_ENHANCEMENTS:
        sensory.extend(CATEGORY_ENHANCEMENTS[category]["sensory_themes"][:2])
    
    # Add rarity-based sensory
    if rarity in ["Mundane", "Common"]:
        sensory.append("practical condition")
    elif rarity == "Uncommon":
        sensory.append("quality craftsmanship")
    elif rarity == "Rare":
        sensory.append("exceptional artistry")
    elif rarity in ["Very Rare", "Legendary"]:
        sensory.append("legendary provenance")
    
    return sensory[:3]  # Max 3 sensory details


def generate_immediate_choices(category: str, rarity: str) -> List[str]:
    """Generate SiS immediate choice options."""
    # Get category-specific pattern if available
    if category in CATEGORY_ENHANCEMENTS:
        pattern = CATEGORY_ENHANCEMENTS[category]["choice_pattern"]
    else:
        pattern = "keep_trade"
    
    choice_templates = {
        "combat_utility": ["Deploy it in next conflict", "Keep it concealed for now"],
        "protection_burden": ["Wear it and accept the trade-offs", "Carry it for emergency use"],
        "consume_save": ["Use it immediately", "Save for critical need"],
        "study_trade": ["Study its contents", "Trade it for something immediate"],
        "keep_gift": ["Wear it yourself", "Gift it to build alliance"],
        "use_examine": ["Activate it to test function", "Study it before use"],
        "keep_trade": ["Keep it for later use", "Trade it for something needed"]
    }
    
    return choice_templates.get(pattern, ["Keep it", "Trade it"])


def generate_gm_guidance(item_name: str, description: str, category: str, 
                         properties: str, value: str, rarity: str) -> Dict[str, str]:
    """Generate GM guidance section with adaptation notes and mechanical suggestions."""
    
    # Adaptation notes - how to reskin for any campaign
    adaptation_map = {
        "Weapon": "This could manifest as any campaign-appropriate weapon (firearm, blade, energy weapon, mystic focus, etc.). Adapt the form to fit your setting while preserving the item's essential character.",
        "Armor": "This protective gear can take any form appropriate to your campaign (ballistic vest, powered armor, enchanted robes, cybernetic implants, etc.). Scale the protection level to your system.",
        "Potion": "This consumable can be a potion, stim-shot, nano-patch, ritual component, or any finite-use item appropriate to your setting. The effect should feel significant but temporary.",
        "Book": "This knowledge source can be a book, data-slate, encrypted file, memory crystal, or oral tradition appropriate to your campaign. It provides specialized information.",
        "Ring": "This personal item can be jewelry, a cybernetic implant, a tattoo, a charm, or any personal adornment appropriate to your setting.",
        "Wondrous Item": "This special item's form depends entirely on your campaign's magic/technology level. Focus on its unusual properties rather than its physical form.",
        "Treasure": "This valuable item can be currency, rare materials, art, data, or anything your campaign considers wealth. Adapt its liquidity to your economy.",
        "Adventuring Gear": "Standard utility equipment appropriate to your setting - climbing gear, survival tools, technical equipment, etc."
    }
    
    # Mechanical suggestions based on rarity
    mechanical_map = {
        "Mundane": "Standard equipment stats for your system. No special bonuses.",
        "Common": "Standard equipment stats, possibly well-maintained or high quality. +0 to +1 equivalent.",
        "Uncommon": "Enhanced equipment with minor benefits. +1 to +2 equivalent, or a minor special ability.",
        "Rare": "Exceptional equipment with significant benefits. +2 to +3 equivalent, or a notable special ability.",
        "Very Rare": "Legendary equipment with major benefits. +3 to +4 equivalent, or powerful special abilities.",
        "Legendary": "Artifact-tier equipment. +4+ equivalent, multiple special abilities, potentially game-changing effects."
    }
    
    return {
        "adaptation_notes": adaptation_map.get(category, "Adapt this item's form to fit your campaign setting while preserving its essential character and function."),
        "mechanical_suggestions": mechanical_map.get(rarity, "Use system-appropriate stats."),
        "value_reference": f"D&D value: {value}" if value else "Value varies by setting",
        "original_inspiration": f"{item_name} (D&D {rarity}, {category})" + (f" - {properties}" if properties else "")
    }


def convert_csv_to_spar(csv_path: str, output_path: str):
    """Main conversion function."""
    print(f"Converting {csv_path} to SiS format...")
    
    entries = []
    item_count = 0
    
    # Try different encodings for CSV
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    reader = None
    
    for encoding in encodings:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                # Test read first row
                next(reader)
                print(f"✓ Using encoding: {encoding}")
                break
        except (UnicodeDecodeError, StopIteration):
            continue
    
    if reader is None:
        raise ValueError(f"Could not decode {csv_path} with any standard encoding")
    
    # Re-open with correct encoding
    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            item_name = row.get('Item', '').strip()
            description = row.get('Description', '').strip()
            value = row.get('Est. Value', '').strip()
            rarity = row.get('Rarity', 'Common').strip()
            category = row.get('Category', 'Treasure').strip()
            properties = row.get('Properties', '').strip()
            requirements = row.get('Requirements', '').strip()
            
            # Skip empty rows
            if not item_name or not description:
                continue
            
            # Get rarity parameters
            rarity_params = RARITY_MAP.get(rarity, RARITY_MAP["Common"])
            
            # Build tags
            tags = rarity_params["base_tags"].copy()
            if category in CATEGORY_ENHANCEMENTS:
                extra_tags = CATEGORY_ENHANCEMENTS[category]["additional_tags"]
                tags.extend([t for t in extra_tags if t not in tags])
            
            # Build entry
            entry = {
                "event_id": sanitize_event_id(item_name, idx),
                "title": item_name,
                "tags": tags,
                "allowed_environments": ["any"],  # Items work anywhere
                "allowed_scene_phases": ["aftermath"],  # Loot typically found after conflict
                "severity_band": rarity_params["severity_band"],
                "weight": rarity_params["weight"],
                "cooldown": {
                    "event": 2 if rarity in ["Mundane", "Common"] else 3,
                    "tags": {
                        "opportunity": 2
                    }
                },
                "effect_vector_template": {
                    "opportunity": [1, 3] if rarity in ["Mundane", "Common"] else [2, 4]
                },
                "fiction": {
                    "prompt": generate_fiction_prompt(item_name, description, rarity, category),
                    "sensory": generate_sensory_details(description, category, rarity),
                    "immediate_choice": generate_immediate_choices(category, rarity)
                },
                "gm_guidance": generate_gm_guidance(item_name, description, category, 
                                                    properties, value, rarity)
            }
            
            entries.append(entry)
            item_count += 1
    
    # Build complete pack
    pack = {
        "name": "One Loot Table",
        "generator_type": "loot",
        "description": "Classic fantasy items adapted for any campaign setting. 400+ items from mundane gear to legendary artifacts, with GM guidance for system-agnostic conversion.",
        "metadata": {
            "version": "1.0",
            "author": "Converted from D&D One Loot Table",
            "item_count": item_count,
            "source": "Community-compiled D&D loot table",
            "conversion_notes": "Items converted to SiS consequence-driven format with GM adaptation guidance. Rarity scales from mundane utility to legendary reputation effects."
        },
        "entries": entries
    }
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Converted {item_count} items")
    print(f"✓ Created {output_path}")
    
    # Distribution summary
    rarity_counts = {}
    for entry in entries:
        # Extract rarity from original_inspiration
        orig = entry["gm_guidance"]["original_inspiration"]
        for r in RARITY_MAP.keys():
            if r in orig:
                rarity_counts[r] = rarity_counts.get(r, 0) + 1
                break
    
    print("\nRarity Distribution:")
    for rarity, count in sorted(rarity_counts.items(), key=lambda x: RARITY_MAP[x[0]]["rarity_number"]):
        print(f"  {rarity}: {count} items")
    
    return pack


if __name__ == "__main__":
    csv_path = "docs/One Loot Table.csv"
    output_path = "data/one_loot_table.json"
    
    pack = convert_csv_to_spar(csv_path, output_path)
    
    print(f"\n✓ One Loot Table pack created successfully!")
    print(f"  Total entries: {len(pack['entries'])}")
