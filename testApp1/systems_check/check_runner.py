#!/usr/bin/env python3
"""
Systems Check Runner
Runs all system checks and returns results with percentage score
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class SystemsCheckRunner:
    """Runs system checks and returns formatted results"""
    
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.test_csvs_dir = os.path.join(self.base_dir, 'testcases', 'test_csvs')
        self.db_path = os.path.join(self.base_dir, 'src', 'core', 'data', 'basketball.db')
        
    def check_csv_files(self) -> Dict[str, Any]:
        """Check that CSV files exist and are readable"""
        check = {
            'name': 'CSV Files Exist',
            'status': 'unknown',
            'message': '',
            'details': []
        }
        
        try:
            if not os.path.exists(self.test_csvs_dir):
                check['status'] = 'fail'
                check['message'] = f'Test CSV directory not found: {self.test_csvs_dir}'
                return check
            
            csv_files = [f for f in os.listdir(self.test_csvs_dir) if f.endswith('.csv')]
            csv_files.sort()
            
            check['details'].append(f'Found {len(csv_files)} CSV files')
            
            if len(csv_files) >= 6:
                check['status'] = 'pass'
                check['message'] = f'Found {len(csv_files)} CSV files (expected 6+)'
                for csv_file in csv_files:
                    file_path = os.path.join(self.test_csvs_dir, csv_file)
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        check['details'].append(f'  ✓ {csv_file} ({size:,} bytes)')
            else:
                check['status'] = 'fail'
                check['message'] = f'Found only {len(csv_files)} CSV files (expected 6+)'
                
        except Exception as e:
            check['status'] = 'error'
            check['message'] = f'Error checking CSV files: {str(e)}'
            
        return check
    
    def check_database(self) -> Dict[str, Any]:
        """Check that database exists and is accessible"""
        check = {
            'name': 'Database Accessible',
            'status': 'unknown',
            'message': '',
            'details': []
        }
        
        try:
            if not os.path.exists(self.db_path):
                check['status'] = 'fail'
                check['message'] = f'Database file not found: {self.db_path}'
                return check
            
            # Try to import and use database manager
            from src.database.db_manager import DatabaseManager
            
            db_manager = DatabaseManager(self.db_path)
            db_manager.init_database()
            
            # Check for team statistics
            stats = db_manager.get_team_statistics(team='Heat')
            overall_scores = db_manager.get_team_statistics_overall_scores(team='Heat')
            game_info = db_manager.get_team_statistics_game_info(team='Heat')
            
            unique_dates = set(s['date'] for s in stats) if stats else set()
            
            check['details'].append(f'Database file exists: {os.path.getsize(self.db_path):,} bytes')
            check['details'].append(f'Team statistics records: {len(stats)}')
            check['details'].append(f'Unique game dates: {len(unique_dates)}')
            check['details'].append(f'Overall scores: {len(overall_scores)}')
            check['details'].append(f'Game info entries: {len(game_info)}')
            
            if len(unique_dates) >= 6:
                check['status'] = 'pass'
                check['message'] = f'Database accessible with {len(unique_dates)} games'
            else:
                check['status'] = 'warn'
                check['message'] = f'Database accessible but only {len(unique_dates)} games found (expected 6+)'
                
        except Exception as e:
            check['status'] = 'error'
            check['message'] = f'Error accessing database: {str(e)}'
            
        return check
    
    def check_api_endpoint(self, base_url: str = 'http://localhost:5000') -> Dict[str, Any]:
        """Check that API endpoint is accessible"""
        check = {
            'name': 'API Endpoint Accessible',
            'status': 'unknown',
            'message': '',
            'details': []
        }
        
        try:
            import requests
            
            url = f'{base_url}/api/team-statistics'
            response = requests.get(url, timeout=5)
            
            check['details'].append(f'HTTP Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    overall_scores = data.get('overall_scores', {})
                    game_info = data.get('game_info', {})
                    statistics = data.get('statistics', [])
                    
                    check['details'].append(f'Response success: {data.get("success")}')
                    check['details'].append(f'Overall scores: {len(overall_scores)} games')
                    check['details'].append(f'Game info: {len(game_info)} games')
                    check['details'].append(f'Statistics records: {len(statistics)}')
                    
                    if len(overall_scores) >= 6:
                        check['status'] = 'pass'
                        check['message'] = f'API accessible with {len(overall_scores)} games'
                    else:
                        check['status'] = 'warn'
                        check['message'] = f'API accessible but only {len(overall_scores)} games (expected 6+)'
                else:
                    check['status'] = 'fail'
                    check['message'] = f'API returned success=false: {data.get("error", "Unknown error")}'
            else:
                check['status'] = 'fail'
                check['message'] = f'API returned status {response.status_code}'
                
        except requests.exceptions.ConnectionError:
            check['status'] = 'fail'
            check['message'] = 'Cannot connect to API endpoint (is Flask app running?)'
        except ImportError:
            check['status'] = 'error'
            check['message'] = 'requests library not available'
        except Exception as e:
            check['status'] = 'error'
            check['message'] = f'Error checking API: {str(e)}'
            
        return check
    
    def check_file_structure(self) -> Dict[str, Any]:
        """Check that required files and directories exist"""
        check = {
            'name': 'File Structure',
            'status': 'unknown',
            'message': '',
            'details': []
        }
        
        required_paths = [
            ('testcases/test_csvs', 'Test CSV directory'),
            ('src/core/app.py', 'Flask app'),
            ('src/database/db_manager.py', 'Database manager'),
            ('src/processors/cog_score_calculator.py', 'Score calculator'),
            ('templates/analytics_dashboard.html', 'Analytics dashboard template'),
            ('static/js/analytics_dashboard.js', 'Analytics dashboard JS'),
        ]
        
        missing = []
        found = []
        
        for rel_path, description in required_paths:
            full_path = os.path.join(self.base_dir, rel_path)
            if os.path.exists(full_path):
                found.append(f'  ✓ {description}: {rel_path}')
            else:
                missing.append(f'  ✗ {description}: {rel_path}')
        
        check['details'] = found + missing
        
        if len(missing) == 0:
            check['status'] = 'pass'
            check['message'] = f'All {len(required_paths)} required files/directories found'
        else:
            check['status'] = 'warn'
            check['message'] = f'Missing {len(missing)} of {len(required_paths)} required files/directories'
            
        return check
    
    def check_csv_processing(self) -> Dict[str, Any]:
        """Check that CSV files can be processed"""
        check = {
            'name': 'CSV Processing',
            'status': 'unknown',
            'message': '',
            'details': []
        }
        
        try:
            from src.processors.cog_score_calculator import CogScoreCalculator
            from src.core.app import parse_date_from_filename
            
            csv_files = [f for f in os.listdir(self.test_csvs_dir) if f.endswith('.csv')]
            csv_files.sort()
            
            processed = 0
            errors = []
            
            for csv_file in csv_files[:6]:  # Test first 6 files
                csv_path = os.path.join(self.test_csvs_dir, csv_file)
                try:
                    # Parse filename
                    date_string, date_iso, opponent, _ = parse_date_from_filename(csv_file)
                    
                    if not date_iso:
                        errors.append(f'{csv_file}: Could not parse date')
                        continue
                    
                    # Calculate scores
                    calculator = CogScoreCalculator(csv_path)
                    scores, overall = calculator.calculate_all_scores()
                    
                    processed += 1
                    check['details'].append(f'  ✓ {csv_file}: {overall:.2f}% ({len(scores)} categories)')
                    
                except Exception as e:
                    errors.append(f'{csv_file}: {str(e)}')
            
            if len(errors) > 0:
                for error in errors:
                    check['details'].append(f'  ✗ {error}')
            
            if processed >= 6:
                check['status'] = 'pass'
                check['message'] = f'Successfully processed {processed} CSV files'
            elif processed > 0:
                check['status'] = 'warn'
                check['message'] = f'Processed {processed} files with {len(errors)} errors'
            else:
                check['status'] = 'fail'
                check['message'] = f'Failed to process CSV files: {len(errors)} errors'
                
        except ImportError as e:
            check['status'] = 'error'
            check['message'] = f'Missing dependencies: {str(e)}'
        except Exception as e:
            check['status'] = 'error'
            check['message'] = f'Error checking CSV processing: {str(e)}'
            
        return check
    
    def check_chart_toggle(self, base_url: str = 'http://localhost:5000') -> Dict[str, Any]:
        """Check that chart toggle functionality is available"""
        check = {
            'name': 'Chart Toggle Functionality',
            'status': 'unknown',
            'message': '',
            'details': []
        }
        
        try:
            import requests
            
            # Check if test file exists
            test_file_path = os.path.join(self.base_dir, 'tests', 'test_chart_toggle.js')
            if not os.path.exists(test_file_path):
                check['status'] = 'warn'
                check['message'] = 'Chart toggle test file not found'
                check['details'].append('Test file missing: tests/test_chart_toggle.js')
                return check
            
            # Check if analytics dashboard page exists and loads
            try:
                url = f'{base_url}/analytics-dashboard'
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    # Check if toggle-related HTML elements are present
                    html_content = response.text
                    
                    has_toggle_menu = 'chartLineMenu' in html_content
                    has_toggle_functions = 'toggleChartLine' in html_content or 'getChartInstance' in html_content
                    has_test_script = 'test_chart_toggle.js' in html_content
                    
                    check['details'].append(f'Analytics dashboard accessible: ✓')
                    check['details'].append(f'Toggle menu element: {"✓" if has_toggle_menu else "✗"}')
                    check['details'].append(f'Toggle functions: {"✓" if has_toggle_functions else "✗"}')
                    check['details'].append(f'Test script included: {"✓" if has_test_script else "✗"}')
                    
                    if has_toggle_menu and has_toggle_functions:
                        check['status'] = 'pass'
                        check['message'] = 'Chart toggle functionality available on analytics dashboard'
                    else:
                        check['status'] = 'warn'
                        check['message'] = 'Analytics dashboard accessible but toggle elements may be missing'
                else:
                    check['status'] = 'fail'
                    check['message'] = f'Analytics dashboard returned status {response.status_code}'
                    
            except requests.exceptions.ConnectionError:
                check['status'] = 'warn'
                check['message'] = 'Cannot connect to analytics dashboard (is Flask app running?)'
            except Exception as e:
                check['status'] = 'warn'
                check['message'] = f'Error checking analytics dashboard: {str(e)}'
                
        except ImportError:
            check['status'] = 'warn'
            check['message'] = 'requests library not available for HTTP check'
        except Exception as e:
            check['status'] = 'error'
            check['message'] = f'Error checking chart toggle: {str(e)}'
            
        return check
    
    def run_all_checks(self, base_url: str = 'http://localhost:5000') -> Dict[str, Any]:
        """Run all system checks"""
        checks = [
            self.check_file_structure(),
            self.check_csv_files(),
            self.check_csv_processing(),
            self.check_database(),
            self.check_api_endpoint(base_url),
            self.check_chart_toggle(base_url),
        ]
        
        # Calculate score
        total_checks = len(checks)
        passed = sum(1 for c in checks if c['status'] == 'pass')
        warnings = sum(1 for c in checks if c['status'] == 'warn')
        failed = sum(1 for c in checks if c['status'] == 'fail')
        errors = sum(1 for c in checks if c['status'] == 'error')
        
        # Score calculation: pass=100%, warn=50%, fail=0%, error=0%
        score = ((passed * 100) + (warnings * 50)) / total_checks if total_checks > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'score': round(score, 1),
            'total_checks': total_checks,
            'passed': passed,
            'warnings': warnings,
            'failed': failed,
            'errors': errors,
            'checks': checks,
            'status': 'healthy' if score >= 80 else 'degraded' if score >= 50 else 'unhealthy'
        }

if __name__ == '__main__':
    runner = SystemsCheckRunner()
    results = runner.run_all_checks()
    print(json.dumps(results, indent=2))

