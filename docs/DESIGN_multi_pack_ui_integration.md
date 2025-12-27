# Multi-Pack UI Integration Design

**Date**: 2025-12-26  
**Goal**: Integrate Content Pack selection into Campaign Manager UI

## Screenshot Analysis

Based on the current Campaign Manager interface, I can see:
- Campaign landing/selector page
- Dashboard view with multiple sections
- Content Sources section (already exists)
- Various campaign management controls

## UI Integration Plan

### 1. Campaign Model Extension

**Add to `spar_campaign/models.py`:**
```python
@dataclass
class Campaign:
    # ... existing fields ...
    enabled_content_packs: List[str] = field(default_factory=lambda: ["data/core_complications.json"])
```

**Default Behavior:**
- New campaigns start with core pack only
- Existing campaigns migrate with default value
- Core pack cannot be disabled (always in list)

### 2. Dashboard UI - Content Packs Section

**Location**: Add new section to campaign dashboard, below or alongside Content Sources

**UI Layout:**
```
┌─────────────────────────────────────┐
│ 🎲 Content Packs                    │
├─────────────────────────────────────┤
│ ✓ Core Complications (107 entries)  │  [Always enabled, grayed]
│ □ Urban Intrigue (0 entries)        │  [Toggle when available]
│ □ Frontier Survival (0 entries)     │  [Toggle when available]
│                                      │
│ Active: 1 pack, 107 total entries   │  [Summary line]
└─────────────────────────────────────┘
```

**Controls:**
- **Core Pack**: Always checked, disabled (grayed checkbox)
- **Optional Packs**: Checkboxes that toggle enabled state
- **Summary Line**: Shows active pack count + total entry count
- **Help Text**: "Choose content packs for this campaign. Core pack always included."

### 3. Pack Discovery

**Available Packs Registry:**
```python
AVAILABLE_PACKS = [
    {
        "path": "data/core_complications.json",
        "name": "Core Complications",
        "description": "Setting-neutral situations (confined/populated/open/derelict)",
        "required": True  # Cannot be disabled
    },
    # Future packs discovered from data/packs/ directory
]
```

**Pack Discovery Function:**
```python
def discover_content_packs() -> List[Dict[str, Any]]:
    """Discover available content packs from data/ and data/packs/ directories."""
    packs = [CORE_PACK]  # Core always first
    
    # Scan data/packs/ for additional packs
    packs_dir = Path("data/packs")
    if packs_dir.exists():
        for pack_file in packs_dir.glob("*.json"):
            # Load pack metadata
            try:
                data = json.loads(pack_file.read_text())
                if "$schema" in data and data.get("pack_id"):
                    packs.append({
                        "path": str(pack_file),
                        "name": data.get("pack_name", pack_file.stem),
                        "description": data.get("description", ""),
                        "required": False
                    })
            except:
                continue  # Skip invalid packs
    
    return packs
```

### 4. UI Implementation - Dashboard Section

**Add to `streamlit_harness/campaign_ui.py` dashboard:**

```python
# Content Packs Section
st.subheader("🎲 Content Packs")
st.caption("Choose content packs for this campaign. Core pack always included.")

# Discover available packs
available_packs = discover_content_packs()

# Initialize enabled packs if needed
if not hasattr(campaign, 'enabled_content_packs'):
    campaign.enabled_content_packs = ["data/core_complications.json"]

# Show each available pack with toggle
for pack in available_packs:
    col1, col2 = st.columns([8, 2])
    
    with col1:
        # Load entry count
        try:
            entries = load_pack(pack["path"])
            entry_count = len(entries)
        except:
            entry_count = 0
        
        # Pack checkbox
        is_enabled = pack["path"] in campaign.enabled_content_packs
        
        if pack["required"]:
            # Core pack - always enabled, grayed
            st.checkbox(
                f"{pack['name']} ({entry_count} entries)",
                value=True,
                disabled=True,
                help=pack["description"]
            )
        else:
            # Optional pack - toggleable
            enabled = st.checkbox(
                f"{pack['name']} ({entry_count} entries)",
                value=is_enabled,
                key=f"pack_{pack['path']}",
                help=pack["description"]
            )
            
            # Update campaign's enabled packs
            if enabled and pack["path"] not in campaign.enabled_content_packs:
                campaign.enabled_content_packs.append(pack["path"])
                campaign.save()
                st.rerun()
            elif not enabled and pack["path"] in campaign.enabled_content_packs:
                campaign.enabled_content_packs.remove(pack["path"])
                campaign.save()
                st.rerun()

# Summary line
total_entries = sum(
    len(load_pack(p)) for p in campaign.enabled_content_packs
)
active_count = len(campaign.enabled_content_packs)
st.caption(f"Active: {active_count} pack(s), {total_entries} total entries")
```

### 5. Generator Integration

**Update Event Generator to use campaign packs:**

**In `streamlit_harness/app.py`:**
```python
# Get active campaign's enabled packs
if st.session_state.get("current_campaign_id"):
    campaign = Campaign.load(st.session_state.current_campaign_id)
    pack_paths = campaign.enabled_content_packs
else:
    pack_paths = ["data/core_complications.json"]  # Default

# Load all enabled packs
from spar_engine.content import load_packs
entries = load_packs(pack_paths)
```

**Update Context Strip to show active packs:**
```python
if context and st.session_state.get("context_enabled", True):
    with st.container(border=True):
        col1, col2 = st.columns([10, 2])
        
        with col1:
            st.markdown(f"**🎯 Campaign Context:** {context.campaign_name}")
            
            # Show active packs
            pack_names = [Path(p).stem for p in campaign.enabled_content_packs]
            if len(pack_names) > 1:
                st.caption(f"📦 Packs: {', '.join(pack_names)}")
            
            # ... rest of context strip ...
```

### 6. Pack Validation

**Add validation when loading campaign:**
```python
def validate_content_packs(campaign: Campaign) -> List[str]:
    """Validate enabled packs exist and are loadable."""
    valid_packs = []
    
    for pack_path in campaign.enabled_content_packs:
        try:
            # Try to load pack
            load_pack(pack_path)
            valid_packs.append(pack_path)
        except Exception as e:
            print(f"Warning: Pack {pack_path} failed to load: {e}")
    
    # Ensure core pack is always included
    if "data/core_complications.json" not in valid_packs:
        valid_packs.insert(0, "data/core_complications.json")
    
    return valid_packs
```

### 7. Migration Strategy

**Existing Campaigns:**
- On first load after update, campaigns without `enabled_content_packs` field get default value
- Core pack automatically added
- No data loss or breaking changes

**Backward Compatibility:**
- Event Generator defaults to core pack if no campaign selected
- All existing code continues working
- Tests don't need updates (use single pack)

### 8. User Experience Flow

**Setting Up Packs (Campaign Manager):**
1. User opens campaign dashboard
2. Scrolls to "Content Packs" section
3. Sees Core pack (always enabled, grayed)
4. Toggles optional packs on/off
5. Changes auto-save to campaign
6. Summary line shows total content available

**Using Packs (Event Generator):**
1. User selects campaign in Event Generator
2. Context strip shows: "Core Complications + Urban Intrigue (143 entries)"
3. Generator automatically uses merged pack content
4. No additional controls needed - transparent to user

### 9. Benefits

✅ **No Generator UX complexity** - packs are transparent  
✅ **Campaign identity** - pack selection defines campaign voice  
✅ **Clear indication** - context strip shows what's active  
✅ **Validation built-in** - invalid packs automatically skipped  
✅ **Backward compatible** - existing campaigns work unchanged  

### 10. Implementation Checklist

Phase 2 Tasks:
- [ ] Add `enabled_content_packs` field to Campaign model
- [ ] Create pack discovery function
- [ ] Add Content Packs section to campaign dashboard
- [ ] Implement pack toggle UI with live updates
- [ ] Update generator to use `load_packs()` with campaign packs
- [ ] Update context strip to show active pack names
- [ ] Add validation for pack loading
- [ ] Test with synthetic multi-pack scenarios
- [ ] Migration support for existing campaigns

### 11. Visual Mockup

```
Campaign Dashboard:
┌────────────────────────────────────────┐
│ Space Opera Campaign                   │
├────────────────────────────────────────┤
│ Canon Summary                          │
│ [Editable text area]                   │
├────────────────────────────────────────┤
│ 🎲 Content Packs                       │
│ ✓ Core Complications (107 entries)    │ ← Grayed, always on
│ ☑ Urban Intrigue (20 entries)         │ ← Active, toggleable
│ ☐ Frontier Survival (20 entries)      │ ← Inactive, toggleable
│                                        │
│ Active: 2 packs, 127 total entries    │
├────────────────────────────────────────┤
│ Session Ledger                         │
│ ...                                    │
└────────────────────────────────────────┘

Event Generator Context Strip:
┌────────────────────────────────────────┐
│ 🎯 Campaign Context: Space Opera       │
│ 📦 Packs: Core + Urban Intrigue        │
│ 👥 Faction focus: Imperial Navy        │
│ 🎚️ Volatile pressure • 🌡️ Hunted heat │
└────────────────────────────────────────┘
```

## Next Steps

1. Implement Phase 2 (Campaign Integration)
2. Create first thematic pack for testing (Urban Intrigue)
3. Validate multi-pack workflow end-to-end
4. Document for users

This design maintains v1.0 UX simplicity while enabling powerful content customization.
