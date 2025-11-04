"""
Game ID Generator
Generates deterministic hash-based game IDs from date and opponent information.
"""

import hashlib
import re
from datetime import datetime
from typing import Tuple, Optional


def generate_game_id(date_string: str, opponent: str, team: str = "Heat") -> str:
    """
    Generate a deterministic game ID based on date and opponent.
    
    Args:
        date_string (str): Date string in MM.DD.YY format
        opponent (str): Opponent team name
        team (str): Team name (default: "Heat")
        
    Returns:
        str: 16-character hexadecimal hash ID
    """
    # Normalize inputs
    normalized_date = date_string.strip()
    normalized_opponent = opponent.strip().lower()
    normalized_team = team.strip().lower()
    
    # Create hash input: date_team_opponent
    hash_input = f"{normalized_date}_{normalized_team}_{normalized_opponent}"
    
    # Generate SHA256 hash and take first 16 characters
    hash_obj = hashlib.sha256(hash_input.encode('utf-8'))
    game_id = hash_obj.hexdigest()[:16]
    
    return game_id


def parse_game_metadata(timeline_value: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parse game metadata from Timeline column value.
    
    Args:
        timeline_value (str): Timeline value from CSV (e.g., "10.04.25 Heat v Magic")
        
    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]: (date_string, team, opponent)
        Returns (None, None, None) if parsing fails
    """
    if not timeline_value or not isinstance(timeline_value, str):
        return None, None, None
    
    timeline_value = timeline_value.strip()
    
    # Pattern 1: "MM.DD.YY Team v Opponent" or "MM.DD.YY Team vs Opponent"
    pattern1 = re.match(r'(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+v(?:s)?\s+(.+)', timeline_value)
    if pattern1:
        date_str = pattern1.group(1)
        team = pattern1.group(2).strip()
        opponent = pattern1.group(3).split()[0].strip()  # Take first word after "v"
        return date_str, team, opponent
    
    # Pattern 2: "MM.DD.YY Team @ Opponent" or "MM.DD.YY Team at Opponent"
    pattern2 = re.match(r'(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(?:@|at)\s+(.+)', timeline_value)
    if pattern2:
        date_str = pattern2.group(1)
        team = pattern2.group(2).strip()
        opponent = pattern2.group(3).split()[0].strip()
        return date_str, team, opponent
    
    # Pattern 3: "MM.DD.YY Team Opponent" (no separator)
    pattern3 = re.match(r'(\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(.+)', timeline_value)
    if pattern3:
        date_str = pattern3.group(1)
        parts = pattern3.group(2).split()
        if len(parts) >= 2:
            team = parts[0]
            opponent = parts[-1]
            return date_str, team, opponent
    
    # Fallback: try to extract date only
    date_match = re.match(r'(\d{2}\.\d{2}\.\d{2})', timeline_value)
    if date_match:
        return date_match.group(1), "Heat", "Unknown"
    
    return None, None, None


def date_string_to_timestamp(date_string: str) -> Optional[int]:
    """
    Convert date string (MM.DD.YY) to Unix timestamp.
    
    Args:
        date_string (str): Date in MM.DD.YY format
        
    Returns:
        Optional[int]: Unix timestamp, or None if parsing fails
    """
    try:
        parts = date_string.split('.')
        if len(parts) != 3:
            return None
        
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
        
        # Convert 2-digit year to 4-digit (assuming 2000s)
        if year < 100:
            year += 2000
        
        dt = datetime(year, month, day)
        return int(dt.timestamp())
    except (ValueError, IndexError):
        return None

