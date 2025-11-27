"""
CSV to Database Importer
Processes CSV files and imports game, player, and scorecard data into the database.
Uses CSVPreprocessor to split mega CSVs and CogScoreCalculator/StatisticsCalculator to process data.
"""

import pandas as pd
import os
import logging
from typing import Dict, Any, Optional, List
from src.database.db_manager import DatabaseManager
from src.models.game import Game
from src.models.player import Player
from src.models.scorecard import Scorecard
from src.utils.game_id_generator import generate_game_id, parse_game_metadata, date_string_to_timestamp
from src.processors.cog_score_calculator import CogScoreCalculator
from src.processors.csv_preprocessor import CSVPreprocessor
from src.utils.statistics_calculator import StatisticsCalculator
from src.services.game_validator import GameValidator
from datetime import datetime

logger = logging.getLogger(__name__)


class CSVToDatabaseImporter:
    """
    Imports CSV files into the database, creating Game, Player, and Scorecard records.
    Supports mega CSV files that contain both team and player data grouped by the Row column.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the importer.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.validator = GameValidator(db_manager)
        self.stats_calculator = StatisticsCalculator()
    
    def import_mega_csv(self, csv_path: str) -> Dict[str, Any]:
        """
        Import a mega CSV file by splitting it into team and player CSVs,
        processing each with calculators, and storing in database.
        
        Args:
            csv_path: Path to the mega CSV file
            
        Returns:
            Dict with success status, game_id, and detailed import statistics
        """
        try:
            # Validate the upload
            validation_result = self.validator.validate_csv_upload(csv_path)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result.get('error', 'Validation failed'),
                    'duplicate': validation_result.get('duplicate', False)
                }
            
            # Preprocess the CSV
            preprocessor = CSVPreprocessor(csv_path)
            preprocess_result = preprocessor.preprocess()
            
            game_id = preprocess_result['game_id']
            date_string = preprocess_result['date']
            opponent = preprocess_result['opponent']
            team = preprocess_result['team']
            team_csv_path = preprocess_result['team_csv']
            player_csvs = preprocess_result['player_csvs']
            player_names = preprocess_result['player_names']
            
            logger.info(f"Preprocessed {csv_path}: game_id={game_id}, team_csv={'present' if team_csv_path else 'none'}, players={len(player_names)}")
            
            # Create Game record
            date_timestamp = date_string_to_timestamp(date_string)
            if not date_timestamp:
                raise ValueError(f"Could not parse date: {date_string}")
            
            game = Game(
                game_id=game_id,
                date=date_timestamp,
                date_string=date_string,
                opponent=opponent,
                team=team
            )
            
            self.db_manager.create_game(game)
            logger.info(f"Created game record: {game_id}")
            
            # Process team CSV if present
            team_stats = None
            if team_csv_path and os.path.exists(team_csv_path):
                team_stats = self._process_team_csv(team_csv_path, game_id, team, preprocess_result['date'], preprocess_result['opponent'])
                logger.info(f"Processed team CSV with cog score: {team_stats.get('cog_score', 'N/A')}")
            
            # Process player CSVs
            players_processed = []
            scorecards_created = 0
            
            for player_name, player_csv_path in player_csvs.items():
                if not os.path.exists(player_csv_path):
                    logger.warning(f"Player CSV not found: {player_csv_path}")
                    continue
                
                player_stats = self._process_player_csv(player_csv_path, game_id, player_name)
                
                if player_stats['success']:
                    players_processed.append(player_name)
                    scorecards_created += 1
                    logger.info(f"Processed player {player_name} with cog score: {player_stats.get('cog_score', 'N/A')}")
                else:
                    logger.error(f"Failed to process player {player_name}: {player_stats.get('error', 'Unknown error')}")
            
            # Cleanup temporary files
            preprocessor.cleanup()
            
            return {
                'success': True,
                'game_id': game_id,
                'date': date_string,
                'opponent': opponent,
                'team': team,
                'team_cog_score': team_stats.get('cog_score', 0.0) if team_stats else 0.0,
                'team_stats': team_stats,
                'players_processed': len(players_processed),
                'player_names': players_processed,
                'scorecards_created': scorecards_created,
                'message': f'Successfully imported game {date_string} vs {opponent} with {len(players_processed)} players'
            }
            
        except Exception as e:
            logger.exception(f"Error importing mega CSV {csv_path}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_team_csv(self, csv_path: str, game_id: str, team_name: str, date_str: str = None, opponent: str = None) -> Dict[str, Any]:
        """
        Process team CSV with CogScoreCalculator and StatisticsCalculator.
        
        Args:
            csv_path: Path to team CSV
            game_id: Game ID
            team_name: Team name
            date_str: Optional date string
            opponent: Optional opponent name
            
        Returns:
            Dict with team stats and cog score
        """
        try:
            # Calculate cog score
            cog_calculator = CogScoreCalculator(csv_path)
            cog_report = cog_calculator.get_full_report()
            
            cog_score = cog_report.get('overall_score', 0.0)
            category_scores = cog_report.get('breakdown', {})
            
            # Create team scorecard
            scorecard = self._create_scorecard_from_csv(csv_path, game_id, team_name)
            
            if scorecard:
                self.db_manager.create_scorecard(scorecard)
                
                # Store team cog score (using insert method from db_manager)
                if date_str and opponent:
                    try:
                        self.db_manager.insert_team_cog_score(
                            game_date=date_string_to_timestamp(date_str),
                            team=team_name,
                            opponent=opponent,
                            score=cog_score,
                            note=f"Auto-imported from {os.path.basename(csv_path)}"
                        )
                    except Exception as e:
                        logger.warning(f"Could not insert team cog score: {e}")
                
                # Calculate and store team statistics
                stats_dict = self._calculate_statistics_from_scorecard([scorecard])
                if date_str and opponent:
                    try:
                        # Convert to proper format for insert_team_statistics
                        game_date_timestamp = date_string_to_timestamp(date_str)
                        game_date_iso = datetime.fromtimestamp(game_date_timestamp).strftime('%Y-%m-%d')
                        
                        for category, percentage in stats_dict.items():
                            # Get counts from scorecard by summing all relevant fields
                            positive_count = 0
                            negative_count = 0
                            
                            if category in self.stats_calculator.CATEGORIES:
                                # Sum all positive fields for this category
                                for field in self.stats_calculator.CATEGORIES[category]['positive']:
                                    positive_count += getattr(scorecard, field, 0) or 0
                                
                                # Sum all negative fields for this category
                                for field in self.stats_calculator.CATEGORIES[category]['negative']:
                                    negative_count += getattr(scorecard, field, 0) or 0
                            
                            total_count = positive_count + negative_count
                            
                            self.db_manager.insert_team_statistics(
                                game_date_iso=game_date_iso,
                                game_date_timestamp=game_date_timestamp,
                                date_string=date_str,
                                team=team_name,
                                opponent=opponent,
                                category=category,
                                percentage=percentage,
                                positive_count=positive_count,
                                negative_count=negative_count,
                                total_count=total_count,
                                overall_score=cog_score,
                                csv_filename=os.path.basename(csv_path)
                            )
                    except Exception as e:
                        logger.warning(f"Could not insert team statistics: {e}")
            
            return {
                'cog_score': cog_score,
                'category_scores': category_scores,
                'statistics': stats_dict if scorecard else {}
            }
            
        except Exception as e:
            logger.exception(f"Error processing team CSV {csv_path}")
            return {
                'cog_score': 0.0,
                'error': str(e)
            }
    
    def _process_player_csv(self, csv_path: str, game_id: str, player_name: str) -> Dict[str, Any]:
        """
        Process player CSV with CogScoreCalculator and create scorecard.
        
        Args:
            csv_path: Path to player CSV
            game_id: Game ID
            player_name: Player name
            
        Returns:
            Dict with success status and player stats
        """
        try:
            # Create or get player
            player = self.db_manager.get_player_by_name(player_name)
            if not player:
                player = Player(name=player_name)
                self.db_manager.create_player(player)
                logger.info(f"Created player: {player_name}")
            
            # Calculate cog score
            cog_calculator = CogScoreCalculator(csv_path)
            cog_report = cog_calculator.get_full_report()
            
            cog_score = cog_report.get('overall_score', 0.0)
            category_scores = cog_report.get('breakdown', {})
            
            # Create scorecard
            scorecard = self._create_scorecard_from_csv(csv_path, game_id, player_name)
            
            if scorecard:
                self.db_manager.create_scorecard(scorecard)
                
                # Store player cog score (using insert method from db_manager)
                try:
                    # Get game date from preprocessor result
                    from src.processors.csv_preprocessor import CSVPreprocessor
                    temp_preprocessor = CSVPreprocessor(csv_path)
                    date_string, opponent = temp_preprocessor.parse_filename_metadata()
                    
                    if date_string:
                        self.db_manager.insert_player_cog_score(
                            game_date=date_string_to_timestamp(date_string),
                            player_name=player_name,
                            team="Heat",
                            opponent=opponent or "Unknown",
                            score=cog_score,
                            note=f"Auto-imported from CSV"
                        )
                except Exception as e:
                    logger.warning(f"Could not insert player cog score: {e}")
            
            return {
                'success': True,
                'player_name': player_name,
                'cog_score': cog_score,
                'category_scores': category_scores
            }
            
        except Exception as e:
            logger.exception(f"Error processing player CSV for {player_name}")
            return {
                'success': False,
                'player_name': player_name,
                'error': str(e)
            }
    
    def _calculate_statistics_from_scorecard(self, scorecards: List[Scorecard]) -> Dict[str, float]:
        """
        Calculate statistics percentages from scorecards.
        
        Args:
            scorecards: List of Scorecard objects
            
        Returns:
            Dict mapping category names to percentages
        """
        stats = {}
        
        for category in self.stats_calculator.CATEGORIES.keys():
            percentage = self.stats_calculator.calculate_category_percentage(scorecards, category)
            if percentage is not None:
                stats[category] = percentage
        
        return stats
    
    def _create_scorecard_from_csv(self, csv_path: str, game_id: str, 
                                   player_name: str) -> Optional[Scorecard]:
        """
        Create a scorecard from a CSV file.
        
        Args:
            csv_path: Path to CSV file
            game_id: Game ID
            player_name: Player or team name
            
        Returns:
            Scorecard instance or None
        """
        try:
            # Check if first line is "Table 1" and skip it
            skip_rows = 0
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line == 'Table 1':
                        skip_rows = 1
            except:
                pass
            
            df = pd.read_csv(csv_path, skiprows=skip_rows)
            return self._create_scorecard_from_row(df, game_id, player_name)
        except Exception as e:
            logger.exception(f"Error creating scorecard from CSV {csv_path}")
            return None
    
    def import_csv(self, csv_path: str, skip_if_exists: bool = True) -> Dict[str, Any]:
        """
        Import a CSV file into the database.
        
        Args:
            csv_path: Path to the CSV file
            skip_if_exists: If True, skip importing if game already exists
            
        Returns:
            Dict with success status, game_id, and import statistics
        """
        try:
            if not os.path.exists(csv_path):
                return {
                    'success': False,
                    'error': f'File not found: {csv_path}'
                }
            
            # Parse game metadata from CSV
            game_metadata = self._parse_game_metadata(csv_path)
            
            if not game_metadata:
                return {
                    'success': False,
                    'error': 'Could not parse game metadata from CSV'
                }
            
            date_string = game_metadata['date_string']
            opponent = game_metadata['opponent']
            team = game_metadata['team']
            
            # Generate game_id
            game_id = generate_game_id(date_string, opponent, team)
            
            # Check if game already exists
            existing_game = self.db_manager.get_game_by_id(game_id)
            
            if existing_game and skip_if_exists:
                return {
                    'success': True,
                    'skipped': True,
                    'game_id': game_id,
                    'message': 'Game already exists in database'
                }
            
            # Create or update game
            date_timestamp = date_string_to_timestamp(date_string)
            if not date_timestamp:
                return {
                    'success': False,
                    'error': f'Could not parse date: {date_string}'
                }
            
            game = Game(
                game_id=game_id,
                date=date_timestamp,
                date_string=date_string,
                opponent=opponent,
                team=team
            )
            
            if not existing_game:
                self.db_manager.create_game(game)
            
            # Process CSV and create player/scorecard records
            import_stats = self._process_csv_data(csv_path, game_id)
            
            return {
                'success': True,
                'game_id': game_id,
                'players_created': import_stats['players_created'],
                'scorecards_created': import_stats['scorecards_created'],
                'date_string': date_string,
                'opponent': opponent,
                'team': team
            }
            
        except Exception as e:
            logger.exception(f"Error importing CSV {csv_path}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_game_metadata(self, csv_path: str) -> Optional[Dict[str, str]]:
        """
        Parse game metadata from CSV file.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Dict with date_string, opponent, team, or None if parsing fails
        """
        try:
            # Read just the first row to get Timeline
            df = pd.read_csv(csv_path, nrows=1)
            
            if 'Timeline' in df.columns and len(df) > 0:
                timeline = str(df['Timeline'].iloc[0])
                date_str, team, opponent = parse_game_metadata(timeline)
                
                if date_str and team and opponent:
                    return {
                        'date_string': date_str,
                        'team': team,
                        'opponent': opponent
                    }
            
            # Fallback: try to parse from filename
            filename = os.path.basename(csv_path)
            date_str, team, opponent = self._parse_from_filename(filename)
            
            if date_str:
                return {
                    'date_string': date_str,
                    'team': team or 'Heat',
                    'opponent': opponent or 'Unknown'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing game metadata: {e}")
            return None
    
    def _parse_from_filename(self, filename: str) -> tuple:
        """
        Parse game info from filename.
        
        Args:
            filename: CSV filename
            
        Returns:
            Tuple of (date_string, team, opponent)
        """
        import re
        
        # Pattern: MM.DD.YY Team v Opponent
        pattern = r'(\d{2}\.\d{2}\.\d{2})\s+(\w+)\s+v\s+(\w+)'
        match = re.search(pattern, filename)
        
        if match:
            return match.group(1), match.group(2), match.group(3)
        
        # Try to extract just the date
        date_pattern = r'(\d{2}\.\d{2}\.\d{2})'
        date_match = re.search(date_pattern, filename)
        
        if date_match:
            return date_match.group(1), None, None
        
        return None, None, None
    
    def _process_csv_data(self, csv_path: str, game_id: str) -> Dict[str, int]:
        """
        Process CSV data and create player/scorecard records.
        
        Args:
            csv_path: Path to CSV file
            game_id: The game ID
            
        Returns:
            Dict with counts of created records
        """
        try:
            # Load CSV
            df = pd.read_csv(csv_path)
            
            players_created = 0
            scorecards_created = 0
            
            # Check if Row column exists
            if 'Row' not in df.columns:
                logger.warning(f"No 'Row' column found in {csv_path}, treating as team data")
                # Create a team-level scorecard
                scorecard = self._create_scorecard_from_row(df, game_id, team_name="Team")
                if scorecard:
                    self.db_manager.create_scorecard(scorecard)
                    scorecards_created += 1
                
                return {
                    'players_created': 0,
                    'scorecards_created': scorecards_created
                }
            
            # Group by Row (player name or team name)
            unique_rows = df['Row'].unique()
            
            for row_name in unique_rows:
                if pd.isna(row_name) or not row_name:
                    continue
                
                row_name_str = str(row_name).strip()
                
                # Filter data for this row
                row_df = df[df['Row'] == row_name]
                
                # Create or get player
                player = self.db_manager.get_player_by_name(row_name_str)
                if not player:
                    player = Player(name=row_name_str)
                    if self.db_manager.create_player(player):
                        players_created += 1
                
                # Create scorecard for this player/row
                scorecard = self._create_scorecard_from_row(row_df, game_id, row_name_str)
                if scorecard:
                    if self.db_manager.create_scorecard(scorecard):
                        scorecards_created += 1
            
            return {
                'players_created': players_created,
                'scorecards_created': scorecards_created
            }
            
        except Exception as e:
            logger.exception(f"Error processing CSV data from {csv_path}")
            return {
                'players_created': 0,
                'scorecards_created': 0
            }
    
    def _create_scorecard_from_row(self, df: pd.DataFrame, game_id: str, 
                                   player_name: str) -> Optional[Scorecard]:
        """
        Create a scorecard from DataFrame rows.
        
        Args:
            df: DataFrame with player/row data
            game_id: The game ID
            player_name: Player or team name
            
        Returns:
            Scorecard instance or None
        """
        try:
            # Count positive and negative occurrences for each category
            stats = {}
            
            # Define column mappings
            column_mappings = {
                'Space Read': {
                    '+ve Space Read: Live Dribble': 'space_read_live_dribble',
                    '+ve Space Read: Catch': 'space_read_catch',
                    '-ve Space Read: Live Dribble': 'space_read_live_dribble_negative',
                    '-ve Space Read: Catch': 'space_read_catch_negative'
                },
                'DM Catch': {
                    '+ve DM Catch: Back-to-Back': 'dm_catch_back_to_back_positive',
                    '-ve DM Catch: Back-to-Back': 'dm_catch_back_to_back_negative',
                    '+ve DM Catch: Uncontested Shot': 'dm_catch_uncontested_shot_positive',
                    '-ve DM Catch: Uncontested Shot': 'dm_catch_uncontested_shot_negative',
                    '+ve DM Catch: Swing': 'dm_catch_swing_positive',
                    '-ve DM Catch: Swing': 'dm_catch_swing_negative',
                    '+ve DM Catch: Drive Pass': 'dm_catch_drive_pass_positive',
                    '-ve DM Catch: Drive Pass': 'dm_catch_drive_pass_negative',
                    '+ve DM Catch: Drive a Swing/Skip Pass': 'dm_catch_drive_swing_skip_pass_positive',
                    '-ve DM Catch: Drive a Swing/Skip Pass': 'dm_catch_drive_swing_skip_pass_negative'
                },
                'QB12 DM': {
                    '+ve QB12: Strong Side': 'qb12_strong_side_positive',
                    '-ve QB12: Strong Side': 'qb12_strong_side_negative',
                    '+ve QB12: Baseline': 'qb12_baseline_positive',
                    '-ve QB12: Baseline': 'qb12_baseline_negative',
                    '+ve QB12: Fill Behind': 'qb12_fill_behind_positive',
                    '-ve QB12: Fill Behind': 'qb12_fill_behind_negative',
                    '+ve QB12: Weak Side': 'qb12_weak_side_positive',
                    '-ve QB12: Weak Side': 'qb12_weak_side_negative',
                    '+ve QB12: Roller': 'qb12_roller_positive',
                    '-ve QB12: Roller': 'qb12_roller_negative',
                    '+ve QB12: Skip Pass': 'qb12_skip_pass_positive',
                    '-ve QB12: Skip Pass': 'qb12_skip_pass_negative',
                    '+ve QB12: Cutter': 'qb12_cutter_positive',
                    '-ve QB12: Cutter': 'qb12_cutter_negative'
                },
                'Driving': {
                    '+ve Driving: Paint Touch': 'driving_paint_touch_positive',
                    '-ve Driving: Paint Touch': 'driving_paint_touch_negative',
                    '+ve Driving: Physicality': 'driving_physicality_positive',
                    '-ve Driving: Physicality': 'driving_physicality_negative'
                },
                'Positioning': {
                    '+ve Positioning - Create Shape': 'offball_positioning_create_shape_positive',
                    '-ve Positioning - Create Shape': 'offball_positioning_create_shape_negative',
                    '+ve Positioning - Advantage Awareness': 'offball_positioning_adv_awareness_positive',
                    '-ve Positioning - Advantage Awareness': 'offball_positioning_adv_awareness_negative'
                },
                'Transition': {
                    '+ve Transition: Effort and Pace': 'transition_effort_pace_positive',
                    '-ve Transition: Effort and Pace': 'transition_effort_pace_negative'
                },
                'Cutting & Screeing': {
                    '+ve Cutting & Screening: Denial': 'cs_denial_positive',
                    '-ve Cutting & Screening: Denial': 'cs_denial_negative',
                    '+ve Cutting & Screening: Movement': 'cs_movement_positive',
                    '-ve Cutting & Screening: Movement': 'cs_movement_negative',
                    '+ve Cutting & Screening: Body to Body': 'cs_body_to_body_positive',
                    '-ve Cutting & Screening: Body to Body': 'cs_body_to_body_negative',
                    '+ve Cutting & Screening: Principle': 'cs_screen_principle_positive',
                    '-ve Cutting & Screening: Principle': 'cs_screen_principle_negative',
                    '+ve Cutting & Screening: Cut Fill': 'cs_cut_fill_positive',
                    '-ve Cutting & Screening: Cut Fill': 'cs_cut_fill_negative'
                },
                'Relocation': {
                    '+ve Relocate: Weak Corner': 'relocation_weak_corner_positive',
                    '-ve Relocate: Weak Corner': 'relocation_weak_corner_negative',
                    '+ve Relocate: 45 Cut': 'relocation_45_cut_positive',
                    '-ve Relocate: 45 Cut': 'relocation_45_cut_negative',
                    '+ve Relocate: Slide Away': 'relocation_slide_away_positive',
                    '-ve Relocate: Slide Away': 'relocation_slide_away_negative',
                    '+ve Relocate: Fill Behind': 'relocation_fill_behind_positive',
                    '-ve Relocate: Fill Behind': 'relocation_fill_behind_negative',
                    '+ve Relocate: Dunker- Baseline Cut': 'relocation_dunker_baseline_positive',
                    '-ve Relocate: Dunker- Baseline Cut': 'relocation_dunker_baseline_negative',
                    '+ve Relocate: Corner Fill': 'relocation_corner_fill_positive',
                    '-ve Relocate: Corner Fill': 'relocation_corner_fill_negative',
                    '+ve Relocate: Reverse Direction': 'relocation_reverse_direction_positive',
                    '-ve Relocate: Reverse Direction': 'relocation_reverse_direction_negative'
                },
                'Footwork': {
                    '+ve Footwork: Step to Ball': 'footwork_step_to_ball_positive',
                    '-ve Footwork: Step to Ball': 'footwork_step_to_ball_negative',
                    '+ve Footwork: Patient Pickup': 'footwork_patient_pickup_positive',
                    '-ve Footwork: Patient Pickup': 'footwork_patient_pickup_negative',
                    '+ve Footwork: Long 2': 'footwork_long_2_positive',
                    '-ve Footwork: Long 2': 'footwork_long_2_negative'
                },
                'Passing': {
                    '+ve Passing: Teammate on the Move': 'passing_teammate_on_move_positive',
                    '-ve Passing: Teammate on the Move': 'passing_teammate_on_move_negative',
                    '+ve Passing: Read the Length': 'passing_read_length_positive',
                    '-ve Passing: Read the Length': 'passing_read_length_negative'
                },
                'Finishing': {
                    '+ve Finishing: Stride Pivot': 'finishing_stride_pivot_positive',
                    '-ve Finishing: Stride Pivot': 'finishing_stride_pivot_negative',
                    '+ve Finishing: Read the Length': 'finishing_read_length_positive',
                    '-ve Finishing: Read the Length': 'finishing_read_length_negative',
                    '+ve Finishing: Ball Security': 'finishing_ball_security_positive',
                    '-ve Finishing: Ball Security': 'finishing_ball_security_negative',
                    '+ve Finishing: Earn a Foul': 'finishing_earn_foul_positive',
                    '-ve Finishing: Earn a Foul': 'finishing_earn_foul_negative',
                    '+ve Finishing: Physicality': 'finishing_physicality_positive',
                    '-ve Finishing: Physicality': 'finishing_physicality_negative',
                    '+ve Finishing: Stride Holds': 'finishing_stride_holds_positive',
                    '-ve Finishing: Stride Holds': 'finishing_stride_holds_negative'
                }
            }
            
            # Count occurrences in each category column
            import re
            for col_name, patterns in column_mappings.items():
                if col_name in df.columns:
                    col_data = df[col_name].fillna('').astype(str)
                    
                    for pattern, stat_field in patterns.items():
                        # Escape regex special characters in pattern
                        escaped_pattern = re.escape(pattern)
                        count = col_data.str.count(escaped_pattern).sum()
                        stats[stat_field] = int(count)
            
            # Create scorecard with all stats
            scorecard = Scorecard(
                player_name=player_name,
                game_id=game_id,
                **stats
            )
            
            return scorecard
            
        except Exception as e:
            logger.exception(f"Error creating scorecard for {player_name}")
            return None

