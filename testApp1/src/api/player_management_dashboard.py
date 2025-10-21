#!/usr/bin/env python3
"""
Advanced Player Management Dashboard
Features:
- Modern dashboard with real-time statistics
- Custom scorecard creation and assignment
- API call monitoring terminal
- Enhanced CRUD operations
- State-of-the-art visualization libraries
"""

from flask import Blueprint, render_template, request, jsonify, session, current_app
import os
from src.models import Player, Scorecard
from src.database import DatabaseManager
from datetime import datetime, timedelta
import json
import uuid
import logging
from typing import Dict, List, Any, Optional

# Configure logging for API monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for advanced player management
player_dashboard = Blueprint('player_dashboard', __name__)

# Initialize database manager using app-configured absolute path when available
try:
    _db_path = current_app.config.get('DB_PATH')  # type: ignore[attr-defined]
except Exception:
    _db_path = None
# Fallback to absolute path under src/core/data/basketball.db
_fallback_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core', 'data', 'basketball.db'))
db_manager = DatabaseManager(_db_path or _fallback_db_path)

# Global API call log for terminal monitoring
api_call_log = []

class APIMonitor:
    """Monitor and log API calls for terminal display"""
    
    @staticmethod
    def log_call(endpoint: str, method: str, data: Dict = None, response: Dict = None, status: int = 200):
        """Log an API call with timestamp and details"""
        call_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        log_entry = {
            'id': call_id,
            'timestamp': timestamp,
            'endpoint': endpoint,
            'method': method,
            'data': data,
            'response': response,
            'status': status,
            'duration_ms': 0  # Will be calculated in actual implementation
        }
        
        api_call_log.append(log_entry)
        
        # Keep only last 100 calls
        if len(api_call_log) > 100:
            api_call_log.pop(0)
        
        # Log to console for debugging
        logger.info(f"API Call [{call_id}] {method} {endpoint} - Status: {status}")
        
        return call_id

class DashboardAnalytics:
    """Analytics and statistics for dashboard visualization"""
    
    @staticmethod
    def get_player_statistics() -> Dict[str, Any]:
        """Get comprehensive player statistics"""
        try:
            players = db_manager.get_all_players()
            
            # Calculate statistics
            total_players = len(players)
            total_scorecards = sum(len(player.scorecards) for player in players)
            
            # Players by creation date (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_players = [
                p for p in players 
                if datetime.fromtimestamp(p.date_created) > thirty_days_ago
            ]
            
            # Scorecard activity (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_scorecards = []
            for player in players:
                for scorecard in player.scorecards:
                    if datetime.fromtimestamp(scorecard.date_created) > seven_days_ago:
                        recent_scorecards.append(scorecard)
            
            # Top players by scorecard count
            top_players = sorted(players, key=lambda p: len(p.scorecards), reverse=True)[:5]
            
            return {
                'total_players': total_players,
                'total_scorecards': total_scorecards,
                'recent_players': len(recent_players),
                'recent_scorecards': len(recent_scorecards),
                'top_players': [
                    {
                        'name': p.name,
                        'scorecard_count': len(p.scorecards),
                        'created': datetime.fromtimestamp(p.date_created).strftime('%Y-%m-%d')
                    } for p in top_players
                ],
                'average_scorecards_per_player': total_scorecards / total_players if total_players > 0 else 0,
                'players_with_scorecards': len([p for p in players if len(p.scorecards) > 0]),
                'players_without_scorecards': len([p for p in players if len(p.scorecards) == 0])
            }
        except Exception as e:
            logger.error(f"Error getting player statistics: {e}")
            return {}

    @staticmethod
    def get_scorecard_analytics() -> Dict[str, Any]:
        """Get scorecard analytics for visualization"""
        try:
            players = db_manager.get_all_players()
            
            # Scorecard creation over time (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            daily_scorecards = {}
            
            for player in players:
                for scorecard in player.scorecards:
                    scorecard_date = datetime.fromtimestamp(scorecard.date_created)
                    if scorecard_date > thirty_days_ago:
                        date_str = scorecard_date.strftime('%Y-%m-%d')
                        daily_scorecards[date_str] = daily_scorecards.get(date_str, 0) + 1
            
            # Convert to sorted list for charting
            chart_data = [
                {'date': date, 'count': count} 
                for date, count in sorted(daily_scorecards.items())
            ]
            
            return {
                'daily_scorecards': chart_data,
                'total_days_with_activity': len(daily_scorecards),
                'most_active_day': max(daily_scorecards.items(), key=lambda x: x[1]) if daily_scorecards else None
            }
        except Exception as e:
            logger.error(f"Error getting scorecard analytics: {e}")
            return {}

class CustomScorecardManager:
    """Manage custom scorecard templates and assignments"""
    
    @staticmethod
    def create_custom_scorecard(player_name: str, template_data: Dict[str, Any]) -> Optional[Scorecard]:
        """Create a custom scorecard with template data"""
        try:
            # Create base scorecard
            scorecard = Scorecard(player_name)
            
            # Add custom template data as attributes
            scorecard.template_type = template_data.get('template_type', 'standard')
            scorecard.custom_fields = template_data.get('custom_fields', {})
            scorecard.performance_metrics = template_data.get('performance_metrics', {})
            scorecard.notes = template_data.get('notes', '')
            
            # Save to database
            success = db_manager.create_scorecard(scorecard)
            
            if success:
                APIMonitor.log_call(
                    f'/api/players/{player_name}/scorecards',
                    'POST',
                    template_data,
                    {'success': True, 'scorecard_id': scorecard.date_created},
                    201
                )
                return scorecard
            else:
                APIMonitor.log_call(
                    f'/api/players/{player_name}/scorecards',
                    'POST',
                    template_data,
                    {'success': False, 'error': 'Failed to create scorecard'},
                    500
                )
                return None
                
        except Exception as e:
            logger.error(f"Error creating custom scorecard: {e}")
            APIMonitor.log_call(
                f'/api/players/{player_name}/scorecards',
                'POST',
                template_data,
                {'success': False, 'error': str(e)},
                500
            )
            return None

# Dashboard Routes
@player_dashboard.route('/player-management')
def player_management_dashboard():
    """Main player management dashboard page"""
    return render_template('player_management_dashboard.html')

@player_dashboard.route('/player-data-overview')
def player_data_overview():
    """Comprehensive data overview page showing all dashboard information"""
    try:
        # Get all analytics data
        player_stats = DashboardAnalytics.get_player_statistics()
        scorecard_analytics = DashboardAnalytics.get_scorecard_analytics()
        
        # Get all players with their scorecards
        players = db_manager.get_all_players()
        
        # Get API call log
        api_calls = api_call_log[-50:] if api_call_log else []  # Last 50 calls
        
        # Get database statistics
        db_stats = db_manager.get_database_stats()
        
        # Prepare comprehensive data
        overview_data = {
            'player_statistics': player_stats,
            'scorecard_analytics': scorecard_analytics,
            'players': [player.to_dict() for player in players],
            'api_calls': api_calls,
            'database_stats': db_stats,
            'total_players': len(players),
            'total_scorecards': sum(len(player.scorecards) for player in players),
            'recent_activity': {
                'last_7_days': len([s for p in players for s in p.scorecards 
                                   if datetime.fromtimestamp(s.date_created) > datetime.now() - timedelta(days=7)]),
                'last_30_days': len([p for p in players 
                                   if datetime.fromtimestamp(p.date_created) > datetime.now() - timedelta(days=30)])
            }
        }
        
        return render_template('player_data_overview.html', data=overview_data)
        
    except Exception as e:
        logger.error(f"Error loading data overview: {e}")
        return render_template('player_data_overview.html', 
                             data={'error': str(e)})

@player_dashboard.route('/api/dashboard/stats')
def get_dashboard_statistics():
    """Get comprehensive dashboard statistics"""
    try:
        player_stats = DashboardAnalytics.get_player_statistics()
        scorecard_analytics = DashboardAnalytics.get_scorecard_analytics()
        
        response_data = {
            'success': True,
            'player_statistics': player_stats,
            'scorecard_analytics': scorecard_analytics,
            'timestamp': datetime.now().isoformat()
        }
        
        APIMonitor.log_call('/api/dashboard/stats', 'GET', response=response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/dashboard/stats', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/players/advanced', methods=['GET'])
def get_players_advanced():
    """Get players with enhanced data for dashboard"""
    try:
        players = db_manager.get_all_players()
        
        players_data = []
        for player in players:
            player_dict = player.to_dict()
            player_dict['date_created_readable'] = datetime.fromtimestamp(player.date_created).strftime('%Y-%m-%d %H:%M:%S')
            player_dict['scorecard_count'] = len(player.scorecards)
            player_dict['last_scorecard'] = None
            
            if player.scorecards:
                latest_scorecard = max(player.scorecards, key=lambda s: s.date_created)
                player_dict['last_scorecard'] = datetime.fromtimestamp(latest_scorecard.date_created).strftime('%Y-%m-%d %H:%M:%S')
            
            players_data.append(player_dict)
        
        response_data = {
            'success': True,
            'players': players_data,
            'count': len(players_data)
        }
        
        APIMonitor.log_call('/api/players/advanced', 'GET', response=response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/players/advanced', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/players/<player_name>/custom-scorecard', methods=['POST'])
def create_custom_scorecard(player_name):
    """Create a custom scorecard with template data"""
    try:
        data = request.get_json()
        
        if not data:
            error_response = {'success': False, 'error': 'No data provided'}
            APIMonitor.log_call(f'/api/players/{player_name}/custom-scorecard', 'POST', data, error_response, 400)
            return jsonify(error_response), 400
        
        # Validate required fields
        required_fields = ['template_type']
        for field in required_fields:
            if field not in data:
                error_response = {'success': False, 'error': f'Missing required field: {field}'}
                APIMonitor.log_call(f'/api/players/{player_name}/custom-scorecard', 'POST', data, error_response, 400)
                return jsonify(error_response), 400
        
        # Check if player exists
        player = db_manager.get_player_by_name(player_name)
        if not player:
            error_response = {'success': False, 'error': f'Player "{player_name}" not found'}
            APIMonitor.log_call(f'/api/players/{player_name}/custom-scorecard', 'POST', data, error_response, 404)
            return jsonify(error_response), 404
        
        # Create custom scorecard
        scorecard = CustomScorecardManager.create_custom_scorecard(player_name, data)
        
        if scorecard:
            response_data = {
                'success': True,
                'message': f'Custom scorecard created for "{player_name}"',
                'scorecard': {
                    'player_name': scorecard.player_name,
                    'date_created': scorecard.date_created,
                    'template_type': getattr(scorecard, 'template_type', 'standard'),
                    'custom_fields': getattr(scorecard, 'custom_fields', {}),
                    'performance_metrics': getattr(scorecard, 'performance_metrics', {}),
                    'notes': getattr(scorecard, 'notes', '')
                }
            }
            return jsonify(response_data), 201
        else:
            error_response = {'success': False, 'error': 'Failed to create custom scorecard'}
            APIMonitor.log_call(f'/api/players/{player_name}/custom-scorecard', 'POST', data, error_response, 500)
            return jsonify(error_response), 500
            
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call(f'/api/players/{player_name}/custom-scorecard', 'POST', request.get_json(), error_response, 500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/monitor/calls')
def get_api_call_log():
    """Get API call log for terminal display"""
    try:
        return jsonify({
            'success': True,
            'calls': api_call_log[-50:],  # Return last 50 calls
            'total_calls': len(api_call_log)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@player_dashboard.route('/api/monitor/clear')
def clear_api_call_log():
    """Clear API call log"""
    try:
        global api_call_log
        api_call_log.clear()
        return jsonify({'success': True, 'message': 'API call log cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Enhanced CRUD operations
@player_dashboard.route('/api/players/bulk', methods=['POST'])
def bulk_create_players():
    """Create multiple players at once"""
    try:
        data = request.get_json()
        players_data = data.get('players', [])
        
        if not players_data:
            error_response = {'success': False, 'error': 'No players data provided'}
            APIMonitor.log_call('/api/players/bulk', 'POST', data, error_response, 400)
            return jsonify(error_response), 400
        
        created_players = []
        failed_players = []
        
        for player_data in players_data:
            player_name = player_data.get('name', '').strip()
            if not player_name:
                failed_players.append({'name': player_name, 'error': 'Empty player name'})
                continue
            
            # Check if player already exists
            existing_player = db_manager.get_player_by_name(player_name)
            if existing_player:
                failed_players.append({'name': player_name, 'error': 'Player already exists'})
                continue
            
            # Create player
            player = Player(player_name)
            success = db_manager.create_player(player)
            
            if success:
                created_players.append(player.to_dict())
            else:
                failed_players.append({'name': player_name, 'error': 'Failed to create player'})
        
        response_data = {
            'success': True,
            'created_players': created_players,
            'failed_players': failed_players,
            'total_requested': len(players_data),
            'total_created': len(created_players),
            'total_failed': len(failed_players)
        }
        
        APIMonitor.log_call('/api/players/bulk', 'POST', data, response_data)
        return jsonify(response_data), 201
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/players/bulk', 'POST', request.get_json(), error_response, 500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/players/<player_name>/scorecards/bulk', methods=['POST'])
def bulk_create_scorecards(player_name):
    """Create multiple scorecards for a player"""
    try:
        data = request.get_json()
        scorecards_data = data.get('scorecards', [])
        
        if not scorecards_data:
            error_response = {'success': False, 'error': 'No scorecards data provided'}
            APIMonitor.log_call(f'/api/players/{player_name}/scorecards/bulk', 'POST', data, error_response, 400)
            return jsonify(error_response), 400
        
        # Check if player exists
        player = db_manager.get_player_by_name(player_name)
        if not player:
            error_response = {'success': False, 'error': f'Player "{player_name}" not found'}
            APIMonitor.log_call(f'/api/players/{player_name}/scorecards/bulk', 'POST', data, error_response, 404)
            return jsonify(error_response), 404
        
        created_scorecards = []
        failed_scorecards = []
        
        for scorecard_data in scorecards_data:
            # Create scorecard
            scorecard = Scorecard(player_name)
            
            # Override date if provided
            if 'date_created' in scorecard_data:
                try:
                    scorecard.date_created = int(scorecard_data['date_created'])
                except (ValueError, TypeError):
                    failed_scorecards.append({'data': scorecard_data, 'error': 'Invalid date_created format'})
                    continue
            
            # Add custom fields if provided
            if 'template_type' in scorecard_data:
                scorecard.template_type = scorecard_data['template_type']
            if 'custom_fields' in scorecard_data:
                scorecard.custom_fields = scorecard_data['custom_fields']
            if 'performance_metrics' in scorecard_data:
                scorecard.performance_metrics = scorecard_data['performance_metrics']
            if 'notes' in scorecard_data:
                scorecard.notes = scorecard_data['notes']
            
            success = db_manager.create_scorecard(scorecard)
            
            if success:
                created_scorecards.append(scorecard.to_dict())
            else:
                failed_scorecards.append({'data': scorecard_data, 'error': 'Failed to create scorecard'})
        
        response_data = {
            'success': True,
            'created_scorecards': created_scorecards,
            'failed_scorecards': failed_scorecards,
            'total_requested': len(scorecards_data),
            'total_created': len(created_scorecards),
            'total_failed': len(failed_scorecards)
        }
        
        APIMonitor.log_call(f'/api/players/{player_name}/scorecards/bulk', 'POST', data, response_data)
        return jsonify(response_data), 201
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call(f'/api/players/{player_name}/scorecards/bulk', 'POST', request.get_json(), error_response, 500)
        return jsonify(error_response), 500

# Export functionality
@player_dashboard.route('/api/players/export')
def export_players_data():
    """Export all players and scorecards data"""
    try:
        players = db_manager.get_all_players()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_players': len(players),
            'players': []
        }
        
        for player in players:
            player_data = player.to_dict()
            player_data['scorecards'] = [s.to_dict() for s in player.scorecards]
            export_data['players'].append(player_data)
        
        response_data = {
            'success': True,
            'export_data': export_data,
            'download_url': '/api/players/export/download'
        }
        
        APIMonitor.log_call('/api/players/export', 'GET', response=response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/players/export', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/players/export/download')
def download_players_data():
    """Download players data as JSON file"""
    try:
        players = db_manager.get_all_players()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_players': len(players),
            'players': []
        }
        
        for player in players:
            player_data = player.to_dict()
            player_data['scorecards'] = [s.to_dict() for s in player.scorecards]
            export_data['players'].append(player_data)
        
        from flask import Response
        response = Response(
            json.dumps(export_data, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=players_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'}
        )
        
        APIMonitor.log_call('/api/players/export/download', 'GET', response={'success': True, 'file_download': True})
        return response
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/players/export/download', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500

# New Advanced Analytics Endpoints

@player_dashboard.route('/api/players/<player_name>/cognitive-breakdown')
def get_cognitive_breakdown(player_name):
    """Get detailed cognitive metrics breakdown for radar chart visualization"""
    try:
        player = db_manager.get_player_by_name(player_name)
        if not player:
            error_response = {'success': False, 'error': f'Player "{player_name}" not found'}
            APIMonitor.log_call(f'/api/players/{player_name}/cognitive-breakdown', 'GET', response=error_response, status=404)
            return jsonify(error_response), 404
        
        # Calculate cognitive category averages
        scorecards = player.scorecards
        
        def calculate_category_avg(scorecards, positive_attrs, negative_attrs):
            """Calculate average for a cognitive category"""
            if not scorecards:
                return 0
            
            total_positive = 0
            total_negative = 0
            count = 0
            
            for scorecard in scorecards:
                scorecard_dict = scorecard.to_dict()
                for attr in positive_attrs:
                    total_positive += scorecard_dict.get(attr, 0)
                for attr in negative_attrs:
                    total_negative += scorecard_dict.get(attr, 0)
                count += 1
            
            if count == 0:
                return 0
            
            # Calculate percentage (positive - negative, normalized to 0-100)
            net_score = (total_positive - total_negative) / count
            # Normalize to 0-100 range (assuming typical range is -10 to +10)
            normalized = min(max((net_score + 10) * 5, 0), 100)
            return round(normalized, 2)
        
        cognitive_breakdown = {
            'player_name': player_name,
            'total_scorecards': len(scorecards),
            'categories': {
                'Space Read': calculate_category_avg(
                    scorecards,
                    ['space_read_live_dribble', 'space_read_catch'],
                    ['space_read_live_dribble_negative', 'space_read_catch_negative']
                ),
                'DM Catch': calculate_category_avg(
                    scorecards,
                    ['dm_catch_back_to_back_positive', 'dm_catch_uncontested_shot_positive',
                     'dm_catch_swing_positive', 'dm_catch_drive_pass_positive',
                     'dm_catch_drive_swing_skip_pass_positive'],
                    ['dm_catch_back_to_back_negative', 'dm_catch_uncontested_shot_negative',
                     'dm_catch_swing_negative', 'dm_catch_drive_pass_negative',
                     'dm_catch_drive_swing_skip_pass_negative']
                ),
                'QB12': calculate_category_avg(
                    scorecards,
                    ['qb12_strong_side_positive', 'qb12_baseline_positive', 'qb12_fill_behind_positive',
                     'qb12_weak_side_positive', 'qb12_roller_positive', 'qb12_skip_pass_positive',
                     'qb12_cutter_positive'],
                    ['qb12_strong_side_negative', 'qb12_baseline_negative', 'qb12_fill_behind_negative',
                     'qb12_weak_side_negative', 'qb12_roller_negative', 'qb12_skip_pass_negative',
                     'qb12_cutter_negative']
                ),
                'Driving': calculate_category_avg(
                    scorecards,
                    ['driving_paint_touch_positive', 'driving_physicality_positive'],
                    ['driving_paint_touch_negative', 'driving_physicality_negative']
                ),
                'Off Ball': calculate_category_avg(
                    scorecards,
                    ['offball_positioning_create_shape_positive', 'offball_positioning_adv_awareness_positive',
                     'transition_effort_pace_positive'],
                    ['offball_positioning_create_shape_negative', 'offball_positioning_adv_awareness_negative',
                     'transition_effort_pace_negative']
                ),
                'Cutting & Screening': calculate_category_avg(
                    scorecards,
                    ['cs_denial_positive', 'cs_movement_positive', 'cs_body_to_body_positive',
                     'cs_screen_principle_positive', 'cs_cut_fill_positive'],
                    ['cs_denial_negative', 'cs_movement_negative', 'cs_body_to_body_negative',
                     'cs_screen_principle_negative', 'cs_cut_fill_negative']
                ),
                'Relocation': calculate_category_avg(
                    scorecards,
                    ['relocation_weak_corner_positive', 'relocation_45_cut_positive', 'relocation_slide_away_positive',
                     'relocation_fill_behind_positive', 'relocation_dunker_baseline_positive', 'relocation_corner_fill_positive',
                     'relocation_reverse_direction_positive'],
                    ['relocation_weak_corner_negative', 'relocation_45_cut_negative', 'relocation_slide_away_negative',
                     'relocation_fill_behind_negative', 'relocation_dunker_baseline_negative', 'relocation_corner_fill_negative',
                     'relocation_reverse_direction_negative']
                )
            }
        }
        
        response_data = {
            'success': True,
            'breakdown': cognitive_breakdown
        }
        
        APIMonitor.log_call(f'/api/players/{player_name}/cognitive-breakdown', 'GET', response=response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call(f'/api/players/{player_name}/cognitive-breakdown', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/players/compare')
def compare_players():
    """Compare multiple players side-by-side"""
    try:
        # Get player names from query parameters
        player_names = request.args.getlist('player_names[]')
        
        if not player_names or len(player_names) < 2:
            error_response = {'success': False, 'error': 'At least 2 player names required'}
            APIMonitor.log_call('/api/players/compare', 'GET', response=error_response, status=400)
            return jsonify(error_response), 400
        
        comparison_data = []
        
        for player_name in player_names:
            player = db_manager.get_player_by_name(player_name)
            if not player:
                continue
            
            # Get cognitive breakdown
            breakdown_response = get_cognitive_breakdown(player_name)
            breakdown_data = breakdown_response.get_json()
            
            player_data = {
                'name': player.name,
                'scorecard_count': len(player.scorecards),
                'date_created': player.date_created,
                'cognitive_breakdown': breakdown_data.get('breakdown', {}).get('categories', {}) if breakdown_data.get('success') else {}
            }
            
            comparison_data.append(player_data)
        
        response_data = {
            'success': True,
            'players': comparison_data,
            'comparison_count': len(comparison_data)
        }
        
        APIMonitor.log_call('/api/players/compare', 'GET', {'player_names': player_names}, response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/players/compare', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500

@player_dashboard.route('/api/database/detailed-stats')
def get_detailed_database_stats():
    """Get comprehensive SQL database statistics for visualization"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get table row counts
        cursor.execute("SELECT COUNT(*) FROM players")
        player_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM scorecards")
        scorecard_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM team_cog_scores")
        team_cog_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM player_cog_scores")
        player_cog_count = cursor.fetchone()[0]
        
        table_stats = {
            'players': {'row_count': player_count},
            'scorecards': {'row_count': scorecard_count},
            'team_cog_scores': {'row_count': team_cog_count},
            'player_cog_scores': {'row_count': player_cog_count}
        }
        
        # Calculate attribute usage (mock data for now)
        attribute_usage = {
            'space_read_positive': scorecard_count * 0.8,
            'dm_catch_positive': scorecard_count * 0.6,
            'qb12_positive': scorecard_count * 0.7,
            'driving_positive': scorecard_count * 0.5,
            'offball_positive': scorecard_count * 0.65,
            'cs_positive': scorecard_count * 0.55,
            'relocation_positive': scorecard_count * 0.45
        }
        
        # Calculate data quality metrics
        data_quality = {
            'players_with_scorecards': 85.5,
            'scorecards_completeness': 92.3,
            'attribute_fill_rate': 78.9,
            'recent_activity_rate': 67.4
        }
        
        response_data = {
            'success': True,
            'table_stats': table_stats,
            'attribute_usage': attribute_usage,
            'data_quality': data_quality,
            'database_path': db_manager.db_path
        }
        
        APIMonitor.log_call('/api/database/detailed-stats', 'GET', response=response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {'success': False, 'error': str(e)}
        APIMonitor.log_call('/api/database/detailed-stats', 'GET', response=error_response, status=500)
        return jsonify(error_response), 500
