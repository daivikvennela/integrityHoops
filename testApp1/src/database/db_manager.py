import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.player import Player
from src.models.scorecard import Scorecard


class DatabaseManager:
    """
    Database manager for handling SQL operations for Player and Scorecard entities.
    """
    
    def __init__(self, db_path: str = "basketball.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection and enable foreign key enforcement.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('PRAGMA foreign_keys = ON')
        except Exception:
            pass
        return conn
    
    def init_database(self) -> None:
        """
        Initialize the database with required tables.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    date_created INTEGER NOT NULL
                )
            ''')
            
            # Create scorecards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scorecards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    date_created INTEGER NOT NULL,
                    space_read_live_dribble INTEGER DEFAULT 0,
                    space_read_catch INTEGER DEFAULT 0,
                    space_read_live_dribble_negative INTEGER DEFAULT 0,
                    space_read_catch_negative INTEGER DEFAULT 0,
                    dm_catch_back_to_back_positive INTEGER DEFAULT 0,
                    dm_catch_back_to_back_negative INTEGER DEFAULT 0,
                    dm_catch_uncontested_shot_positive INTEGER DEFAULT 0,
                    dm_catch_uncontested_shot_negative INTEGER DEFAULT 0,
                    dm_catch_swing_positive INTEGER DEFAULT 0,
                    dm_catch_swing_negative INTEGER DEFAULT 0,
                    dm_catch_drive_pass_positive INTEGER DEFAULT 0,
                    dm_catch_drive_pass_negative INTEGER DEFAULT 0,
                    dm_catch_drive_swing_skip_pass_positive INTEGER DEFAULT 0,
                    dm_catch_drive_swing_skip_pass_negative INTEGER DEFAULT 0,
                    qb12_strong_side_positive INTEGER DEFAULT 0,
                    qb12_strong_side_negative INTEGER DEFAULT 0,
                    qb12_baseline_positive INTEGER DEFAULT 0,
                    qb12_baseline_negative INTEGER DEFAULT 0,
                    qb12_fill_behind_positive INTEGER DEFAULT 0,
                    qb12_fill_behind_negative INTEGER DEFAULT 0,
                    qb12_weak_side_positive INTEGER DEFAULT 0,
                    qb12_weak_side_negative INTEGER DEFAULT 0,
                    qb12_roller_positive INTEGER DEFAULT 0,
                    qb12_roller_negative INTEGER DEFAULT 0,
                    qb12_skip_pass_positive INTEGER DEFAULT 0,
                    qb12_skip_pass_negative INTEGER DEFAULT 0,
                    qb12_cutter_positive INTEGER DEFAULT 0,
                    qb12_cutter_negative INTEGER DEFAULT 0,
                    driving_paint_touch_positive INTEGER DEFAULT 0,
                    driving_paint_touch_negative INTEGER DEFAULT 0,
                    driving_physicality_positive INTEGER DEFAULT 0,
                    driving_physicality_negative INTEGER DEFAULT 0,
                    FOREIGN KEY (player_name) REFERENCES players (name)
                )
            ''')
            
            conn.commit()
    
    def create_player(self, player: Player) -> bool:
        """
        Create a new player in the database.
        
        Args:
            player (Player): Player object to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO players (name, date_created) VALUES (?, ?)',
                    (player.name, player.date_created)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Player with this name already exists
            return False
        except Exception as e:
            print(f"Error creating player: {e}")
            return False
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """
        Retrieve a player by name.
        
        Args:
            name (str): Player name to search for
            
        Returns:
            Optional[Player]: Player object if found, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT name, date_created FROM players WHERE name = ?',
                    (name,)
                )
                row = cursor.fetchone()
                
                if row:
                    player = Player(row[0], row[1])
                    # Load associated scorecards
                    self._load_player_scorecards(player)
                    return player
                return None
        except Exception as e:
            print(f"Error retrieving player: {e}")
            return None
    
    def get_all_players(self) -> List[Player]:
        """
        Retrieve all players from the database.
        
        Returns:
            List[Player]: List of all players
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT name, date_created FROM players ORDER BY name')
                rows = cursor.fetchall()
                
                players = []
                for row in rows:
                    player = Player(row[0], row[1])
                    self._load_player_scorecards(player)
                    players.append(player)
                
                return players
        except Exception as e:
            print(f"Error retrieving all players: {e}")
            return []
    
    def update_player(self, player: Player) -> bool:
        """
        Update an existing player in the database.
        
        Args:
            player (Player): Player object with updated data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE players SET date_created = ? WHERE name = ?',
                    (player.date_created, player.name)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating player: {e}")
            return False
    
    def delete_player(self, name: str) -> bool:
        """
        Delete a player from the database.
        
        Args:
            name (str): Name of the player to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Delete associated scorecards first
                cursor.execute('DELETE FROM scorecards WHERE player_name = ?', (name,))
                # Delete the player
                cursor.execute('DELETE FROM players WHERE name = ?', (name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting player: {e}")
            return False
    
    def create_scorecard(self, scorecard: Scorecard) -> bool:
        """
        Create a new scorecard in the database.
        
        Args:
            scorecard (Scorecard): Scorecard object to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"🔧 DB DEBUG: Starting database scorecard creation for {scorecard.player_name}")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Ensure player exists; create if missing to keep pipeline robust
                cursor.execute('SELECT 1 FROM players WHERE name = ?', (scorecard.player_name,))
                if cursor.fetchone() is None:
                    print(f"🔧 DB DEBUG: Player {scorecard.player_name} doesn't exist, creating...")
                    cursor.execute('INSERT INTO players (name, date_created) VALUES (?, ?)', (scorecard.player_name, scorecard.date_created))
                    print(f"🔧 DB DEBUG: Player {scorecard.player_name} created successfully")
                else:
                    print(f"🔧 DB DEBUG: Player {scorecard.player_name} already exists")
                
                print(f"🔧 DB DEBUG: Inserting scorecard record...")
                cursor.execute(
                    'INSERT INTO scorecards (player_name, date_created, space_read_live_dribble, space_read_catch, space_read_live_dribble_negative, space_read_catch_negative, dm_catch_back_to_back_positive, dm_catch_back_to_back_negative, dm_catch_uncontested_shot_positive, dm_catch_uncontested_shot_negative, dm_catch_swing_positive, dm_catch_swing_negative, dm_catch_drive_pass_positive, dm_catch_drive_pass_negative, dm_catch_drive_swing_skip_pass_positive, dm_catch_drive_swing_skip_pass_negative, qb12_strong_side_positive, qb12_strong_side_negative, qb12_baseline_positive, qb12_baseline_negative, qb12_fill_behind_positive, qb12_fill_behind_negative, qb12_weak_side_positive, qb12_weak_side_negative, qb12_roller_positive, qb12_roller_negative, qb12_skip_pass_positive, qb12_skip_pass_negative, qb12_cutter_positive, qb12_cutter_negative, driving_paint_touch_positive, driving_paint_touch_negative, driving_physicality_positive, driving_physicality_negative) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (scorecard.player_name, scorecard.date_created, scorecard.space_read_live_dribble, scorecard.space_read_catch, scorecard.space_read_live_dribble_negative, scorecard.space_read_catch_negative, scorecard.dm_catch_back_to_back_positive, scorecard.dm_catch_back_to_back_negative, scorecard.dm_catch_uncontested_shot_positive, scorecard.dm_catch_uncontested_shot_negative, scorecard.dm_catch_swing_positive, scorecard.dm_catch_swing_negative, scorecard.dm_catch_drive_pass_positive, scorecard.dm_catch_drive_pass_negative, scorecard.dm_catch_drive_swing_skip_pass_positive, scorecard.dm_catch_drive_swing_skip_pass_negative, scorecard.qb12_strong_side_positive, scorecard.qb12_strong_side_negative, scorecard.qb12_baseline_positive, scorecard.qb12_baseline_negative, scorecard.qb12_fill_behind_positive, scorecard.qb12_fill_behind_negative, scorecard.qb12_weak_side_positive, scorecard.qb12_weak_side_negative, scorecard.qb12_roller_positive, scorecard.qb12_roller_negative, scorecard.qb12_skip_pass_positive, scorecard.qb12_skip_pass_negative, scorecard.qb12_cutter_positive, scorecard.qb12_cutter_negative, scorecard.driving_paint_touch_positive, scorecard.driving_paint_touch_negative, scorecard.driving_physicality_positive, scorecard.driving_physicality_negative)
                )
                conn.commit()
                print(f"✅ DB DEBUG: Scorecard successfully inserted for {scorecard.player_name}")
                return True
        except Exception as e:
            print(f"🚨 DB DEBUG: Error creating scorecard for {scorecard.player_name}: {e}")
            print(f"Error creating scorecard: {e}")
            return False
    
    def get_scorecards_by_player(self, player_name: str) -> List[Scorecard]:
        """
        Get all scorecards for a specific player.
        
        Args:
            player_name (str): Name of the player
            
        Returns:
            List[Scorecard]: List of scorecards for the player
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT player_name, date_created, space_read_live_dribble, space_read_catch, space_read_live_dribble_negative, space_read_catch_negative, dm_catch_back_to_back_positive, dm_catch_back_to_back_negative, dm_catch_uncontested_shot_positive, dm_catch_uncontested_shot_negative, dm_catch_swing_positive, dm_catch_swing_negative, dm_catch_drive_pass_positive, dm_catch_drive_pass_negative, dm_catch_drive_swing_skip_pass_positive, dm_catch_drive_swing_skip_pass_negative, qb12_strong_side_positive, qb12_strong_side_negative, qb12_baseline_positive, qb12_baseline_negative, qb12_fill_behind_positive, qb12_fill_behind_negative, qb12_weak_side_positive, qb12_weak_side_negative, qb12_roller_positive, qb12_roller_negative, qb12_skip_pass_positive, qb12_skip_pass_negative, qb12_cutter_positive, qb12_cutter_negative, driving_paint_touch_positive, driving_paint_touch_negative, driving_physicality_positive, driving_physicality_negative FROM scorecards WHERE player_name = ? ORDER BY date_created DESC',
                    (player_name,)
                )
                rows = cursor.fetchall()
                
                scorecards = []
                for row in rows:
                    # Row mapping: 0..33 inclusive (34 values)
                    scorecard = Scorecard(
                        row[0],  # player_name
                        row[1],  # date_created
                        row[2], row[3], row[4], row[5],
                        row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                        row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                        row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33]
                    )
                    scorecards.append(scorecard)
                
                return scorecards
        except Exception as e:
            print(f"Error retrieving scorecards: {e}")
            return []
    
    def delete_scorecard(self, player_name: str, date_created: int) -> bool:
        """
        Delete a specific scorecard.
        
        Args:
            player_name (str): Name of the player
            date_created (int): Creation timestamp of the scorecard
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM scorecards WHERE player_name = ? AND date_created = ?',
                    (player_name, date_created)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting scorecard: {e}")
            return False
    
    def _load_player_scorecards(self, player: Player) -> None:
        """
        Load scorecards for a player from the database.
        
        Args:
            player (Player): Player object to load scorecards for
        """
        scorecards = self.get_scorecards_by_player(player.name)
        player.scorecards = scorecards
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Count players
                cursor.execute('SELECT COUNT(*) FROM players')
                player_count = cursor.fetchone()[0]
                
                # Count scorecards
                cursor.execute('SELECT COUNT(*) FROM scorecards')
                scorecard_count = cursor.fetchone()[0]
                
                return {
                    'player_count': player_count,
                    'scorecard_count': scorecard_count,
                    'database_path': self.db_path
                }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {'error': str(e)} 