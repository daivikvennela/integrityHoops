"""
Game Results Fetcher
Fetches NBA game results to determine win/loss for Miami Heat games
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def fetch_game_result(date_iso: str, team: str = 'Miami Heat', opponent: str = None) -> Optional[str]:
    """
    Fetch game result (win/loss) for a given date and team.
    
    Args:
        date_iso: Date in YYYY-MM-DD format
        team: Team name (default: Miami Heat)
        opponent: Opponent name (optional, for better matching)
    
    Returns:
        'win', 'loss', or None if unable to determine
    """
    try:
        # Parse date
        game_date = datetime.strptime(date_iso, '%Y-%m-%d')
        
        # Use balldontlie API (free, no API key required)
        # Format: https://www.balldontlie.io/api/v1/games?dates[]=2024-10-04&team_ids[]=14
        # Miami Heat team ID: 14
        
        year = game_date.year
        month = game_date.month
        day = game_date.day
        
        # Try balldontlie API
        url = f"https://www.balldontlie.io/api/v1/games"
        params = {
            'dates[]': date_iso,
            'team_ids[]': 14,  # Miami Heat team ID
            'per_page': 100
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data') and len(data['data']) > 0:
                    game = data['data'][0]
                    
                    # Check if Miami Heat won
                    home_team_id = game.get('home_team', {}).get('id')
                    visitor_team_id = game.get('visitor_team', {}).get('id')
                    home_team_score = game.get('home_team_score')
                    visitor_team_score = game.get('visitor_team_score')
                    
                    if home_team_id == 14:  # Miami Heat is home
                        if home_team_score and visitor_team_score:
                            return 'win' if home_team_score > visitor_team_score else 'loss'
                    elif visitor_team_id == 14:  # Miami Heat is visitor
                        if home_team_score and visitor_team_score:
                            return 'win' if visitor_team_score > home_team_score else 'loss'
                    
                    logger.info(f"Found game for {date_iso} but scores not available")
                    return None
                    
        except Exception as e:
            logger.debug(f"balldontlie API error for {date_iso}: {str(e)}")
        
        # Fallback: Try ESPN API (may require different approach)
        # For now, return None if we can't determine
        logger.warning(f"Could not determine game result for {date_iso}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching game result for {date_iso}: {str(e)}")
        return None

def fetch_multiple_game_results(dates: list, team: str = 'Miami Heat') -> Dict[str, str]:
    """
    Fetch game results for multiple dates.
    
    Args:
        dates: List of dates in YYYY-MM-DD format
        team: Team name
    
    Returns:
        Dictionary mapping date_iso -> 'win' or 'loss'
    """
    results = {}
    
    for date_iso in dates:
        result = fetch_game_result(date_iso, team)
        if result:
            results[date_iso] = result
    
    return results

