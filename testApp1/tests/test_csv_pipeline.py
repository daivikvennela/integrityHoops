"""
Test Cases for CSV Processing Pipeline
Tests the complete workflow from CSV upload to database storage.
"""

import unittest
import os
import tempfile
import shutil
from src.processors.csv_preprocessor import CSVPreprocessor
from src.services.game_validator import GameValidator
from src.processors.csv_to_database_importer import CSVToDatabaseImporter
from src.database.db_manager import DatabaseManager
from src.utils.game_id_generator import generate_game_id


class TestCSVPreprocessor(unittest.TestCase):
    """Test CSV preprocessing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_csvs_dir = os.path.join(
            os.path.dirname(__file__), 
            '..', 'testcases', 'test_csvs'
        )
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_filename_parsing(self):
        """Test parsing game metadata from filename."""
        test_filename = "10.12.25 MIA v ORL(team).csv"
        test_path = os.path.join(self.temp_dir, test_filename)
        
        # Create dummy file
        with open(test_path, 'w') as f:
            f.write("Timeline,Start time,Duration,Row\n")
            f.write("10.12.25 MIA v ORL Team,100,10,Miami Heat\n")
        
        preprocessor = CSVPreprocessor(test_path, self.temp_dir)
        date, opponent = preprocessor.parse_filename_metadata()
        
        self.assertEqual(date, "10.12.25")
        self.assertEqual(opponent, "ORL")
    
    def test_game_id_generation(self):
        """Test that game_id is generated correctly."""
        date = "10.12.25"
        opponent = "ORL"
        team = "Heat"
        
        game_id = generate_game_id(date, opponent, team)
        
        self.assertIsNotNone(game_id)
        self.assertEqual(len(game_id), 16)  # SHA256 hash truncated to 16 chars
        
        # Test determinism - same inputs should produce same game_id
        game_id2 = generate_game_id(date, opponent, team)
        self.assertEqual(game_id, game_id2)
    
    def test_csv_loading(self):
        """Test loading CSV file."""
        test_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(test_path, 'w') as f:
            f.write("Timeline,Start time,Duration,Row,Instance number\n")
            f.write("10.12.25 MIA v ORL Team,100,10,Miami Heat,1\n")
            f.write("10.12.25 MIA v ORL Team,110,10,Jimmy Butler,1\n")
        
        preprocessor = CSVPreprocessor(test_path, self.temp_dir)
        df = preprocessor.load_csv()
        
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)
        self.assertIn('Row', df.columns)
    
    def test_split_by_row(self):
        """Test splitting CSV by Row column."""
        test_path = os.path.join(self.temp_dir, "10.12.25 MIA v ORL.csv")
        
        with open(test_path, 'w') as f:
            f.write("Timeline,Start time,Duration,Row,Instance number\n")
            f.write("10.12.25 MIA v ORL Team,100,10,Miami Heat,1\n")
            f.write("10.12.25 MIA v ORL Team,110,10,Miami Heat,2\n")
            f.write("10.12.25 MIA v ORL Team,120,10,Jimmy Butler,1\n")
            f.write("10.12.25 MIA v ORL Team,130,10,Bam Adebayo,1\n")
        
        preprocessor = CSVPreprocessor(test_path, self.temp_dir)
        preprocessor.load_csv()
        split_dfs = preprocessor.split_by_row()
        
        self.assertEqual(len(split_dfs), 3)  # Miami Heat, Jimmy Butler, Bam Adebayo
        self.assertIn('Miami Heat', split_dfs)
        self.assertIn('Jimmy Butler', split_dfs)
        self.assertIn('Bam Adebayo', split_dfs)
        self.assertEqual(len(split_dfs['Miami Heat']), 2)
        self.assertEqual(len(split_dfs['Jimmy Butler']), 1)


class TestGameValidator(unittest.TestCase):
    """Test game validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.validator = GameValidator(self.db_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_csv_file_validation(self):
        """Test CSV file validation."""
        # Test non-existent file
        result = self.validator.validate_csv_file('/nonexistent/file.csv')
        self.assertFalse(result['valid'])
        
        # Test non-CSV file
        txt_path = os.path.join(self.temp_dir, 'test.txt')
        with open(txt_path, 'w') as f:
            f.write("test")
        
        result = self.validator.validate_csv_file(txt_path)
        self.assertFalse(result['valid'])
        
        # Test valid CSV file
        csv_path = os.path.join(self.temp_dir, '10.12.25 MIA v ORL.csv')
        with open(csv_path, 'w') as f:
            f.write("Timeline,Row\n")
            f.write("10.12.25 MIA v ORL Team,Miami Heat\n")
        
        result = self.validator.validate_csv_file(csv_path)
        self.assertTrue(result['valid'])
    
    def test_filename_parsing(self):
        """Test parsing filename for game metadata."""
        test_cases = [
            ('10.12.25 MIA v ORL.csv', ('10.12.25', 'ORL')),
            ('10.13.25 MIA v ATL(team).csv', ('10.13.25', 'ATL')),
            ('invalid_filename.csv', (None, None))
        ]
        
        for filename, expected in test_cases:
            filepath = os.path.join(self.temp_dir, filename)
            date, opponent = self.validator.parse_filename(filepath)
            self.assertEqual((date, opponent), expected)
    
    def test_duplicate_detection(self):
        """Test duplicate game detection."""
        from src.models.game import Game
        from src.utils.game_id_generator import date_string_to_timestamp
        
        # Create a game
        date_string = "10.12.25"
        opponent = "ORL"
        team = "Heat"
        game_id = generate_game_id(date_string, opponent, team)
        
        game = Game(
            game_id=game_id,
            date=date_string_to_timestamp(date_string),
            date_string=date_string,
            opponent=opponent,
            team=team
        )
        
        self.db_manager.create_game(game)
        
        # Check for duplicate
        is_duplicate, existing_id = self.validator.is_duplicate_game(date_string, opponent, team)
        
        self.assertTrue(is_duplicate)
        self.assertEqual(existing_id, game_id)
        
        # Check for non-duplicate
        is_duplicate, _ = self.validator.is_duplicate_game("10.13.25", "ATL", team)
        self.assertFalse(is_duplicate)


class TestCSVToDatabaseImporter(unittest.TestCase):
    """Test CSV to database import functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.importer = CSVToDatabaseImporter(self.db_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_import_mega_csv(self):
        """Test importing a mega CSV with team and player data."""
        # Create test CSV
        csv_path = os.path.join(self.temp_dir, "10.12.25 MIA v ORL.csv")
        
        with open(csv_path, 'w') as f:
            f.write("Timeline,Start time,Duration,Row,Instance number,")
            f.write("Cutting & Screeing,DM Catch,Driving,Finishing,Footwork,")
            f.write("Passing,Points,Positioning,QB12 DM,Relocation,")
            f.write("Shot Location,Shot Outcome,Shot Specific,Space Read,Transition,Ungrouped\n")
            
            # Team row
            f.write("10.12.25 MIA v ORL Team,100,10,Miami Heat,1,")
            f.write("+ve Cutting & Screening: Movement,+ve DM Catch: Swing,")
            f.write("+ve Driving: Paint Touch,+ve Finishing: Stride Pivot,,")
            f.write("+ve Passing: Teammate on the Move,,,+ve QB12: Strong Side,")
            f.write("+ve Relocate: Fill Behind,Short 2,Miss Short,6z7,")
            f.write("+ve Space Read: Catch,+ve Transition: Effort and Pace,Neutral\n")
            
            # Player rows
            f.write("10.12.25 MIA v ORL Team,110,10,Jimmy Butler,1,")
            f.write("+ve Cutting & Screening: Movement,+ve DM Catch: Swing,")
            f.write("+ve Driving: Paint Touch,+ve Finishing: Stride Pivot,,")
            f.write("+ve Passing: Teammate on the Move,,,+ve QB12: Strong Side,")
            f.write("+ve Relocate: Fill Behind,Short 2,Made,6z7,")
            f.write("+ve Space Read: Catch,+ve Transition: Effort and Pace,Neutral\n")
        
        # Import
        result = self.importer.import_mega_csv(csv_path)
        
        # Assertions
        self.assertTrue(result['success'], f"Import failed: {result.get('error')}")
        self.assertIn('game_id', result)
        self.assertEqual(result['date'], '10.12.25')
        self.assertEqual(result['opponent'], 'ORL')
        self.assertGreaterEqual(result['players_processed'], 0)
        
        # Verify game was created
        game = self.db_manager.get_game_by_id(result['game_id'])
        self.assertIsNotNone(game)
    
    def test_duplicate_game_prevention(self):
        """Test that duplicate games are prevented."""
        csv_path = os.path.join(self.temp_dir, "10.12.25 MIA v ORL.csv")
        
        with open(csv_path, 'w') as f:
            f.write("Timeline,Start time,Duration,Row,Instance number\n")
            f.write("10.12.25 MIA v ORL Team,100,10,Miami Heat,1\n")
        
        # First import should succeed
        result1 = self.importer.import_mega_csv(csv_path)
        self.assertTrue(result1['success'])
        
        # Second import should fail (duplicate)
        result2 = self.importer.import_mega_csv(csv_path)
        self.assertFalse(result2['success'])
        self.assertTrue(result2.get('duplicate', False))


class TestPipelineIntegration(unittest.TestCase):
    """Test complete pipeline integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test the complete CSV processing workflow."""
        # Create test CSV
        csv_path = os.path.join(self.temp_dir, "10.12.25 MIA v ORL.csv")
        
        with open(csv_path, 'w') as f:
            f.write("Timeline,Start time,Duration,Row,Instance number,")
            f.write("Cutting & Screeing,DM Catch,Space Read,Transition\n")
            
            # Team data
            f.write("10.12.25 MIA v ORL Team,100,10,Miami Heat,1,")
            f.write("+ve Cutting & Screening: Movement,+ve DM Catch: Swing,")
            f.write("+ve Space Read: Catch,+ve Transition: Effort and Pace\n")
            
            # Player 1
            f.write("10.12.25 MIA v ORL Team,110,10,Jimmy Butler,1,")
            f.write("+ve Cutting & Screening: Movement,+ve DM Catch: Swing,")
            f.write("+ve Space Read: Catch,+ve Transition: Effort and Pace\n")
            
            # Player 2
            f.write("10.12.25 MIA v ORL Team,120,10,Bam Adebayo,1,")
            f.write("-ve Cutting & Screening: Denial,+ve DM Catch: Uncontested Shot,")
            f.write("-ve Space Read: Catch,-ve Transition: Effort and Pace\n")
        
        # Initialize components
        db_manager = DatabaseManager(self.db_path)
        importer = CSVToDatabaseImporter(db_manager)
        
        # Execute import
        result = importer.import_mega_csv(csv_path)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertIn('game_id', result)
        
        game_id = result['game_id']
        
        # Verify game exists
        game = db_manager.get_game_by_id(game_id)
        self.assertIsNotNone(game)
        self.assertEqual(game['opponent'], 'ORL')
        
        # Verify players exist
        players = db_manager.get_players_by_game(game_id)
        self.assertGreaterEqual(len(players), 1)  # At least one player
        
        # Verify scorecards exist
        all_games = db_manager.get_games_with_stats()
        game_data = next((g for g in all_games if g['game_id'] == game_id), None)
        self.assertIsNotNone(game_data)
        self.assertGreaterEqual(game_data.get('scorecard_count', 0), 1)


def run_all_tests():
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCSVPreprocessor))
    suite.addTests(loader.loadTestsFromTestCase(TestGameValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestCSVToDatabaseImporter))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_all_tests()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Please review the output above.")

