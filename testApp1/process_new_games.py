#!/usr/bin/env python3
"""
Process new CSV game files using the standard CSV processing pipeline.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.db_manager import DatabaseManager
from src.processors.csv_to_database_importer import CSVToDatabaseImporter
from src.core.app import DATA_ROOT, DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_csv_files(root_dir):
    """Find all CSV files in the root directory and subdirectories."""
    csv_files = []
    root_path = Path(root_dir)
    
    # Look for CSV files in root and immediate subdirectories
    for item in root_path.iterdir():
        if item.is_file() and item.suffix.lower() == '.csv':
            # Skip if it's a processed file or in test_csvs
            if 'processed' not in str(item) and 'test_csvs' not in str(item):
                csv_files.append(item)
        elif item.is_dir() and not item.name.startswith('.') and item.name != 'testApp1':
            # Look in subdirectories
            for subitem in item.iterdir():
                if subitem.is_file() and subitem.suffix.lower() == '.csv':
                    # Prefer files with "Table 1" or "Sheet 1" in name, or main CSV
                    if 'Table 1' in subitem.name or 'Sheet 1' in subitem.name or not any(x in subitem.name for x in ['Table', 'Sheet']):
                        csv_files.append(subitem)
    
    return csv_files

def process_csv_files():
    """Process all found CSV files."""
    # Initialize database manager
    db_path = DB_PATH
    logger.info(f"Using database: {db_path}")
    
    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}, creating...")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    db_manager = DatabaseManager(db_path)
    importer = CSVToDatabaseImporter(db_manager)
    
    # Find CSV files in the parent directory
    parent_dir = Path(__file__).parent.parent
    logger.info(f"Searching for CSV files in: {parent_dir}")
    
    csv_files = find_csv_files(parent_dir)
    
    if not csv_files:
        logger.warning("No CSV files found!")
        return
    
    logger.info(f"Found {len(csv_files)} CSV file(s) to process:")
    for csv_file in csv_files:
        logger.info(f"  - {csv_file}")
    
    # Process each CSV file
    success_count = 0
    error_count = 0
    
    for csv_file in csv_files:
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"Processing: {csv_file.name}")
            logger.info(f"Full path: {csv_file}")
            logger.info(f"{'='*70}")
            
            result = importer.import_mega_csv(str(csv_file))
            
            if result.get('success'):
                success_count += 1
                logger.info(f"✅ Successfully processed: {csv_file.name}")
                logger.info(f"   Game ID: {result.get('game_id', 'N/A')}")
                logger.info(f"   Players processed: {result.get('players_processed', 0)}")
                logger.info(f"   Scorecards created: {result.get('scorecards_created', 0)}")
            else:
                error_count += 1
                error_msg = result.get('error', 'Unknown error')
                if 'duplicate' in error_msg.lower() or 'already exists' in error_msg.lower():
                    logger.warning(f"⚠️  Skipped (duplicate): {csv_file.name} - {error_msg}")
                else:
                    logger.error(f"❌ Failed to process: {csv_file.name} - {error_msg}")
                    
        except Exception as e:
            error_count += 1
            logger.exception(f"❌ Exception processing {csv_file.name}: {e}")
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing complete!")
    logger.info(f"  ✅ Success: {success_count}")
    logger.info(f"  ❌ Errors: {error_count}")
    logger.info(f"  📊 Total: {len(csv_files)}")
    logger.info(f"{'='*70}")

if __name__ == '__main__':
    process_csv_files()

