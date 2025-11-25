#!/usr/bin/env python3
"""
Process new CSV files and add scores to player dashboard
Calculates cognitive scores and stores them in the database
"""

import sys
import os
from datetime import datetime
import re

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.processors.cog_score_calculator import CogScoreCalculator
from src.database.db_manager import DatabaseManager
from src.core.app import parse_date_from_filename

def process_csv_file(csv_path, db_manager):
    """Process a single CSV file and add scores to database"""
    filename = os.path.basename(csv_path)
    print(f"\n📊 Processing: {filename}")
    
    try:
        # Parse date and opponent from filename
        date_string, date_iso, opponent, full_filename = parse_date_from_filename(filename)
        
        if not date_string or not date_iso:
            print(f"  ❌ Could not parse date from filename: {filename}")
            return False
        
        print(f"  📅 Date: {date_string} ({date_iso})")
        print(f"  🏀 Opponent: {opponent or 'Unknown'}")
        
        # Calculate scores
        calculator = CogScoreCalculator(csv_path)
        scores, overall = calculator.calculate_all_scores()
        
        print(f"  ✅ Overall Score: {overall:.2f}%")
        print(f"  📈 Categories: {len(scores)}")
        
        # Convert date_iso to timestamp
        dt = datetime.strptime(date_iso, '%Y-%m-%d')
        game_date_timestamp = int(dt.timestamp())
        
        # Determine team name (default to Heat)
        team = 'Heat'
        
        # Check if already exists
        if db_manager.team_cog_score_exists(game_date_timestamp, team, opponent or 'Unknown'):
            print(f"  ⚠️  Score already exists in database, updating...")
        
        # Store team score
        overall_int = int(round(overall))
        result = db_manager.upsert_team_cog_score(
            game_date=game_date_timestamp,
            team=team,
            opponent=opponent or 'Unknown',
            score=overall_int,
            source='csv',
            note=f'Processed from {filename}'
        )
        
        if result is True:
            print(f"  ✅ Successfully stored team score in database")
        else:
            print(f"  ❌ Failed to store team score")
            return False
        
        # Store category statistics in team_statistics table
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
        
        categories_stored = 0
        for csv_col, display_name in COLUMN_NAME_MAP.items():
            if csv_col in scores and display_name in DISPLAY_CATEGORIES:
                score_data = scores[csv_col]
                percentage = score_data['score']
                positive_count = score_data.get('positive', 0)
                negative_count = score_data.get('negative', 0)
                total_count = score_data.get('total', 0)
                
                # Store in team_statistics table
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
                    csv_filename=filename
                )
                categories_stored += 1
        
        print(f"  ✅ Stored {categories_stored} category statistics")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to process new CSV files"""
    print("=" * 70)
    print("🚀 PROCESSING NEW CSV FILES FOR PLAYER DASHBOARD")
    print("=" * 70)
    
    # Get database path
    db_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'src', 'core', 'data', 'basketball.db'
    ))
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"📁 Database: {db_path}")
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path)
    db_manager.init_database()
    
    # Find CSV files in testcases directory
    test_csvs_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'testcases', 'test_csvs'
    ))
    
    if not os.path.exists(test_csvs_dir):
        print(f"❌ Test CSVs directory not found: {test_csvs_dir}")
        return
    
    print(f"📁 CSV Directory: {test_csvs_dir}")
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(test_csvs_dir) if f.endswith('.csv')]
    csv_files.sort()
    
    print(f"\n📋 Found {len(csv_files)} CSV files")
    
    # Process each CSV file
    processed = []
    failed = []
    
    for csv_file in csv_files:
        csv_path = os.path.join(test_csvs_dir, csv_file)
        if process_csv_file(csv_path, db_manager):
            processed.append(csv_file)
        else:
            failed.append(csv_file)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PROCESSING SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully processed: {len(processed)}")
    for f in processed:
        print(f"   - {f}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for f in failed:
            print(f"   - {f}")
    
    print("\n✅ Done! Scores are now available in the player dashboard.")
    print("=" * 70)

if __name__ == '__main__':
    main()

