"""
Systems Check API Routes
"""

from flask import Blueprint, jsonify, render_template, request
from .check_runner import SystemsCheckRunner

systems_check_bp = Blueprint('systems_check', __name__, url_prefix='/systems-check')

@systems_check_bp.route('/')
def systems_check_page():
    """Display systems check page"""
    return render_template('systems_check.html')

@systems_check_bp.route('/api/run', methods=['GET', 'POST'])
def run_checks():
    """Run all system checks and return results"""
    try:
        # Get base URL from request or use default
        base_url = request.args.get('base_url', 'http://localhost:5000')
        if request.is_json and request.json:
            base_url = request.json.get('base_url', base_url)
        
        runner = SystemsCheckRunner()
        results = runner.run_all_checks(base_url=base_url)
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

