from datetime import datetime
from typing import List, Optional
from src.models.scorecard import Scorecard


class Player:
    """
    Player class representing a basketball player with associated scorecards.
    """
    
    def __init__(self, name: str, date_created: Optional[int] = None):
        """
        Initialize a new Player instance.
        
        Args:
            name (str): The player's name
            date_created (int, optional): Unix timestamp of creation date. 
                                        If None, uses current timestamp.
        """
        self.name = name
        self.date_created = date_created or int(datetime.now().timestamp())
        self.scorecards: List[Scorecard] = []
    
    def add_scorecard(self, scorecard: Scorecard) -> None:
        """
        Add a scorecard to the player's list of scorecards.
        
        Args:
            scorecard (Scorecard): The scorecard to add
        """
        if not isinstance(scorecard, Scorecard):
            raise ValueError("scorecard must be an instance of Scorecard")
        self.scorecards.append(scorecard)
    
    def remove_scorecard(self, scorecard: Scorecard) -> bool:
        """
        Remove a scorecard from the player's list.
        
        Args:
            scorecard (Scorecard): The scorecard to remove
            
        Returns:
            bool: True if scorecard was found and removed, False otherwise
        """
        try:
            self.scorecards.remove(scorecard)
            return True
        except ValueError:
            return False
    
    def get_scorecards(self) -> List[Scorecard]:
        """
        Get all scorecards for this player.
        
        Returns:
            List[Scorecard]: List of all scorecards
        """
        return self.scorecards.copy()
    
    def to_dict(self) -> dict:
        """
        Convert player to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the player
        """
        return {
            'name': self.name,
            'date_created': self.date_created,
            'scorecards': [scorecard.to_dict() for scorecard in self.scorecards]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """
        Create a Player instance from dictionary data.
        
        Args:
            data (dict): Dictionary containing player data
            
        Returns:
            Player: New Player instance
        """
        player = cls(data['name'], data['date_created'])
        for scorecard_data in data.get('scorecards', []):
            scorecard = Scorecard.from_dict(scorecard_data)
            player.add_scorecard(scorecard)
        return player
    
    def __str__(self) -> str:
        """String representation of the player."""
        return f"Player(name='{self.name}', scorecards_count={len(self.scorecards)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the player."""
        return f"Player(name='{self.name}', date_created={self.date_created}, scorecards={self.scorecards})" 