"""
Game Validator Service
Validates game uploads and checks for duplicates.
"""

import os
import re
from typing import Dict, Optional, Tuple
from src.database.db_manager import DatabaseManager
from src.utils.game_id_generator import generate_game_id
import logging

logger = logging.getLogger(__name__)


class GameValidator:
    """
    Validates game CSV uploads and checks for duplicate games in the database.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the validator.
        
        Args:
            db_manager: DatabaseManager instance for database queries
        """
        self.db_manager = db_manager
    
    def validate_csv_file(self, file_path: str) -> Dict[str, any]:
        """
        Validate that a CSV file exists and is readable.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dict with 'valid' (bool) and 'error' (str, optional) keys
        """
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'error': f'File does not exist: {file_path}'
            }
        
        if not file_path.lower().endswith('.csv'):
            return {
                'valid': False,
                'error': 'File must be a CSV file (.csv extension)'
            }
        
        # Try to open and read first few lines
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if not first_line:
                    return {
                        'valid': False,
                        'error': 'CSV file is empty'
                    }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Cannot read CSV file: {str(e)}'
            }
        
        return {'valid': True}
    
    def parse_filename(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse game date and opponent from filename.
        
        Expected formats:
        - "MM.DD.YY TEAM v OPPONENT.csv"
        - "MM.DD.YY TEAM v OPPONENT(team).csv"
        - "MM.D.YY TEAM v OPPONENT.csv" (single digit day/month)
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Tuple[Optional[str], Optional[str]]: (date_string, opponent)
        """
        filename = os.path.basename(file_path)
        
        # Pattern: "10.12.25 MIA v ORL.csv" or "11.2.25 MIA v LAL.csv"
        pattern = r'(\d{1,2}\.\d{1,2}\.\d{2})\s+\w+\s+v\s+(\w+)'
        match = re.search(pattern, filename)
        
        if match:
            date_string = match.group(1)
            opponent = match.group(2)
            
            # Normalize date to MM.DD.YY format
            parts = date_string.split('.')
            if len(parts) == 3:
                month = parts[0].zfill(2)
                day = parts[1].zfill(2)
                year = parts[2]
                date_string = f"{month}.{day}.{year}"
            
            return date_string, opponent
        
        # Fallback: try to extract date only
        date_match = re.search(r'(\d{1,2}\.\d{1,2}\.\d{2})', filename)
        if date_match:
            date_string = date_match.group(1)
            # Normalize date
            parts = date_string.split('.')
            if len(parts) == 3:
                month = parts[0].zfill(2)
                day = parts[1].zfill(2)
                year = parts[2]
                date_string = f"{month}.{day}.{year}"
            return date_string, "Unknown"
        
        return None, None
    
    def check_game_exists(self, game_id: str) -> bool:
        """
        Check if a game with the given game_id already exists in the database.
        
        Args:
            game_id: The game ID to check
            
        Returns:
            bool: True if game exists, False otherwise
        """
        try:
            game = self.db_manager.get_game_by_id(game_id)
            return game is not None
        except Exception as e:
            logger.error(f"Error checking game existence: {e}")
            return False
    
    def is_duplicate_game(self, date_string: str, opponent: str = None, team: str = "Heat") -> Tuple[bool, Optional[str]]:
        """
        Check if a game on the same date already exists.
        Note: A team can only play one game per date, regardless of opponent.
        
        Args:
            date_string: Date string in MM.DD.YY format
            opponent: Opponent team name (optional, for error messages)
            team: Team name (default: "Heat")
            
        Returns:
            Tuple[bool, Optional[str]]: (is_duplicate, game_id if duplicate)
        """
        game_id = generate_game_id(date_string, None, team)
        exists = self.check_game_exists(game_id)
        
        return exists, game_id if exists else None
    
    def validate_csv_upload(self, file_path: str, team: str = "Heat") -> Dict[str, any]:
        """
        Comprehensive validation of a CSV upload.
        
        Checks:
        1. File exists and is readable
        2. Filename can be parsed for date and opponent
        3. Game doesn't already exist in database
        
        Args:
            file_path: Path to the CSV file
            team: Team name (default: "Heat")
            
        Returns:
            Dict with:
                - valid (bool): Overall validation result
                - error (str, optional): Error message if invalid
                - game_id (str, optional): Generated game ID if valid
                - date (str, optional): Parsed date string
                - opponent (str, optional): Parsed opponent name
                - duplicate (bool): True if game already exists
        """
        # Check file validity
        file_validation = self.validate_csv_file(file_path)
        if not file_validation['valid']:
            return file_validation
        
        # Parse filename
        date_string, opponent = self.parse_filename(file_path)
        if not date_string or not opponent:
            return {
                'valid': False,
                'error': 'Cannot parse game date and opponent from filename. Expected format: "MM.DD.YY TEAM v OPPONENT.csv"'
            }
        
        # Check for duplicate
        is_duplicate, existing_game_id = self.is_duplicate_game(date_string, opponent, team)
        
        if is_duplicate:
            return {
                'valid': False,
                'error': f'Game already exists for {date_string} vs {opponent}',
                'duplicate': True,
                'game_id': existing_game_id,
                'date': date_string,
                'opponent': opponent
            }
        
        # Generate new game_id
        new_game_id = generate_game_id(date_string, opponent, team)
        
        return {
            'valid': True,
            'duplicate': False,
            'game_id': new_game_id,
            'date': date_string,
            'opponent': opponent,
            'team': team
        }

