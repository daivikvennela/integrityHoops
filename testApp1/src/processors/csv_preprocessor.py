"""
CSV Preprocessor
Splits mega CSV files by Row column into team and player-specific CSVs.
"""

import pandas as pd
import os
import re
from typing import Dict, List, Tuple, Optional
from src.utils.game_id_generator import generate_game_id
import logging

logger = logging.getLogger(__name__)


class CSVPreprocessor:
    """
    Preprocesses mega CSV files by splitting them into team and player CSVs.
    Groups rows by the 'Row' column value (4th column).
    """
    
    def __init__(self, csv_path: str, temp_dir: Optional[str] = None):
        """
        Initialize the preprocessor.
        
        Args:
            csv_path: Path to the mega CSV file
            temp_dir: Temporary directory to save preprocessed CSVs (default: ./temp_csvs)
        """
        self.csv_path = csv_path
        self.temp_dir = temp_dir or os.path.join(os.path.dirname(csv_path), 'temp_csvs')
        self.df = None
        self.game_id = None
        self.game_date = None
        self.opponent = None
        self.team = "Heat"
        
    def parse_filename_metadata(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract game date and opponent from filename.
        
        Expected formats:
        - "MM.DD.YY TEAM v OPPONENT.csv"
        - "MM.DD.YY TEAM v OPPONENT(team).csv"
        - "MM.D.YY TEAM v OPPONENT.csv" (single digit day/month)
        
        Returns:
            Tuple[Optional[str], Optional[str]]: (date_string, opponent)
        """
        filename = os.path.basename(self.csv_path)
        
        # Pattern: "10.12.25 MIA v ORL.csv" or "10.12.25 MIA v ORL(team).csv"
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
        
        logger.warning(f"Could not parse filename: {filename}")
        return None, None
    
    def load_csv(self) -> pd.DataFrame:
        """
        Load the CSV file.
        
        Returns:
            pd.DataFrame: Loaded CSV data
        """
        # Check if first line is "Table 1" and skip it
        skip_rows = 0
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line == 'Table 1':
                    skip_rows = 1
        except:
            pass
        
        try:
            # Try UTF-8 first
            self.df = pd.read_csv(self.csv_path, skiprows=skip_rows, low_memory=False)
        except Exception as e:
            try:
                # Fallback to latin-1
                self.df = pd.read_csv(self.csv_path, skiprows=skip_rows, encoding='latin-1', low_memory=False)
            except Exception as e2:
                raise Exception(f"Failed to read CSV file: {str(e2)}")
        
        # Verify Row column exists
        if 'Row' not in self.df.columns:
            raise ValueError("CSV file missing 'Row' column (4th column)")
        
        logger.info(f"Loaded CSV with {len(self.df)} rows and {len(self.df.columns)} columns")
        return self.df
    
    def split_by_row(self) -> Dict[str, pd.DataFrame]:
        """
        Split the DataFrame by unique values in the 'Row' column.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping Row value to DataFrame
        """
        if self.df is None:
            self.load_csv()
        
        # Get unique Row values
        unique_rows = self.df['Row'].unique()
        logger.info(f"Found {len(unique_rows)} unique Row values: {list(unique_rows)}")
        
        split_dfs = {}
        for row_value in unique_rows:
            if pd.notna(row_value):  # Skip NaN values
                split_dfs[str(row_value)] = self.df[self.df['Row'] == row_value].copy()
        
        return split_dfs
    
    def preprocess(self) -> Dict[str, any]:
        """
        Main preprocessing method: load, split, save, and return metadata.
        
        Returns:
            Dict containing:
                - game_id: Generated game ID
                - date: Game date string
                - opponent: Opponent name
                - team_csv: Path to team CSV (or None if no team data)
                - player_csvs: Dict mapping player names to CSV paths
                - player_names: List of player names
        """
        # Parse filename metadata
        self.game_date, self.opponent = self.parse_filename_metadata()
        if not self.game_date or not self.opponent:
            raise ValueError("Could not extract game metadata from filename")
        
        # Generate game_id
        self.game_id = generate_game_id(self.game_date, self.opponent, self.team)
        logger.info(f"Generated game_id: {self.game_id} for {self.game_date} vs {self.opponent}")
        
        # Load and split CSV
        self.load_csv()
        split_dfs = self.split_by_row()
        
        # Create temp directory
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Save split CSVs
        team_csv_path = None
        player_csvs = {}
        player_names = []
        
        for row_value, df_subset in split_dfs.items():
            if row_value == "Miami Heat" or row_value == "Heat":
                # This is team data
                team_csv_path = os.path.join(self.temp_dir, f"{self.game_id}_team.csv")
                df_subset.to_csv(team_csv_path, index=False)
                logger.info(f"Saved team CSV: {team_csv_path} ({len(df_subset)} rows)")
            else:
                # This is player data
                # Sanitize player name for filename
                safe_player_name = re.sub(r'[^\w\s-]', '', row_value).strip().replace(' ', '_')
                player_csv_path = os.path.join(self.temp_dir, f"{self.game_id}_player_{safe_player_name}.csv")
                df_subset.to_csv(player_csv_path, index=False)
                player_csvs[row_value] = player_csv_path
                player_names.append(row_value)
                logger.info(f"Saved player CSV: {player_csv_path} ({len(df_subset)} rows)")
        
        result = {
            'game_id': self.game_id,
            'date': self.game_date,
            'opponent': self.opponent,
            'team': self.team,
            'team_csv': team_csv_path,
            'player_csvs': player_csvs,
            'player_names': player_names
        }
        
        logger.info(f"Preprocessing complete: {len(player_names)} players, team_csv={'present' if team_csv_path else 'missing'}")
        return result
    
    def cleanup(self):
        """Remove temporary CSV files."""
        if os.path.exists(self.temp_dir):
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")

