from datetime import datetime
from typing import Optional


class Game:
    """
    Game class representing a basketball game.
    """
    
    def __init__(self, game_id: str, date: int, date_string: str, opponent: str, 
                 team: str = "Heat", created_at: Optional[int] = None):
        """
        Initialize a new Game instance.
        
        Args:
            game_id (str): Deterministic hash-based game ID
            date (int): Unix timestamp of the game date
            date_string (str): Human-readable date string (MM.DD.YY format)
            opponent (str): Opponent team name
            team (str): Team name (default: "Heat")
            created_at (int, optional): Unix timestamp of creation. If None, uses current timestamp.
        """
        self.id = game_id
        self.date = date
        self.date_string = date_string
        self.opponent = opponent
        self.team = team
        self.created_at = created_at or int(datetime.now().timestamp())
    
    def to_dict(self) -> dict:
        """
        Convert game to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the game
        """
        return {
            'id': self.id,
            'date': self.date,
            'date_string': self.date_string,
            'opponent': self.opponent,
            'team': self.team,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Game':
        """
        Create a Game instance from dictionary data.
        
        Args:
            data (dict): Dictionary containing game data
            
        Returns:
            Game: New Game instance
        """
        return cls(
            game_id=data['id'],
            date=data['date'],
            date_string=data['date_string'],
            opponent=data['opponent'],
            team=data.get('team', 'Heat'),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        """String representation of the game."""
        return f"Game({self.date_string} {self.team} vs {self.opponent})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the game."""
        return f"Game(id={self.id}, date={self.date_string}, team={self.team}, opponent={self.opponent})"
    
    def __eq__(self, other) -> bool:
        """Check if two games are equal."""
        if not isinstance(other, Game):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash the game for use in sets and as dictionary keys."""
        return hash(self.id)

