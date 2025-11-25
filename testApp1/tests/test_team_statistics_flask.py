#!/usr/bin/env python3
"""
Flask-based test cases for Team Statistics API
Tests the actual Flask endpoints
"""

import unittest
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Flask app
from src.core.app import app

class TestTeamStatisticsFlask(unittest.TestCase):
    """Test team statistics Flask endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_01_api_endpoint_accessible(self):
        """Test that API endpoint is accessible"""
        print("\n📡 Test 1: API Endpoint Accessibility")
        
        response = self.app.get('/api/team-statistics')
        self.assertEqual(response.status_code, 200, "API endpoint should return 200")
        
        data = json.loads(response.data)
        self.assertIn('success', data, "Response should have 'success' field")
        
        print(f"   ✓ API endpoint accessible (status: {response.status_code})")
        print(f"   ✓ Response has 'success' field: {data.get('success')}")
        
        return data
    
    def test_02_api_returns_data(self):
        """Test that API returns data structure"""
        print("\n📊 Test 2: API Returns Data Structure")
        
        response = self.app.get('/api/team-statistics')
        data = json.loads(response.data)
        
        if data.get('success'):
            self.assertIn('statistics', data, "Response should have 'statistics' field")
            self.assertIn('overall_scores', data, "Response should have 'overall_scores' field")
            self.assertIn('game_info', data, "Response should have 'game_info' field")
            
            print(f"   ✓ Statistics: {len(data.get('statistics', []))} records")
            print(f"   ✓ Overall scores: {len(data.get('overall_scores', {}))} games")
            print(f"   ✓ Game info: {len(data.get('game_info', {}))} games")
        else:
            print(f"   ⚠️  API returned success=false: {data.get('error', 'Unknown error')}")
        
        return data
    
    def test_03_six_games_present(self):
        """Test that API returns 6 games"""
        print("\n🎮 Test 3: Six Games Present")
        
        # Force recalculation
        response = self.app.get('/api/team-statistics?force_recalculate=true')
        data = json.loads(response.data)
        
        if data.get('success'):
            overall_scores = data.get('overall_scores', {})
            game_info = data.get('game_info', {})
            
            overall_count = len(overall_scores)
            game_info_count = len(game_info)
            
            print(f"   • Overall scores: {overall_count} games")
            print(f"   • Game info: {game_info_count} games")
            
            if overall_count > 0:
                print("\n   Games found:")
                for date_iso in sorted(overall_scores.keys()):
                    info = game_info.get(date_iso, {})
                    opponent = info.get('opponent', 'Unknown')
                    score = overall_scores[date_iso]
                    print(f"     • {date_iso} vs {opponent}: {score:.2f}%")
            
            self.assertGreaterEqual(overall_count, 6, 
                f"Should have at least 6 games in overall_scores, but found {overall_count}")
            self.assertGreaterEqual(game_info_count, 6, 
                f"Should have at least 6 games in game_info, but found {game_info_count}")
            
            print(f"\n   ✅ Found {overall_count} games (expected 6+)")
        else:
            print(f"   ❌ API failed: {data.get('error', 'Unknown error')}")
            self.fail(f"API returned success=false: {data.get('error')}")
    
    def test_04_statistics_data_structure(self):
        """Test that statistics data has correct structure"""
        print("\n📋 Test 4: Statistics Data Structure")
        
        response = self.app.get('/api/team-statistics')
        data = json.loads(response.data)
        
        if data.get('success') and data.get('statistics'):
            statistics = data['statistics']
            self.assertIsInstance(statistics, list, "Statistics should be a list")
            
            if len(statistics) > 0:
                first_stat = statistics[0]
                required_fields = ['date', 'category', 'percentage']
                
                for field in required_fields:
                    self.assertIn(field, first_stat, f"Statistics should have '{field}' field")
                
                print(f"   ✓ Statistics is a list with {len(statistics)} records")
                print(f"   ✓ First record has required fields: {', '.join(required_fields)}")
                
                # Check unique dates
                unique_dates = set(s['date'] for s in statistics)
                print(f"   ✓ Unique dates: {len(unique_dates)}")
                
                # Check categories
                unique_categories = set(s['category'] for s in statistics)
                print(f"   ✓ Unique categories: {len(unique_categories)}")
            else:
                print("   ⚠️  No statistics data found")
        else:
            print("   ⚠️  API did not return statistics data")
    
    def test_05_force_recalculate_works(self):
        """Test that force_recalculate parameter works"""
        print("\n🔄 Test 5: Force Recalculate Works")
        
        # First call without force
        response1 = self.app.get('/api/team-statistics')
        data1 = json.loads(response1.data)
        
        # Then call with force
        response2 = self.app.get('/api/team-statistics?force_recalculate=true')
        data2 = json.loads(response2.data)
        
        self.assertEqual(response2.status_code, 200, "Force recalculate should return 200")
        self.assertTrue(data2.get('success'), "Force recalculate should return success")
        
        if data2.get('source') == 'csv_calculated':
            print("   ✓ Force recalculate triggered CSV calculation")
            if data2.get('diagnostics'):
                diag = data2['diagnostics']
                print(f"     • Files found: {diag.get('files_found', 0)}")
                print(f"     • Files processed: {diag.get('files_processed', 0)}")
                print(f"     • Data points: {diag.get('data_points', 0)}")
        else:
            print(f"   ℹ️  Used {data2.get('source', 'unknown')} source")
    
    def test_06_category_filter_works(self):
        """Test that category filter works"""
        print("\n🔍 Test 6: Category Filter Works")
        
        # Get all categories
        response_all = self.app.get('/api/team-statistics')
        data_all = json.loads(response_all.data)
        
        if data_all.get('success') and data_all.get('statistics'):
            all_stats = data_all['statistics']
            all_categories = set(s['category'] for s in all_stats)
            
            print(f"   • Available categories: {len(all_categories)}")
            
            # Test filtering by a specific category
            if len(all_categories) > 0:
                test_category = list(all_categories)[0]
                response_filtered = self.app.get(f'/api/team-statistics?category={test_category}')
                data_filtered = json.loads(response_filtered.data)
                
                if data_filtered.get('success') and data_filtered.get('statistics'):
                    filtered_stats = data_filtered['statistics']
                    filtered_categories = set(s['category'] for s in filtered_stats)
                    
                    print(f"   ✓ Filtered by '{test_category}': {len(filtered_stats)} records")
                    self.assertEqual(len(filtered_categories), 1, 
                        f"Should have only one category after filtering, but found {len(filtered_categories)}")
                    self.assertEqual(list(filtered_categories)[0], test_category,
                        f"Filtered category should be '{test_category}'")

if __name__ == '__main__':
    print("=" * 70)
    print("🧪 TEAM STATISTICS FLASK API TEST SUITE")
    print("=" * 70)
    print()
    
    unittest.main(verbosity=2)

