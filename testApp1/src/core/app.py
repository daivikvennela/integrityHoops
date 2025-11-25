import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file, make_response
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import logging
from src.processors.custom_etl_processor import StatisticalDataProcessor
from src.processors.basketball_cognitive_processor import BasketballCognitiveProcessor
from src.processors.cog_score_calculator import CogScoreCalculator
from src.api.player_api import player_api
from src.api.player_management_dashboard import player_dashboard
from src.core.dashboard import dashboard_bp
from src.database.db_manager import DatabaseManager
from src.api.notebook_api import notebook_api, notebook_bp
try:
    import sys
    import os
    # Add testApp1 to path for systems_check module
    testapp1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if testapp1_path not in sys.path:
        sys.path.insert(0, testapp1_path)
    from systems_check.api import systems_check_bp
except ImportError as e:
    # Systems check is optional, don't fail if it's not available
    logger.warning(f"Systems check module not available: {e}")
    systems_check_bp = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Production configuration - PostgreSQL support
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
if FLASK_ENV == 'production':
    # Use PostgreSQL in production
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Render uses postgres://, but psycopg2 needs postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
else:
    # Use SQLite in development
    DATABASE_URL = None

app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Register blueprints
app.register_blueprint(player_api)
app.register_blueprint(player_dashboard)
app.register_blueprint(dashboard_bp)
app.register_blueprint(notebook_api)
app.register_blueprint(notebook_bp)
if systems_check_bp:
    app.register_blueprint(systems_check_bp)

# Configuration (use absolute paths based on app.root_path)
DATA_ROOT = os.path.join(app.root_path, 'data')

# Use environment variables for production or fallback to defaults
if FLASK_ENV == 'production':
    # Production uses ephemeral storage
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    PROCESSED_FOLDER = os.environ.get('PROCESSED_FOLDER', '/tmp/processed')
else:
    # Development uses local storage
    UPLOAD_FOLDER = os.path.join(DATA_ROOT, 'uploads')
    PROCESSED_FOLDER = os.path.join(DATA_ROOT, 'processed')

# Database path - PostgreSQL in production, SQLite in development
if DATABASE_URL:
    DB_PATH = DATABASE_URL  # PostgreSQL connection string
else:
    DB_PATH = os.path.join(DATA_ROOT, 'basketball.db')  # SQLite for local

# If running in production without a DATABASE_URL, force a writable SQLite path
if not DATABASE_URL and FLASK_ENV == 'production':
    DB_PATH = os.environ.get('DB_PATH', '/tmp/basketball.db')

# Ensure parent directory exists for file-based DB_PATH
if not str(DB_PATH).startswith(('postgres://', 'postgresql://')):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create data directories if they don't exist (for development)
if FLASK_ENV != 'production':
    os.makedirs(DATA_ROOT, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['DB_PATH'] = DB_PATH
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


 # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_csv_file(file_path):
    """Load CSV file and return DataFrame"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
        return df
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise

from werkzeug.exceptions import RequestEntityTooLarge

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    flash('File too large (max 16MB). Please upload a smaller file.')
    return redirect(url_for('smartdash'))

# -----------------------------
# Analytics Dashboard (Cog Scores)
# -----------------------------

@app.route('/analytics-dashboard')
def analytics_dashboard():
    """Main analytics dashboard page (visualizations + ETL)."""
    return render_template('analytics_dashboard.html')

@app.route('/animated-scorecard')
def animated_scorecard():
    """Animated scorecard dashboard page"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    return render_template('animated_scorecard.html', latest_file=latest_file, processed_files=processed_files)

@app.route('/animated-scorecard/<filename>')
def animated_scorecard_with_data(filename):
    """Animated scorecard with specific data file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('animated_scorecard'))
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Generate animated scorecard data
        processor = BasketballCognitiveProcessor()
        scorecard_data = processor.generate_animated_scorecard_data(df)
        
        # Get the original CSV filename for display
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        
        return render_template('animated_scorecard.html', 
                             filename=filename,
                             original_filename=original_filename,
                             scorecard_data=scorecard_data)
        
    except Exception as e:
        logger.exception("Error loading animated scorecard data")
        flash(f'Error loading data: {str(e)}')
        return redirect(url_for('animated_scorecard'))

@app.route('/api/scorecard-data/<filename>')
def api_scorecard_data(filename):
    """API endpoint to return scorecard data as JSON for animations"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Generate animated scorecard data
        processor = BasketballCognitiveProcessor()
        scorecard_data = processor.generate_animated_scorecard_data(df)
        
        return jsonify({'success': True, 'data': scorecard_data})
        
    except Exception as e:
        logger.exception("Error generating scorecard data API response")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/tests/<path:filename>')
def serve_test_file(filename):
    """Serve test files for browser-based testing"""
    import os
    test_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'tests')
    return send_from_directory(test_dir, filename)

@app.route('/api/cog-scores')
def api_cog_scores():
    """Return cog scores over games for charting.
    Query params:
      level=team|player (default team)
      team=<team name>
      player_name=<player name>
    """
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        level = request.args.get('level', 'team')
        team = request.args.get('team')
        player_name = request.args.get('player_name')
        points = db_manager.get_cog_scores_over_time(level=level, team=team, player_name=player_name)
        
        # Fetch game results (win/loss) for team level
        game_results = {}
        if level == 'team' and points:
            from src.core.game_results import fetch_multiple_game_results
            # Extract dates from points (points now have 'date_iso' field)
            dates = []
            for point in points:
                if 'date_iso' in point and point['date_iso']:
                    dates.append(point['date_iso'])
                elif 'timestamp' in point:
                    dt = datetime.fromtimestamp(point['timestamp'])
                    date_iso = dt.strftime('%Y-%m-%d')
                    dates.append(date_iso)
            
            if dates:
                game_results = fetch_multiple_game_results(dates)
                logger.info(f"Fetched game results for {len(game_results)} of {len(dates)} games")
        
        return jsonify({
            'success': True, 
            'level': level, 
            'points': points,
            'game_results': game_results  # Add win/loss data
        })
    except Exception as e:
        logger.exception('Error fetching cog scores')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/team', methods=['POST'])
def api_add_team_cog_score():
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        data = request.get_json() or {}
        game_date = int(data.get('game_date'))  # epoch seconds
        team = (data.get('team') or '').strip()
        opponent = (data.get('opponent') or '').strip()
        score = int(data.get('score'))
        source = data.get('source')
        note = data.get('note')
        if not team or not opponent:
            return jsonify({'success': False, 'error': 'team and opponent are required'}), 400
        ok = db_manager.insert_team_cog_score(game_date, team, opponent, score, source, note)
        return jsonify({'success': ok})
    except Exception as e:
        logger.exception('Error adding team cog score')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/reset', methods=['POST'])
def api_reset_cog_scores():
    """Clear all team and player cog scores (does not affect other data)."""
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM team_cog_scores')
            cursor.execute('DELETE FROM player_cog_scores')
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.exception('Error resetting cog scores')
        return jsonify({'success': False, 'error': str(e)}), 500

def _sync_overall_scores_to_analytics(overall_scores: dict, game_info: dict, db_manager: DatabaseManager):
    """
    Sync overall cognitive scores from team statistics to team_cog_scores table.
    This ensures that games shown in Team Statistics Over Time are also available
    in the main Analytics Dashboard.
    
    Args:
        overall_scores: Dict mapping date_iso (YYYY-MM-DD) to overall score (float)
        game_info: Dict mapping date_iso to game info dict with 'opponent', 'date_string', 'filename'
        db_manager: DatabaseManager instance
    """
    if not overall_scores or not game_info:
        return
    
    synced_count = 0
    skipped_count = 0
    
    for date_iso, overall_score in overall_scores.items():
        info = game_info.get(date_iso, {})
        opponent = info.get('opponent', 'Unknown')
        team = 'Heat'  # Default team name
        
        # Convert date_iso (YYYY-MM-DD) to timestamp
        try:
            dt = datetime.strptime(date_iso, '%Y-%m-%d')
            game_date_timestamp = int(dt.timestamp())
        except ValueError:
            logger.warning(f"Invalid date format in overall_scores: {date_iso}")
            continue
        
        # Check if this game already exists in team_cog_scores
        if db_manager.team_cog_score_exists(game_date_timestamp, team, opponent):
            skipped_count += 1
            logger.debug(f"Skipping {date_iso} vs {opponent} - already exists in team_cog_scores")
            continue
        
        # Insert new score
        overall_int = int(round(overall_score))
        result = db_manager.upsert_team_cog_score(
            game_date=game_date_timestamp,
            team=team,
            opponent=opponent,
            score=overall_int,
            source='team_statistics',
            note=f'Auto-synced from team statistics'
        )
        
        if result is True:  # Inserted
            synced_count += 1
            logger.info(f"Synced overall score to analytics dashboard: {date_iso} vs {opponent} = {overall_int}%")
        elif result is False:  # Updated
            synced_count += 1
            logger.info(f"Updated overall score in analytics dashboard: {date_iso} vs {opponent} = {overall_int}%")
        else:  # Error
            logger.error(f"Failed to sync overall score: {date_iso} vs {opponent}")
    
    if synced_count > 0:
        logger.info(f"Synced {synced_count} overall scores to analytics dashboard (skipped {skipped_count} duplicates)")

def parse_date_from_filename(filename: str) -> tuple:
    """
    Parse date and game info from CSV filename.
    Expected format: "MM.DD.YY Team v Opponent(team).csv"
    
    Returns:
        tuple: (date_string (MM.DD.YY), date_iso (YYYY-MM-DD), opponent, filename)
    """
    import re
    from datetime import datetime
    
    # Extract date from filename (e.g., "10.04.25" from "10.04.25 Heat v Magic(team).csv")
    date_match = re.match(r'(\d{2}\.\d{2}\.\d{2})', filename)
    if not date_match:
        return None, None, None, filename
    
    date_string = date_match.group(1)  # MM.DD.YY format
    
    # Parse date directly to avoid timezone issues
    # MM.DD.YY -> YYYY-MM-DD (no timestamp conversion)
    try:
        dt = datetime.strptime(date_string, '%m.%d.%y')
        date_iso = dt.strftime('%Y-%m-%d')  # Direct conversion to YYYY-MM-DD
    except ValueError:
        return None, None, None, filename
    
    # Extract opponent from filename
    # Try different patterns:
    # 1. "10.04.25 Heat v Magic(team).csv" -> "Magic"
    # 2. "06.21.25_KP_v_MIN_Offense.csv" -> "MIN"
    # 3. "10.01.25_Miami_csv.csv" -> "Unknown" (no opponent pattern)
    opponent = 'Unknown'
    
    # Pattern 1: " v Opponent" (space v space)
    opponent_match = re.search(r'v\s+([A-Za-z]+)', filename)
    if opponent_match:
        opponent = opponent_match.group(1)
    else:
        # Pattern 2: "_v_OPPONENT" (underscore v underscore)
        opponent_match = re.search(r'_v_([A-Z]+)', filename)
        if opponent_match:
            opponent = opponent_match.group(1)
        else:
            # Pattern 3: "_v_OPPONENT_" (underscore v underscore with trailing underscore)
            opponent_match = re.search(r'_v_([A-Z]+)_', filename)
            if opponent_match:
                opponent = opponent_match.group(1)
    
    return date_string, date_iso, opponent, filename


@app.route('/api/team-statistics', methods=['GET'])
def api_team_statistics():
    """Get team statistics over time for cognitive categories.
    
    First checks database for stored statistics. If not found or if force_recalculate=true,
    calculates from CSV files and stores in database for future use.
    
    Query params:
      category: Optional category name (if not provided, returns all categories)
      force_recalculate: Optional flag to force recalculation from CSV files
      use_database: Optional flag (default True) to use database if available
    
    Returns:
      JSON with statistics grouped by game date
    """
    try:
        category = request.args.get('category')  # Optional: filter by category
        force_recalculate = request.args.get('force_recalculate', 'false').lower() == 'true'
        use_database = request.args.get('use_database', 'true').lower() == 'true'
        
        db_manager = DatabaseManager(app.config['DB_PATH'])
        
        # Map CSV column names to display names
        COLUMN_NAME_MAP = {
            'Cutting & Screeing': 'Cutting & Screening',  # Fix typo
            'DM Catch': 'DM Catch',
            'Driving': 'Driving',
            'Finishing': 'Finishing',
            'Footwork': 'Footwork',
            'Passing': 'Passing',
            'Positioning': 'Positioning',
            'QB12 DM': 'QB12 DM',
            'Relocation': 'Relocation',
            'Space Read': 'Space Read',
            'Transition': 'Transition'
        }
        
        # Categories we want to display
        DISPLAY_CATEGORIES = [
            'Cutting & Screening',
            'DM Catch',
            'Finishing',
            'Footwork',
            'Passing',
            'Positioning',
            'QB12 DM',
            'Relocation',
            'Space Read',
            'Transition'
        ]
        
        # Try to get from database first (unless force_recalculate is true)
        if use_database and not force_recalculate:
            db_stats = db_manager.get_team_statistics(category=category, team='Heat')
            if db_stats:
                logger.info(f"Retrieved {len(db_stats)} statistics records from database")
                
                # Convert database format to API response format
                statistics_data = []
                overall_scores = db_manager.get_team_statistics_overall_scores(team='Heat')
                game_info = db_manager.get_team_statistics_game_info(team='Heat')
                
                for stat in db_stats:
                    statistics_data.append({
                        'date': stat['date'],
                        'date_string': stat['date_string'],
                        'category': stat['category'],
                        'percentage': stat['percentage'],
                        'opponent': stat['opponent'],
                        'filename': stat['filename']
                    })
                
                # Filter by category if specified (already filtered in query, but double-check)
                if category:
                    statistics_data = [s for s in statistics_data if s['category'] == category]
                
                # Sort by date
                statistics_data.sort(key=lambda x: x['date'])
                
                # Sync overall scores to team_cog_scores table (for analytics dashboard)
                _sync_overall_scores_to_analytics(overall_scores, game_info, db_manager)
                
                # Fetch game results (win/loss) for all dates
                from src.core.game_results import fetch_multiple_game_results
                unique_dates = list(set(stat['date'] for stat in statistics_data))
                game_results = fetch_multiple_game_results(unique_dates)
                
                # Log how many unique games we have
                logger.info(f"Retrieved {len(unique_dates)} unique game dates from database")
                logger.info(f"Found game results for {len(game_results)} games")
                
                return jsonify({
                    'success': True,
                    'statistics': statistics_data,
                    'category': category,
                    'overall_scores': overall_scores,
                    'game_info': game_info,
                    'game_results': game_results,  # Add win/loss data
                    'source': 'database',
                    'unique_games': len(unique_dates)
                })
        
        # If not in database or force_recalculate, calculate from CSV files
        logger.info("Calculating team statistics from CSV files...")
        
        # Find all CSV files in test_csvs folder
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  # src/core
        test_csvs_dir = os.path.join(current_file_dir, '..', '..', 'testcases', 'test_csvs')
        test_csvs_dir = os.path.abspath(test_csvs_dir)
        
        if not os.path.exists(test_csvs_dir):
            logger.error(f"Test CSV directory not found: {test_csvs_dir}")
            return jsonify({'success': False, 'error': 'Test CSV directory not found'}), 500
        
        # Get all CSV files (exclude .numbers files and other non-CSV files)
        csv_files = [f for f in os.listdir(test_csvs_dir) if f.endswith('.csv') and not f.endswith('.numbers')]
        csv_files.sort()  # Sort by filename (which includes date)
        
        if not csv_files:
            logger.warning(f"No CSV files found in {test_csvs_dir}")
            return jsonify({
                'success': True,
                'statistics': [],
                'category': category,
                'overall_scores': {},
                'game_info': {}
            })
        
        statistics_data = []
        overall_scores = {}
        game_info = {}  # Store filename and opponent per date
        processing_errors = []  # Track errors for diagnostics
        processed_files = []  # Track successfully processed files
        
        # Process each CSV file
        for csv_file in csv_files:
            csv_path = os.path.join(test_csvs_dir, csv_file)
            
            # Parse date and opponent from filename
            date_string, date_iso, opponent, full_filename = parse_date_from_filename(csv_file)
            
            if not date_string or not date_iso:
                error_msg = f"Could not parse date from filename: {csv_file}"
                logger.warning(error_msg)
                processing_errors.append(error_msg)
                continue
            
            try:
                # Calculate statistics using CogScoreCalculator
                calculator = CogScoreCalculator(csv_path)
                scores, overall = calculator.calculate_all_scores()
                
                logger.info(f"Successfully processed {csv_file}: overall={overall:.2f}%, scores keys={list(scores.keys())}")
                
                # Convert date_iso to timestamp for database
                dt = datetime.strptime(date_iso, '%Y-%m-%d')
                game_date_timestamp = int(dt.timestamp())
                
                # Store overall score
                overall_scores[date_iso] = overall
                
                # Store game info
                game_info[date_iso] = {
                    'filename': full_filename,
                    'opponent': opponent,
                    'date_string': date_string
                }
                
                # Map CSV column names to display categories and build statistics
                categories_found = 0
                for csv_col, display_name in COLUMN_NAME_MAP.items():
                    if csv_col in scores and display_name in DISPLAY_CATEGORIES:
                        score_data = scores[csv_col]
                        percentage = score_data['score']
                        positive_count = score_data.get('positive', 0)
                        negative_count = score_data.get('negative', 0)
                        total_count = score_data.get('total', 0)
                        
                        # Store in database
                        db_manager.insert_team_statistics(
                            game_date_iso=date_iso,
                            game_date_timestamp=game_date_timestamp,
                            date_string=date_string,
                            team='Heat',
                            opponent=opponent or 'Unknown',
                            category=display_name,
                            percentage=percentage,
                            positive_count=positive_count,
                            negative_count=negative_count,
                            total_count=total_count,
                            overall_score=overall,
                            csv_filename=full_filename
                        )
                        
                        statistics_data.append({
                            'date': date_iso,
                            'date_string': date_string,
                            'category': display_name,
                            'percentage': percentage,
                            'opponent': opponent,
                            'filename': full_filename
                        })
                        categories_found += 1
                
                logger.info(f"Added {categories_found} categories from {csv_file} to database")
                processed_files.append(csv_file)
                
            except Exception as e:
                error_msg = str(e)
                full_error = f"Error processing CSV file {csv_file}: {error_msg}"
                logger.error(full_error, exc_info=True)
                processing_errors.append(full_error)
                # Log more details about the error
                if "Cannot convert numpy.ndarray" in error_msg:
                    logger.error(f"This is likely a pandas/numpy version compatibility issue. File: {csv_file}")
                continue
        
        # Filter by category if specified
        if category:
            statistics_data = [s for s in statistics_data if s['category'] == category]
        
        # Sort by date
        statistics_data.sort(key=lambda x: x['date'])
        
        # Sync overall scores to team_cog_scores table (for analytics dashboard)
        _sync_overall_scores_to_analytics(overall_scores, game_info, db_manager)
        
        # Fetch game results (win/loss) for all dates
        from src.core.game_results import fetch_multiple_game_results
        unique_dates = list(set(stat['date'] for stat in statistics_data))
        game_results = fetch_multiple_game_results(unique_dates)
        
        # Log summary
        logger.info(f"Team statistics summary: {len(processed_files)} files processed, {len(unique_dates)} unique games, {len(statistics_data)} data points, {len(processing_errors)} errors")
        logger.info(f"Found game results for {len(game_results)} games")
        
        # Build response with diagnostic info
        response_data = {
            'success': True,
            'statistics': statistics_data,
            'category': category,
            'overall_scores': overall_scores,  # Overall cog scores by date
            'game_info': game_info,  # Additional game metadata
            'game_results': game_results,  # Add win/loss data
            'source': 'csv_calculated',
            'diagnostics': {
                'files_found': len(csv_files),
                'files_processed': len(processed_files),
                'data_points': len(statistics_data),
                'errors': processing_errors if processing_errors else None
            }
        }
        
        # If we have files but no data, this is a warning condition
        if csv_files and not statistics_data:
            logger.warning(f"Found {len(csv_files)} CSV files but generated 0 statistics data points. This may indicate a data processing issue.")
            response_data['warning'] = f'Processed {len(processed_files)} files but found no statistics data. Check logs for errors.'
        
        # Sync overall scores to team_cog_scores table (for analytics dashboard)
        _sync_overall_scores_to_analytics(overall_scores, game_info, db_manager)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.exception('Error fetching team statistics')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/games-dashboard', methods=['GET'])
def api_games_dashboard():
    """
    Get all games with their statistics from the database.
    Returns games with overall scores and category breakdowns.
    """
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        
        # Get games with statistics from database
        games = db_manager.get_games_with_statistics()
        
        # Also get category statistics from CSV files (similar to team-statistics)
        # This will help populate category breakdowns
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        test_csvs_dir = os.path.join(current_file_dir, '..', '..', 'testcases', 'test_csvs')
        test_csvs_dir = os.path.abspath(test_csvs_dir)
        
        # Create a mapping of date -> category statistics
        date_to_stats = {}
        
        if os.path.exists(test_csvs_dir):
            csv_files = [f for f in os.listdir(test_csvs_dir) if f.endswith('.csv') and not f.endswith('.numbers')]
            
            for csv_file in csv_files:
                csv_path = os.path.join(test_csvs_dir, csv_file)
                date_string, date_iso, opponent, full_filename = parse_date_from_filename(csv_file)
                
                if not date_iso:
                    continue
                
                try:
                    calculator = CogScoreCalculator(csv_path)
                    scores, overall = calculator.calculate_all_scores()
                    
                    # Map CSV column names to display categories
                    COLUMN_NAME_MAP = {
                        'Space Read': 'Space Read',
                        'DM Catch': 'DM Catch',
                        'Driving': 'Driving',
                        'Finishing': 'Finishing',
                        'Footwork': 'Footwork',
                        'Passing': 'Passing',
                        'Positioning': 'Positioning',
                        'QB12 DM': 'QB12 DM',
                        'Relocation': 'Relocation',
                        'Cutting & Screeing': 'Cutting & Screening',
                        'Transition': 'Transition'
                    }
                    
                    categories = {}
                    for csv_col, display_name in COLUMN_NAME_MAP.items():
                        if csv_col in scores:
                            score_data = scores[csv_col]
                            categories[display_name] = score_data['score']
                    
                    date_to_stats[date_iso] = {
                        'overall': overall,
                        'categories': categories
                    }
                except Exception as e:
                    logger.warning(f"Error processing {csv_file} for games dashboard: {e}")
                    continue
        
        # Merge database games with CSV statistics
        games_with_full_stats = []
        for game in games:
            game_date_iso = datetime.fromtimestamp(game['date']).strftime('%Y-%m-%d')
            
            # If we have CSV stats for this date, merge them
            if game_date_iso in date_to_stats:
                game['overall_score'] = game['overall_score'] or date_to_stats[game_date_iso]['overall']
                game['categories'] = date_to_stats[game_date_iso]['categories']
            else:
                # If no CSV stats, keep what we have from DB
                if not game.get('categories'):
                    game['categories'] = {}
            
            games_with_full_stats.append(game)
        
        return jsonify({
            'success': True,
            'games': games_with_full_stats
        })
        
    except Exception as e:
        logger.exception('Error fetching games dashboard')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/player', methods=['POST'])
def api_add_player_cog_score():
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        data = request.get_json() or {}
        game_date = int(data.get('game_date'))
        player_name = (data.get('player_name') or '').strip()
        team = data.get('team')
        opponent = data.get('opponent')
        score = int(data.get('score'))
        source = data.get('source')
        note = data.get('note')
        if not player_name:
            return jsonify({'success': False, 'error': 'player_name is required'}), 400
        ok = db_manager.insert_player_cog_score(game_date, player_name, team, opponent, score, source, note)
        return jsonify({'success': ok})
    except Exception as e:
        logger.exception('Error adding player cog score')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/team/<int:score_id>', methods=['DELETE'])
def api_delete_team_cog_score(score_id: int):
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        ok = db_manager.delete_team_cog_score_by_id(score_id)
        return jsonify({'success': ok})
    except Exception as e:
        logger.exception('Error deleting team cog score')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/player/<int:score_id>', methods=['DELETE'])
def api_delete_player_cog_score(score_id: int):
    try:
        db_manager = DatabaseManager(app.config['DB_PATH'])
        ok = db_manager.delete_player_cog_score_by_id(score_id)
        return jsonify({'success': ok})
    except Exception as e:
        logger.exception('Error deleting player cog score')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/calculate-from-csv', methods=['POST'])
def api_calculate_cog_score_from_csv():
    """Calculate cognitive scores from an uploaded CSV file."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only CSV files are allowed'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_{filename}')
        file.save(temp_path)
        
        try:
            # Calculate cognitive scores
            calculator = CogScoreCalculator(temp_path)
            report = calculator.get_full_report()
            
            logger.info(f"Calculated cog scores for {filename}: {report['overall_score']:.2f}%")
            
            return jsonify({
                'success': True,
                'data': report
            })
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.exception('Error calculating cog scores from CSV')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/team-statistics/export-pdf', methods=['POST'])
def api_export_team_statistics_pdf():
    """Generate premium PDF report with team statistics, charts, and analytics insights."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfgen import canvas
        from io import BytesIO
        import base64
        
        data = request.get_json() or {}
        chart_image = data.get('chart_image', '')
        statistics = data.get('statistics', [])
        overall_scores = data.get('overall_scores', {})
        game_info = data.get('game_info', {})
        category = data.get('category', '')
        insights = data.get('insights', {})
        
        if not chart_image:
            return jsonify({'success': False, 'error': 'No chart image provided'}), 400
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#F9423A'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#F9423A'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Cover Page
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph('HEAT TEAM STATISTICS', title_style))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph('Premium Analytics Report', styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Date range
        if overall_scores:
            dates = sorted(overall_scores.keys())
            if dates:
                date_str = f"{dates[0]} - {dates[-1]}"
                elements.append(Paragraph(f'<i>Report Period: {date_str}</i>', styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f'<i>Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}</i>', styles['Normal']))
        elements.append(PageBreak())
        
        # Executive Summary
        elements.append(Paragraph('Executive Summary', heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        if insights.get('overall_average'):
            avg = insights['overall_average']
            trend = insights.get('overall_trend', '0.00')
            trend_text = f"<b>+{trend}%</b>" if float(trend) > 0 else f"<b>{trend}%</b>"
            elements.append(Paragraph(f'Overall Cognitive Score Average: <b>{avg}%</b>', styles['Normal']))
            elements.append(Paragraph(f'Overall Trend: {trend_text}', styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Top Categories
        if insights.get('top_categories'):
            elements.append(Paragraph('Top Performing Categories:', subheading_style))
            for cat in insights['top_categories']:
                elements.append(Paragraph(f"• {cat['category']}: {cat['average']}%", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Areas for Improvement
        if insights.get('weak_categories'):
            elements.append(Paragraph('Areas for Improvement:', subheading_style))
            for cat in insights['weak_categories']:
                elements.append(Paragraph(f"• {cat['category']}: {cat['average']}%", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Improving/Declining Categories
        if insights.get('improving_categories'):
            elements.append(Paragraph('Improving Categories:', subheading_style))
            for cat in insights['improving_categories']:
                elements.append(Paragraph(f"• {cat['category']}: +{cat['trend']}% (avg: {cat['average']}%)", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        if insights.get('declining_categories'):
            elements.append(Paragraph('Categories Needing Attention:', subheading_style))
            for cat in insights['declining_categories']:
                elements.append(Paragraph(f"• {cat['category']}: {cat['trend']}% (avg: {cat['average']}%)", styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        
        elements.append(PageBreak())
        
        # Chart Section
        elements.append(Paragraph('Performance Visualization', heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        if category:
            elements.append(Paragraph(f'<i>Category: {category}</i>', styles['Normal']))
        else:
            elements.append(Paragraph('<i>All Categories Overview</i>', styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Decode and add chart image
        try:
            chart_data = chart_image.split(',')[1] if ',' in chart_image else chart_image
            chart_bytes = base64.b64decode(chart_data)
            chart_img = Image(BytesIO(chart_bytes), width=7*inch, height=5*inch)
            elements.append(chart_img)
        except Exception as e:
            logger.error(f"Error adding chart image: {e}")
            elements.append(Paragraph('<i>Chart image could not be included</i>', styles['Normal']))
        
        elements.append(PageBreak())
        
        # Overall Scores Table
        if overall_scores:
            elements.append(Paragraph('Game-by-Game Overall Scores', heading_style))
            elements.append(Spacer(1, 0.2*inch))
            
            table_data = [['Date', 'Opponent', 'Overall Score']]
            for date in sorted(overall_scores.keys()):
                score = overall_scores[date]
                info = game_info.get(date, {})
                opponent = info.get('opponent', 'Unknown')
                date_label = info.get('date_string', date).replace('.', '/')
                table_data.append([date_label, opponent, f"{score:.5f}%"])
            
            table = Table(table_data, colWidths=[2*inch, 2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F9423A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5F5')])
            ]))
            elements.append(table)
            elements.append(PageBreak())
        
        # Category Statistics Summary
        if insights.get('stats_summary'):
            elements.append(Paragraph('Category Performance Summary', heading_style))
            elements.append(Spacer(1, 0.2*inch))
            
            table_data = [['Category', 'Average', 'Min', 'Max', 'Trend']]
            for cat, stats in sorted(insights['stats_summary'].items(), 
                                   key=lambda x: float(x[1]['average']), reverse=True):
                table_data.append([
                    cat,
                    f"{stats['average']}%",
                    f"{stats['min']}%",
                    f"{stats['max']}%",
                    f"{stats['trend']}%"
                ])
            
            table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F9423A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5F5')]),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Return PDF as response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=heat_team_statistics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        return response
        
    except Exception as e:
        logger.exception('Error generating PDF report')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/reseed-from-testcases', methods=['POST'])
def api_reseed_from_testcases():
    """Recompute and insert/update team cog scores from the three known testcase CSVs.
    Only inserts if the game (date + team + opponent) doesn't already exist.
    The testcases are used to verify the calculator works correctly.
    """
    try:
        # Locate test_csvs directory relative to this file
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  # src/core
        test_csvs_dir = os.path.abspath(os.path.join(current_file_dir, '..', '..', 'testcases', 'test_csvs'))

        if not os.path.isdir(test_csvs_dir):
            return jsonify({'success': False, 'error': f'Test CSV directory not found: {test_csvs_dir}'}), 500

        # Fixed order of files to process (for testing calculator)
        filenames = [
            '10.04.25 Heat v Magic(team).csv',
            '10.06.25 Heat v Bucks(team).csv',
            '10.13.25 MIA v ATL(team).csv',
        ]

        db_manager = DatabaseManager(app.config['DB_PATH'])

        processed: list[dict] = []
        skipped: list[dict] = []
        errors: list[str] = []

        for fname in filenames:
            csv_path = os.path.join(test_csvs_dir, fname)
            if not os.path.exists(csv_path):
                errors.append(f'Missing file: {fname}')
                continue

            # Compute overall score (to verify calculator works)
            calculator = CogScoreCalculator(csv_path)
            scores, overall = calculator.calculate_all_scores()
            overall_int = int(round(overall))

            # Parse date/opponent from filename
            date_string, date_iso, opponent, _ = parse_date_from_filename(fname)
            if not date_iso:
                errors.append(f'Could not parse date: {fname}')
                continue

            # Convert YYYY-MM-DD -> epoch seconds at midnight
            dt = datetime.strptime(date_iso, '%Y-%m-%d')
            ts = int(dt.timestamp())

            # Check if this game already exists
            if db_manager.team_cog_score_exists(ts, 'Heat', opponent or 'Unknown'):
                skipped.append({
                    'filename': fname,
                    'date_iso': date_iso,
                    'opponent': opponent,
                    'overall': overall_int,
                    'reason': 'Already exists'
                })
                continue

            # Insert new score
            result = db_manager.upsert_team_cog_score(
                game_date=ts,
                team='Heat',
                opponent=opponent or 'Unknown',
                score=overall_int,
                source='csv',
                note='Auto reseed'
            )
            if result is not None:
                processed.append({
                    'filename': fname,
                    'date_iso': date_iso,
                    'opponent': opponent,
                    'overall': overall_int,
                    'action': 'inserted' if result else 'updated'
                })
            else:
                errors.append(f'Upsert failed: {fname}')

        return jsonify({
            'success': True,
            'processed': processed,
            'skipped': skipped,
            'errors': errors
        })
    except Exception as e:
        logger.exception('Error reseeding from testcases')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cog-scores/process-all-csvs', methods=['POST'])
def api_process_all_csvs():
    """Process all CSV files in testcases/test_csvs and add scores to database.
    This will calculate scores and store them in team_cog_scores and team_statistics tables.
    """
    try:
        # Locate test_csvs directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  # src/core
        test_csvs_dir = os.path.abspath(os.path.join(current_file_dir, '..', '..', 'testcases', 'test_csvs'))

        if not os.path.isdir(test_csvs_dir):
            return jsonify({'success': False, 'error': f'Test CSV directory not found: {test_csvs_dir}'}), 500

        db_manager = DatabaseManager(app.config['DB_PATH'])

        # Get all CSV files
        csv_files = [f for f in os.listdir(test_csvs_dir) if f.endswith('.csv') and not f.endswith('.numbers')]
        csv_files.sort()

        processed: list[dict] = []
        skipped: list[dict] = []
        errors: list[str] = []

        COLUMN_NAME_MAP = {
            'Space Read': 'Space Read',
            'DM Catch': 'DM Catch',
            'Driving': 'Driving',
            'Finishing': 'Finishing',
            'Footwork': 'Footwork',
            'Passing': 'Passing',
            'Positioning': 'Positioning',
            'QB12 DM': 'QB12 DM',
            'Relocation': 'Relocation',
            'Cutting & Screeing': 'Cutting & Screening',
            'Transition': 'Transition'
        }
        
        DISPLAY_CATEGORIES = [
            'Space Read', 'DM Catch', 'Driving', 'Finishing', 'Footwork',
            'Passing', 'Positioning', 'QB12 DM', 'Relocation',
            'Cutting & Screening', 'Transition'
        ]

        for csv_file in csv_files:
            csv_path = os.path.join(test_csvs_dir, csv_file)
            
            try:
                # Parse date and opponent from filename
                date_string, date_iso, opponent, full_filename = parse_date_from_filename(csv_file)
                
                if not date_string or not date_iso:
                    errors.append(f'Could not parse date from filename: {csv_file}')
                    continue

                # Calculate statistics using CogScoreCalculator
                calculator = CogScoreCalculator(csv_path)
                scores, overall = calculator.calculate_all_scores()
                overall_int = int(round(overall))

                # Convert date_iso to timestamp for database
                dt = datetime.strptime(date_iso, '%Y-%m-%d')
                game_date_timestamp = int(dt.timestamp())

                # Check if already exists
                team = 'Heat'
                already_exists = db_manager.team_cog_score_exists(game_date_timestamp, team, opponent or 'Unknown')
                
                # Store team cog score
                result = db_manager.upsert_team_cog_score(
                    game_date=game_date_timestamp,
                    team=team,
                    opponent=opponent or 'Unknown',
                    score=overall_int,
                    source='csv',
                    note=f'Processed from {csv_file}'
                )

                # Store category statistics
                categories_stored = 0
                for csv_col, display_name in COLUMN_NAME_MAP.items():
                    if csv_col in scores and display_name in DISPLAY_CATEGORIES:
                        score_data = scores[csv_col]
                        percentage = score_data['score']
                        positive_count = score_data.get('positive', 0)
                        negative_count = score_data.get('negative', 0)
                        total_count = score_data.get('total', 0)
                        
                        db_manager.insert_team_statistics(
                            game_date_iso=date_iso,
                            game_date_timestamp=game_date_timestamp,
                            date_string=date_string,
                            team=team,
                            opponent=opponent or 'Unknown',
                            category=display_name,
                            percentage=percentage,
                            positive_count=positive_count,
                            negative_count=negative_count,
                            total_count=total_count,
                            overall_score=overall,
                            csv_filename=csv_file
                        )
                        categories_stored += 1

                if result is not None:
                    processed.append({
                        'filename': csv_file,
                        'date_iso': date_iso,
                        'opponent': opponent,
                        'overall': overall_int,
                        'categories': categories_stored,
                        'action': 'updated' if already_exists else 'inserted'
                    })
                else:
                    errors.append(f'Failed to store score for: {csv_file}')

            except Exception as e:
                error_msg = str(e)
                errors.append(f'Error processing {csv_file}: {error_msg}')
                logger.error(f'Error processing CSV file {csv_file}: {error_msg}', exc_info=True)
                continue

        return jsonify({
            'success': True,
            'processed': processed,
            'skipped': skipped,
            'errors': errors,
            'total_files': len(csv_files)
        })
    except Exception as e:
        logger.exception('Error processing all CSVs')
        return jsonify({'success': False, 'error': str(e)}), 500

def scrape_company_data(company_name):
    """Scrape additional data for a company (example function)"""
    try:
        # This is a mock scraping function - in real implementation, you'd scrape actual websites
        # For demonstration, we'll return mock data
        mock_data = {
            'website': f"https://{company_name.lower().replace(' ', '')}.com",
            'industry': 'Technology',
            'employees': '1000-5000',
            'revenue': '$10M-$50M',
            'location': 'San Francisco, CA',
            'founded': '2010',
            'description': f'{company_name} is a leading technology company.'
        }
        return mock_data
    except Exception as e:
        logger.error(f"Error scraping data for {company_name}: {e}")
        return {}

def process_data_etl(df, processing_options):
    """ETL processing function with specialized basketball cognitive data processing"""
    try:
        # Initialize processors
        stats_processor = StatisticalDataProcessor()
        cognitive_processor = BasketballCognitiveProcessor()
        
        # Check if this is basketball cognitive performance data
        detected = cognitive_processor.detect_cognitive_data(df)
        logger.info(f"detected_cognitive={detected} rows={len(df)} cols={list(df.columns)}")
        if detected:
            logger.info("Detected basketball cognitive performance data - using specialized processor")
            
            # Process with cognitive processor
            processed_df, performance_summary_df = cognitive_processor.process_cognitive_data(df, processing_options)
            
            # Save both the detailed data and performance summary
            output_filename = f"processed_cognitive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            processed_df.to_csv(output_path, index=False)
            
            # Save performance summary
            summary_filename = f"performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            summary_path = os.path.join(app.config['PROCESSED_FOLDER'], summary_filename)
            performance_summary_df.to_csv(summary_path, index=False)
            
            # Store summary path in attributes for template access
            processed_df.attrs['performance_summary_path'] = summary_path
            
            return processed_df, output_path
            
        else:
            # Use general statistical processor
            logger.info("Using general statistical data processor")
            processed_df = stats_processor.process_data(df, processing_options)
            
            # Add additional scraping if requested
            if processing_options.get('scrape_additional_data'):
                # Add scraped data for each row (using PLAYER column if available, otherwise first column)
                scraped_data = []
                for index, row in processed_df.iterrows():
                    try:
                        # Try to use PLAYER column first, fallback to first column
                        if 'PLAYER' in row.index and pd.notna(row['PLAYER']):
                            identifier = str(row['PLAYER'])
                        elif len(row) > 0:
                            identifier = str(row.iloc[0])
                        else:
                            identifier = f"Entry_{index}"
                        
                        scraped_info = scrape_company_data(identifier)
                        scraped_data.append(scraped_info)
                    except Exception as e:
                        # If there's any error, add empty data
                        scraped_data.append({})
                
                # Add scraped data as new columns
                if scraped_data:
                    scraped_df = pd.DataFrame(scraped_data)
                    processed_df = pd.concat([processed_df, scraped_df], axis=1)
            
            # Load: Save processed data
            output_filename = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            processed_df.to_csv(output_path, index=False)
            
            return processed_df, output_path
        
    except Exception as e:
        logger.error(f"Error in ETL processing: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/heat-theme-demo')
def heat_theme_demo():
    """Miami Heat Professional Theme Demo"""
    return render_template('heat_theme_demo.html')

@app.route('/healthz')
def healthz():
    """Lightweight health check endpoint for cloud platforms."""
    return jsonify({'status': 'ok'}), 200

@app.route('/settings')
def settings():
    """Application Settings"""
    return render_template('settings.html')

# -----------------------------
# Games UI (Index + Detail)
# -----------------------------

@app.route('/games')
def games_index():
    """Games index page - Heat themed with filters and game cards.
    Uses mock data initially; will be wired to DatabaseManager.list_games.
    """
    # Mock data structure for initial UI wiring
    mock_games = [
        {
            'id': 1,
            'game_date': int(datetime(2025, 10, 6).timestamp()),
            'team': 'Heat',
            'opponent': 'Bucks',
            'is_home': True,
            'team_score': 66,
            'player_scorecards_count': 8,
        },
        {
            'id': 2,
            'game_date': int(datetime(2025, 10, 4).timestamp()),
            'team': 'Heat',
            'opponent': 'Magic',
            'is_home': False,
            'team_score': 72,
            'player_scorecards_count': 10,
        },
    ]
    return render_template('games.html', games=mock_games)


@app.route('/games/<int:game_id>')
def game_detail(game_id: int):
    """Game detail page - Shows team scorecard and player performances.
    Uses mock data initially; will be wired to DatabaseManager.get_game.
    """
    # Mock detail payload
    mock = {
        'meta': {
            'id': game_id,
            'game_date': int(datetime(2025, 10, 6).timestamp()),
            'team': 'Heat',
            'opponent': 'Bucks',
            'is_home': True,
            'venue': 'Kaseya Center',
            'final_score_team': 110,
            'final_score_opp': 105,
        },
        'teamScorecard': {
            'score': 66,
            'source': 'csv',
            'note': 'Auto-calculated from CSV',
        },
        'playerScorecards': [
            {'player_name': 'Jimmy Butler', 'bars': [], 'totals': {'positive': 24, 'negative': 8}},
            {'player_name': 'Bam Adebayo', 'bars': [], 'totals': {'positive': 20, 'negative': 6}},
            {'player_name': 'Tyler Herro', 'bars': [], 'totals': {'positive': 18, 'negative': 9}},
        ],
        'roster': [
            {'player_name': 'Jimmy Butler', 'status': 'active', 'minutes': 34, 'points': 22, 'rebounds': 6, 'assists': 5},
            {'player_name': 'Bam Adebayo', 'status': 'active', 'minutes': 36, 'points': 24, 'rebounds': 11, 'assists': 4},
            {'player_name': 'Tyler Herro', 'status': 'active', 'minutes': 31, 'points': 19, 'rebounds': 4, 'assists': 3},
        ],
    }

    return render_template('game_detail.html', game=mock)

@app.route('/scorecard')
def scorecard():
    """ScoreCard dashboard route"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    return render_template('scorecard.html', latest_file=latest_file)

@app.route('/scorecard/<filename>')
def scorecard_with_data(filename):
    """ScoreCard dashboard with specific data file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('scorecard'))
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Extract performance data using the basketball cognitive processor
        processor = BasketballCognitiveProcessor()
        performance_data = processor.extract_performance_data(df)
        
        # Get the original CSV filename for display
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        
        return render_template('scorecard.html', 
                             filename=filename,
                             original_filename=original_filename,
                             performance_data=performance_data,
                             df=df)
        
    except Exception as e:
        flash(f'Error loading data: {str(e)}')
        return redirect(url_for('scorecard'))

@app.route('/scorecard-plus')
def scorecard_plus():
    """ScoreCard Plus comprehensive dashboard route"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    return render_template('scorecard_plus.html', latest_file=latest_file)

## Removed duplicate handlers for /scorecard-plus/<filename> and refresh.
## Blueprint `dashboard_bp` owns those endpoints.

@app.route('/players')
def players():
    """Player management page"""
    return render_template('players.html')

@app.route('/player-management')
def player_management():
    # Prefer the blueprint route for the main dashboard page
    return redirect(url_for('player_dashboard.player_management_dashboard'))
def players():
    """Player management page"""
    return render_template('players.html')

@app.route('/smartdash')
def smartdash():
    """SmartDash dashboard route"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    # Check if a specific file was requested
    requested_file = request.args.get('file')
    if requested_file and requested_file in processed_files:
        return redirect(url_for('smartdash_with_data', filename=requested_file))
    
    # Get all players for the dropdown
    db_manager = DatabaseManager(app.config['DB_PATH'])
    # Ensure database has required columns
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(scorecards)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Add space_read_live_dribble if missing
            if "space_read_live_dribble" not in columns:
                cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble INTEGER DEFAULT 0")
                print("Added space_read_live_dribble column")
            
            # Add space_read_catch if missing
            if "space_read_catch" not in columns:
                cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch INTEGER DEFAULT 0")
                print("Added space_read_catch column")
            
            conn.commit()
            print("Database migration completed successfully")
    except Exception as e:
        print(f"Error during database migration: {e}")
    players = db_manager.get_all_players()
    
    return render_template('smartdash.html', 
                         latest_file=latest_file, 
                         processed_files=processed_files,
                         players=players)

@app.route('/smartdash/<filename>')
def smartdash_with_data(filename):
    """SmartDash dashboard with specific data file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('smartdash'))
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Extract smart dashboard metrics using the basketball cognitive processor
        processor = BasketballCognitiveProcessor()
        smart_metrics = processor.calculate_smart_dashboard_metrics(df)
        
        # Get the flattened tally table
        flattened_tally = processor.create_flattened_tally_table(df)
        
        # Get the original CSV filename for display
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        
        return render_template('smartdash.html', 
                             filename=filename,
                             original_filename=original_filename,
                             smart_metrics=smart_metrics,
                             flattened_tally=flattened_tally,
                             df=df)
        
    except Exception as e:
        flash(f'Error loading data: {str(e)}')
        return redirect(url_for('smartdash'))

@app.route('/player-bars/<filename>')
def player_bars(filename):
    """Player All-in-One Bars dashboard for a processed file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('smartdash'))

        df = pd.read_csv(file_path)
        processor = BasketballCognitiveProcessor()
        stat_bars = processor.build_stat_bars(df)

        return render_template('player_bar_dashboard.html',
                               filename=filename,
                               stat_bars=stat_bars)
    except Exception as e:
        flash(f'Error loading player bars: {str(e)}')
        return redirect(url_for('smartdash'))

@app.route('/smartdash-upload', methods=['POST'])
def smartdash_upload():
    """Handle file upload specifically for SmartDash with results table"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('smartdash'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('smartdash'))
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Load the file
            try:
                df = load_csv_file(file_path)
            except Exception as ex:
                if file_path.lower().endswith('.csv'):
                    try:
                        df = pd.read_csv(file_path, encoding='latin-1')
                    except Exception as ex2:
                        flash(f'Failed to read CSV: {ex2}')
                        return redirect(url_for('smartdash'))
                else:
                    flash(f'Failed to read file: {ex}')
                    return redirect(url_for('smartdash'))
            
            # Get processing options
            processing_options = {
                'remove_duplicates': request.form.get('remove_duplicates') == 'on',
                'fill_missing': request.form.get('fill_missing') == 'on',
                'add_timestamp': request.form.get('add_timestamp') == 'on',
                'scrape_additional_data': False  # Disable for SmartDash
            }
            
            # Process the data
            processed_df, output_path = process_data_etl(df, processing_options)
            
            # Convert to JSON for display (same as main upload)
            data_json = processed_df.to_json(orient='records', date_format='iso')
            
            # Get data type and summary statistics
            data_type = getattr(processed_df, 'attrs', {}).get('data_type', 'general_stats')
            summary_stats = getattr(processed_df, 'attrs', {}).get('summary_stats', {})
            completeness = summary_stats.get('completeness_percentage', 100)
            performance_summary_path = getattr(processed_df, 'attrs', {}).get('performance_summary_path', None)
            
            # Check if this is basketball cognitive data
            processor = BasketballCognitiveProcessor()
            is_cognitive_data = processor.detect_cognitive_data(processed_df)
            
            if is_cognitive_data:
                data_type = 'basketball_cognitive_performance'
            
            flash('File uploaded and processed successfully!')
            
            # Get all players for the dropdown - using configured absolute database path
            db_manager = DatabaseManager(app.config['DB_PATH'])
            
            # Extract game metadata and create/get game
            game_id = None
            if 'Timeline' in processed_df.columns and len(processed_df) > 0:
                from src.utils.game_id_generator import parse_game_metadata
                timeline_value = processed_df['Timeline'].iloc[0]
                date_string, team, opponent = parse_game_metadata(str(timeline_value))
                if date_string and opponent:
                    game = db_manager.get_or_create_game(date_string, opponent, team or "Heat")
                    if game:
                        game_id = game.id
            
            # Ensure database has required columns
            try:
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(scorecards)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    # Add space_read_live_dribble if missing
                    if "space_read_live_dribble" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble INTEGER DEFAULT 0")
                        print("Added space_read_live_dribble column")
                    
                    # Add space_read_catch if missing
                    if "space_read_catch" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch INTEGER DEFAULT 0")
                        print("Added space_read_catch column")
                    
                    # Add driving_paint_touch_positive if missing
                    if "driving_paint_touch_positive" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_positive INTEGER DEFAULT 0")
                        print("Added driving_paint_touch_positive column")
                    
                    # Add driving_paint_touch_negative if missing
                    if "driving_paint_touch_negative" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_negative INTEGER DEFAULT 0")
                        print("Added driving_paint_touch_negative column")
                    
                    # Add driving_physicality_positive if missing
                    if "driving_physicality_positive" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_positive INTEGER DEFAULT 0")
                        print("Added driving_physicality_positive column")
                    
                    # Add driving_physicality_negative if missing
                    if "driving_physicality_negative" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_negative INTEGER DEFAULT 0")
                        print("Added driving_physicality_negative column")
                    
                    conn.commit()
                    print("Database migration completed successfully")
            except Exception as e:
                print(f"Error during database migration: {e}")
            
            players = db_manager.get_all_players()
            
            return render_template('smartdash_results.html', 
                                 data=json.loads(data_json),
                                 columns=processed_df.columns.tolist(),
                                 filename=filename,
                                 output_path=output_path,
                                 data_type=data_type,
                                 completeness=completeness,
                                 summary_stats=summary_stats,
                                 performance_summary_path=performance_summary_path,
                                 players=players,
                                 game_id=game_id)
    
        except Exception as e:
            logger.exception("Error processing SmartDash upload")
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('smartdash'))
    
    flash('Invalid file type. Please upload a CSV or Excel file.')
    return redirect(url_for('smartdash'))

@app.route('/create-scorecard', methods=['POST'])
def create_scorecard():
    """Create a new scorecard for a selected player"""
    print("🔧 DEBUG: Starting scorecard creation...")
    try:
        from src.models.scorecard import Scorecard
        
        # Get form data
        # Accept either the select field (preferred) or legacy 'player_name'
        player_name = request.form.get('player_name') or request.form.get('player_dropdown') or request.form.get('player_name_display')
        print(f"🔧 DEBUG: Form data received - player_name: '{player_name}'")
        print(f"🔧 DEBUG: All form keys: {list(request.form.keys())}")
        
        date_created = int(datetime.now().timestamp())
        print(f"🔧 DEBUG: Date created: {date_created}")
        game_id = request.form.get('game_id')  # Optional game_id
        space_read_live_dribble = int(request.form.get('space_read_live_dribble', 0))
        space_read_catch = int(request.form.get('space_read_catch', 0))
        space_read_live_dribble_negative = int(request.form.get('space_read_live_dribble_negative', 0))
        space_read_catch_negative = int(request.form.get('space_read_catch_negative', 0))
        dm_catch_back_to_back_positive = int(request.form.get('dm_catch_back_to_back_positive', 0))
        dm_catch_back_to_back_negative = int(request.form.get('dm_catch_back_to_back_negative', 0))
        dm_catch_uncontested_shot_positive = int(request.form.get('dm_catch_uncontested_shot_positive', 0))
        dm_catch_uncontested_shot_negative = int(request.form.get('dm_catch_uncontested_shot_negative', 0))
        dm_catch_swing_positive = int(request.form.get('dm_catch_swing_positive', 0))
        dm_catch_swing_negative = int(request.form.get('dm_catch_swing_negative', 0))
        dm_catch_drive_pass_positive = int(request.form.get('dm_catch_drive_pass_positive', 0))
        dm_catch_drive_pass_negative = int(request.form.get('dm_catch_drive_pass_negative', 0))
        dm_catch_drive_swing_skip_pass_positive = int(request.form.get('dm_catch_drive_swing_skip_pass_positive', 0))
        dm_catch_drive_swing_skip_pass_negative = int(request.form.get('dm_catch_drive_swing_skip_pass_negative', 0))
        qb12_strong_side_positive = int(request.form.get('qb12_strong_side_positive', 0))
        qb12_strong_side_negative = int(request.form.get('qb12_strong_side_negative', 0))
        qb12_baseline_positive = int(request.form.get('qb12_baseline_positive', 0))
        qb12_baseline_negative = int(request.form.get('qb12_baseline_negative', 0))
        qb12_fill_behind_positive = int(request.form.get('qb12_fill_behind_positive', 0))
        qb12_fill_behind_negative = int(request.form.get('qb12_fill_behind_negative', 0))
        qb12_weak_side_positive = int(request.form.get('qb12_weak_side_positive', 0))
        qb12_weak_side_negative = int(request.form.get('qb12_weak_side_negative', 0))
        qb12_roller_positive = int(request.form.get('qb12_roller_positive', 0))
        qb12_roller_negative = int(request.form.get('qb12_roller_negative', 0))
        qb12_skip_pass_positive = int(request.form.get('qb12_skip_pass_positive', 0))
        qb12_skip_pass_negative = int(request.form.get('qb12_skip_pass_negative', 0))
        qb12_cutter_positive = int(request.form.get('qb12_cutter_positive', 0))
        qb12_cutter_negative = int(request.form.get('qb12_cutter_negative', 0))
        driving_paint_touch_positive = int(request.form.get('driving_paint_touch_positive', 0))
        driving_paint_touch_negative = int(request.form.get('driving_paint_touch_negative', 0))
        driving_physicality_positive = int(request.form.get('driving_physicality_positive', 0))
        driving_physicality_negative = int(request.form.get('driving_physicality_negative', 0))
        # Off Ball - Positioning
        offball_positioning_create_shape_positive = int(request.form.get('offball_positioning_create_shape_positive', 0))
        offball_positioning_create_shape_negative = int(request.form.get('offball_positioning_create_shape_negative', 0))
        offball_positioning_adv_awareness_positive = int(request.form.get('offball_positioning_adv_awareness_positive', 0))
        offball_positioning_adv_awareness_negative = int(request.form.get('offball_positioning_adv_awareness_negative', 0))
        # Off Ball - Transition
        transition_effort_pace_positive = int(request.form.get('transition_effort_pace_positive', 0))
        transition_effort_pace_negative = int(request.form.get('transition_effort_pace_negative', 0))
        # Cutting & Screening
        cs_denial_positive = int(request.form.get('cs_denial_positive', 0))
        cs_denial_negative = int(request.form.get('cs_denial_negative', 0))
        cs_movement_positive = int(request.form.get('cs_movement_positive', 0))
        cs_movement_negative = int(request.form.get('cs_movement_negative', 0))
        cs_body_to_body_positive = int(request.form.get('cs_body_to_body_positive', 0))
        cs_body_to_body_negative = int(request.form.get('cs_body_to_body_negative', 0))
        cs_screen_principle_positive = int(request.form.get('cs_screen_principle_positive', 0))
        cs_screen_principle_negative = int(request.form.get('cs_screen_principle_negative', 0))
        cs_cut_fill_positive = int(request.form.get('cs_cut_fill_positive', 0))
        cs_cut_fill_negative = int(request.form.get('cs_cut_fill_negative', 0))
        # Relocation
        relocation_weak_corner_positive = int(request.form.get('relocation_weak_corner_positive', 0))
        relocation_weak_corner_negative = int(request.form.get('relocation_weak_corner_negative', 0))
        relocation_45_cut_positive = int(request.form.get('relocation_45_cut_positive', 0))
        relocation_45_cut_negative = int(request.form.get('relocation_45_cut_negative', 0))
        relocation_slide_away_positive = int(request.form.get('relocation_slide_away_positive', 0))
        relocation_slide_away_negative = int(request.form.get('relocation_slide_away_negative', 0))
        relocation_fill_behind_positive = int(request.form.get('relocation_fill_behind_positive', 0))
        relocation_fill_behind_negative = int(request.form.get('relocation_fill_behind_negative', 0))
        relocation_dunker_baseline_positive = int(request.form.get('relocation_dunker_baseline_positive', 0))
        relocation_dunker_baseline_negative = int(request.form.get('relocation_dunker_baseline_negative', 0))
        relocation_corner_fill_positive = int(request.form.get('relocation_corner_fill_positive', 0))
        relocation_corner_fill_negative = int(request.form.get('relocation_corner_fill_negative', 0))
        relocation_reverse_direction_positive = int(request.form.get('relocation_reverse_direction_positive', 0))
        relocation_reverse_direction_negative = int(request.form.get('relocation_reverse_direction_negative', 0))
        
        if not player_name:
            print("🚨 DEBUG: No player name provided!")
            flash('Please select a player')
            return redirect(url_for('smartdash'))
        
        print(f"🔧 DEBUG: Creating scorecard for player: {player_name}")
        print(f"🔧 DEBUG: Sample metrics - space_read_live_dribble: {space_read_live_dribble}, dm_catch_back_to_back_positive: {dm_catch_back_to_back_positive}")
        
        # Create scorecard with new attributes
        scorecard = Scorecard(
            player_name=player_name, 
            date_created=date_created,
            game_id=game_id,
            space_read_live_dribble=space_read_live_dribble,
            space_read_catch=space_read_catch,
            space_read_live_dribble_negative=space_read_live_dribble_negative,
            space_read_catch_negative=space_read_catch_negative,
            dm_catch_back_to_back_positive=dm_catch_back_to_back_positive,
            dm_catch_back_to_back_negative=dm_catch_back_to_back_negative,
            dm_catch_uncontested_shot_positive=dm_catch_uncontested_shot_positive,
            dm_catch_uncontested_shot_negative=dm_catch_uncontested_shot_negative,
            dm_catch_swing_positive=dm_catch_swing_positive,
            dm_catch_swing_negative=dm_catch_swing_negative,
            dm_catch_drive_pass_positive=dm_catch_drive_pass_positive,
            dm_catch_drive_pass_negative=dm_catch_drive_pass_negative,
            dm_catch_drive_swing_skip_pass_positive=dm_catch_drive_swing_skip_pass_positive,
            dm_catch_drive_swing_skip_pass_negative=dm_catch_drive_swing_skip_pass_negative,
            qb12_strong_side_positive=qb12_strong_side_positive,
            qb12_strong_side_negative=qb12_strong_side_negative,
            qb12_baseline_positive=qb12_baseline_positive,
            qb12_baseline_negative=qb12_baseline_negative,
            qb12_fill_behind_positive=qb12_fill_behind_positive,
            qb12_fill_behind_negative=qb12_fill_behind_negative,
            qb12_weak_side_positive=qb12_weak_side_positive,
            qb12_weak_side_negative=qb12_weak_side_negative,
            qb12_roller_positive=qb12_roller_positive,
            qb12_roller_negative=qb12_roller_negative,
            qb12_skip_pass_positive=qb12_skip_pass_positive,
            qb12_skip_pass_negative=qb12_skip_pass_negative,
            qb12_cutter_positive=qb12_cutter_positive,
            qb12_cutter_negative=qb12_cutter_negative,
            driving_paint_touch_positive=driving_paint_touch_positive,
            driving_paint_touch_negative=driving_paint_touch_negative,
            driving_physicality_positive=driving_physicality_positive,
            driving_physicality_negative=driving_physicality_negative,
            # Off Ball - Positioning
            offball_positioning_create_shape_positive=offball_positioning_create_shape_positive,
            offball_positioning_create_shape_negative=offball_positioning_create_shape_negative,
            offball_positioning_adv_awareness_positive=offball_positioning_adv_awareness_positive,
            offball_positioning_adv_awareness_negative=offball_positioning_adv_awareness_negative,
            # Off Ball - Transition
            transition_effort_pace_positive=transition_effort_pace_positive,
            transition_effort_pace_negative=transition_effort_pace_negative,
            # Cutting & Screening
            cs_denial_positive=cs_denial_positive,
            cs_denial_negative=cs_denial_negative,
            cs_movement_positive=cs_movement_positive,
            cs_movement_negative=cs_movement_negative,
            cs_body_to_body_positive=cs_body_to_body_positive,
            cs_body_to_body_negative=cs_body_to_body_negative,
            cs_screen_principle_positive=cs_screen_principle_positive,
            cs_screen_principle_negative=cs_screen_principle_negative,
            cs_cut_fill_positive=cs_cut_fill_positive,
            cs_cut_fill_negative=cs_cut_fill_negative,
            # Relocation
            relocation_weak_corner_positive=relocation_weak_corner_positive,
            relocation_weak_corner_negative=relocation_weak_corner_negative,
            relocation_45_cut_positive=relocation_45_cut_positive,
            relocation_45_cut_negative=relocation_45_cut_negative,
            relocation_slide_away_positive=relocation_slide_away_positive,
            relocation_slide_away_negative=relocation_slide_away_negative,
            relocation_fill_behind_positive=relocation_fill_behind_positive,
            relocation_fill_behind_negative=relocation_fill_behind_negative,
            relocation_dunker_baseline_positive=relocation_dunker_baseline_positive,
            relocation_dunker_baseline_negative=relocation_dunker_baseline_negative,
            relocation_corner_fill_positive=relocation_corner_fill_positive,
            relocation_corner_fill_negative=relocation_corner_fill_negative,
            relocation_reverse_direction_positive=relocation_reverse_direction_positive,
            relocation_reverse_direction_negative=relocation_reverse_direction_negative,
        )
        
        print("🔧 DEBUG: Scorecard object created successfully")
        
        # Save to database (use absolute path to avoid env-dependent issues)
        db_path = app.config['DB_PATH']
        print(f"🔧 DEBUG: Using database path: {db_path}")
        # Ensure data directory exists before connecting
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        except Exception as e:
            print(f"🚨 DEBUG: Failed to ensure DB directory exists: {e}")
        db_manager = DatabaseManager(db_path)
        # Ensure database has required columns
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(scorecards)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Add space_read_live_dribble if missing
                if "space_read_live_dribble" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble INTEGER DEFAULT 0")
                    print("Added space_read_live_dribble column")
                
                # Add space_read_catch if missing
                if "space_read_catch" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch INTEGER DEFAULT 0")
                    print("Added space_read_catch column")
                
                # Add space_read_live_dribble_negative if missing
                if "space_read_live_dribble_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble_negative INTEGER DEFAULT 0")
                    print("Added space_read_live_dribble_negative column")
                
                # Add space_read_catch_negative if missing
                if "space_read_catch_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch_negative INTEGER DEFAULT 0")
                    print("Added space_read_catch_negative column")
                
                # Add DM Catch columns if missing
                if "dm_catch_back_to_back_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_back_to_back_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_back_to_back_positive column")
                
                if "dm_catch_back_to_back_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_back_to_back_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_back_to_back_negative column")
                
                if "dm_catch_uncontested_shot_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_uncontested_shot_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_uncontested_shot_positive column")
                
                if "dm_catch_uncontested_shot_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_uncontested_shot_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_uncontested_shot_negative column")
                
                if "dm_catch_swing_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_swing_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_swing_positive column")
                
                if "dm_catch_swing_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_swing_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_swing_negative column")
                
                if "dm_catch_drive_pass_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_pass_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_pass_positive column")
                
                if "dm_catch_drive_pass_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_pass_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_pass_negative column")
                
                if "dm_catch_drive_swing_skip_pass_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_swing_skip_pass_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_swing_skip_pass_positive column")
                
                if "dm_catch_drive_swing_skip_pass_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_swing_skip_pass_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_swing_skip_pass_negative column")

                # Add QB12 columns if missing
                if "qb12_strong_side_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_strong_side_positive INTEGER DEFAULT 0")
                    print("Added qb12_strong_side_positive column")
                if "qb12_strong_side_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_strong_side_negative INTEGER DEFAULT 0")
                    print("Added qb12_strong_side_negative column")
                if "qb12_baseline_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_baseline_positive INTEGER DEFAULT 0")
                    print("Added qb12_baseline_positive column")
                if "qb12_baseline_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_baseline_negative INTEGER DEFAULT 0")
                    print("Added qb12_baseline_negative column")
                if "qb12_fill_behind_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_fill_behind_positive INTEGER DEFAULT 0")
                    print("Added qb12_fill_behind_positive column")
                if "qb12_fill_behind_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_fill_behind_negative INTEGER DEFAULT 0")
                    print("Added qb12_fill_behind_negative column")
                if "qb12_weak_side_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_weak_side_positive INTEGER DEFAULT 0")
                    print("Added qb12_weak_side_positive column")
                if "qb12_weak_side_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_weak_side_negative INTEGER DEFAULT 0")
                    print("Added qb12_weak_side_negative column")
                if "qb12_roller_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_roller_positive INTEGER DEFAULT 0")
                    print("Added qb12_roller_positive column")
                if "qb12_roller_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_roller_negative INTEGER DEFAULT 0")
                    print("Added qb12_roller_negative column")
                if "qb12_skip_pass_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_skip_pass_positive INTEGER DEFAULT 0")
                    print("Added qb12_skip_pass_positive column")
                if "qb12_skip_pass_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_skip_pass_negative INTEGER DEFAULT 0")
                    print("Added qb12_skip_pass_negative column")
                if "qb12_cutter_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_cutter_positive INTEGER DEFAULT 0")
                    print("Added qb12_cutter_positive column")
                if "qb12_cutter_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_cutter_negative INTEGER DEFAULT 0")
                    print("Added qb12_cutter_negative column")
                
                # Add driving_paint_touch_positive if missing
                if "driving_paint_touch_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_positive INTEGER DEFAULT 0")
                    print("Added driving_paint_touch_positive column")
                
                # Add driving_paint_touch_negative if missing
                if "driving_paint_touch_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_negative INTEGER DEFAULT 0")
                    print("Added driving_paint_touch_negative column")
                
                # Add driving_physicality_positive if missing
                if "driving_physicality_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_positive INTEGER DEFAULT 0")
                    print("Added driving_physicality_positive column")
                
                # Add driving_physicality_negative if missing
                if "driving_physicality_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_negative INTEGER DEFAULT 0")
                    print("Added driving_physicality_negative column")
                # Off Ball - Positioning
                if "offball_positioning_create_shape_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN offball_positioning_create_shape_positive INTEGER DEFAULT 0")
                if "offball_positioning_create_shape_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN offball_positioning_create_shape_negative INTEGER DEFAULT 0")
                if "offball_positioning_adv_awareness_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN offball_positioning_adv_awareness_positive INTEGER DEFAULT 0")
                if "offball_positioning_adv_awareness_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN offball_positioning_adv_awareness_negative INTEGER DEFAULT 0")
                # Off Ball - Transition
                if "transition_effort_pace_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN transition_effort_pace_positive INTEGER DEFAULT 0")
                if "transition_effort_pace_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN transition_effort_pace_negative INTEGER DEFAULT 0")
                # Cutting & Screening
                if "cs_denial_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_denial_positive INTEGER DEFAULT 0")
                if "cs_denial_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_denial_negative INTEGER DEFAULT 0")
                if "cs_movement_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_movement_positive INTEGER DEFAULT 0")
                if "cs_movement_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_movement_negative INTEGER DEFAULT 0")
                if "cs_body_to_body_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_body_to_body_positive INTEGER DEFAULT 0")
                if "cs_body_to_body_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_body_to_body_negative INTEGER DEFAULT 0")
                if "cs_screen_principle_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_screen_principle_positive INTEGER DEFAULT 0")
                if "cs_screen_principle_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_screen_principle_negative INTEGER DEFAULT 0")
                if "cs_cut_fill_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_cut_fill_positive INTEGER DEFAULT 0")
                if "cs_cut_fill_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN cs_cut_fill_negative INTEGER DEFAULT 0")
                # Relocation
                if "relocation_weak_corner_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_weak_corner_positive INTEGER DEFAULT 0")
                if "relocation_weak_corner_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_weak_corner_negative INTEGER DEFAULT 0")
                if "relocation_45_cut_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_45_cut_positive INTEGER DEFAULT 0")
                if "relocation_45_cut_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_45_cut_negative INTEGER DEFAULT 0")
                if "relocation_slide_away_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_slide_away_positive INTEGER DEFAULT 0")
                if "relocation_slide_away_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_slide_away_negative INTEGER DEFAULT 0")
                if "relocation_fill_behind_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_fill_behind_positive INTEGER DEFAULT 0")
                if "relocation_fill_behind_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_fill_behind_negative INTEGER DEFAULT 0")
                if "relocation_dunker_baseline_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_dunker_baseline_positive INTEGER DEFAULT 0")
                if "relocation_dunker_baseline_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_dunker_baseline_negative INTEGER DEFAULT 0")
                if "relocation_corner_fill_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_corner_fill_positive INTEGER DEFAULT 0")
                if "relocation_corner_fill_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_corner_fill_negative INTEGER DEFAULT 0")
                if "relocation_reverse_direction_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_reverse_direction_positive INTEGER DEFAULT 0")
                if "relocation_reverse_direction_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN relocation_reverse_direction_negative INTEGER DEFAULT 0")
                
                conn.commit()
                print("🔧 DEBUG: Database migration completed successfully")
        except Exception as e:
            print(f"🚨 DEBUG: Error during database migration: {e}")
        
        print("🔧 DEBUG: Starting scorecard creation in database...")
        success = db_manager.create_scorecard(scorecard)
        print(f"🔧 DEBUG: Scorecard creation result: {success}")
        
        if success:
            print(f"✅ DEBUG: Success! Scorecard created for {player_name}")
            flash(f'Scorecard created successfully for {player_name}!')
        else:
            print(f"❌ DEBUG: Failed to create scorecard for {player_name}")
            flash(f'Failed to create scorecard for {player_name}')
        
        print("🔧 DEBUG: Redirecting to smartdash...")
        return redirect(url_for('smartdash'))
        
    except Exception as e:
        print(f"🚨 DEBUG: Exception caught in create_scorecard: {e}")
        logger.error(f"Error creating scorecard: {e}")
        flash(f'Error creating scorecard: {str(e)}')
        return redirect(url_for('smartdash'))

@app.route('/autofill-scorecard', methods=['POST'])
def autofill_scorecard():
    """Autofill scorecard attributes from uploaded data"""
    try:
        from src.processors.scorecard_autofill_processor import ScorecardAutofillProcessor
        
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
            file.save(file_path)
            
            # Load the file
            df = load_csv_file(file_path)
            
            # Process with autofill processor
            processor = ScorecardAutofillProcessor()
            autofill_data = processor.autofill_scorecard_attributes(df)
            
            # Clean up temp file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'autofill_data': autofill_data
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error in autofill: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Load the file
            df = load_csv_file(file_path)
            
            # Get processing options
            processing_options = {
                'remove_duplicates': request.form.get('remove_duplicates') == 'on',
                'fill_missing': request.form.get('fill_missing') == 'on',
                'add_timestamp': request.form.get('add_timestamp') == 'on',
                'scrape_additional_data': request.form.get('scrape_additional_data') == 'on'
            }
            
            # Process the data
            processed_df, output_path = process_data_etl(df, processing_options)
            
            # Convert to JSON for display
            data_json = processed_df.to_json(orient='records', date_format='iso')
            
            # Get data type and summary statistics
            data_type = getattr(processed_df, 'attrs', {}).get('data_type', 'general_stats')
            summary_stats = getattr(processed_df, 'attrs', {}).get('summary_stats', {})
            completeness = summary_stats.get('completeness_percentage', 100)
            performance_summary_path = getattr(processed_df, 'attrs', {}).get('performance_summary_path', None)
            
            flash('File uploaded and processed successfully!')
            return render_template('results.html', 
                                 data=json.loads(data_json),
                                 columns=processed_df.columns.tolist(),
                                 filename=filename,
                                 output_path=output_path,
                                 data_type=data_type,
                                 completeness=completeness,
                                 summary_stats=summary_stats,
                                 performance_summary_path=performance_summary_path)
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for processing data"""
    try:
        data = request.get_json()
        csv_data = data.get('csv_data')
        processing_options = data.get('processing_options', {})
        
        # Convert CSV string to DataFrame
        df = pd.read_csv(pd.StringIO(csv_data))
        
        # Process the data
        processed_df, output_path = process_data_etl(df, processing_options)
        
        return jsonify({
            'success': True,
            'data': processed_df.to_dict('records'),
            'columns': processed_df.columns.tolist(),
            'output_path': output_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081) 