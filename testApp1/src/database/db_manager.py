import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.player import Player
from src.models.scorecard import Scorecard
from src.models.game import Game


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
        # Normalize to absolute path to avoid environment-dependent relative lookups
        self.db_path = os.path.abspath(db_path)
        # Ensure parent directory exists for SQLite/file DBs
        try:
            if not str(self.db_path).startswith(('postgres://', 'postgresql://')):
                dirpath = os.path.dirname(self.db_path) or '.'
                os.makedirs(dirpath, exist_ok=True)
        except Exception:
            # Non-fatal; continue and let connect raise if needed
            pass
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
            
            # Create games table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    date INTEGER NOT NULL,
                    date_string TEXT NOT NULL,
                    opponent TEXT NOT NULL,
                    team TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
            ''')
            
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
                    -- Off Ball - Positioning
                    offball_positioning_create_shape_positive INTEGER DEFAULT 0,
                    offball_positioning_create_shape_negative INTEGER DEFAULT 0,
                    offball_positioning_adv_awareness_positive INTEGER DEFAULT 0,
                    offball_positioning_adv_awareness_negative INTEGER DEFAULT 0,
                    -- Off Ball - Transition
                    transition_effort_pace_positive INTEGER DEFAULT 0,
                    transition_effort_pace_negative INTEGER DEFAULT 0,
                    -- Cutting & Screening
                    cs_denial_positive INTEGER DEFAULT 0,
                    cs_denial_negative INTEGER DEFAULT 0,
                    cs_movement_positive INTEGER DEFAULT 0,
                    cs_movement_negative INTEGER DEFAULT 0,
                    cs_body_to_body_positive INTEGER DEFAULT 0,
                    cs_body_to_body_negative INTEGER DEFAULT 0,
                    cs_screen_principle_positive INTEGER DEFAULT 0,
                    cs_screen_principle_negative INTEGER DEFAULT 0,
                    cs_cut_fill_positive INTEGER DEFAULT 0,
                    cs_cut_fill_negative INTEGER DEFAULT 0,
                    -- Relocation
                    relocation_weak_corner_positive INTEGER DEFAULT 0,
                    relocation_weak_corner_negative INTEGER DEFAULT 0,
                    relocation_45_cut_positive INTEGER DEFAULT 0,
                    relocation_45_cut_negative INTEGER DEFAULT 0,
                    relocation_slide_away_positive INTEGER DEFAULT 0,
                    relocation_slide_away_negative INTEGER DEFAULT 0,
                    relocation_fill_behind_positive INTEGER DEFAULT 0,
                    relocation_fill_behind_negative INTEGER DEFAULT 0,
                    relocation_dunker_baseline_positive INTEGER DEFAULT 0,
                    relocation_dunker_baseline_negative INTEGER DEFAULT 0,
                    relocation_corner_fill_positive INTEGER DEFAULT 0,
                    relocation_corner_fill_negative INTEGER DEFAULT 0,
                    relocation_reverse_direction_positive INTEGER DEFAULT 0,
                    relocation_reverse_direction_negative INTEGER DEFAULT 0,
                    game_id TEXT,
                    FOREIGN KEY (player_name) REFERENCES players (name),
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
            ''')

            # Create team cog scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_cog_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_date INTEGER NOT NULL,
                    team TEXT NOT NULL,
                    opponent TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    source TEXT,
                    note TEXT
                )
            ''')

            # Create player cog scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_cog_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_date INTEGER NOT NULL,
                    player_name TEXT NOT NULL,
                    team TEXT,
                    opponent TEXT,
                    score INTEGER NOT NULL,
                    source TEXT,
                    note TEXT
                )
            ''')
            
            # Create team_statistics table for storing calculated category statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS team_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_date_iso TEXT NOT NULL,
                    game_date_timestamp INTEGER NOT NULL,
                    date_string TEXT NOT NULL,
                    team TEXT NOT NULL,
                    opponent TEXT NOT NULL,
                    category TEXT NOT NULL,
                    percentage REAL NOT NULL,
                    positive_count INTEGER DEFAULT 0,
                    negative_count INTEGER DEFAULT 0,
                    total_count INTEGER DEFAULT 0,
                    overall_score REAL NOT NULL,
                    csv_filename TEXT,
                    calculated_at INTEGER NOT NULL,
                    UNIQUE(game_date_iso, team, opponent, category)
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_team_statistics_date 
                ON team_statistics(game_date_iso)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_team_statistics_category 
                ON team_statistics(category)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_team_statistics_date_category 
                ON team_statistics(game_date_iso, category)
            ''')
            
            # Ensure any missing columns are added (handles upgrades)
            self._ensure_scorecard_columns(conn)
            # Ensure game_id column exists in scorecards
            self._ensure_game_id_column(conn)
            # Seed initial cog scores if empty
            self._seed_initial_cog_scores(conn)
            conn.commit()

    def _ensure_scorecard_columns(self, conn: sqlite3.Connection) -> None:
        """Ensure all expected scorecard columns exist on the database table."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(scorecards)")
        existing = {row[1] for row in cursor.fetchall()}

        def add(col: str) -> None:
            if col not in existing:
                cursor.execute(f"ALTER TABLE scorecards ADD COLUMN {col} INTEGER DEFAULT 0")
                existing.add(col)

        columns = [
            # Space Read
            'space_read_live_dribble', 'space_read_catch', 'space_read_live_dribble_negative', 'space_read_catch_negative',
            # DM Catch
            'dm_catch_back_to_back_positive','dm_catch_back_to_back_negative','dm_catch_uncontested_shot_positive','dm_catch_uncontested_shot_negative',
            'dm_catch_swing_positive','dm_catch_swing_negative','dm_catch_drive_pass_positive','dm_catch_drive_pass_negative',
            'dm_catch_drive_swing_skip_pass_positive','dm_catch_drive_swing_skip_pass_negative',
            # QB12
            'qb12_strong_side_positive','qb12_strong_side_negative','qb12_baseline_positive','qb12_baseline_negative',
            'qb12_fill_behind_positive','qb12_fill_behind_negative','qb12_weak_side_positive','qb12_weak_side_negative',
            'qb12_roller_positive','qb12_roller_negative','qb12_skip_pass_positive','qb12_skip_pass_negative',
            'qb12_cutter_positive','qb12_cutter_negative',
            # Driving
            'driving_paint_touch_positive','driving_paint_touch_negative','driving_physicality_positive','driving_physicality_negative',
            # Off Ball - Positioning
            'offball_positioning_create_shape_positive','offball_positioning_create_shape_negative',
            'offball_positioning_adv_awareness_positive','offball_positioning_adv_awareness_negative',
            # Off Ball - Transition
            'transition_effort_pace_positive','transition_effort_pace_negative',
            # Cutting & Screening
            'cs_denial_positive','cs_denial_negative','cs_movement_positive','cs_movement_negative',
            'cs_body_to_body_positive','cs_body_to_body_negative','cs_screen_principle_positive','cs_screen_principle_negative',
            'cs_cut_fill_positive','cs_cut_fill_negative',
            # Relocation
            'relocation_weak_corner_positive','relocation_weak_corner_negative','relocation_45_cut_positive','relocation_45_cut_negative',
            'relocation_slide_away_positive','relocation_slide_away_negative','relocation_fill_behind_positive','relocation_fill_behind_negative',
            'relocation_dunker_baseline_positive','relocation_dunker_baseline_negative','relocation_corner_fill_positive','relocation_corner_fill_negative',
            'relocation_reverse_direction_positive','relocation_reverse_direction_negative',
        ]
        for c in columns:
            add(c)
    
    def _ensure_game_id_column(self, conn: sqlite3.Connection) -> None:
        """Ensure game_id column exists in scorecards table."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(scorecards)")
        existing = {row[1] for row in cursor.fetchall()}
        
        if 'game_id' not in existing:
            cursor.execute("ALTER TABLE scorecards ADD COLUMN game_id TEXT")
            print("Added game_id column to scorecards table")

    def _seed_initial_cog_scores(self, conn: sqlite3.Connection) -> None:
        """Seed initial team cog scores if tables are empty.
        Adds:
          - 10.06.25 Heat v Bucks -> 66
          - 10.04.25 Heat v Magic -> 72
        """
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM team_cog_scores')
            count = cursor.fetchone()[0]
            if count and count > 0:
                return

            def to_ts(year: int, month: int, day: int) -> int:
                return int(datetime(year, month, day).timestamp())

            seed_rows = [
                (to_ts(2025, 10, 6), 'Heat', 'Bucks', 66, 'seed', '10.06.25 Heat v Bucks Cog Score.png'),
                (to_ts(2025, 10, 4), 'Heat', 'Magic', 72, 'seed', '10.04.25 Heat v Magic Cog Score.png'),
            ]
            cursor.executemany(
                'INSERT INTO team_cog_scores (game_date, team, opponent, score, source, note) VALUES (?, ?, ?, ?, ?, ?)',
                seed_rows
            )
        except Exception as e:
            print(f"Error seeding initial cog scores: {e}")

    # ----------------------
    # Cog Scores - Team/Player helpers
    # ----------------------
    def insert_team_cog_score(
        self,
        game_date: int,
        team: str,
        opponent: str,
        score: int,
        source: str | None = None,
        note: str | None = None,
    ) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO team_cog_scores (game_date, team, opponent, score, source, note) VALUES (?, ?, ?, ?, ?, ?)',
                    (game_date, team, opponent, score, source, note)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting team cog score: {e}")
            return False

    def insert_player_cog_score(
        self,
        game_date: int,
        player_name: str,
        team: str | None,
        opponent: str | None,
        score: int,
        source: str | None = None,
        note: str | None = None,
    ) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO player_cog_scores (game_date, player_name, team, opponent, score, source, note) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (game_date, player_name, team, opponent, score, source, note)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting player cog score: {e}")
            return False

    def get_team_cog_scores(self, team: str | None = None) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if team:
                    cursor.execute(
                        'SELECT id, game_date, team, opponent, score, source, note FROM team_cog_scores WHERE team = ? ORDER BY game_date ASC',
                        (team,)
                    )
                else:
                    cursor.execute(
                        'SELECT id, game_date, team, opponent, score, source, note FROM team_cog_scores ORDER BY game_date ASC'
                    )
                rows = cursor.fetchall()
                results: List[Dict[str, Any]] = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'game_date': row[1],
                        'team': row[2],
                        'opponent': row[3],
                        'score': row[4],
                        'source': row[5],
                        'note': row[6],
                    })
                return results
        except Exception as e:
            print(f"Error fetching team cog scores: {e}")
            return []

    def get_player_cog_scores(self, player_name: str | None = None) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if player_name:
                    cursor.execute(
                        'SELECT id, game_date, player_name, team, opponent, score, source, note FROM player_cog_scores WHERE player_name = ? ORDER BY game_date ASC',
                        (player_name,)
                    )
                else:
                    cursor.execute(
                        'SELECT id, game_date, player_name, team, opponent, score, source, note FROM player_cog_scores ORDER BY game_date ASC'
                    )
                rows = cursor.fetchall()
                results: List[Dict[str, Any]] = []
                for row in rows:
                    results.append({
                        'id': row[0],
                        'game_date': row[1],
                        'player_name': row[2],
                        'team': row[3],
                        'opponent': row[4],
                        'score': row[5],
                        'source': row[6],
                        'note': row[7],
                    })
                return results
        except Exception as e:
            print(f"Error fetching player cog scores: {e}")
            return []

    def get_cog_scores_over_time(
        self,
        level: str = 'team',
        team: str | None = None,
        player_name: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Return list of dicts with date label and score for charts."""
        data: List[Dict[str, Any]]
        if level == 'player':
            data = self.get_player_cog_scores(player_name)
        else:
            data = self.get_team_cog_scores(team)

        # Prepare chart points
        points: List[Dict[str, Any]] = []
        for row in data:
            ts = row['game_date']
            try:
                label = datetime.fromtimestamp(ts).strftime('%m.%d.%y')
            except Exception:
                label = str(ts)
            if level == 'player':
                title = f"{label} {row.get('team') or ''} v {row.get('opponent') or ''}".strip()
            else:
                title = f"{label} {row.get('team')} v {row.get('opponent')}"
            points.append({
                'id': row.get('id'),
                'label': title,
                'date': label,
                'timestamp': ts,
                'score': row['score'],
                'source': row.get('source', 'Manual'),
                'note': row.get('note', ''),
            })
        return points

    def delete_team_cog_score_by_id(self, score_id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM team_cog_scores WHERE id = ?', (score_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting team cog score: {e}")
            return False

    def delete_player_cog_score_by_id(self, score_id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM player_cog_scores WHERE id = ?', (score_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting player cog score: {e}")
            return False

    def team_cog_score_exists(self, game_date: int, team: str, opponent: str) -> bool:
        """Check if a team cog score already exists for the given game_date, team, and opponent."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT COUNT(*) FROM team_cog_scores WHERE game_date = ? AND team = ? AND opponent = ?',
                    (game_date, team, opponent)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"Error checking team cog score existence: {e}")
            return False

    def upsert_team_cog_score(
        self,
        game_date: int,
        team: str,
        opponent: str,
        score: int,
        source: str | None = None,
        note: str | None = None,
    ) -> bool | None:
        """
        Insert or update a team cog score.
        Returns True if inserted, False if updated, None on error.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Check if exists
                cursor.execute(
                    'SELECT id FROM team_cog_scores WHERE game_date = ? AND team = ? AND opponent = ?',
                    (game_date, team, opponent)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    cursor.execute(
                        'UPDATE team_cog_scores SET score = ?, source = ?, note = ? WHERE id = ?',
                        (score, source, note, existing[0])
                    )
                    conn.commit()
                    return False  # Updated
                else:
                    # Insert new
                    cursor.execute(
                        'INSERT INTO team_cog_scores (game_date, team, opponent, score, source, note) VALUES (?, ?, ?, ?, ?, ?)',
                        (game_date, team, opponent, score, source, note)
                    )
                    conn.commit()
                    return True  # Inserted
        except Exception as e:
            print(f"Error upserting team cog score: {e}")
            return None
    
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
                # Build dynamic insert from scorecard dict to keep columns and values aligned
                sc_dict = scorecard.to_dict()
                columns = ', '.join(sc_dict.keys())
                placeholders = ', '.join(['?'] * len(sc_dict))
                values = tuple(sc_dict.values())
                sql = f"INSERT INTO scorecards ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, values)
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
                    '''SELECT player_name, date_created, game_id,
                        space_read_live_dribble, space_read_catch, space_read_live_dribble_negative, space_read_catch_negative,
                        dm_catch_back_to_back_positive, dm_catch_back_to_back_negative, dm_catch_uncontested_shot_positive, dm_catch_uncontested_shot_negative,
                        dm_catch_swing_positive, dm_catch_swing_negative, dm_catch_drive_pass_positive, dm_catch_drive_pass_negative,
                        dm_catch_drive_swing_skip_pass_positive, dm_catch_drive_swing_skip_pass_negative,
                        qb12_strong_side_positive, qb12_strong_side_negative, qb12_baseline_positive, qb12_baseline_negative,
                        qb12_fill_behind_positive, qb12_fill_behind_negative, qb12_weak_side_positive, qb12_weak_side_negative,
                        qb12_roller_positive, qb12_roller_negative, qb12_skip_pass_positive, qb12_skip_pass_negative,
                        qb12_cutter_positive, qb12_cutter_negative,
                        driving_paint_touch_positive, driving_paint_touch_negative, driving_physicality_positive, driving_physicality_negative,
                        offball_positioning_create_shape_positive, offball_positioning_create_shape_negative,
                        offball_positioning_adv_awareness_positive, offball_positioning_adv_awareness_negative,
                        transition_effort_pace_positive, transition_effort_pace_negative,
                        cs_denial_positive, cs_denial_negative, cs_movement_positive, cs_movement_negative,
                        cs_body_to_body_positive, cs_body_to_body_negative, cs_screen_principle_positive, cs_screen_principle_negative,
                        cs_cut_fill_positive, cs_cut_fill_negative,
                        relocation_weak_corner_positive, relocation_weak_corner_negative,
                        relocation_45_cut_positive, relocation_45_cut_negative,
                        relocation_slide_away_positive, relocation_slide_away_negative,
                        relocation_fill_behind_positive, relocation_fill_behind_negative,
                        relocation_dunker_baseline_positive, relocation_dunker_baseline_negative,
                        relocation_corner_fill_positive, relocation_corner_fill_negative,
                        relocation_reverse_direction_positive, relocation_reverse_direction_negative
                     FROM scorecards WHERE player_name = ? ORDER BY date_created DESC''',
                    (player_name,)
                )
                rows = cursor.fetchall()
                
                scorecards = []
                for row in rows:
                    # Map row to Scorecard constructor in order
                    scorecard = Scorecard(
                        row[0],  # player_name
                        row[1],  # date_created
                        row[2],  # game_id
                        row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
                        row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26],
                        row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
                        # Off Ball - Positioning
                        row[35], row[36], row[37], row[38],
                        # Off Ball - Transition
                        row[39], row[40],
                        # Cutting & Screening
                        row[41], row[42], row[43], row[44], row[45], row[46], row[47], row[48], row[49], row[50],
                        # Relocation
                        row[51], row[52], row[53], row[54], row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63], row[64],
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
    
    def create_game(self, game: Game) -> bool:
        """
        Create a new game in the database.
        
        Args:
            game (Game): Game object to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO games (id, date, date_string, opponent, team, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (game.id, game.date, game.date_string, game.opponent, game.team, game.created_at)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Game already exists (id is primary key)
            return True
        except Exception as e:
            print(f"Error creating game: {e}")
            return False
    
    def get_game_by_id(self, game_id: str) -> Optional[Game]:
        """
        Get a game by its ID.
        
        Args:
            game_id (str): Game ID
            
        Returns:
            Optional[Game]: Game object if found, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, date, date_string, opponent, team, created_at FROM games WHERE id = ?',
                    (game_id,)
                )
                row = cursor.fetchone()
                if row:
                    return Game(
                        game_id=row[0],
                        date=row[1],
                        date_string=row[2],
                        opponent=row[3],
                        team=row[4],
                        created_at=row[5]
                    )
                return None
        except Exception as e:
            print(f"Error getting game: {e}")
            return None
    
    def get_or_create_game(self, date_string: str, opponent: str, team: str = "Heat") -> Optional[Game]:
        """
        Get existing game or create a new one.
        
        Args:
            date_string (str): Date string in MM.DD.YY format
            opponent (str): Opponent team name
            team (str): Team name (default: "Heat")
            
        Returns:
            Optional[Game]: Game object, or None if creation fails
        """
        from src.utils.game_id_generator import generate_game_id, date_string_to_timestamp
        
        game_id = generate_game_id(date_string, opponent, team)
        existing_game = self.get_game_by_id(game_id)
        
        if existing_game:
            return existing_game
        
        # Create new game
        date_timestamp = date_string_to_timestamp(date_string)
        if date_timestamp is None:
            print(f"Error: Could not parse date string: {date_string}")
            return None
        
        new_game = Game(
            game_id=game_id,
            date=date_timestamp,
            date_string=date_string,
            opponent=opponent,
            team=team
        )
        
        if self.create_game(new_game):
            return new_game
        return None
    
    def get_scorecards_by_game(self, game_id: str) -> List[Scorecard]:
        """
        Get all scorecards for a specific game.
        
        Args:
            game_id (str): Game ID
            
        Returns:
            List[Scorecard]: List of scorecards for the game
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT player_name, date_created, game_id,
                        space_read_live_dribble, space_read_catch, space_read_live_dribble_negative, space_read_catch_negative,
                        dm_catch_back_to_back_positive, dm_catch_back_to_back_negative, dm_catch_uncontested_shot_positive, dm_catch_uncontested_shot_negative,
                        dm_catch_swing_positive, dm_catch_swing_negative, dm_catch_drive_pass_positive, dm_catch_drive_pass_negative,
                        dm_catch_drive_swing_skip_pass_positive, dm_catch_drive_swing_skip_pass_negative,
                        qb12_strong_side_positive, qb12_strong_side_negative, qb12_baseline_positive, qb12_baseline_negative,
                        qb12_fill_behind_positive, qb12_fill_behind_negative, qb12_weak_side_positive, qb12_weak_side_negative,
                        qb12_roller_positive, qb12_roller_negative, qb12_skip_pass_positive, qb12_skip_pass_negative,
                        qb12_cutter_positive, qb12_cutter_negative,
                        driving_paint_touch_positive, driving_paint_touch_negative, driving_physicality_positive, driving_physicality_negative,
                        offball_positioning_create_shape_positive, offball_positioning_create_shape_negative,
                        offball_positioning_adv_awareness_positive, offball_positioning_adv_awareness_negative,
                        transition_effort_pace_positive, transition_effort_pace_negative,
                        cs_denial_positive, cs_denial_negative, cs_movement_positive, cs_movement_negative,
                        cs_body_to_body_positive, cs_body_to_body_negative, cs_screen_principle_positive, cs_screen_principle_negative,
                        cs_cut_fill_positive, cs_cut_fill_negative,
                        relocation_weak_corner_positive, relocation_weak_corner_negative,
                        relocation_45_cut_positive, relocation_45_cut_negative,
                        relocation_slide_away_positive, relocation_slide_away_negative,
                        relocation_fill_behind_positive, relocation_fill_behind_negative,
                        relocation_dunker_baseline_positive, relocation_dunker_baseline_negative,
                        relocation_corner_fill_positive, relocation_corner_fill_negative,
                        relocation_reverse_direction_positive, relocation_reverse_direction_negative
                     FROM scorecards WHERE game_id = ? ORDER BY date_created DESC''',
                    (game_id,)
                )
                rows = cursor.fetchall()
                
                scorecards = []
                for row in rows:
                    scorecard = Scorecard(
                        row[0],  # player_name
                        row[1],  # date_created
                        row[2],  # game_id
                        row[3], row[4], row[5], row[6],
                        row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16],
                        row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26],
                        row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34],
                        # Off Ball - Positioning
                        row[35], row[36], row[37], row[38],
                        # Off Ball - Transition
                        row[39], row[40],
                        # Cutting & Screening
                        row[41], row[42], row[43], row[44], row[45], row[46], row[47], row[48], row[49], row[50],
                        # Relocation
                        row[51], row[52], row[53], row[54], row[55], row[56], row[57], row[58], row[59], row[60],
                        row[61], row[62], row[63], row[64]
                    )
                    scorecards.append(scorecard)
                
                return scorecards
        except Exception as e:
            print(f"Error getting scorecards by game: {e}")
            return []
    
    def get_all_games(self) -> List[Game]:
        """
        Get all games from the database.
        
        Returns:
            List[Game]: List of all games
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, date, date_string, opponent, team, created_at FROM games ORDER BY date DESC'
                )
                rows = cursor.fetchall()
                
                games = []
                for row in rows:
                    games.append(Game(
                        game_id=row[0],
                        date=row[1],
                        date_string=row[2],
                        opponent=row[3],
                        team=row[4],
                        created_at=row[5]
                    ))
                
                return games
        except Exception as e:
            print(f"Error getting all games: {e}")
            return []
    
    def get_games_with_statistics(self) -> List[Dict[str, Any]]:
        """
        Get all games with their statistics (overall cog scores and category breakdowns).
        
        Returns:
            List[Dict]: List of games with statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all games
                cursor.execute(
                    '''SELECT g.id, g.date, g.date_string, g.opponent, g.team, g.created_at,
                              tcs.score as overall_score, tcs.source, tcs.note
                       FROM games g
                       LEFT JOIN team_cog_scores tcs ON g.date = tcs.game_date AND g.team = tcs.team
                       ORDER BY g.date DESC'''
                )
                rows = cursor.fetchall()
                
                games_with_stats = []
                for row in rows:
                    game_data = {
                        'id': row[0],
                        'date': row[1],
                        'date_string': row[2],
                        'opponent': row[3],
                        'team': row[4],
                        'created_at': row[5],
                        'overall_score': row[6] if row[6] is not None else None,
                        'source': row[7],
                        'note': row[8],
                        'categories': {}  # Will be populated from CSV processing if needed
                    }
                    games_with_stats.append(game_data)
                
                return games_with_stats
        except Exception as e:
            print(f"Error getting games with statistics: {e}")
            return []
    
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
                
                # Count team statistics
                cursor.execute('SELECT COUNT(*) FROM team_statistics')
                team_stats_count = cursor.fetchone()[0]
                
                return {
                    'player_count': player_count,
                    'scorecard_count': scorecard_count,
                    'team_statistics_count': team_stats_count,
                    'database_path': self.db_path
                }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {'error': str(e)}
    
    # ----------------------
    # Team Statistics Methods
    # ----------------------
    
    def insert_team_statistics(
        self,
        game_date_iso: str,
        game_date_timestamp: int,
        date_string: str,
        team: str,
        opponent: str,
        category: str,
        percentage: float,
        positive_count: int,
        negative_count: int,
        total_count: int,
        overall_score: float,
        csv_filename: str
    ) -> bool:
        """
        Insert or update team statistics for a specific game and category.
        Uses INSERT OR REPLACE to handle duplicates.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                calculated_at = int(datetime.now().timestamp())
                
                cursor.execute('''
                    INSERT OR REPLACE INTO team_statistics 
                    (game_date_iso, game_date_timestamp, date_string, team, opponent, 
                     category, percentage, positive_count, negative_count, total_count, 
                     overall_score, csv_filename, calculated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game_date_iso, game_date_timestamp, date_string, team, opponent,
                    category, percentage, positive_count, negative_count, total_count,
                    overall_score, csv_filename, calculated_at
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting team statistics: {e}")
            return False
    
    def get_team_statistics(
        self,
        category: Optional[str] = None,
        game_date_iso: Optional[str] = None,
        team: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get team statistics from database.
        
        Args:
            category: Optional category filter
            game_date_iso: Optional date filter (YYYY-MM-DD)
            team: Optional team filter
            
        Returns:
            List of dictionaries with statistics data
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT game_date_iso, date_string, team, opponent, category, 
                           percentage, positive_count, negative_count, total_count,
                           overall_score, csv_filename, calculated_at
                    FROM team_statistics
                    WHERE 1=1
                '''
                params = []
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                
                if game_date_iso:
                    query += ' AND game_date_iso = ?'
                    params.append(game_date_iso)
                
                if team:
                    query += ' AND team = ?'
                    params.append(team)
                
                query += ' ORDER BY game_date_iso ASC, category ASC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'date': row[0],
                        'date_string': row[1],
                        'team': row[2],
                        'opponent': row[3],
                        'category': row[4],
                        'percentage': row[5],
                        'positive_count': row[6],
                        'negative_count': row[7],
                        'total_count': row[8],
                        'overall_score': row[9],
                        'filename': row[10],
                        'calculated_at': row[11]
                    })
                
                return results
        except Exception as e:
            print(f"Error getting team statistics: {e}")
            return []
    
    def get_team_statistics_overall_scores(self, team: Optional[str] = None) -> Dict[str, float]:
        """
        Get overall scores grouped by game date.
        
        Args:
            team: Optional team filter
            
        Returns:
            Dictionary mapping date_iso -> overall_score
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if team:
                    cursor.execute('''
                        SELECT DISTINCT game_date_iso, overall_score
                        FROM team_statistics
                        WHERE team = ?
                        ORDER BY game_date_iso ASC
                    ''', (team,))
                else:
                    cursor.execute('''
                        SELECT DISTINCT game_date_iso, overall_score
                        FROM team_statistics
                        ORDER BY game_date_iso ASC
                    ''')
                
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}
        except Exception as e:
            print(f"Error getting overall scores: {e}")
            return {}
    
    def get_team_statistics_game_info(self, team: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get game info (date_string, opponent, filename) grouped by game date.
        
        Args:
            team: Optional team filter
            
        Returns:
            Dictionary mapping date_iso -> game_info dict
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if team:
                    cursor.execute('''
                        SELECT DISTINCT game_date_iso, date_string, opponent, csv_filename
                        FROM team_statistics
                        WHERE team = ?
                        ORDER BY game_date_iso ASC
                    ''', (team,))
                else:
                    cursor.execute('''
                        SELECT DISTINCT game_date_iso, date_string, opponent, csv_filename
                        FROM team_statistics
                        ORDER BY game_date_iso ASC
                    ''')
                
                rows = cursor.fetchall()
                return {
                    row[0]: {
                        'date_string': row[1],
                        'opponent': row[2],
                        'filename': row[3]
                    }
                    for row in rows
                }
        except Exception as e:
            print(f"Error getting game info: {e}")
            return {}
    
    def team_statistics_exists(self, game_date_iso: str, team: str, opponent: str) -> bool:
        """
        Check if team statistics already exist for a game.
        
        Args:
            game_date_iso: Date in YYYY-MM-DD format
            team: Team name
            opponent: Opponent name
            
        Returns:
            bool: True if statistics exist, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM team_statistics
                    WHERE game_date_iso = ? AND team = ? AND opponent = ?
                ''', (game_date_iso, team, opponent))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"Error checking team statistics existence: {e}")
            return False
    
    def delete_team_statistics(self, game_date_iso: str, team: str, opponent: str) -> bool:
        """
        Delete all team statistics for a specific game.
        
        Args:
            game_date_iso: Date in YYYY-MM-DD format
            team: Team name
            opponent: Opponent name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM team_statistics
                    WHERE game_date_iso = ? AND team = ? AND opponent = ?
                ''', (game_date_iso, team, opponent))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting team statistics: {e}")
            return False 