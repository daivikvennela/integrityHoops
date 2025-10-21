#!/usr/bin/env python3
"""
Test script to verify database connection and player retrieval.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager
from datetime import datetime

def test_database_connection():
    """Test database connection and player retrieval."""
    
    print("🔍 Testing Database Connection")
    print("=" * 40)
    
    # Test with correct path
    print("\n1. Testing with correct database path...")
    try:
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'core', 'data', 'basketball.db'))
        db_manager = DatabaseManager(db_path)
        players = db_manager.get_all_players()
        print(f"   ✅ Found {len(players)} players in database")
        
        if players:
            print("   Players found:")
            for player in players:
                created_date = datetime.fromtimestamp(player.date_created)
                print(f"   - {player.name} (Created: {created_date})")
        else:
            print("   ⚠️  No players found in database")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with default path (should fail or be empty)
    print("\n2. Testing with default database path...")
    try:
        db_manager_default = DatabaseManager()
        players_default = db_manager_default.get_all_players()
        print(f"   📊 Found {len(players_default)} players in default database")
        
        if players_default:
            print("   Players in default database:")
            for player in players_default:
                created_date = datetime.fromtimestamp(player.date_created)
                print(f"   - {player.name} (Created: {created_date})")
        else:
            print("   ✅ No players in default database (expected)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    test_database_connection() 