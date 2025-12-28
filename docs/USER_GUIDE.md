<!--
Version History:
- v0.1 (2025-12-28): Initial user-facing guide
-->

# SiS Tool Engine: User Guide

**Powered by Spirals in Spirals (SiS)**  
**For Game Masters and Campaign Runners**  
**Version:** 1.0  
**Last Updated:** 2025-12-28

---

## What Is This Tool?

SiS Tool Engine is a **pressure-driven campaign management system** for tabletop RPGs. Built on the Spirals in Spirals (SiS) framework, it helps you run narrative-focused campaigns where consequences accumulate, factions remember, and tension builds organically over time.

Think of it as your campaign's memory and conscience—tracking what can't be undone, surfacing what matters, and injecting complications that feel earned rather than arbitrary.

### The SiS System

**Spirals in Spirals (SiS)** is the underlying framework—a system-agnostic approach to managing narrative pressure in any tabletop RPG. The core concept:

- Pressure accumulates from player decisions
- Consequences route through different channels (Attention, Obligation, Dependency, Reputation)
- Critical moments emerge organically rather than being scheduled
- The system tracks what you can't ignore

SiS works with any game system and any setting:
- Fantasy (D&D, Pathfinder)
- Modern/Horror (Call of Cthulhu, VtM)
- Sci-fi (Traveller, Stars Without Number)
- Your own homebrew
- **SPAR** (pulp/noir, see below)

### Example Setting: SPAR

**SPAR (Serial Pulp Adventures Reborn)** is one campaign setting built on SiS—specifically a pulp/noir setting (1920s-1940s era) with themes of decay, corruption, and revelation. The SiS Tool Engine includes SPAR content packs as examples, but the engine itself is setting-neutral.

You don't need to run SPAR to use SiS. You can create your own setting-specific content packs for your preferred genre.

---

## What Can You Do With It?

### Campaign Management
- **Track multiple campaigns** with their own history, pressure, and factions
- **Remember consequences** across sessions (scars, faction relationships, accumulating problems)
- **Build narrative momentum** through pressure and heat mechanics
- **Import existing campaign notes** and structure them automatically

### Generate Complications
- **Events:** Situational complications for scenes (hazards, reinforcements, terrain shifts)
- **Loot:** Resource opportunities with consequences (gains that create obligations)
- **Batches for planning:** Generate 25-50 complications at once, pick what you need

### Session Workflow
1. Generate complications during prep or play
2. Stage them in your **Prep Queue** (non-canon scratch space)
3. Promote the ones that actually happened to **Canon**
4. Finalize the session to update campaign state
5. Export session notes or full campaign history

---

## How Does It Work? (The Non-Technical Version)

### The Sandpile Principle (SOC)

SiS uses a concept called **Self-Organized Criticality**—the same math that describes sandpile avalanches. Here's what that means for you:

**Pressure accumulates gradually:**
- From player decisions
- From unresolved problems
- From faction attention
- From resource scarcity

**Pressure releases in bursts:**
- Many small complications
- Fewer medium ones
- Rare critical moments

**You don't schedule the avalanche:**
- You inject pressure (play the game)
- The system decides when it breaks
- Critical moments feel earned, not triggered

**Example:** You don't set a "boss fight at session 5." Instead, pressure builds from sessions 1-4 (heat rises, faction attention grows, resources dwindle), and by session 5, something has to give. The system decides what.

### Pressure Spirals (How Consequences Route)

Pressure in SiS flows through four channels we call **Pressure Spirals:**

1. **Attention Spiral** - Being watched compounds; secrets become impossible
2. **Obligation Spiral** - Debts accumulate; autonomy erodes
3. **Dependency Spiral** - Systems fail; infrastructure crumbles
4. **Reputation Spiral** - Past actions haunt present choices

Different campaigns emphasize different Spirals. A noir detective campaign might lean Obligation. A heist campaign might lean Attention. SiS lets you bias which Spirals dominate without forcing outcomes.

### Why This Feels Different

**Traditional Tools:**
- "Roll on the random encounter table"
- "Here's a complication because it's turn 3"
- GM manually decides escalation

**SiS:**
- "Here's what pressure looks like right now"
- "This complication emerged from your campaign state"
- System tracks escalation; GM interprets results

---

## Common Use Cases

### Use Case 1: Running Long Campaigns

**Goal:** Track faction relationships, scars, and unresolved problems across 10+ sessions.

**Workflow:**
1. Create campaign with starting pressure
2. Generate complications per session
3. Finalize to record outcomes
4. Watch pressure/heat evolve
5. Factions remember your choices
6. Scars persist and matter

**Result:** Campaign feels like a living world with memory.

---

### Use Case 2: Planning Multiple Sessions at Once

**Goal:** Generate 25-50 complications, cherry-pick 5-8 for upcoming sessions, keep rest as backup.

**Workflow:**
1. Set batch size to 50
2. Generate once
3. Review variety analytics (expands to show diversity)
4. Select complications that fit your arc
5. Save unused ones for reactive moments

**Result:** You have a planning stash without repetitive generation.

---

### Use Case 3: Importing Existing Campaign Notes

**Goal:** Structure your freeform campaign notes into SiS's tracking system.

**Workflow:**
1. Copy/paste your campaign narrative
2. Parser extracts sessions, factions, key events
3. Review and correct entity classifications
4. Merge into new or existing campaign
5. Continue with tracked state

**Result:** Historical context becomes structured data.

---

### Use Case 4: System-Agnostic Play

**Goal:** Use SiS with D&D, GURPS, your homebrew, SPAR RPG, or any other system.

**Workflow:**
1. SiS outputs situations, not mechanics
2. You interpret severity in your system's terms
3. Tags guide what kind of complication it is
4. Effect vectors suggest fictional impact

**Result:** Works with any RPG system, any genre, any setting.

---

## Key Concepts (Quick Reference)

### Pressure (0-10)
Long-term problem accumulation. Decays slowly (~0.3/session).
- 0-3: Stable
- 4-6: Strained
- 7-10: Volatile

### Heat (0-10)
Immediate attention/pursuit. Decays faster (~0.8/session).
- 0-3: Quiet
- 4-6: Noticed
- 7-10: Hunted

### Scars
Lasting campaign-wide conditions (not PC-specific).
- Severity 1-2: Minor
- Severity 3: Significant
- Severity 4-5: Major

### Factions
Organizations that remember your actions.
- Disposition -5 (hostile) to +5 (allied)
- Attention 0-20 (how much they're watching)
- Affects future complication themes

### Severity (1-10)
How unstable/intense a complication is.
- 1-3: Manageable pressure
- 4-6: Significant challenge
- 7-10: Critical situation

### Tags
What kind of complication it is:
- `hazard`, `reinforcements`, `time_pressure`
- `visibility`, `social_friction`, `information`
- `terrain`, `attrition`, `cost`, `opportunity`

### Rarity Mode
How extreme outcomes can get:
- **Calm:** Gentle pressure, rare spikes
- **Normal:** Balanced distribution (default)
- **Spiky:** More extreme outcomes, higher tension

### Content Packs
Collections of complications/loot you can mix and match:
- Events (complications)
- Loot (resource shocks)
- Future: Rumors, NPCs, Hooks

---

## What SPAR Doesn't Do

**Not a Virtual Tabletop:**
- No maps, tokens, or combat tracker
- No dice roller or character sheets
- No game system rules or mechanics

**Not a Story Writer:**
- Generates situations, not solutions
- You decide what happens next
- Players create the narrative

**Not a Difficulty Slider:**
- No "make it harder" button
- Pressure accumulates from play
- You control inputs (decisions), not outcomes

---

## Philosophy in Practice

**SPAR's Core Mantra:**
> SPAR does not decide what happens. SPAR decides when accumulated pressure can no longer be ignored.

**What This Means for You:**
- You play the game normally
- SPAR tracks what you can't ignore
- Complications feel like consequences, not random events
- Critical moments emerge, they aren't scheduled

**Designer Truth:**
> "You're not fighting SOC—you're making it legible at human scale."

---

## Getting Started (5-Minute Quickstart)

### First Time Setup
```sh
# Install (one time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r streamlit_harness/requirements.txt

# Launch
streamlit run streamlit_harness/app.py
```

### Your First Campaign (2 Minutes)
1. Click **"+ New Campaign"**
2. Name it (e.g., "Wasteland Survival")
3. Leave pressure/heat at 0 (start fresh)
4. Click **"Create"**

### Generate First Complications (1 Minute)
1. From dashboard, click **"Run Session ⚡"**
2. Pick a scene preset (confined/populated/open/derelict)
3. Click **"Generate"**
4. Review complications

### Finalize First Session (2 Minutes)
1. Click **"Finalize This Session"**
2. Record what happened (2-3 bullets)
3. Add any major injuries as scars
4. Note faction interactions
5. Click **"Finalize"**

You've now tracked your first session. Repeat for session 2, and watch pressure/heat evolve.

---

## Where to Go Next

**For Campaign Usage:**
- `docs/PLAY_GUIDE_campaigns.md` - Detailed campaign workflows

**For Content Creation:**
- `docs/templates/README.md` - How to author content packs

**For Understanding the System:**
- `README.md` - Technical overview and API
- `docs/engineering_rules.md` Rule 00 - SOC foundation deep dive

**For Developers:**
- `docs/ARCH_campaign_integration.md` - System architecture
- `docs/KEY_DOCS.md` - Document index

---

## Common Questions

### "Do I need to use campaigns?"
No. You can use just the generators for one-shots or scene-level complications. Campaigns add memory and long-term consequence tracking.

### "Does this work with my game system?"
Yes. SiS is system-agnostic. It generates situations, not mechanics. You interpret severity, tags, and effects in your system's terms. SPAR is one example setting that runs on SiS.

### "How much content is included?"
- 107 core event complications (setting-neutral)
- 27 loot situations (15 core + 12 Salvage & Black Market)
- SPAR-specific packs available for pulp/noir campaigns
- More packs coming (Urban Intrigue, Horror Pressure, etc.)
- You can author your own setting-specific packs

### "What's the learning curve?"
- **Basic generation:** 5 minutes
- **Campaign management:** 15 minutes
- **Advanced features:** 30 minutes
- **Content authoring:** 1 hour with templates

### "Can I import my existing campaign notes?"
Yes. The history parser extracts structure from freeform narrative. Works with bullet lists, session logs, and natural language from any game system.

### "What if I want more control?"
SiS is designed around emergence, not control. If you want to manually set escalation, schedule encounters, or force specific outcomes, this tool will fight you. If you want pressure to build and break naturally, SiS is for you.

---

## Design Philosophy (The Why)

SiS Tool Engine started from a simple question:

> "Can we make procedural generation feel intentional?"

The answer was Self-Organized Criticality—the math of sandpiles, earthquakes, and forest fires. Pressure builds gradually. Release is uneven. Critical moments emerge.

This isn't just interesting math. It's the difference between:
- "Random encounter because dice" vs. "This threat was inevitable"
- "Loot because reward table" vs. "This resource comes with strings"
- "Boss fight at session 5" vs. "Everything has been building to this"

SiS tracks pressure so you don't have to. It remembers consequences so the world feels alive. It generates complications that answer "Why now?" instead of "Why not?"

**That's the tool's purpose: Make emergence legible for humans running campaigns.**

---

**Guide Version:** v0.1  
**SiS Tool Engine:** v1.0  
**For Support:** See docs/KEY_DOCS.md or GitHub issues
