"""
Statistics Calculator
Calculates percentage statistics for cognitive categories from scorecards.
"""

from typing import Dict, List, Optional
from src.models.scorecard import Scorecard


class StatisticsCalculator:
    """
    Calculates team statistics from scorecards.
    Formula: (positives / (positives + negatives)) * 100
    """
    
    # Category definitions mapping to scorecard fields
    CATEGORIES = {
        'Cutting & Screening': {
            'positive': [
                'cs_denial_positive', 'cs_movement_positive', 
                'cs_body_to_body_positive', 'cs_screen_principle_positive', 
                'cs_cut_fill_positive'
            ],
            'negative': [
                'cs_denial_negative', 'cs_movement_negative',
                'cs_body_to_body_negative', 'cs_screen_principle_negative',
                'cs_cut_fill_negative'
            ]
        },
        'DM Catch': {
            'positive': [
                'dm_catch_back_to_back_positive',
                'dm_catch_uncontested_shot_positive',
                'dm_catch_swing_positive',
                'dm_catch_drive_pass_positive',
                'dm_catch_drive_swing_skip_pass_positive'
            ],
            'negative': [
                'dm_catch_back_to_back_negative',
                'dm_catch_uncontested_shot_negative',
                'dm_catch_swing_negative',
                'dm_catch_drive_pass_negative',
                'dm_catch_drive_swing_skip_pass_negative'
            ]
        },
        'Finishing': {
            'positive': [
                'driving_paint_touch_positive'
            ],
            'negative': [
                'driving_paint_touch_negative'
            ]
        },
        'Footwork': {
            'positive': [],  # Note: Footwork fields may need to be added to scorecard model
            'negative': []
        },
        'Passing': {
            'positive': [],  # Note: Passing fields may need to be added to scorecard model
            'negative': []
        },
        'Positioning': {
            'positive': [
                'offball_positioning_create_shape_positive',
                'offball_positioning_adv_awareness_positive'
            ],
            'negative': [
                'offball_positioning_create_shape_negative',
                'offball_positioning_adv_awareness_negative'
            ]
        },
        'QB12 DM': {
            'positive': [
                'qb12_strong_side_positive', 'qb12_baseline_positive',
                'qb12_fill_behind_positive', 'qb12_weak_side_positive',
                'qb12_roller_positive', 'qb12_skip_pass_positive',
                'qb12_cutter_positive'
            ],
            'negative': [
                'qb12_strong_side_negative', 'qb12_baseline_negative',
                'qb12_fill_behind_negative', 'qb12_weak_side_negative',
                'qb12_roller_negative', 'qb12_skip_pass_negative',
                'qb12_cutter_negative'
            ]
        },
        'Relocation': {
            'positive': [
                'relocation_weak_corner_positive',
                'relocation_45_cut_positive',
                'relocation_slide_away_positive',
                'relocation_fill_behind_positive',
                'relocation_dunker_baseline_positive',
                'relocation_corner_fill_positive',
                'relocation_reverse_direction_positive'
            ],
            'negative': [
                'relocation_weak_corner_negative',
                'relocation_45_cut_negative',
                'relocation_slide_away_negative',
                'relocation_fill_behind_negative',
                'relocation_dunker_baseline_negative',
                'relocation_corner_fill_negative',
                'relocation_reverse_direction_negative'
            ]
        },
        'Space Read': {
            'positive': [
                'space_read_live_dribble',
                'space_read_catch'
            ],
            'negative': [
                'space_read_live_dribble_negative',
                'space_read_catch_negative'
            ]
        },
        'Transition': {
            'positive': [
                'transition_effort_pace_positive'
            ],
            'negative': [
                'transition_effort_pace_negative'
            ]
        }
    }
    
    @staticmethod
    def calculate_category_percentage(scorecards: List[Scorecard], category: str) -> Optional[float]:
        """
        Calculate percentage for a specific category across multiple scorecards.
        
        Args:
            scorecards (List[Scorecard]): List of scorecards to aggregate
            category (str): Category name (must be in CATEGORIES)
            
        Returns:
            Optional[float]: Percentage (0-100), or None if category not found or no data
        """
        if category not in StatisticsCalculator.CATEGORIES:
            return None
        
        category_def = StatisticsCalculator.CATEGORIES[category]
        
        total_positive = 0
        total_negative = 0
        
        for scorecard in scorecards:
            sc_dict = scorecard.to_dict()
            
            # Sum positive values
            for field in category_def['positive']:
                total_positive += sc_dict.get(field, 0)
            
            # Sum negative values
            for field in category_def['negative']:
                total_negative += sc_dict.get(field, 0)
        
        # Calculate percentage
        total_attempts = total_positive + total_negative
        if total_attempts == 0:
            return None
        
        percentage = (total_positive / total_attempts) * 100
        return round(percentage, 2)
    
    @staticmethod
    def calculate_all_categories(scorecards: List[Scorecard]) -> Dict[str, Optional[float]]:
        """
        Calculate percentages for all categories.
        
        Args:
            scorecards (List[Scorecard]): List of scorecards to aggregate
            
        Returns:
            Dict[str, Optional[float]]: Dictionary mapping category names to percentages
        """
        results = {}
        for category in StatisticsCalculator.CATEGORIES.keys():
            results[category] = StatisticsCalculator.calculate_category_percentage(scorecards, category)
        return results
    
    @staticmethod
    def get_category_color(category: str) -> str:
        """
        Get the color for a category.
        
        Args:
            category (str): Category name
            
        Returns:
            str: Hex color code
        """
        colors = {
            'Cutting & Screening': '#FF6B6B',
            'DM Catch': '#4ECDC4',
            'Finishing': '#FFE66D',
            'Footwork': '#95E1D3',
            'Passing': '#F38181',
            'Positioning': '#AA96DA',
            'QB12 DM': '#FCBAD3',
            'Relocation': '#A8E6CF',
            'Space Read': '#FFD3A5',
            'Transition': '#C7CEEA'
        }
        return colors.get(category, '#CCCCCC')

