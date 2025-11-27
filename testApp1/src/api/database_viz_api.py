"""
Database Visualization API
Provides endpoints for visualizing game and player data from the database.
"""

from flask import Blueprint, jsonify, request, send_file
import logging
from src.database.db_manager import DatabaseManager
from src.processors.csv_to_database_importer import CSVToDatabaseImporter
from src.services.pdf_export_service import PDFExportService
import os
import io
from datetime import datetime

logger = logging.getLogger(__name__)

database_viz_api = Blueprint('database_viz_api', __name__)


@database_viz_api.route('/api/database-viz/games', methods=['GET'])
def get_games():
    """
    Get all games with aggregated stats and SQL query.
    
    Returns:
        JSON with games list, SQL query used, and success status
    """
    try:
        from flask import current_app
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        
        games = db_manager.get_games_with_stats()
        
        # Get the SQL query that was used
        sql_query = """
        SELECT 
            g.id as game_id,
            g.date,
            g.date_string,
            g.opponent,
            g.team,
            g.created_at,
            COUNT(DISTINCT s.player_name) as player_count,
            COUNT(s.id) as scorecard_count
        FROM games g
        LEFT JOIN scorecards s ON g.id = s.game_id
        GROUP BY g.id
        ORDER BY g.date DESC
        """
        
        return jsonify({
            'success': True,
            'games': games,
            'sql_query': sql_query,
            'count': len(games)
        })
    except Exception as e:
        logger.exception("Error fetching games")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/games/<game_id>', methods=['GET'])
def get_game_by_id(game_id):
    """
    Get specific game with players array and stats.
    
    Args:
        game_id: The game ID
        
    Returns:
        JSON with game details, players array, and stats
    """
    try:
        from flask import current_app
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        
        game_data = db_manager.get_game_with_players(game_id)
        
        if not game_data:
            return jsonify({
                'success': False,
                'error': 'Game not found'
            }), 404
        
        # Get the SQL query that was used
        sql_query = f"""
        -- Get game details
        SELECT * FROM games WHERE id = '{game_id}';
        
        -- Get players and their scorecards for this game
        SELECT 
            p.name,
            s.*
        FROM players p
        INNER JOIN scorecards s ON p.name = s.player_name
        WHERE s.game_id = '{game_id}'
        ORDER BY p.name;
        """
        
        return jsonify({
            'success': True,
            'game': game_data,
            'sql_query': sql_query
        })
    except Exception as e:
        logger.exception(f"Error fetching game {game_id}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/players', methods=['GET'])
def get_players():
    """
    Get all players with game_id and stats.
    
    Query params:
        game_id (optional): Filter by game ID
        
    Returns:
        JSON with players list and SQL query
    """
    try:
        from flask import current_app
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        
        game_id = request.args.get('game_id')
        
        if game_id:
            players = db_manager.get_players_by_game(game_id)
            sql_query = f"""
            SELECT 
                p.name,
                s.*
            FROM players p
            INNER JOIN scorecards s ON p.name = s.player_name
            WHERE s.game_id = '{game_id}'
            ORDER BY p.name;
            """
        else:
            # Get all players with their scorecards
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        p.name,
                        p.date_created,
                        COUNT(s.id) as scorecard_count
                    FROM players p
                    LEFT JOIN scorecards s ON p.name = s.player_name
                    GROUP BY p.name
                    ORDER BY p.name
                ''')
                rows = cursor.fetchall()
                players = []
                for row in rows:
                    players.append({
                        'name': row[0],
                        'date_created': row[1],
                        'scorecard_count': row[2]
                    })
            
            sql_query = """
            SELECT 
                p.name,
                p.date_created,
                COUNT(s.id) as scorecard_count
            FROM players p
            LEFT JOIN scorecards s ON p.name = s.player_name
            GROUP BY p.name
            ORDER BY p.name;
            """
        
        return jsonify({
            'success': True,
            'players': players,
            'sql_query': sql_query,
            'count': len(players)
        })
    except Exception as e:
        logger.exception("Error fetching players")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/players/<game_id>', methods=['GET'])
def get_players_by_game(game_id):
    """
    Get players for a specific game.
    
    Args:
        game_id: The game ID
        
    Returns:
        JSON with players list and their stats for the game
    """
    try:
        from flask import current_app
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        
        players = db_manager.get_players_by_game(game_id)
        
        sql_query = f"""
        SELECT 
            p.name,
            s.*
        FROM players p
        INNER JOIN scorecards s ON p.name = s.player_name
        WHERE s.game_id = '{game_id}'
        ORDER BY p.name;
        """
        
        return jsonify({
            'success': True,
            'players': players,
            'sql_query': sql_query,
            'count': len(players),
            'game_id': game_id
        })
    except Exception as e:
        logger.exception(f"Error fetching players for game {game_id}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/sql/games', methods=['GET'])
def get_games_sql():
    """
    Get the SQL query used for fetching games.
    
    Returns:
        JSON with SQL query string
    """
    sql_query = """
    SELECT 
        g.id as game_id,
        g.date,
        g.date_string,
        g.opponent,
        g.team,
        g.created_at,
        COUNT(DISTINCT s.player_name) as player_count,
        COUNT(s.id) as scorecard_count
    FROM games g
    LEFT JOIN scorecards s ON g.id = s.game_id
    GROUP BY g.id
    ORDER BY g.date DESC;
    """
    
    return jsonify({
        'success': True,
        'sql_query': sql_query,
        'description': 'SQL query to fetch all games with aggregated player and scorecard counts'
    })


@database_viz_api.route('/api/database-viz/sql/players', methods=['GET'])
def get_players_sql():
    """
    Get the SQL query used for fetching players.
    
    Returns:
        JSON with SQL query string
    """
    sql_query = """
    -- Get all players with scorecard counts
    SELECT 
        p.name,
        p.date_created,
        COUNT(s.id) as scorecard_count
    FROM players p
    LEFT JOIN scorecards s ON p.name = s.player_name
    GROUP BY p.name
    ORDER BY p.name;
    
    -- Get players for a specific game
    SELECT 
        p.name,
        s.*
    FROM players p
    INNER JOIN scorecards s ON p.name = s.player_name
    WHERE s.game_id = :game_id
    ORDER BY p.name;
    """
    
    return jsonify({
        'success': True,
        'sql_query': sql_query,
        'description': 'SQL queries to fetch players with their scorecards'
    })


@database_viz_api.route('/api/database-viz/import-test-csvs', methods=['POST'])
def import_test_csvs():
    """
    Import test CSV files into the database.
    
    Returns:
        JSON with import results (processed, skipped, errors)
    """
    try:
        from flask import current_app
        
        # Get test_csvs directory
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        test_csvs_dir = os.path.join(current_file_dir, '..', '..', 'testcases', 'test_csvs')
        test_csvs_dir = os.path.abspath(test_csvs_dir)
        
        if not os.path.exists(test_csvs_dir):
            return jsonify({
                'success': False,
                'error': f'Test CSV directory not found: {test_csvs_dir}'
            }), 404
        
        # Get all CSV files
        csv_files = [f for f in os.listdir(test_csvs_dir) 
                     if f.endswith('.csv') and not f.startswith('.')]
        
        if not csv_files:
            return jsonify({
                'success': False,
                'error': 'No CSV files found in test directory'
            }), 404
        
        # Initialize importer
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        importer = CSVToDatabaseImporter(db_manager)
        
        processed = []
        skipped = []
        errors = []
        
        for csv_file in csv_files:
            csv_path = os.path.join(test_csvs_dir, csv_file)
            
            try:
                result = importer.import_csv(csv_path)
                
                if result['success']:
                    processed.append({
                        'filename': csv_file,
                        'game_id': result.get('game_id'),
                        'players_created': result.get('players_created', 0),
                        'scorecards_created': result.get('scorecards_created', 0)
                    })
                else:
                    if result.get('skipped'):
                        skipped.append({
                            'filename': csv_file,
                            'reason': result.get('message', 'Unknown reason')
                        })
                    else:
                        errors.append({
                            'filename': csv_file,
                            'error': result.get('error', 'Unknown error')
                        })
            except Exception as e:
                logger.exception(f"Error importing {csv_file}")
                errors.append({
                    'filename': csv_file,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'processed': processed,
            'skipped': skipped,
            'errors': errors,
            'total_files': len(csv_files),
            'processed_count': len(processed),
            'skipped_count': len(skipped),
            'error_count': len(errors)
        })
    except Exception as e:
        logger.exception("Error importing test CSVs")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/stats/aggregate/<game_id>', methods=['GET'])
def aggregate_game_stats(game_id):
    """
    Aggregate stats for a game from all players.
    
    Args:
        game_id: The game ID
        
    Returns:
        JSON with aggregated statistics
    """
    try:
        from flask import current_app
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        
        stats = db_manager.aggregate_game_stats(game_id)
        
        if not stats:
            return jsonify({
                'success': False,
                'error': 'Game not found or no stats available'
            }), 404
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'stats': stats
        })
    except Exception as e:
        logger.exception(f"Error aggregating stats for game {game_id}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/upload-mega-csv', methods=['POST'])
def upload_mega_csv():
    """
    Upload and process a mega CSV file containing team and player data.
    
    Expects:
        - file: CSV file in multipart/form-data
        
    Returns:
        JSON with detailed processing results and notifications at each step
    """
    try:
        from flask import current_app
        from werkzeug.utils import secure_filename
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'notification': {
                    'type': 'error',
                    'message': 'Please select a CSV file to upload'
                }
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'notification': {
                    'type': 'error',
                    'message': 'No file selected'
                }
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Invalid file type',
                'notification': {
                    'type': 'error',
                    'message': 'Only CSV files are allowed'
                }
            }), 400
        
        # Save file temporarily
        uploads_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            '..', '..', 'config_data_docx', 'data', 'uploads'
        )
        os.makedirs(uploads_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(uploads_dir, filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filepath}")
        
        # Initialize importer
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        importer = CSVToDatabaseImporter(db_manager)
        
        # Process the mega CSV with notifications
        notifications = []
        
        # Step 1: File validation
        notifications.append({
            'step': 1,
            'type': 'info',
            'message': f'Validating file: {filename}',
            'timestamp': datetime.now().isoformat()
        })
        
        result = importer.import_mega_csv(filepath)
        
        if not result['success']:
            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
            
            notifications.append({
                'step': 2,
                'type': 'error',
                'message': f"Validation failed: {result.get('error', 'Unknown error')}",
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'duplicate': result.get('duplicate', False),
                'notifications': notifications
            }), 400
        
        # Step 2: CSV preprocessing
        notifications.append({
            'step': 2,
            'type': 'success',
            'message': 'File validated successfully',
            'timestamp': datetime.now().isoformat()
        })
        
        notifications.append({
            'step': 3,
            'type': 'info',
            'message': f"Processing game: {result['date']} vs {result['opponent']}",
            'timestamp': datetime.now().isoformat()
        })
        
        # Step 3: Team data processing
        if result.get('team_stats'):
            notifications.append({
                'step': 4,
                'type': 'success',
                'message': f"Team data processed - Cog Score: {result['team_stats'].get('cog_score', 'N/A')}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Step 4: Player data processing
        players_processed = result.get('players_processed', 0)
        player_names = result.get('player_names', [])
        
        notifications.append({
            'step': 5,
            'type': 'success',
            'message': f"Processed {players_processed} players: {', '.join(player_names[:3])}{'...' if len(player_names) > 3 else ''}",
            'timestamp': datetime.now().isoformat()
        })
        
        # Step 5: Database storage
        notifications.append({
            'step': 6,
            'type': 'success',
            'message': f"Game {result['game_id']} saved to database",
            'timestamp': datetime.now().isoformat()
        })
        
        # Step 6: Final success
        notifications.append({
            'step': 7,
            'type': 'success',
            'message': f"Import complete! Game ID: {result['game_id']}",
            'timestamp': datetime.now().isoformat()
        })
        
        # Cleanup uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'game_id': result['game_id'],
            'date': result['date'],
            'opponent': result['opponent'],
            'team': result['team'],
            'players_processed': players_processed,
            'player_names': player_names,
            'scorecards_created': result.get('scorecards_created', 0),
            'team_cog_score': result.get('team_stats', {}).get('cog_score'),
            'notifications': notifications,
            'message': result.get('message', 'Import successful')
        })
        
    except Exception as e:
        logger.exception("Error uploading mega CSV")
        
        # Cleanup on error
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': False,
            'error': str(e),
            'notification': {
                'type': 'error',
                'message': f'Error processing file: {str(e)}'
            }
        }), 500


@database_viz_api.route('/api/database-viz/export-player-card/<game_id>/<player_name>', methods=['GET'])
def export_player_card(game_id, player_name):
    """
    Export a player performance card as PDF.
    
    Args:
        game_id: The game ID
        player_name: The player name
        
    Returns:
        PDF file download
    """
    try:
        from flask import current_app
        
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        
        # Get game info
        game = db_manager.get_game_by_id(game_id)
        if not game:
            return jsonify({'success': False, 'error': 'Game not found'}), 404
        
        # Get player cog scores
        player_cog = db_manager.get_player_cog_score(game_id, player_name)
        
        if not player_cog:
            return jsonify({'success': False, 'error': 'Player cog score not found'}), 404
        
        # Prepare player data
        player_data = {
            'player_name': player_name,
            'game_date': game.get('date_string', 'N/A'),
            'opponent': game.get('opponent', 'N/A'),
            'cog_score': player_cog.get('overall_score', 0.0),
            'category_scores': player_cog.get('category_scores', {})
        }
        
        # Generate PDF
        pdf_service = PDFExportService()
        pdf_bytes = pdf_service.generate_player_card(player_data)
        
        # Return as downloadable file
        filename = f"{player_name.replace(' ', '_')}_{game.get('date_string', 'game')}_vs_{game.get('opponent', 'OPP')}.pdf"
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.exception(f"Error exporting player card for {player_name} in game {game_id}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@database_viz_api.route('/api/database-viz/export-player-comparison', methods=['POST'])
def export_player_comparison():
    """
    Export a player comparison card as PDF.
    
    Expects JSON:
        {
            "players": [
                {"game_id": "...", "player_name": "..."},
                ...
            ]
        }
        
    Returns:
        PDF file download
    """
    try:
        from flask import current_app
        
        data = request.get_json()
        players_input = data.get('players', [])
        
        if not players_input or len(players_input) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 players required for comparison'
            }), 400
        
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        players_data = []
        
        for player_input in players_input:
            game_id = player_input.get('game_id')
            player_name = player_input.get('player_name')
            
            # Get game and player data
            game = db_manager.get_game_by_id(game_id)
            player_cog = db_manager.get_player_cog_score(game_id, player_name)
            
            if game and player_cog:
                players_data.append({
                    'player_name': player_name,
                    'game_date': game.get('date_string', 'N/A'),
                    'opponent': game.get('opponent', 'N/A'),
                    'cog_score': player_cog.get('overall_score', 0.0),
                    'category_scores': player_cog.get('category_scores', {})
                })
        
        if len(players_data) < 2:
            return jsonify({
                'success': False,
                'error': 'Could not find data for enough players'
            }), 404
        
        # Generate PDF
        pdf_service = PDFExportService()
        pdf_bytes = pdf_service.generate_comparison_card(players_data)
        
        # Return as downloadable file
        filename = f"player_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.exception("Error exporting player comparison")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

