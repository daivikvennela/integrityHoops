#!/usr/bin/env python3
"""
Test cases for Team Statistics API
Tests CSV processing, score calculation, and database storage
"""

import unittest
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.processors.cog_score_calculator import CogScoreCalculator
from src.database.db_manager import DatabaseManager
from src.core.app import parse_date_from_filename

class TestTeamStatisticsAPI(unittest.TestCase):
    """Test team statistics API functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_csvs_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'testcases', 'test_csvs'
        ))
        cls.db_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'src', 'core', 'data', 'basketball.db'
        ))
        cls.db_manager = DatabaseManager(cls.db_path)
        cls.db_manager.init_database()
        
    def test_01_csv_files_exist(self):
        """Test that all 6 CSV files exist"""
        csv_files = [f for f in os.listdir(self.test_csvs_dir) if f.endswith('.csv')]
        csv_files.sort()
        
        print(f"\n📋 Found {len(csv_files)} CSV files:")
        for f in csv_files:
            print(f"   ✓ {f}")
        
        self.assertGreaterEqual(len(csv_files), 6, "Should have at least 6 CSV files")
        
        # Verify expected files exist
        expected_files = [
            '10.04.25 Heat v Magic(team).csv',
            '10.06.25 Heat v Bucks(team).csv',
            '10.12.25 MIA v ORL(team).csv',
            '10.13.25 MIA v ATL Team(1).csv',
            '10.24.25 MIA v MEM(team).csv',
            '10.26.25 MIA v NYK.csv'
        ]
        
        for expected_file in expected_files:
            file_path = os.path.join(self.test_csvs_dir, expected_file)
            self.assertTrue(os.path.exists(file_path), f"Expected file not found: {expected_file}")
            print(f"   ✓ {expected_file} exists")
    
    def test_02_csv_files_parseable(self):
        """Test that CSV files can be parsed and dates extracted"""
        csv_files = [f for f in os.listdir(self.test_csvs_dir) if f.endswith('.csv')]
        
        parsed_count = 0
        for csv_file in csv_files:
            date_string, date_iso, opponent, full_filename = parse_date_from_filename(csv_file)
            
            if date_string and date_iso:
                parsed_count += 1
                print(f"   ✓ {csv_file}: {date_string} ({date_iso}) vs {opponent}")
            else:
                print(f"   ✗ {csv_file}: Could not parse date")
        
        self.assertGreaterEqual(parsed_count, 6, f"Should parse at least 6 files, but parsed {parsed_count}")
    
    def test_03_scores_calculated(self):
        """Test that scores can be calculated from CSV files"""
        csv_files = [f for f in os.listdir(self.test_csvs_dir) if f.endswith('.csv')]
        csv_files.sort()
        
        calculated_count = 0
        scores_summary = []
        
        for csv_file in csv_files:
            csv_path = os.path.join(self.test_csvs_dir, csv_file)
            
            try:
                calculator = CogScoreCalculator(csv_path)
                scores, overall = calculator.calculate_all_scores()
                
                date_string, date_iso, opponent, _ = parse_date_from_filename(csv_file)
                
                calculated_count += 1
                scores_summary.append({
                    'file': csv_file,
                    'date': date_iso,
                    'opponent': opponent,
                    'overall': overall,
                    'categories': len(scores)
                })
                
                print(f"   ✓ {csv_file}: Overall={overall:.2f}%, Categories={len(scores)}")
                
                # Verify we have some categories
                self.assertGreater(len(scores), 0, f"No categories found for {csv_file}")
                
            except Exception as e:
                print(f"   ✗ {csv_file}: Error calculating scores - {str(e)}")
                raise
        
        self.assertGreaterEqual(calculated_count, 6, f"Should calculate scores for at least 6 files, but calculated {calculated_count}")
        
        # Print summary
        print(f"\n📊 Score Calculation Summary:")
        for summary in scores_summary:
            print(f"   • {summary['date']} vs {summary['opponent']}: {summary['overall']:.2f}%")
    
    def test_04_database_storage(self):
        """Test that scores are stored in database"""
        # Process all CSV files and store in database
        csv_files = [f for f in os.listdir(self.test_csvs_dir) if f.endswith('.csv')]
        csv_files.sort()
        
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
        
        stored_games = []
        
        for csv_file in csv_files:
            csv_path = os.path.join(self.test_csvs_dir, csv_file)
            
            date_string, date_iso, opponent, full_filename = parse_date_from_filename(csv_file)
            if not date_iso:
                continue
            
            try:
                calculator = CogScoreCalculator(csv_path)
                scores, overall = calculator.calculate_all_scores()
                
                dt = datetime.strptime(date_iso, '%Y-%m-%d')
                game_date_timestamp = int(dt.timestamp())
                
                # Store team cog score
                self.db_manager.upsert_team_cog_score(
                    game_date=game_date_timestamp,
                    team='Heat',
                    opponent=opponent or 'Unknown',
                    score=int(round(overall)),
                    source='csv',
                    note=f'Test processed from {csv_file}'
                )
                
                # Store category statistics
                categories_stored = 0
                for csv_col, display_name in COLUMN_NAME_MAP.items():
                    if csv_col in scores and display_name in DISPLAY_CATEGORIES:
                        score_data = scores[csv_col]
                        self.db_manager.insert_team_statistics(
                            game_date_iso=date_iso,
                            game_date_timestamp=game_date_timestamp,
                            date_string=date_string,
                            team='Heat',
                            opponent=opponent or 'Unknown',
                            category=display_name,
                            percentage=score_data['score'],
                            positive_count=score_data.get('positive', 0),
                            negative_count=score_data.get('negative', 0),
                            total_count=score_data.get('total', 0),
                            overall_score=overall,
                            csv_filename=csv_file
                        )
                        categories_stored += 1
                
                stored_games.append({
                    'date': date_iso,
                    'opponent': opponent,
                    'overall': overall,
                    'categories': categories_stored
                })
                
                print(f"   ✓ Stored {csv_file}: {categories_stored} categories")
                
            except Exception as e:
                print(f"   ✗ Error storing {csv_file}: {str(e)}")
                raise
        
        self.assertGreaterEqual(len(stored_games), 6, f"Should store at least 6 games, but stored {len(stored_games)}")
        
        # Verify data in database
        db_stats = self.db_manager.get_team_statistics(team='Heat')
        unique_dates = set(stat['date'] for stat in db_stats)
        
        print(f"\n📊 Database Verification:")
        print(f"   • Total statistics records: {len(db_stats)}")
        print(f"   • Unique game dates: {len(unique_dates)}")
        
        self.assertGreaterEqual(len(unique_dates), 6, f"Should have at least 6 unique game dates, but found {len(unique_dates)}")
        
        # Verify overall scores
        overall_scores = self.db_manager.get_team_statistics_overall_scores(team='Heat')
        print(f"   • Overall scores: {len(overall_scores)}")
        
        for date_iso in sorted(overall_scores.keys()):
            print(f"     - {date_iso}: {overall_scores[date_iso]:.2f}%")
        
        self.assertGreaterEqual(len(overall_scores), 6, f"Should have at least 6 overall scores, but found {len(overall_scores)}")
    
    def test_05_api_response_format(self):
        """Test that API would return correct format"""
        # Get data from database
        db_stats = self.db_manager.get_team_statistics(team='Heat')
        overall_scores = self.db_manager.get_team_statistics_overall_scores(team='Heat')
        game_info = self.db_manager.get_team_statistics_game_info(team='Heat')
        
        # Simulate API response format
        statistics_data = []
        for stat in db_stats:
            statistics_data.append({
                'date': stat['date'],
                'date_string': stat['date_string'],
                'category': stat['category'],
                'percentage': stat['percentage'],
                'opponent': stat['opponent'],
                'filename': stat['filename']
            })
        
        # Verify response structure
        self.assertIsInstance(statistics_data, list, "Statistics should be a list")
        self.assertGreater(len(statistics_data), 0, "Should have statistics data")
        
        self.assertIsInstance(overall_scores, dict, "Overall scores should be a dict")
        self.assertGreaterEqual(len(overall_scores), 6, f"Should have at least 6 overall scores, but found {len(overall_scores)}")
        
        self.assertIsInstance(game_info, dict, "Game info should be a dict")
        self.assertGreaterEqual(len(game_info), 6, f"Should have at least 6 game info entries, but found {len(game_info)}")
        
        # Verify each game has required fields
        for date_iso, info in game_info.items():
            self.assertIn('date_string', info, f"Game info for {date_iso} missing date_string")
            self.assertIn('opponent', info, f"Game info for {date_iso} missing opponent")
            self.assertIn('filename', info, f"Game info for {date_iso} missing filename")
        
        print(f"\n✅ API Response Format Verification:")
        print(f"   • Statistics records: {len(statistics_data)}")
        print(f"   • Overall scores: {len(overall_scores)}")
        print(f"   • Game info entries: {len(game_info)}")
        print(f"   • Unique dates: {len(set(s['date'] for s in statistics_data))}")

if __name__ == '__main__':
    print("=" * 70)
    print("🧪 TEAM STATISTICS API TEST SUITE")
    print("=" * 70)
    print()
    
    unittest.main(verbosity=2)

