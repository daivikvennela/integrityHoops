from datetime import datetime
from typing import Optional


class Scorecard:
    """
    Scorecard class representing a player's performance scorecard.
    """
    
    def __init__(self, player_name: str, date_created: Optional[int] = None):
        """
        Initialize a new Scorecard instance.
        
        Args:
            player_name (str): The name of the player this scorecard belongs to
            date_created (int, optional): Unix timestamp of creation date. 
                                        If None, uses current timestamp.
        """
        self.player_name = player_name
        self.date_created = date_created or int(datetime.now().timestamp())
    
    def to_dict(self) -> dict:
        """
        Convert scorecard to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the scorecard
        """
        return {
            'player_name': self.player_name,
            'date_created': self.date_created
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Scorecard':
        """
        Create a Scorecard instance from dictionary data.
        
        Args:
            data (dict): Dictionary containing scorecard data
            
        Returns:
            Scorecard: New Scorecard instance
        """
        return cls(data['player_name'], data['date_created'])
    
    def __str__(self) -> str:
        """String representation of the scorecard."""
        return f"Scorecard(player_name='{self.player_name}', date_created={self.date_created})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the scorecard."""
        return f"Scorecard(player_name='{self.player_name}', date_created={self.date_created})"
    
    def __eq__(self, other) -> bool:
        """Check if two scorecards are equal."""
        if not isinstance(other, Scorecard):
            return False
        return (self.player_name == other.player_name and 
                self.date_created == other.date_created)
    
    def __hash__(self) -> int:
        """Hash the scorecard for use in sets and as dictionary keys."""
        return hash((self.player_name, self.date_created)) 