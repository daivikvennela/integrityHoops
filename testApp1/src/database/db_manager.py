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
                    FOREIGN KEY (player_name) REFERENCES players (name)
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
            
            # Ensure any missing columns are added (handles upgrades)
            self._ensure_scorecard_columns(conn)
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
                    '''SELECT player_name, date_created,
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
                        row[2], row[3], row[4], row[5],
                        row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                        row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                        row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33],
                        # Off Ball - Positioning
                        row[34], row[35], row[36], row[37],
                        # Off Ball - Transition
                        row[38], row[39],
                        # Cutting & Screening
                        row[40], row[41], row[42], row[43], row[44], row[45], row[46], row[47], row[48], row[49],
                        # Relocation
                        row[50], row[51], row[52], row[53], row[54], row[55], row[56], row[57], row[58], row[59], row[60], row[61], row[62], row[63],
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