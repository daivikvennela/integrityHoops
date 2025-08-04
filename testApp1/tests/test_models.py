#!/usr/bin/env python3
"""
Test script for Player and Scorecard models with database CRUD operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models import Player, Scorecard
from src.database import DatabaseManager
from datetime import datetime


def test_player_and_scorecard():
    """Test the Player and Scorecard classes with database operations."""
    
    print("🏀 Basketball Player and Scorecard Test")
    print("=" * 50)
    
    # Initialize database manager
    db = DatabaseManager("data/test_basketball.db")
    
    # Test 1: Create players
    print("\n1. Creating players...")
    player1 = Player("LeBron James")
    player2 = Player("Stephen Curry")
    player3 = Player("Kevin Durant")
    
    # Add players to database
    for player in [player1, player2, player3]:
        success = db.create_player(player)
        print(f"   Created {player.name}: {'✅' if success else '❌'}")
    
    # Test 2: Create scorecards
    print("\n2. Creating scorecards...")
    scorecard1 = Scorecard("LeBron James")
    scorecard2 = Scorecard("LeBron James")
    scorecard3 = Scorecard("Stephen Curry")
    scorecard4 = Scorecard("Kevin Durant")
    
    # Add scorecards to database
    for scorecard in [scorecard1, scorecard2, scorecard3, scorecard4]:
        success = db.create_scorecard(scorecard)
        print(f"   Created scorecard for {scorecard.player_name}: {'✅' if success else '❌'}")
    
    # Test 3: Retrieve all players
    print("\n3. Retrieving all players...")
    players = db.get_all_players()
    for player in players:
        print(f"   Player: {player.name} (Created: {datetime.fromtimestamp(player.date_created)})")
        print(f"   Scorecards: {len(player.scorecards)}")
    
    # Test 4: Get specific player
    print("\n4. Retrieving specific player...")
    lebron = db.get_player_by_name("LeBron James")
    if lebron:
        print(f"   Found: {lebron.name}")
        print(f"   Scorecards: {len(lebron.scorecards)}")
        for scorecard in lebron.scorecards:
            print(f"     - Scorecard created: {datetime.fromtimestamp(scorecard.date_created)}")
    
    # Test 5: Update player
    print("\n5. Updating player...")
    if lebron:
        old_timestamp = lebron.date_created
        lebron.date_created = int(datetime.now().timestamp())
        success = db.update_player(lebron)
        print(f"   Updated {lebron.name}: {'✅' if success else '❌'}")
    
    # Test 6: Database statistics
    print("\n6. Database statistics...")
    stats = db.get_database_stats()
    print(f"   Players: {stats['player_count']}")
    print(f"   Scorecards: {stats['scorecard_count']}")
    print(f"   Database: {stats['database_path']}")
    
    # Test 7: Delete operations
    print("\n7. Testing delete operations...")
    
    # Delete a scorecard
    if lebron and lebron.scorecards:
        scorecard_to_delete = lebron.scorecards[0]
        success = db.delete_scorecard(scorecard_to_delete.player_name, scorecard_to_delete.date_created)
        print(f"   Deleted scorecard for {scorecard_to_delete.player_name}: {'✅' if success else '❌'}")
    
    # Delete a player
    success = db.delete_player("Kevin Durant")
    print(f"   Deleted player Kevin Durant: {'✅' if success else '❌'}")
    
    # Final statistics
    print("\n8. Final database statistics...")
    stats = db.get_database_stats()
    print(f"   Players: {stats['player_count']}")
    print(f"   Scorecards: {stats['scorecard_count']}")
    
    print("\n✅ Test completed successfully!")


def test_model_methods():
    """Test the model methods directly."""
    
    print("\n🧪 Testing Model Methods")
    print("=" * 30)
    
    # Test Player class
    player = Player("Test Player")
    print(f"Player: {player}")
    print(f"Player dict: {player.to_dict()}")
    
    # Test Scorecard class
    scorecard = Scorecard("Test Player")
    print(f"Scorecard: {scorecard}")
    print(f"Scorecard dict: {scorecard.to_dict()}")
    
    # Test adding scorecard to player
    player.add_scorecard(scorecard)
    print(f"Player with scorecard: {player}")
    
    # Test from_dict methods
    player_dict = player.to_dict()
    new_player = Player.from_dict(player_dict)
    print(f"Recreated player: {new_player}")


if __name__ == "__main__":
    test_model_methods()
    test_player_and_scorecard() 