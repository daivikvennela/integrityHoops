from datetime import datetime
from typing import Optional


class Scorecard:
    """
    Scorecard class representing a player's performance scorecard.
    """
    
    def __init__(self, player_name: str, date_created: Optional[int] = None, 
                 space_read_live_dribble: int = 0, space_read_catch: int = 0,
                 space_read_live_dribble_negative: int = 0, space_read_catch_negative: int = 0,
                 dm_catch_back_to_back_positive: int = 0, dm_catch_back_to_back_negative: int = 0,
                 dm_catch_uncontested_shot_positive: int = 0, dm_catch_uncontested_shot_negative: int = 0,
                 dm_catch_swing_positive: int = 0, dm_catch_swing_negative: int = 0,
                 dm_catch_drive_pass_positive: int = 0, dm_catch_drive_pass_negative: int = 0,
                 dm_catch_drive_swing_skip_pass_positive: int = 0, dm_catch_drive_swing_skip_pass_negative: int = 0,
                 driving_paint_touch_positive: int = 0, driving_paint_touch_negative: int = 0,
                 driving_physicality_positive: int = 0, driving_physicality_negative: int = 0):
        """
        Initialize a new Scorecard instance.
        
        Args:
            player_name (str): The name of the player this scorecard belongs to
            date_created (int, optional): Unix timestamp of creation date. 
                                        If None, uses current timestamp.
            space_read_live_dribble (int): Count of positive space read live dribble actions
            space_read_catch (int): Count of positive space read catch actions
            space_read_live_dribble_negative (int): Count of negative space read live dribble actions
            space_read_catch_negative (int): Count of negative space read catch actions
            dm_catch_back_to_back_positive (int): Count of positive DM Catch: Back-to-Back actions
            dm_catch_back_to_back_negative (int): Count of negative DM Catch: Back-to-Back actions
            dm_catch_uncontested_shot_positive (int): Count of positive DM Catch: Uncontested Shot actions
            dm_catch_uncontested_shot_negative (int): Count of negative DM Catch: Uncontested Shot actions
            dm_catch_swing_positive (int): Count of positive DM Catch: Swing actions
            dm_catch_swing_negative (int): Count of negative DM Catch: Swing actions
            dm_catch_drive_pass_positive (int): Count of positive DM Catch: Drive Pass actions
            dm_catch_drive_pass_negative (int): Count of negative DM Catch: Drive Pass actions
            dm_catch_drive_swing_skip_pass_positive (int): Count of positive DM Catch: Drive a Swing/Skip Pass actions
            dm_catch_drive_swing_skip_pass_negative (int): Count of negative DM Catch: Drive a Swing/Skip Pass actions
            driving_paint_touch_positive (int): Count of positive driving paint touch actions
            driving_paint_touch_negative (int): Count of negative driving paint touch actions
            driving_physicality_positive (int): Count of positive driving physicality actions
            driving_physicality_negative (int): Count of negative driving physicality actions
        """
        self.player_name = player_name
        self.date_created = date_created or int(datetime.now().timestamp())
        self.space_read_live_dribble = space_read_live_dribble
        self.space_read_catch = space_read_catch
        self.space_read_live_dribble_negative = space_read_live_dribble_negative
        self.space_read_catch_negative = space_read_catch_negative
        self.dm_catch_back_to_back_positive = dm_catch_back_to_back_positive
        self.dm_catch_back_to_back_negative = dm_catch_back_to_back_negative
        self.dm_catch_uncontested_shot_positive = dm_catch_uncontested_shot_positive
        self.dm_catch_uncontested_shot_negative = dm_catch_uncontested_shot_negative
        self.dm_catch_swing_positive = dm_catch_swing_positive
        self.dm_catch_swing_negative = dm_catch_swing_negative
        self.dm_catch_drive_pass_positive = dm_catch_drive_pass_positive
        self.dm_catch_drive_pass_negative = dm_catch_drive_pass_negative
        self.dm_catch_drive_swing_skip_pass_positive = dm_catch_drive_swing_skip_pass_positive
        self.dm_catch_drive_swing_skip_pass_negative = dm_catch_drive_swing_skip_pass_negative
        self.driving_paint_touch_positive = driving_paint_touch_positive
        self.driving_paint_touch_negative = driving_paint_touch_negative
        self.driving_physicality_positive = driving_physicality_positive
        self.driving_physicality_negative = driving_physicality_negative
    
    def to_dict(self) -> dict:
        """
        Convert scorecard to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the scorecard
        """
        return {
            'player_name': self.player_name,
            'date_created': self.date_created,
            'space_read_live_dribble': self.space_read_live_dribble,
            'space_read_catch': self.space_read_catch,
            'space_read_live_dribble_negative': self.space_read_live_dribble_negative,
            'space_read_catch_negative': self.space_read_catch_negative,
            'dm_catch_back_to_back_positive': self.dm_catch_back_to_back_positive,
            'dm_catch_back_to_back_negative': self.dm_catch_back_to_back_negative,
            'dm_catch_uncontested_shot_positive': self.dm_catch_uncontested_shot_positive,
            'dm_catch_uncontested_shot_negative': self.dm_catch_uncontested_shot_negative,
            'dm_catch_swing_positive': self.dm_catch_swing_positive,
            'dm_catch_swing_negative': self.dm_catch_swing_negative,
            'dm_catch_drive_pass_positive': self.dm_catch_drive_pass_positive,
            'dm_catch_drive_pass_negative': self.dm_catch_drive_pass_negative,
            'dm_catch_drive_swing_skip_pass_positive': self.dm_catch_drive_swing_skip_pass_positive,
            'dm_catch_drive_swing_skip_pass_negative': self.dm_catch_drive_swing_skip_pass_negative,
            'driving_paint_touch_positive': self.driving_paint_touch_positive,
            'driving_paint_touch_negative': self.driving_paint_touch_negative,
            'driving_physicality_positive': self.driving_physicality_positive,
            'driving_physicality_negative': self.driving_physicality_negative
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
        return cls(
            data['player_name'], 
            data['date_created'],
            data.get('space_read_live_dribble', 0),
            data.get('space_read_catch', 0),
            data.get('space_read_live_dribble_negative', 0),
            data.get('space_read_catch_negative', 0),
            data.get('dm_catch_back_to_back_positive', 0),
            data.get('dm_catch_back_to_back_negative', 0),
            data.get('dm_catch_uncontested_shot_positive', 0),
            data.get('dm_catch_uncontested_shot_negative', 0),
            data.get('dm_catch_swing_positive', 0),
            data.get('dm_catch_swing_negative', 0),
            data.get('dm_catch_drive_pass_positive', 0),
            data.get('dm_catch_drive_pass_negative', 0),
            data.get('dm_catch_drive_swing_skip_pass_positive', 0),
            data.get('dm_catch_drive_swing_skip_pass_negative', 0),
            data.get('driving_paint_touch_positive', 0),
            data.get('driving_paint_touch_negative', 0),
            data.get('driving_physicality_positive', 0),
            data.get('driving_physicality_negative', 0)
        )
    
    def __str__(self) -> str:
        """String representation of the scorecard."""
        return f"Scorecard(player_name='{self.player_name}', date_created={self.date_created}, space_read_live_dribble={self.space_read_live_dribble}, space_read_catch={self.space_read_catch}, space_read_live_dribble_negative={self.space_read_live_dribble_negative}, space_read_catch_negative={self.space_read_catch_negative}, dm_catch_back_to_back_positive={self.dm_catch_back_to_back_positive}, dm_catch_back_to_back_negative={self.dm_catch_back_to_back_negative}, dm_catch_uncontested_shot_positive={self.dm_catch_uncontested_shot_positive}, dm_catch_uncontested_shot_negative={self.dm_catch_uncontested_shot_negative}, dm_catch_swing_positive={self.dm_catch_swing_positive}, dm_catch_swing_negative={self.dm_catch_swing_negative}, dm_catch_drive_pass_positive={self.dm_catch_drive_pass_positive}, dm_catch_drive_pass_negative={self.dm_catch_drive_pass_negative}, dm_catch_drive_swing_skip_pass_positive={self.dm_catch_drive_swing_skip_pass_positive}, dm_catch_drive_swing_skip_pass_negative={self.dm_catch_drive_swing_skip_pass_negative}, driving_paint_touch_positive={self.driving_paint_touch_positive}, driving_paint_touch_negative={self.driving_paint_touch_negative}, driving_physicality_positive={self.driving_physicality_positive}, driving_physicality_negative={self.driving_physicality_negative})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the scorecard."""
        return f"Scorecard(player_name='{self.player_name}', date_created={self.date_created}, space_read_live_dribble={self.space_read_live_dribble}, space_read_catch={self.space_read_catch}, space_read_live_dribble_negative={self.space_read_live_dribble_negative}, space_read_catch_negative={self.space_read_catch_negative}, dm_catch_back_to_back_positive={self.dm_catch_back_to_back_positive}, dm_catch_back_to_back_negative={self.dm_catch_back_to_back_negative}, dm_catch_uncontested_shot_positive={self.dm_catch_uncontested_shot_positive}, dm_catch_uncontested_shot_negative={self.dm_catch_uncontested_shot_negative}, dm_catch_swing_positive={self.dm_catch_swing_positive}, dm_catch_swing_negative={self.dm_catch_swing_negative}, dm_catch_drive_pass_positive={self.dm_catch_drive_pass_positive}, dm_catch_drive_pass_negative={self.dm_catch_drive_pass_negative}, dm_catch_drive_swing_skip_pass_positive={self.dm_catch_drive_swing_skip_pass_positive}, dm_catch_drive_swing_skip_pass_negative={self.dm_catch_drive_swing_skip_pass_negative}, driving_paint_touch_positive={self.driving_paint_touch_positive}, driving_paint_touch_negative={self.driving_paint_touch_negative}, driving_physicality_positive={self.driving_physicality_positive}, driving_physicality_negative={self.driving_physicality_negative})"
    
    def __eq__(self, other) -> bool:
        """Check if two scorecards are equal."""
        if not isinstance(other, Scorecard):
            return False
        return (self.player_name == other.player_name and 
                self.date_created == other.date_created and
                self.space_read_live_dribble == other.space_read_live_dribble and
                self.space_read_catch == other.space_read_catch and
                self.space_read_live_dribble_negative == other.space_read_live_dribble_negative and
                self.space_read_catch_negative == other.space_read_catch_negative and
                self.dm_catch_back_to_back_positive == other.dm_catch_back_to_back_positive and
                self.dm_catch_back_to_back_negative == other.dm_catch_back_to_back_negative and
                self.dm_catch_uncontested_shot_positive == other.dm_catch_uncontested_shot_positive and
                self.dm_catch_uncontested_shot_negative == other.dm_catch_uncontested_shot_negative and
                self.dm_catch_swing_positive == other.dm_catch_swing_positive and
                self.dm_catch_swing_negative == other.dm_catch_swing_negative and
                self.dm_catch_drive_pass_positive == other.dm_catch_drive_pass_positive and
                self.dm_catch_drive_pass_negative == other.dm_catch_drive_pass_negative and
                self.dm_catch_drive_swing_skip_pass_positive == other.dm_catch_drive_swing_skip_pass_positive and
                self.dm_catch_drive_swing_skip_pass_negative == other.dm_catch_drive_swing_skip_pass_negative and
                self.driving_paint_touch_positive == other.driving_paint_touch_positive and
                self.driving_paint_touch_negative == other.driving_paint_touch_negative and
                self.driving_physicality_positive == other.driving_physicality_positive and
                self.driving_physicality_negative == other.driving_physicality_negative)
    
    def __hash__(self) -> int:
        """Hash the scorecard for use in sets and as dictionary keys."""
        return hash((self.player_name, self.date_created, self.space_read_live_dribble, self.space_read_catch, self.space_read_live_dribble_negative, self.space_read_catch_negative, self.dm_catch_back_to_back_positive, self.dm_catch_back_to_back_negative, self.dm_catch_uncontested_shot_positive, self.dm_catch_uncontested_shot_negative, self.dm_catch_swing_positive, self.dm_catch_swing_negative, self.dm_catch_drive_pass_positive, self.dm_catch_drive_pass_negative, self.dm_catch_drive_swing_skip_pass_positive, self.dm_catch_drive_swing_skip_pass_negative, self.driving_paint_touch_positive, self.driving_paint_touch_negative, self.driving_physicality_positive, self.driving_physicality_negative)) 