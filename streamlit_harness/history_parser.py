"""Campaign history parser for imports.

Version History:
- v0.1 (2025-12-25): Initial history parsing implementation

Provides heuristic parsing of campaign history documents into:
- Session entries with dates
- Canon summary bullets
- Faction extraction
- Scar candidates
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def detect_dates(text: str) -> List[Tuple[int, str]]:
    """Detect dates in text and return (position, date_string) tuples.
    
    Supports common formats:
    - YYYY-MM-DD
    - MM/DD/YYYY
    - Month DD, YYYY
    - "Session N" headers
    """
    dates = []
    
    # YYYY-MM-DD pattern
    pattern1 = r'\b(\d{4})-(\d{2})-(\d{2})\b'
    for match in re.finditer(pattern1, text):
        dates.append((match.start(), match.group(0)))
    
    # MM/DD/YYYY pattern
    pattern2 = r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
    for match in re.finditer(pattern2, text):
        dates.append((match.start(), match.group(0)))
    
    # Month DD, YYYY pattern
    months = r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
    pattern3 = rf'{months}\s+(\d{{1,2}}),?\s+(\d{{4}})'
    for match in re.finditer(pattern3, text, re.IGNORECASE):
        dates.append((match.start(), match.group(0)))
    
    # Session headers (Session N, Game N, etc.)
    pattern4 = r'Session\s+(\d+)|Game\s+#?(\d+)'
    for match in re.finditer(pattern4, text, re.IGNORECASE):
        dates.append((match.start(), f"Session {match.group(1) or match.group(2)}"))
    
    return sorted(dates, key=lambda x: x[0])


def split_into_sessions(text: str) -> List[Dict[str, Any]]:
    """Split history text into session chunks.
    
    Returns list of session dicts with:
    - session_number: int
    - date: str (detected or "Unknown")
    - content: str (session text)
    """
    dates = detect_dates(text)
    
    if not dates:
        # No dates found - create single imported session
        return [{
            "session_number": 1,
            "date": "Unknown",
            "content": text.strip(),
        }]
    
    sessions = []
    
    # Split at each date marker
    for idx, (pos, date_str) in enumerate(dates):
        # Get content from this date to next date (or end)
        start = pos
        end = dates[idx + 1][0] if idx + 1 < len(dates) else len(text)
        content = text[start:end].strip()
        
        # Remove date header from content
        content_lines = content.split('\n')
        if content_lines and date_str in content_lines[0]:
            content = '\n'.join(content_lines[1:]).strip()
        
        if content:  # Only add non-empty sessions
            sessions.append({
                "session_number": idx + 1,
                "date": date_str,
                "content": content,
            })
    
    return sessions


def extract_canon_summary(text: str, max_bullets: int = 12) -> List[str]:
    """Extract canon summary bullets from history text.
    
    Heuristics:
    - Look for recurring themes/names
    - Extract key outcomes
    - Prioritize recent content (end of text)
    - Limit to max_bullets
    """
    # Simple heuristic: Split into sentences, extract last N substantive ones
    sentences = re.split(r'[.!?]\s+', text)
    
    # Filter out very short sentences
    substantive = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Take last max_bullets (most recent)
    bullets = substantive[-max_bullets:] if len(substantive) > max_bullets else substantive
    
    # Clean up bullets
    cleaned = []
    for bullet in bullets:
        # Capitalize first letter
        if bullet and not bullet[0].isupper():
            bullet = bullet[0].upper() + bullet[1:]
        # Remove leading bullets/numbers
        bullet = re.sub(r'^[\-\*\d\.]+\s*', '', bullet)
        cleaned.append(bullet)
    
    return cleaned


def extract_factions(text: str) -> List[str]:
    """Extract potential faction names from history text.
    
    Looks for:
    - Capitalized multi-word phrases (proper nouns)
    - Recurring named entities
    - Common faction patterns ("X Guild", "The Y", "Z Watch")
    """
    # Pattern for faction-like names (capitalized, 2-3 words)
    faction_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    matches = re.findall(faction_pattern, text)
    
    # Count frequency
    faction_counts = {}
    for match in matches:
        faction_counts[match] = faction_counts.get(match, 0) + 1
    
    # Return top 6 by frequency (appearing at least 2 times)
    frequent = [(name, count) for name, count in faction_counts.items() if count >= 2]
    frequent.sort(key=lambda x: x[1], reverse=True)
    
    return [name for name, _ in frequent[:6]]


def parse_campaign_history(text: str) -> Dict[str, Any]:
    """Parse full campaign history into structured data.
    
    Returns:
        Dictionary with:
        - sessions: List of session dicts
        - canon_summary: List of bullets
        - factions: List of faction names
        - notes: Parsing notes/warnings
    """
    sessions = split_into_sessions(text)
    canon_summary = extract_canon_summary(text)
    factions = extract_factions(text)
    
    notes = []
    if not sessions:
        notes.append("⚠️ No sessions detected - added as single entry")
    else:
        notes.append(f"✓ Detected {len(sessions)} sessions")
    
    unknown_dates = sum(1 for s in sessions if s["date"] == "Unknown")
    if unknown_dates > 0:
        notes.append(f"⚠️ {unknown_dates} sessions have unknown dates (edit before commit)")
    
    if canon_summary:
        notes.append(f"✓ Extracted {len(canon_summary)} canon bullets")
    else:
        notes.append("⚠️ No canon summary extracted (text may be too short)")
    
    if factions:
        notes.append(f"✓ Detected {len(factions)} potential factions")
    else:
        notes.append("ℹ️ No factions detected")
    
    return {
        "sessions": sessions,
        "canon_summary": canon_summary,
        "factions": factions,
        "notes": notes,
    }
