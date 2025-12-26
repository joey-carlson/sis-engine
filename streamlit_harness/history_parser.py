"""Campaign history parser for imports.

Version History:
- v0.6 (2025-12-25): Comprehensive real-world fixes from 5-document test corpus
- v0.5 (2025-12-25): Additive fallbacks for unstructured notes
- v0.4 (2025-12-25): Markdown-it-py + dateparser + rapidfuzz integration COMPLETE
- v0.3 (2025-12-25): Ledger field separation, canon synthesis, faction cleanup
- v0.2 (2025-12-25): Section-aware parsing with entity classification
- v0.1 (2025-12-25): Initial history parsing implementation

v0.6 Major Fixes:
- Normalization pass: Strip separator artifacts, tag structure
- Section-first extraction: Factions, Assets, Parking Lot authority
- Session content: Labeled lines, Date: parsing, GM notes separation
- Entity mining: Appendix, Cast List, Night Map, region snapshots
- Prep document mode: Session 0 goals, questions, opening scene
- Open threads: Next session, Cool stuff, Loose ideas
- Content cleanup: Strip markdown artifacts, repair emphasis, sentence boundaries

Provides section-aware parsing of structured AND unstructured campaign documents.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Set

# Import new dependencies with graceful fallback
try:
    from markdown_it import MarkdownIt
    MARKDOWN_IT_AVAILABLE = True
except ImportError:
    MARKDOWN_IT_AVAILABLE = False

try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


# ===== NORMALIZATION PASS =====

def normalize_content(text: str) -> str:
    """Normalize raw document content for consistent parsing.
    
    Steps:
    1. Preserve line structure and order
    2. Strip decorative separators from stored content (but keep as boundaries)
    3. Clean broken emphasis markers
    4. Remove excessive whitespace
    
    Returns normalized text with cleaner structure.
    """
    lines = text.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Mark separator lines for boundary detection but don't preserve
        if re.match(r'^[\-=]{3,}$', line.strip()):
            normalized_lines.append('__SEPARATOR__')
            continue
        
        # Fix broken emphasis: *text:** → **text**
        line = re.sub(r'\*([^*]+):\*\*', r'**\1:**', line)
        
        # Fix broken emphasis: *text* * → *text*
        line = re.sub(r'\*([^*]+)\*\s+\*', r'*\1*', line)
        
        # Preserve line
        normalized_lines.append(line)
    
    # Rejoin and clean excessive whitespace
    normalized = '\n'.join(normalized_lines)
    normalized = re.sub(r'\n{3,}', '\n\n', normalized)  # Max 2 newlines
    
    return normalized


def clean_text_artifacts(text: str) -> str:
    """Remove markdown and separator artifacts from final output text.
    
    Used for cleaning bullets, content, and canon summaries.
    """
    if not text:
        return text
    
    # Strip heading markers
    text = re.sub(r'^#{1,6}\s+', '', text)
    
    # Strip separator lines
    text = re.sub(r'[\-=]{3,}', '', text)
    
    # Strip __SEPARATOR__ markers
    text = text.replace('__SEPARATOR__', '')
    
    # Clean excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


# ===== DATE NORMALIZATION =====

def normalize_date(date_str: str) -> Optional[str]:
    """Normalize date string to ISO YYYY-MM-DD format using dateparser.
    
    Handles:
    - ISO: 2025-01-05
    - Date: lines: "Date: 2026-01-06 (synthetic)"
    - Flexible formats: "Jan 5, 2025", "January 5 2025"
    
    Returns None if date cannot be parsed.
    """
    if not date_str:
        return None
    
    # Extract date from "Date: ..." lines
    if date_str.startswith('Date:'):
        date_str = date_str[5:].strip()
        # Remove parenthetical notes
        date_str = re.split(r'\s*\(', date_str)[0]
    
    if not DATEPARSER_AVAILABLE:
        # Fallback: try ISO format only
        match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
        if match:
            return match.group(0)
        return None
    
    try:
        parsed = dateparser.parse(date_str)
        if parsed:
            return parsed.strftime('%Y-%m-%d')
    except Exception:
        pass
    
    return None


# ===== FUZZY DEDUPLICATION =====

def fuzzy_dedupe_entities(names: List[str], threshold: int = 85) -> List[str]:
    """Deduplicate entity names using fuzzy matching with rapidfuzz."""
    if not RAPIDFUZZ_AVAILABLE or not names:
        return _simple_dedupe(names)
    
    # Normalize: strip "The " and lowercase for comparison
    normalized_map = {}
    for name in names:
        normalized = re.sub(r'^The\s+', '', name, flags=re.IGNORECASE).lower()
        if normalized not in normalized_map:
            normalized_map[normalized] = []
        normalized_map[normalized].append(name)
    
    # For each cluster, keep variant without "The " if available
    result = []
    for variants in normalized_map.values():
        without_the = [v for v in variants if not v.startswith('The ')]
        if without_the:
            result.append(without_the[0])
        else:
            result.append(variants[0])
    
    # Use rapidfuzz to catch near-duplicates across clusters
    if len(result) > 1:
        seen = set()
        final = []
        for name in sorted(result):
            if name in seen:
                continue
            
            matches = process.extract(name, final, scorer=fuzz.ratio, limit=1)
            if matches and matches[0][1] >= threshold:
                seen.add(name)
                continue
            
            final.append(name)
            seen.add(name)
        
        return sorted(final)
    
    return sorted(result)


def _simple_dedupe(names: List[str]) -> List[str]:
    """Fallback deduplication without rapidfuzz."""
    seen = {}
    for name in names:
        normalized = re.sub(r'^The\s+', '', name, flags=re.IGNORECASE)
        key = normalized.lower()
        if key not in seen:
            seen[key] = normalized
    return sorted(seen.values())


# ===== SECTION SPLITTING =====

def split_by_sections(text: str) -> Dict[str, str]:
    """Split document by top-level markdown headings (##).
    
    Uses markdown-it-py for robust structure parsing.
    Falls back to regex if markdown-it-py unavailable.
    """
    if MARKDOWN_IT_AVAILABLE:
        return _markdown_it_split_sections(text)
    else:
        return _regex_split_sections(text)


def _markdown_it_split_sections(text: str) -> Dict[str, str]:
    """Split sections using markdown-it-py token parsing."""
    md = MarkdownIt()
    tokens = md.parse(text)
    
    text_lines = text.split('\n')
    
    sections = {}
    section_boundaries = []
    
    # Find all h2 headings and their line positions
    for i, token in enumerate(tokens):
        if token.type == 'heading_open' and token.tag == 'h2':
            if i + 1 < len(tokens) and tokens[i + 1].type == 'inline':
                heading_text = tokens[i + 1].content.strip()
                
                # Normalize: remove (parens), lowercase
                normalized = heading_text.lower()
                normalized = re.sub(r'\s*\([^)]*\)\s*', '', normalized)
                normalized = normalized.strip()
                
                if token.map:
                    start_line = token.map[0]
                    section_boundaries.append((normalized, start_line))
    
    # Extract content between boundaries
    if not section_boundaries:
        sections["_preamble"] = text.strip()
        return sections
    
    # Preamble: before first h2
    if section_boundaries[0][1] > 0:
        preamble_lines = text_lines[:section_boundaries[0][1]]
        sections["_preamble"] = '\n'.join(preamble_lines).strip()
    
    # Extract each section's content
    for idx, (heading, start_line) in enumerate(section_boundaries):
        content_start = start_line + 1
        
        if idx + 1 < len(section_boundaries):
            content_end = section_boundaries[idx + 1][1]
        else:
            content_end = len(text_lines)
        
        content_lines = text_lines[content_start:content_end]
        sections[heading] = '\n'.join(content_lines).strip()
    
    return sections


def _regex_split_sections(text: str) -> Dict[str, str]:
    """Fallback regex-based section splitting."""
    sections = {}
    
    parts = re.split(r'\n##\s+(.+?)\n', text)
    
    if parts[0].strip():
        sections["_preamble"] = parts[0].strip()
    
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            heading = parts[i].strip()
            content = parts[i + 1].strip()
            
            key = heading.lower().replace('(', '').replace(')', '').strip()
            sections[key] = content
    
    return sections


# ===== FACTION EXTRACTION =====

def extract_factions_from_section(factions_section: str) -> List[Dict[str, Any]]:
    """Extract factions from explicit Factions section.
    
    Parses:
    - ### Faction Name
      - Description bullets
      - Key faces: NPC1, NPC2
    
    Returns list of faction dicts with name, description, key_npcs.
    """
    if not factions_section:
        return []
    
    factions = []
    
    # Split by ### subsections
    subsections = re.split(r'\n###\s+(.+?)\n', factions_section)
    
    for i in range(1, len(subsections), 2):
        if i + 1 < len(subsections):
            faction_name = subsections[i].strip()
            faction_content = subsections[i + 1].strip()
            
            # Extract description bullets
            description_lines = []
            key_npcs = []
            
            lines = faction_content.split('\n')
            in_key_faces = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect "Key faces:" section
                if re.match(r'^Key faces?:', line, re.IGNORECASE):
                    in_key_faces = True
                    # Parse NPCs from same line if present
                    npc_text = re.sub(r'^Key faces?:\s*', '', line, flags=re.IGNORECASE)
                    if npc_text:
                        key_npcs.extend([n.strip() for n in npc_text.split(',')])
                    continue
                
                # Parse content based on context
                if in_key_faces:
                    # In key faces section - parse NPC names
                    if re.match(r'^[\-\*•]\s+', line):
                        npc_name = re.sub(r'^[\-\*•]\s+', '', line)
                        # Remove parenthetical notes
                        npc_name = re.split(r'\s*\(', npc_name)[0].strip()
                        key_npcs.append(npc_name)
                    else:
                        # Comma-separated NPCs on continuation line
                        key_npcs.extend([n.strip() for n in line.split(',') if n.strip()])
                else:
                    # Regular description content
                    if re.match(r'^[\-\*•]\s+', line):
                        desc_line = re.sub(r'^[\-\*•]\s+', '', line)
                        description_lines.append(desc_line)
                    elif description_lines:
                        # Continuation of previous line
                        description_lines[-1] += ' ' + line
            
            # Build faction dict
            faction_dict = {
                "name": clean_text_artifacts(faction_name),
                "description": ' '.join(description_lines) if description_lines else "",
            }
            
            if key_npcs:
                faction_dict["key_npcs"] = [clean_text_artifacts(npc) for npc in key_npcs if npc]
            
            factions.append(faction_dict)
    
    return factions


# ===== ARTIFACT EXTRACTION =====

def extract_artifacts_from_sections(text: str, sections: Dict[str, str]) -> List[str]:
    """Extract artifacts from multiple potential sources.
    
    Sources (in priority order):
    1. Party assets / Notable gear sections
    2. Parking Lot → Items/Props subsections
    3. Major Artifacts in Canon Summary
    4. Loot/Economy sections
    
    Returns deduplicated list of artifact names.
    """
    artifacts = []
    
    # Source 1: Party assets / Notable gear
    for key in sections.keys():
        if any(term in key for term in ['party asset', 'notable gear', 'equipment', 'party gear']):
            artifacts.extend(_extract_artifacts_from_list(sections[key]))
    
    # Source 2: Parking Lot items/props
    for key in sections.keys():
        if 'parking lot' in key:
            # Look for Items/Props subsection
            parking_content = sections[key]
            items_match = re.search(r'(?:^|\n)#+\s*Items?\s*/\s*Props?\s*\n(.*?)(?=\n#+|\Z)', parking_content, re.DOTALL | re.IGNORECASE)
            if items_match:
                artifacts.extend(_extract_artifacts_from_list(items_match.group(1)))
    
    # Source 3: Major Artifacts in Canon
    for key in sections.keys():
        if 'canon summary' in key or 'campaign overview' in key:
            canon_content = sections[key]
            artifacts_match = re.search(r'(?:^|\n)###\s*(?:Major\s+)?Artifacts?.*?\n(.*?)(?=\n###|\Z)', canon_content, re.DOTALL | re.IGNORECASE)
            if artifacts_match:
                artifacts.extend(_extract_artifacts_from_section(artifacts_match.group(1)))
    
    # Source 4: Loot/Economy sections
    for key in sections.keys():
        if 'loot' in key or 'economy' in key:
            artifacts.extend(_extract_artifacts_from_list(sections[key]))
    
    # Deduplicate
    return fuzzy_dedupe_entities(artifacts)


def _extract_artifacts_from_list(content: str) -> List[str]:
    """Extract artifact names from a bullet list or paragraph."""
    artifacts = []
    
    # Pattern 1: Bullet list items
    for match in re.finditer(r'^[\-\*•]\s+([A-Z][^\n:]{2,60})(?:\s*[:\-–—]|$)', content, re.MULTILINE):
        name = match.group(1).strip()
        name = re.sub(r'[.,;]$', '', name)
        artifacts.append(name)
    
    # Pattern 2: Possessive forms "X's Y"
    for match in re.finditer(r"([A-Z][a-z]+'s(?:s)?\s+[A-Z][a-z]+)", content):
        artifacts.append(match.group(1))
    
    # Pattern 3: "The X" patterns
    for match in re.finditer(r'\bThe\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b', content):
        artifacts.append(match.group(1))
    
    return artifacts


def _extract_artifacts_from_section(artifact_section: str) -> List[str]:
    """Extract artifact names from Major Artifacts section with complex patterns."""
    if not artifact_section:
        return []
    
    artifacts = []
    
    # Pattern 1: Possessives including double-s: "Bryannas's Ring"
    pattern1 = r"([A-Z][a-z]+'s(?:s)?\s+(?:Ring|Device|Crown|Staff|Sword|Orb|Lens|[A-Z][a-z]+))"
    for match in re.finditer(pattern1, artifact_section):
        artifacts.append(match.group(1).strip())
    
    # Pattern 2: "The X:" format
    pattern2 = r'The\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):'
    for match in re.finditer(pattern2, artifact_section):
        artifacts.append(match.group(1).strip())
    
    # Pattern 3: "X of Y" complex forms
    pattern3 = r'((?:Infernal\s+)?Device\s+of\s+[A-Z][a-z]+(?:\s+[a-z]+)?(?:\s+[A-Z][a-z]+)?)'
    for match in re.finditer(pattern3, artifact_section, re.IGNORECASE):
        artifacts.append(match.group(1).strip())
    
    # Pattern 4: Control lever / rod (normalize compound forms)
    pattern4 = r'(Control\s+(?:lever|rod)(?:\s*/\s*(?:lever|rod))?)'
    for match in re.finditer(pattern4, artifact_section, re.IGNORECASE):
        normalized = match.group(1).replace(' / ', ' ').strip()
        artifacts.append(normalized)
    
    return artifacts


# ===== ENTITY MINING =====

def mine_entities_from_sections(text: str, sections: Dict[str, str]) -> Dict[str, List[str]]:
    """Mine entities from explicit entity-rich sections.
    
    Sources:
    - Night Map / Anchors → places
    - NPC Cast List → npcs
    - Appendix: quick names → places/npcs
    - Region snapshot → places
    - Named phenomena → concepts
    
    Returns dict with places, npcs, concepts lists.
    """
    places = []
    npcs = []
    concepts = []
    
    # Source 1: Night Map / Anchors
    for key in sections.keys():
        if 'night map' in key or 'anchors' in key or 'los angeles night map' in key:
            places.extend(_extract_places_from_list(sections[key]))
    
    # Source 2: NPC Cast List
    for key in sections.keys():
        if 'npc' in key and ('cast' in key or 'list' in key):
            npcs.extend(_extract_npcs_from_cast_list(sections[key]))
    
    # Source 3: Appendix quick names
    for key in sections.keys():
        if 'appendix' in key and ('name' in key or 'quick' in key):
            entities = _extract_entities_from_appendix(sections[key])
            places.extend(entities['places'])
            npcs.extend(entities['npcs'])
    
    # Source 4: Region snapshot / Geography
    for key in sections.keys():
        if 'region' in key or 'geography' in key or 'the place' in key:
            places.extend(_extract_places_from_region(sections[key]))
    
    # Source 5: Named phenomena (concepts)
    concepts.extend(_extract_concepts_from_text(text))
    
    return {
        "places": fuzzy_dedupe_entities(places),
        "npcs": fuzzy_dedupe_entities(npcs),
        "concepts": fuzzy_dedupe_entities(concepts),
    }


def _extract_places_from_list(content: str) -> List[str]:
    """Extract place names from a list section."""
    places = []
    
    # Bullet list items
    for match in re.finditer(r'^[\-\*•]\s+([A-Z][^\n:]{2,60})(?:\s*[:\-–—]|$)', content, re.MULTILINE):
        name = match.group(1).strip()
        name = re.sub(r'[.,;]$', '', name)
        name = re.split(r'\s*\(', name)[0].strip()
        places.append(name)
    
    return places


def _extract_npcs_from_cast_list(content: str) -> List[str]:
    """Extract NPC names from cast list section."""
    npcs = []
    
    # Pattern: bullet list with names
    for match in re.finditer(r'^[\-\*•]\s+([A-Z][a-z]+(?:\s+[A-Z][a-z\']+)*)', content, re.MULTILINE):
        name = match.group(1).strip()
        name = re.split(r'\s*\(', name)[0].strip()
        npcs.append(name)
    
    # Pattern: comma-separated names
    for line in content.split('\n'):
        if re.search(r'[A-Z][a-z]+,\s*[A-Z][a-z]+', line):
            names = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z\']+)*)', line)
            npcs.extend(names[:5])
    
    return npcs


def _extract_entities_from_appendix(content: str) -> Dict[str, List[str]]:
    """Extract and classify entities from Appendix section."""
    places = []
    npcs = []
    
    lines = content.split('\n')
    current_category = None
    
    for line in lines:
        # Detect category markers
        if re.match(r'^#+\s*(?:Places?|Locations?)', line, re.IGNORECASE):
            current_category = 'places'
            continue
        elif re.match(r'^#+\s*(?:NPCs?|Characters?|People)', line, re.IGNORECASE):
            current_category = 'npcs'
            continue
        
        # Extract from bullets
        if re.match(r'^[\-\*•]\s+', line):
            name = re.sub(r'^[\-\*•]\s+', '', line).strip()
            name = re.split(r'\s*\(', name)[0].strip()
            name = re.sub(r'[.,;:]$', '', name)
            
            if len(name) > 2 and name[0].isupper():
                if current_category == 'places':
                    places.append(name)
                elif current_category == 'npcs':
                    npcs.append(name)
                else:
                    # Classify by keywords
                    if any(word in name.lower() for word in ['street', 'district', 'pier', 'row', 'hotel', 'market', 'port']):
                        places.append(name)
                    else:
                        npcs.append(name)
    
    return {"places": places, "npcs": npcs}


def _extract_places_from_region(content: str) -> List[str]:
    """Extract place names from region/geography section."""
    places = []
    
    # Pattern 1: "Place: Description" format
    for match in re.finditer(r'^([A-Z][^\n:]{2,40}):\s*', content, re.MULTILINE):
        place = match.group(1).strip()
        places.append(place)
    
    # Pattern 2: Bold place names **Place**
    for match in re.finditer(r'\*\*([A-Z][^\*]{2,40})\*\*', content):
        place = match.group(1).strip()
        places.append(place)
    
    # Pattern 3: Capitalized phrases
    for match in re.finditer(r'\b((?:The\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b', content):
        phrase = match.group(1)
        if any(word in phrase.lower() for word in ['district', 'depot', 'sinks', 'flats', 'line', 'street']):
            places.append(phrase)
    
    return places


def _extract_concepts_from_text(text: str) -> List[str]:
    """Extract named phenomena and concepts from document."""
    concepts = []
    
    # Pattern 1: Quoted phrases
    for match in re.finditer(r'"([A-Z][^"]{3,40})"', text):
        concept = match.group(1).strip()
        if ' ' in concept:
            concepts.append(concept)
    
    # Pattern 2: Hyphenated conditions
    for match in re.finditer(r'\b([A-Z][a-z]+-[a-z]+)\b', text):
        concept = match.group(1)
        if any(word in concept.lower() for word in ['sick', 'fever', 'veil', 'fog']):
            concepts.append(concept)
    
    # Pattern 3: Named mechanics
    for match in re.finditer(r'\b([A-Z][a-z]+\s+(?:Ledger|[Ee]conomy|[Ss]ystem))\b', text):
        concepts.append(match.group(1))
    
    return concepts


# ===== CANON EXTRACTION =====

def _extract_bullets_from_text(text: str, max_bullets: int = 10) -> List[str]:
    """Extract bullet points or sentences from text block.
    
    Prioritizes:
    1. Existing bullet lists
    2. Sentences (if no bullets)
    
    Cleans artifacts and caps at max_bullets.
    """
    bullets = []
    
    # Try bullet list first
    for match in re.finditer(r'^[\-\*•]\s+(.+?)$', text, re.MULTILINE):
        bullet = match.group(1).strip()
        bullet = clean_text_artifacts(bullet)
        if len(bullet) > 20:
            bullets.append(bullet)
    
    # If no bullets, extract sentences
    if not bullets:
        sentences = re.split(r'[.!?]+\s+', text)
        for sentence in sentences:
            sentence = clean_text_artifacts(sentence)
            if len(sentence) > 30:
                bullets.append(sentence)
    
    return bullets[:max_bullets]


def extract_canon_from_section(canon_section: str) -> List[str]:
    """Extract canon bullets from Canon Summary section."""
    if not canon_section:
        return []
    
    bullets = []
    
    # Split by ### subsections
    subsections = re.split(r'\n###\s+(.+?)\n', canon_section)
    
    subsection_content = {}
    for i in range(1, len(subsections), 2):
        if i + 1 < len(subsections):
            heading = subsections[i].strip().lower()
            content = subsections[i + 1].strip()
            subsection_content[heading] = content
    
    def find_subsection(keywords: List[str]) -> Optional[str]:
        for key in subsection_content.keys():
            if any(kw in key for kw in keywords):
                return subsection_content[key]
        return None
    
    # Extract in logical order
    premise = find_subsection(['vibe', 'premise', 'pitch', 'one-sentence', 'elevator'])
    if premise:
        bullets.extend(_extract_bullets_from_text(premise, max_bullets=2))
    
    themes = find_subsection(['core themes', 'theme', 'pillars'])
    if themes:
        bullets.extend(_extract_bullets_from_text(themes, max_bullets=2))
    
    engine = find_subsection(['engine', 'myth-arc', 'myth arc', 'long-haul', 'big idea'])
    if engine:
        bullets.extend(_extract_bullets_from_text(engine, max_bullets=1))
    
    party = find_subsection(['player character', 'the party', 'party'])
    if party:
        bullets.append("Party roster established")
    
    antagonist = find_subsection(['antagonist', 'villain', 'threat'])
    if antagonist:
        bullets.extend(_extract_bullets_from_text(antagonist, max_bullets=2))
    
    ally = find_subsection(['allied forces', 'allies', 'major allied'])
    if ally:
        bullets.extend(_extract_bullets_from_text(ally, max_bullets=1))
    
    npcs = find_subsection(['npc', 'powers in play', 'guardians', 'temporal'])
    if npcs:
        bullets.extend(_extract_bullets_from_text(npcs, max_bullets=2))
    
    # Major Artifacts
    artifacts = find_subsection(['artifact', 'mysteries', 'chronolens'])
    if artifacts:
        bullets.extend(_extract_bullets_from_text(artifacts, max_bullets=2))
    
    cosmology = find_subsection(['cosmology', 'backbone', 'frame twist'])
    if cosmology:
        bullets.extend(_extract_bullets_from_text(cosmology, max_bullets=1))
    
    situation = find_subsection(['current situation', 'current state', 'state of play', 'status'])
    if situation:
        bullets.extend(_extract_bullets_from_text(situation, max_bullets=2))
    
    return bullets[:12]


# ===== SESSION EXTRACTION =====

def parse_ledger_sessions(ledger_section: str) -> List[Dict[str, Any]]:
    """Parse sessions from Campaign Ledger section."""
    if not ledger_section:
        return []
    
    sessions = []
    
    # Pattern for session headers
    session_pattern = r'###\s+(\d{4}-\d{2}-\d{2})\s+[—–]\s+Session\s+(\d+)(?:\s+\(Current\))?\s+[—–]\s+([^\n]+)'
    
    for match in re.finditer(session_pattern, ledger_section):
        date_str = match.group(1)
        session_num = int(match.group(2))
        title = match.group(3).strip()
        
        normalized_date = normalize_date(date_str) or date_str
        
        # Extract content
        content_start = match.end()
        content_end = ledger_section.find('\n###', content_start)
        if content_end == -1:
            content_end = len(ledger_section)
        
        raw_content = ledger_section[content_start:content_end].strip()
        bullets, gm_notes = _extract_session_content(raw_content)
        
        session_dict = {
            "session_number": session_num,
            "date": normalized_date,
            "title": clean_text_artifacts(title),
            "bullets": [clean_text_artifacts(b) for b in bullets],
            "content": clean_text_artifacts(raw_content),
        }
        
        if gm_notes:
            session_dict["gm_notes"] = gm_notes
        
        sessions.append(session_dict)
    
    # Pattern for addendum entries
    addendum_pattern = r'###\s+(\d{4}-\d{2}-\d{2})\s+[—–]\s+Addendum(?:\s+\([^)]+\))?\s+[—–]\s+([^\n]+)'
    
    for match in re.finditer(addendum_pattern, ledger_section):
        date_str = match.group(1)
        title = match.group(2).strip()
        
        normalized_date = normalize_date(date_str) or date_str
        
        content_start = match.end()
        content_end = ledger_section.find('\n###', content_start)
        if content_end == -1:
            content_end = len(ledger_section)
        
        raw_content = ledger_section[content_start:content_end].strip()
        bullets, gm_notes = _extract_session_content(raw_content)
        
        session_dict = {
            "session_number": None,
            "entry_type": "addendum",
            "date": normalized_date,
            "title": clean_text_artifacts(title),
            "bullets": [clean_text_artifacts(b) for b in bullets],
            "content": clean_text_artifacts(raw_content),
        }
        
        if gm_notes:
            session_dict["gm_notes"] = gm_notes
        
        sessions.append(session_dict)
    
    sessions.sort(key=lambda s: s["date"])
    return sessions


def _extract_session_content(content: str) -> Tuple[List[str], List[str]]:
    """Extract bullets and GM notes from session content.
    
    Handles:
    - Labeled lines: Job:, Combat:, Aftermath:, etc.
    - Date: lines within blocks
    - GM notes: "GM note:", "Table note:", "GM seed:"
    
    Returns (bullets, gm_notes).
    """
    bullets = []
    gm_notes = []
    
    lines = content.split('\n')
    current_bullet = None
    
    for line in lines:
        line = line.strip()
        if not line or line == '__SEPARATOR__':
            continue
        
        # Check for GM note patterns
        gm_match = re.match(r'^(?:GM note|Table note|GM seed|GM margin note):\s*(.+)', line, re.IGNORECASE)
        if gm_match:
            gm_notes.append(gm_match.group(1).strip())
            continue
        
        # Check for labeled lines (Job:, Combat:, etc.)
        labeled_match = re.match(r'^([A-Z][a-z]+):\s*(.+)', line)
        if labeled_match:
            label = labeled_match.group(1)
            text = labeled_match.group(2)
            
            # Special handling for Date:
            if label.lower() == 'date':
                continue  # Dates handled separately
            
            # Save previous bullet if any
            if current_bullet:
                bullets.append(current_bullet)
            
            # Start new labeled bullet
            current_bullet = f"{label}: {text}"
            continue
        
        # Check for bullet markers
        if re.match(r'^[\-\*•]\s+', line):
            # Save previous bullet
            if current_bullet:
                bullets.append(current_bullet)
            
            # Start new bullet
            current_bullet = re.sub(r'^[\-\*•]\s+', '', line)
            continue
        
        # Continuation line
        if current_bullet:
            current_bullet += ' ' + line
    
    # Save final bullet
    if current_bullet:
        bullets.append(current_bullet)
    
    return bullets, gm_notes


def parse_relaxed_sessions(text: str) -> List[Dict[str, Any]]:
    """Parse sessions from relaxed header patterns.
    
    Supports: "SESSION 3 — TITLE", "Game 5", "Day 1" etc.
    Extracts labeled lines and Date: lines within blocks.
    """
    sessions = []
    
    # Pattern: SESSION N — "Title" or SESSION N BACK (WHERE...)
    header_pattern = r'(?:^|\n)(SESSION\s+\d+\s+(?:—|BACK)\s+[^\n]{5,100})'
    
    lines = text.split('\n')
    
    for match in re.finditer(header_pattern, text, re.IGNORECASE):
        header = match.group(1).strip()
        
        # Extract session number and title
        session_num_match = re.search(r'SESSION\s+(\d+)', header, re.IGNORECASE)
        session_num = int(session_num_match.group(1)) if session_num_match else None
        
        title_match = re.search(r'(?:—|BACK)\s+(.+)', header, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else header
        title = clean_text_artifacts(title)
        
        # Find position
        pos = match.start()
        line_num = text[:pos].count('\n')
        
        # Extract content until next session or major boundary
        content_lines = []
        found_date = None
        
        for i in range(line_num + 1, min(line_num + 100, len(lines))):
            line = lines[i].strip()
            
            # Stop at next session
            if re.match(r'^SESSION\s+\d+', line, re.IGNORECASE):
                break
            
            # Stop at h2 headers
            if line.startswith('##'):
                break
            
            # Extract Date: if present
            if line.startswith('Date:') and not found_date:
                found_date = normalize_date(line)
            
            if line:
                content_lines.append(lines[i])  # Preserve original indentation
        
        content = '\n'.join(content_lines)
        bullets, gm_notes = _extract_session_content(content)
        
        # Only add if has substantive content
        if bullets or len(content) > 50:
            session_dict = {
                "session_number": session_num,
                "date": found_date or "Unknown",
                "title": title,
                "bullets": [clean_text_artifacts(b) for b in bullets],
                "content": clean_text_artifacts(content),
            }
            
            if gm_notes:
                session_dict["gm_notes"] = gm_notes
            
            sessions.append(session_dict)
    
    return sessions


# ===== OPEN THREADS EXTRACTION =====

def extract_open_threads_from_sections(sections: Dict[str, str]) -> List[str]:
    """Extract open threads from multiple potential sources.
    
    Sources:
    - Open Threads section (direct)
    - Parking Lot section
    - Next session options
    - Cool stuff / Loose ideas
    - Questions to answer
    - Things that can go wrong
    
    Returns deduplicated list of thread descriptions.
    """
    threads = []
    
    # Source 0: Open Threads section (direct extraction)
    for key in sections.keys():
        if 'open thread' in key:
            threads.extend(_extract_threads_from_text(sections[key]))
    
    # Source 1: Parking Lot
    for key in sections.keys():
        if 'parking lot' in key:
            parking_content = sections[key]
            
            # Extract from bullet lists (excluding Items/Props already handled)
            # Look for Encounters, Events, Twists, Questions subsections
            for subsection_type in ['encounter', 'event', 'twist', 'question']:
                pattern = rf'(?:^|\n)#+\s*{subsection_type}.*?\n(.*?)(?=\n#+|\Z)'
                match = re.search(pattern, parking_content, re.DOTALL | re.IGNORECASE)
                if match:
                    threads.extend(_extract_threads_from_text(match.group(1)))
    
    # Source 2: Next session / Future hooks
    for key in sections.keys():
        if 'next session' in key or 'future hook' in key:
            threads.extend(_extract_threads_from_text(sections[key]))
    
    # Source 3: Cool stuff / Loose ideas
    for key in sections.keys():
        if any(term in key for term in ['cool stuff', 'loose idea', 'no slot yet']):
            threads.extend(_extract_threads_from_text(sections[key]))
    
    # Source 4: Questions to answer
    for key in sections.keys():
        if 'question' in key and 'answer' in key:
            threads.extend(_extract_threads_from_text(sections[key]))
    
    # Source 5: Things that can go wrong / Complications
    for key in sections.keys():
        if 'things that can go wrong' in key or 'complications' in key:
            threads.extend(_extract_threads_from_text(sections[key]))
    
    # Deduplicate
    return fuzzy_dedupe_entities(threads)


def _extract_threads_from_text(content: str) -> List[str]:
    """Extract thread descriptions from text."""
    threads = []
    
    # Extract from bullets
    for match in re.finditer(r'^[\-\*•]\s+(.+?)$', content, re.MULTILINE):
        thread = match.group(1).strip()
        thread = clean_text_artifacts(thread)
        if len(thread) > 20:
            threads.append(thread)
    
    return threads


# ===== PREP DOCUMENT SUPPORT =====

def extract_prep_content(sections: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Extract Session 0 prep content from prep-only documents.
    
    Returns dict with:
    - goals: Session 0 goals list
    - questions: Player prompt questions
    - opening_scene: Cold open description
    
    Returns None if no prep content detected.
    """
    prep_content = {}
    
    # Look for Session 0 / Prep markers
    has_prep_marker = False
    for key in sections.keys():
        if 'session 0' in key or 'session zero' in key or 'prep' in key:
            has_prep_marker = True
            break
    
    if not has_prep_marker:
        return None
    
    # Extract goals
    for key in sections.keys():
        if 'session 0' in key and 'goal' in key:
            goals = _extract_bullets_from_text(sections[key])
            if goals:
                prep_content['goals'] = goals
    
    # Extract questions
    for key in sections.keys():
        if 'question' in key and ('player' in key or "i'll ask" in key):
            questions = _extract_bullets_from_text(sections[key])
            if questions:
                prep_content['questions'] = questions
    
    # Extract opening scene
    for key in sections.keys():
        if 'opening scene' in key or 'cold open' in key:
            scene_text = sections[key]
            prep_content['opening_scene'] = clean_text_artifacts(scene_text[:500])
    
    return prep_content if prep_content else None


# ===== FUTURE SESSIONS EXTRACTION =====

def parse_future_sessions(future_section: str) -> List[Dict[str, str]]:
    """Parse future sessions from Future Sessions section."""
    if not future_section:
        return []
    
    future_sessions = []
    
    # Split by ### subsections
    subsections = re.split(r'(?:^|\n)###\s+(.+?)(?:\n|$)', future_section, flags=re.MULTILINE)
    
    for i in range(1, len(subsections), 2):
        if i + 1 < len(subsections):
            title = subsections[i].strip()
            content = subsections[i + 1].strip()
            
            if title and len(content) > 10:
                future_sessions.append({
                    "title": clean_text_artifacts(title),
                    "notes": clean_text_artifacts(content),
                })
    
    return future_sessions


# ===== FALLBACK EXTRACTION =====

def extract_paragraph_canon(text: str, min_bullets: int = 4) -> List[str]:
    """Fallback: extract canon bullets from opening paragraphs."""
    bullets = []
    
    paragraphs = text.split('\n\n')
    opening_text = '\n\n'.join(paragraphs[:5])[:2000]
    
    sentences = re.split(r'[.!?]+\s+', opening_text)
    
    for sentence in sentences[:10]:
        sentence = sentence.strip()
        
        if len(sentence) < 30:
            continue
        if sentence.startswith('#'):
            continue
        if any(skip in sentence.lower() for skip in ['import', 'use:', 'notes for']):
            continue
        
        cleaned = clean_text_artifacts(sentence[:160])
        if len(cleaned) >= 40:
            bullets.append(cleaned)
        
        if len(bullets) >= min_bullets:
            break
    
    return bullets[:min_bullets]


# ===== PARSER INDEX SUPPORT =====

def extract_from_parser_index(text: str) -> Optional[Dict[str, List[str]]]:
    """Extract entities from Parser-Friendly Index section if present."""
    sections = split_by_sections(text)
    
    index_key = None
    for key in sections.keys():
        if ('parser' in key and 'index' in key) or 'key entities' in key:
            index_key = key
            break
    
    if not index_key:
        return None
    
    index_section = sections[index_key]
    result = {
        "factions": [],
        "places": [],
        "artifacts": [],
        "concepts": [],
    }
    
    # Parse category blocks
    category_pattern = r'(Artifacts?|Groups?|Factions?|Places?|Concepts?|Powers?):\s*\n((?:[\-\*•]\s*.+\n?)+)'
    
    for match in re.finditer(category_pattern, index_section, re.IGNORECASE | re.MULTILINE):
        category = match.group(1).lower().rstrip('s')
        items_block = match.group(2)
        
        items = []
        for line in items_block.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            cleaned = re.sub(r'^[\-\*•]\s*', '', line)
            main_name = re.split(r'\s*\(', cleaned)[0].strip()
            
            if main_name:
                items.append(main_name)
        
        # Map category to result keys
        if category in ['group', 'faction']:
            result["factions"].extend(items)
        elif category == 'place':
            result["places"].extend(items)
        elif category == 'artifact':
            result["artifacts"].extend(items)
        elif category in ['concept', 'power']:
            result["concepts"].extend(items)
    
    return result if any(result.values()) else None


# ===== HEURISTIC ENTITY CLASSIFICATION =====

def classify_entities(text: str, canon_section: Optional[str] = None) -> Dict[str, List[str]]:
    """Fallback heuristic classification of entities."""
    entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    matches = re.findall(entity_pattern, text)
    
    entity_counts = {}
    for match in matches:
        entity_counts[match] = entity_counts.get(match, 0) + 1
    
    frequent = {name: count for name, count in entity_counts.items() if count >= 2}
    
    # Filter section headers
    section_headers = ['Future Sessions', 'Open Threads', 'Campaign Ledger', 'Canon Summary', 'Parser Index', 'Key Entities']
    arc_markers = ['Spiral', 'Projected', 'Expected']
    
    filtered = {}
    for name, count in frequent.items():
        if name in section_headers:
            continue
        if any(marker in name for marker in arc_markers):
            continue
        filtered[name] = count
    
    # Add Astral Elves if context suggests
    if 'Astral Elves' not in filtered and 'Astral Elf' in text:
        if any(term in text for term in ['Astral Elf forces', 'Astral Elf splinter', 'Astral Elven']):
            filtered['Astral Elves'] = 1
    
    # Classification
    faction_keywords = ['pact', 'guild', 'order', 'watch', 'cult', 'consortium', 'guardians', 'makers', 'council']
    place_demoters = ['tunnels', 'citadel', 'staircase', 'archives', 'sphere', 'chamber', 'fortress', 'ship', 'city']
    place_keywords = ['citadel', 'city', 'fortress', 'bral', 'sphere', 'staircase', 'tower', 'palace', 'keep']
    artifact_keywords = ['lens', 'ring', 'device', 'crown', 'scepter', 'amulet', 'orb', 'staff', 'sword', 'crystal']
    concept_keywords = ['incarnate', 'seed', 'essence', 'aspect', 'principle']
    
    factions = []
    places = []
    artifacts = []
    concepts = []
    
    for entity in filtered.keys():
        entity_lower = entity.lower()
        normalized = re.sub(r'^The\s+', '', entity)
        
        if any(demoter in entity_lower for demoter in place_demoters):
            places.append(normalized)
        elif any(kw in entity_lower for kw in faction_keywords):
            factions.append(normalized)
        elif any(kw in entity_lower for kw in place_keywords):
            places.append(normalized)
        elif any(kw in entity_lower for kw in artifact_keywords):
            artifacts.append(normalized)
        elif any(kw in entity_lower for kw in concept_keywords):
            concepts.append(normalized)
        elif entity.endswith('s') or ' of ' in entity_lower:
            factions.append(normalized)
    
    return {
        "factions": fuzzy_dedupe_entities(factions),
        "places": fuzzy_dedupe_entities(places),
        "artifacts": fuzzy_dedupe_entities(artifacts),
        "concepts": fuzzy_dedupe_entities(concepts),
    }


# ===== MAIN PARSER =====

def parse_campaign_history(text: str, campaign_id: Optional[str] = None) -> Dict[str, Any]:
    """Parse structured campaign history into components.
    
    v0.6 comprehensive parsing:
    - Normalization pass for content cleanup
    - Section-first extraction (authoritative)
    - Session content with labeled lines and GM notes
    - Entity mining from explicit sections
    - Prep document mode support
    - Open threads from multiple sources
    
    Returns dictionary with all extracted components.
    """
    # Step 1: Normalize content
    text = normalize_content(text)
    
    # Step 2: Split into sections
    sections = split_by_sections(text)
    
    # Step 3: Extract from authoritative sections
    
    # Canon Summary (section-first)
    canon_section_key = None
    canon_synonyms = ['canon summary', 'campaign overview', 'campaign bible', 'elevator pitch']
    for synonym in canon_synonyms:
        for key in sections.keys():
            if synonym in key:
                canon_section_key = key
                break
        if canon_section_key:
            break
    
    canon_summary = []
    canon_source = None
    if canon_section_key:
        canon_summary = extract_canon_from_section(sections[canon_section_key])
        canon_source = canon_section_key.title()
    
    # Sessions (section-first)
    ledger_section_key = None
    ledger_synonyms = ['campaign ledger', 'sessionized history', 'session log', 'session journal', 'session notes']
    for synonym in ledger_synonyms:
        for key in sections.keys():
            if synonym in key:
                ledger_section_key = key
                break
        if ledger_section_key:
            break
    
    sessions = []
    ledger_source = None
    if ledger_section_key:
        sessions = parse_ledger_sessions(sections[ledger_section_key])
        ledger_source = ledger_section_key.title()
    
    # Factions (section-first - AUTHORITATIVE)
    faction_section_key = None
    for key in sections.keys():
        if 'faction' in key or "who's out there" in key:
            faction_section_key = key
            break
    
    faction_dicts = []
    faction_source = None
    if faction_section_key:
        faction_dicts = extract_factions_from_section(sections[faction_section_key])
        faction_source = "Explicit Factions section"
    
    # Extract faction names for backward compatibility
    factions = [f["name"] for f in faction_dicts]
    
    # Entities (section-first mining)
    mined_entities = mine_entities_from_sections(text, sections)
    
    # Artifacts (section-first mining)
    artifacts = extract_artifacts_from_sections(text, sections)
    
    # Open threads (section-first mining)
    open_threads = extract_open_threads_from_sections(sections)
    
    # Future sessions
    future_section_key = None
    for key in sections.keys():
        if 'future session' in key:
            future_section_key = key
            break
    
    future_sessions = []
    if future_section_key:
        future_sessions = parse_future_sessions(sections[future_section_key])
    
    # Prep content (if applicable)
    prep_content = extract_prep_content(sections)
    
    # Step 4: Apply fallbacks if needed
    
    needs_session_fallback = len(sessions) == 0
    needs_canon_fallback = len(canon_summary) < 4
    needs_faction_fallback = len(factions) == 0 and not faction_section_key
    
    fallback_notes = []
    
    # Fallback: Relaxed session headers
    if needs_session_fallback:
        relaxed_sessions = parse_relaxed_sessions(text)
        if relaxed_sessions:
            sessions = relaxed_sessions
            ledger_source = "Relaxed headers"
            fallback_notes.append("🔄 Fallback: relaxed session headers")
    
    # Fallback: Paragraph canon
    if needs_canon_fallback:
        paragraph_canon = extract_paragraph_canon(text, min_bullets=4)
        if paragraph_canon:
            canon_summary = paragraph_canon
            canon_source = "Opening paragraphs"
            fallback_notes.append("🔄 Fallback: paragraph canon")
    
    # Step 5: Entity enrichment (combine mined + classified)
    
    # Try Parser Index first
    index_entities = extract_from_parser_index(text)
    
    if index_entities:
        # Use index as primary source
        entities = {
            "places": index_entities["places"],
            "artifacts": artifacts + index_entities["artifacts"],  # Combine both sources
            "concepts": mined_entities["concepts"] + index_entities["concepts"],
        }
        # Store NPCs in concepts for now (schema limitation)
        if mined_entities["npcs"]:
            entities["concepts"].extend(mined_entities["npcs"])
        notes_prefix = "📋 Using Parser-Friendly Index"
    else:
        # Combine mined + heuristic
        if needs_faction_fallback:
            canon_text = sections.get(canon_section_key, "") if canon_section_key else None
            heuristic = classify_entities(text, canon_section=canon_text)
            if heuristic["factions"]:
                factions.extend(heuristic["factions"])
        
        entities = {
            "places": fuzzy_dedupe_entities(mined_entities["places"]),
            "artifacts": artifacts,
            "concepts": fuzzy_dedupe_entities(mined_entities["concepts"]),
        }
        # Add NPCs to concepts
        if mined_entities["npcs"]:
            entities["concepts"] = fuzzy_dedupe_entities(entities["concepts"] + mined_entities["npcs"])
        
        notes_prefix = "🔍 Using section mining + heuristics"
    
    # Step 6: Build result
    
    result = {
        "sessions": sessions,
        "canon_summary": canon_summary,
        "factions": factions,
        "entities": entities,
        "future_sessions": future_sessions,
        "open_threads": open_threads,
    }
    
    # Add prep content if available
    if prep_content:
        result["session_zero_prep"] = prep_content
    
    # Store faction details if extracted
    if faction_dicts:
        result["faction_details"] = faction_dicts
    
    # Apply import overrides if campaign_id provided
    if campaign_id:
        from streamlit_harness.import_overrides import ImportOverrides
        overrides = ImportOverrides.load(campaign_id)
        result = overrides.apply_to_parsed(result)
    
    # Step 7: Build notes
    
    notes = [notes_prefix]
    notes.extend(fallback_notes)
    
    if canon_source:
        notes.append(f"📖 Canon from: {canon_source}")
    if ledger_source:
        notes.append(f"📅 Sessions from: {ledger_source}")
    if faction_source:
        notes.append(f"👥 Factions from: {faction_source}")
    
    if not sessions:
        notes.append("⚠️ No sessions detected")
    else:
        notes.append(f"✓ Detected {len(sessions)} sessions")
    
    if not canon_summary:
        notes.append("⚠️ No canon summary extracted")
    else:
        notes.append(f"✓ Extracted {len(canon_summary)} canon bullets")
    
    if factions:
        notes.append(f"✓ Classified {len(factions)} factions")
    
    entity_count = len(entities["places"]) + len(entities["artifacts"]) + len(entities["concepts"])
    if entity_count > 0:
        notes.append(f"ℹ️ Detected {entity_count} entities")
    
    if future_sessions:
        notes.append(f"ℹ️ Found {len(future_sessions)} future sessions")
    
    if open_threads:
        notes.append(f"ℹ️ Found {len(open_threads)} open threads")
    
    if prep_content:
        notes.append("ℹ️ Session 0 prep content extracted")
    
    if campaign_id:
        notes.append("ℹ️ Import overrides applied")
    
    result["notes"] = notes
    return result
