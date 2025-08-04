#!/usr/bin/env python3
"""
Flask API routes for Player and Scorecard CRUD operations.
"""

from flask import Blueprint, request, jsonify
from src.models import Player, Scorecard
from src.database import DatabaseManager
from datetime import datetime
import json

# Create Blueprint for player API
player_api = Blueprint('player_api', __name__)

# Initialize database manager
db_manager = DatabaseManager("data/basketball.db")


@player_api.route('/api/players', methods=['GET'])
def get_all_players():
    """Get all players."""
    try:
        players = db_manager.get_all_players()
        players_data = []
        
        for player in players:
            player_dict = player.to_dict()
            # Convert timestamps to readable dates
            player_dict['date_created_readable'] = datetime.fromtimestamp(player.date_created).strftime('%Y-%m-%d %H:%M:%S')
            players_data.append(player_dict)
        
        return jsonify({
            'success': True,
            'players': players_data,
            'count': len(players_data)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players/<player_name>', methods=['GET'])
def get_player(player_name):
    """Get a specific player by name."""
    try:
        player = db_manager.get_player_by_name(player_name)
        
        if not player:
            return jsonify({
                'success': False,
                'error': f'Player "{player_name}" not found'
            }), 404
        
        player_dict = player.to_dict()
        player_dict['date_created_readable'] = datetime.fromtimestamp(player.date_created).strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'success': True,
            'player': player_dict
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players', methods=['POST'])
def create_player():
    """Create a new player."""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Player name is required'
            }), 400
        
        player_name = data['name'].strip()
        if not player_name:
            return jsonify({
                'success': False,
                'error': 'Player name cannot be empty'
            }), 400
        
        # Check if player already exists
        existing_player = db_manager.get_player_by_name(player_name)
        if existing_player:
            return jsonify({
                'success': False,
                'error': f'Player "{player_name}" already exists'
            }), 409
        
        # Create new player
        player = Player(player_name)
        success = db_manager.create_player(player)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Player "{player_name}" created successfully',
                'player': player.to_dict()
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create player'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players/<player_name>', methods=['PUT'])
def update_player(player_name):
    """Update a player."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided for update'
            }), 400
        
        # Get existing player
        player = db_manager.get_player_by_name(player_name)
        if not player:
            return jsonify({
                'success': False,
                'error': f'Player "{player_name}" not found'
            }), 404
        
        # Update player fields
        if 'name' in data and data['name'].strip():
            player.name = data['name'].strip()
        
        if 'date_created' in data:
            try:
                player.date_created = int(data['date_created'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'date_created must be a valid integer timestamp'
                }), 400
        
        success = db_manager.update_player(player)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Player "{player_name}" updated successfully',
                'player': player.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update player'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players/<player_name>', methods=['DELETE'])
def delete_player(player_name):
    """Delete a player."""
    try:
        # Check if player exists
        player = db_manager.get_player_by_name(player_name)
        if not player:
            return jsonify({
                'success': False,
                'error': f'Player "{player_name}" not found'
            }), 404
        
        success = db_manager.delete_player(player_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Player "{player_name}" deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete player'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players/<player_name>/scorecards', methods=['GET'])
def get_player_scorecards(player_name):
    """Get all scorecards for a specific player."""
    try:
        # Check if player exists
        player = db_manager.get_player_by_name(player_name)
        if not player:
            return jsonify({
                'success': False,
                'error': f'Player "{player_name}" not found'
            }), 404
        
        scorecards_data = []
        for scorecard in player.scorecards:
            scorecard_dict = scorecard.to_dict()
            scorecard_dict['date_created_readable'] = datetime.fromtimestamp(scorecard.date_created).strftime('%Y-%m-%d %H:%M:%S')
            scorecards_data.append(scorecard_dict)
        
        return jsonify({
            'success': True,
            'player_name': player_name,
            'scorecards': scorecards_data,
            'count': len(scorecards_data)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players/<player_name>/scorecards', methods=['POST'])
def create_scorecard(player_name):
    """Create a new scorecard for a player."""
    try:
        # Check if player exists
        player = db_manager.get_player_by_name(player_name)
        if not player:
            return jsonify({
                'success': False,
                'error': f'Player "{player_name}" not found'
            }), 404
        
        data = request.get_json() or {}
        
        # Create scorecard
        scorecard = Scorecard(player_name)
        
        # Override date_created if provided
        if 'date_created' in data:
            try:
                scorecard.date_created = int(data['date_created'])
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'date_created must be a valid integer timestamp'
                }), 400
        
        success = db_manager.create_scorecard(scorecard)
        
        if success:
            scorecard_dict = scorecard.to_dict()
            scorecard_dict['date_created_readable'] = datetime.fromtimestamp(scorecard.date_created).strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({
                'success': True,
                'message': f'Scorecard created for "{player_name}"',
                'scorecard': scorecard_dict
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create scorecard'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/players/<player_name>/scorecards/<int:date_created>', methods=['DELETE'])
def delete_scorecard(player_name, date_created):
    """Delete a specific scorecard."""
    try:
        success = db_manager.delete_scorecard(player_name, date_created)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Scorecard deleted for "{player_name}"'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Scorecard not found or failed to delete'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@player_api.route('/api/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics."""
    try:
        stats = db_manager.get_database_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 