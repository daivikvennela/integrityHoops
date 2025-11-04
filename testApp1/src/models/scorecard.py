from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass


class Scorecard:
    """
    Scorecard class representing a player's performance scorecard.
    """
    
    def __init__(self, player_name: str, date_created: Optional[int] = None, 
                 game_id: Optional[str] = None,
                 space_read_live_dribble: int = 0, space_read_catch: int = 0,
                 space_read_live_dribble_negative: int = 0, space_read_catch_negative: int = 0,
                 dm_catch_back_to_back_positive: int = 0, dm_catch_back_to_back_negative: int = 0,
                 dm_catch_uncontested_shot_positive: int = 0, dm_catch_uncontested_shot_negative: int = 0,
                 dm_catch_swing_positive: int = 0, dm_catch_swing_negative: int = 0,
                 dm_catch_drive_pass_positive: int = 0, dm_catch_drive_pass_negative: int = 0,
                 dm_catch_drive_swing_skip_pass_positive: int = 0, dm_catch_drive_swing_skip_pass_negative: int = 0,
                 qb12_strong_side_positive: int = 0, qb12_strong_side_negative: int = 0,
                 qb12_baseline_positive: int = 0, qb12_baseline_negative: int = 0,
                 qb12_fill_behind_positive: int = 0, qb12_fill_behind_negative: int = 0,
                 qb12_weak_side_positive: int = 0, qb12_weak_side_negative: int = 0,
                 qb12_roller_positive: int = 0, qb12_roller_negative: int = 0,
                 qb12_skip_pass_positive: int = 0, qb12_skip_pass_negative: int = 0,
                 qb12_cutter_positive: int = 0, qb12_cutter_negative: int = 0,
                 driving_paint_touch_positive: int = 0, driving_paint_touch_negative: int = 0,
                 driving_physicality_positive: int = 0, driving_physicality_negative: int = 0,
                 # Off Ball - Positioning
                 offball_positioning_create_shape_positive: int = 0,
                 offball_positioning_create_shape_negative: int = 0,
                 offball_positioning_adv_awareness_positive: int = 0,
                 offball_positioning_adv_awareness_negative: int = 0,
                 # Off Ball - Transition
                 transition_effort_pace_positive: int = 0,
                 transition_effort_pace_negative: int = 0,
                 # Cutting & Screening
                 cs_denial_positive: int = 0,
                 cs_denial_negative: int = 0,
                 cs_movement_positive: int = 0,
                 cs_movement_negative: int = 0,
                 cs_body_to_body_positive: int = 0,
                 cs_body_to_body_negative: int = 0,
                 cs_screen_principle_positive: int = 0,
                 cs_screen_principle_negative: int = 0,
                 cs_cut_fill_positive: int = 0,
                 cs_cut_fill_negative: int = 0,
                 # Relocation
                 relocation_weak_corner_positive: int = 0,
                 relocation_weak_corner_negative: int = 0,
                 relocation_45_cut_positive: int = 0,
                 relocation_45_cut_negative: int = 0,
                 relocation_slide_away_positive: int = 0,
                 relocation_slide_away_negative: int = 0,
                 relocation_fill_behind_positive: int = 0,
                 relocation_fill_behind_negative: int = 0,
                 relocation_dunker_baseline_positive: int = 0,
                 relocation_dunker_baseline_negative: int = 0,
                 relocation_corner_fill_positive: int = 0,
                 relocation_corner_fill_negative: int = 0,
                 relocation_reverse_direction_positive: int = 0,
                 relocation_reverse_direction_negative: int = 0):
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
            qb12_strong_side_positive (int): Count of +ve QB12: Strong Side
            qb12_strong_side_negative (int): Count of -ve QB12: Strong Side
            qb12_baseline_positive (int): Count of +ve QB12: Baseline
            qb12_baseline_negative (int): Count of -ve QB12: Baseline
            qb12_fill_behind_positive (int): Count of +ve QB12: Fill Behind
            qb12_fill_behind_negative (int): Count of -ve QB12: Fill Behind
            qb12_weak_side_positive (int): Count of +ve QB12: Weak Side
            qb12_weak_side_negative (int): Count of -ve QB12: Weak Side
            qb12_roller_positive (int): Count of +ve QB12: Roller
            qb12_roller_negative (int): Count of -ve QB12: Roller
            qb12_skip_pass_positive (int): Count of +ve QB12: Skip Pass
            qb12_skip_pass_negative (int): Count of -ve QB12: Skip Pass
            qb12_cutter_positive (int): Count of +ve QB12: Cutter
            qb12_cutter_negative (int): Count of -ve QB12: Cutter
            driving_paint_touch_positive (int): Count of positive driving paint touch actions
            driving_paint_touch_negative (int): Count of negative driving paint touch actions
            driving_physicality_positive (int): Count of positive driving physicality actions
            driving_physicality_negative (int): Count of negative driving physicality actions
        """
        self.player_name = player_name
        self.date_created = date_created or int(datetime.now().timestamp())
        self.game_id = game_id
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
        self.qb12_strong_side_positive = qb12_strong_side_positive
        self.qb12_strong_side_negative = qb12_strong_side_negative
        self.qb12_baseline_positive = qb12_baseline_positive
        self.qb12_baseline_negative = qb12_baseline_negative
        self.qb12_fill_behind_positive = qb12_fill_behind_positive
        self.qb12_fill_behind_negative = qb12_fill_behind_negative
        self.qb12_weak_side_positive = qb12_weak_side_positive
        self.qb12_weak_side_negative = qb12_weak_side_negative
        self.qb12_roller_positive = qb12_roller_positive
        self.qb12_roller_negative = qb12_roller_negative
        self.qb12_skip_pass_positive = qb12_skip_pass_positive
        self.qb12_skip_pass_negative = qb12_skip_pass_negative
        self.qb12_cutter_positive = qb12_cutter_positive
        self.qb12_cutter_negative = qb12_cutter_negative
        self.driving_paint_touch_positive = driving_paint_touch_positive
        self.driving_paint_touch_negative = driving_paint_touch_negative
        self.driving_physicality_positive = driving_physicality_positive
        self.driving_physicality_negative = driving_physicality_negative
        # Off Ball - Positioning
        self.offball_positioning_create_shape_positive = offball_positioning_create_shape_positive
        self.offball_positioning_create_shape_negative = offball_positioning_create_shape_negative
        self.offball_positioning_adv_awareness_positive = offball_positioning_adv_awareness_positive
        self.offball_positioning_adv_awareness_negative = offball_positioning_adv_awareness_negative
        # Off Ball - Transition
        self.transition_effort_pace_positive = transition_effort_pace_positive
        self.transition_effort_pace_negative = transition_effort_pace_negative
        # Cutting & Screening
        self.cs_denial_positive = cs_denial_positive
        self.cs_denial_negative = cs_denial_negative
        self.cs_movement_positive = cs_movement_positive
        self.cs_movement_negative = cs_movement_negative
        self.cs_body_to_body_positive = cs_body_to_body_positive
        self.cs_body_to_body_negative = cs_body_to_body_negative
        self.cs_screen_principle_positive = cs_screen_principle_positive
        self.cs_screen_principle_negative = cs_screen_principle_negative
        self.cs_cut_fill_positive = cs_cut_fill_positive
        self.cs_cut_fill_negative = cs_cut_fill_negative
        # Relocation
        self.relocation_weak_corner_positive = relocation_weak_corner_positive
        self.relocation_weak_corner_negative = relocation_weak_corner_negative
        self.relocation_45_cut_positive = relocation_45_cut_positive
        self.relocation_45_cut_negative = relocation_45_cut_negative
        self.relocation_slide_away_positive = relocation_slide_away_positive
        self.relocation_slide_away_negative = relocation_slide_away_negative
        self.relocation_fill_behind_positive = relocation_fill_behind_positive
        self.relocation_fill_behind_negative = relocation_fill_behind_negative
        self.relocation_dunker_baseline_positive = relocation_dunker_baseline_positive
        self.relocation_dunker_baseline_negative = relocation_dunker_baseline_negative
        self.relocation_corner_fill_positive = relocation_corner_fill_positive
        self.relocation_corner_fill_negative = relocation_corner_fill_negative
        self.relocation_reverse_direction_positive = relocation_reverse_direction_positive
        self.relocation_reverse_direction_negative = relocation_reverse_direction_negative
        # Note: player bars are derived from the atomic counts above; not persisted
    
    def to_dict(self) -> dict:
        """
        Convert scorecard to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the scorecard
        """
        return {
            'player_name': self.player_name,
            'date_created': self.date_created,
            'game_id': self.game_id,
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
            'qb12_strong_side_positive': self.qb12_strong_side_positive,
            'qb12_strong_side_negative': self.qb12_strong_side_negative,
            'qb12_baseline_positive': self.qb12_baseline_positive,
            'qb12_baseline_negative': self.qb12_baseline_negative,
            'qb12_fill_behind_positive': self.qb12_fill_behind_positive,
            'qb12_fill_behind_negative': self.qb12_fill_behind_negative,
            'qb12_weak_side_positive': self.qb12_weak_side_positive,
            'qb12_weak_side_negative': self.qb12_weak_side_negative,
            'qb12_roller_positive': self.qb12_roller_positive,
            'qb12_roller_negative': self.qb12_roller_negative,
            'qb12_skip_pass_positive': self.qb12_skip_pass_positive,
            'qb12_skip_pass_negative': self.qb12_skip_pass_negative,
            'qb12_cutter_positive': self.qb12_cutter_positive,
            'qb12_cutter_negative': self.qb12_cutter_negative,
            'driving_paint_touch_positive': self.driving_paint_touch_positive,
            'driving_paint_touch_negative': self.driving_paint_touch_negative,
            'driving_physicality_positive': self.driving_physicality_positive,
            'driving_physicality_negative': self.driving_physicality_negative,
            # Off Ball - Positioning
            'offball_positioning_create_shape_positive': self.offball_positioning_create_shape_positive,
            'offball_positioning_create_shape_negative': self.offball_positioning_create_shape_negative,
            'offball_positioning_adv_awareness_positive': self.offball_positioning_adv_awareness_positive,
            'offball_positioning_adv_awareness_negative': self.offball_positioning_adv_awareness_negative,
            # Off Ball - Transition
            'transition_effort_pace_positive': self.transition_effort_pace_positive,
            'transition_effort_pace_negative': self.transition_effort_pace_negative,
            # Cutting & Screening
            'cs_denial_positive': self.cs_denial_positive,
            'cs_denial_negative': self.cs_denial_negative,
            'cs_movement_positive': self.cs_movement_positive,
            'cs_movement_negative': self.cs_movement_negative,
            'cs_body_to_body_positive': self.cs_body_to_body_positive,
            'cs_body_to_body_negative': self.cs_body_to_body_negative,
            'cs_screen_principle_positive': self.cs_screen_principle_positive,
            'cs_screen_principle_negative': self.cs_screen_principle_negative,
            'cs_cut_fill_positive': self.cs_cut_fill_positive,
            'cs_cut_fill_negative': self.cs_cut_fill_negative,
            # Relocation
            'relocation_weak_corner_positive': self.relocation_weak_corner_positive,
            'relocation_weak_corner_negative': self.relocation_weak_corner_negative,
            'relocation_45_cut_positive': self.relocation_45_cut_positive,
            'relocation_45_cut_negative': self.relocation_45_cut_negative,
            'relocation_slide_away_positive': self.relocation_slide_away_positive,
            'relocation_slide_away_negative': self.relocation_slide_away_negative,
            'relocation_fill_behind_positive': self.relocation_fill_behind_positive,
            'relocation_fill_behind_negative': self.relocation_fill_behind_negative,
            'relocation_dunker_baseline_positive': self.relocation_dunker_baseline_positive,
            'relocation_dunker_baseline_negative': self.relocation_dunker_baseline_negative,
            'relocation_corner_fill_positive': self.relocation_corner_fill_positive,
            'relocation_corner_fill_negative': self.relocation_corner_fill_negative,
            'relocation_reverse_direction_positive': self.relocation_reverse_direction_positive,
            'relocation_reverse_direction_negative': self.relocation_reverse_direction_negative,
        }

    # --------------------- Player Bar Model & Builder ---------------------
    @dataclass
    class PlayerBar:
        """Represents a single stat bar with +/- counts and computed percentages."""
        key: str
        label: str
        positive: int
        negative: int
        neutral: int = 0

        @property
        def total(self) -> int:
            return max(int(self.positive) + int(self.negative) + int(self.neutral), 0)

        @property
        def positive_pct(self) -> float:
            denom = self.total or 1
            return round(100.0 * (self.positive / denom), 1)

        @property
        def negative_pct(self) -> float:
            denom = self.total or 1
            return round(100.0 * (self.negative / denom), 1)

        @property
        def neutral_pct(self) -> float:
            val = round(100.0 - self.positive_pct - self.negative_pct, 1)
            return max(0.0, val)

        def to_dict(self) -> dict:
            return {
                'key': self.key,
                'label': self.label,
                'positive': int(self.positive),
                'negative': int(self.negative),
                'neutral': int(self.neutral),
                'positivePct': self.positive_pct,
                'negativePct': self.negative_pct,
                'neutralPct': self.neutral_pct,
            }

    def get_player_bars(self) -> List['Scorecard.PlayerBar']:
        """Build player bars (derived) for this scorecard.

        Currently derives bars for the categories represented in the Scorecard fields:
        - Space Read
        - DM Catch
        - Driving
        - QB12 Decision Making
        """
        # Space Read
        space_read_positive = int(self.space_read_live_dribble) + int(self.space_read_catch)
        space_read_negative = int(self.space_read_live_dribble_negative) + int(self.space_read_catch_negative)

        # DM Catch (aggregate multiple sub-metrics)
        dm_catch_positive = (
            int(self.dm_catch_back_to_back_positive)
            + int(self.dm_catch_uncontested_shot_positive)
            + int(self.dm_catch_swing_positive)
            + int(self.dm_catch_drive_pass_positive)
            + int(self.dm_catch_drive_swing_skip_pass_positive)
        )
        dm_catch_negative = (
            int(self.dm_catch_back_to_back_negative)
            + int(self.dm_catch_uncontested_shot_negative)
            + int(self.dm_catch_swing_negative)
            + int(self.dm_catch_drive_pass_negative)
            + int(self.dm_catch_drive_swing_skip_pass_negative)
        )

        # Driving
        driving_positive = int(self.driving_paint_touch_positive) + int(self.driving_physicality_positive)
        driving_negative = int(self.driving_paint_touch_negative) + int(self.driving_physicality_negative)

        # Off Ball - Positioning
        positioning_positive = (
            int(self.offball_positioning_create_shape_positive)
            + int(self.offball_positioning_adv_awareness_positive)
        )
        positioning_negative = (
            int(self.offball_positioning_create_shape_negative)
            + int(self.offball_positioning_adv_awareness_negative)
        )

        # Off Ball - Transition
        transition_positive = int(self.transition_effort_pace_positive)
        transition_negative = int(self.transition_effort_pace_negative)

        # Cutting & Screening (aggregate multiple sub-metrics)
        cs_positive = (
            int(self.cs_denial_positive)
            + int(self.cs_movement_positive)
            + int(self.cs_body_to_body_positive)
            + int(self.cs_screen_principle_positive)
            + int(self.cs_cut_fill_positive)
        )
        cs_negative = (
            int(self.cs_denial_negative)
            + int(self.cs_movement_negative)
            + int(self.cs_body_to_body_negative)
            + int(self.cs_screen_principle_negative)
            + int(self.cs_cut_fill_negative)
        )

        # Relocation (aggregate multiple sub-metrics)
        relocation_positive = (
            int(self.relocation_weak_corner_positive)
            + int(self.relocation_45_cut_positive)
            + int(self.relocation_slide_away_positive)
            + int(self.relocation_fill_behind_positive)
            + int(self.relocation_dunker_baseline_positive)
            + int(self.relocation_corner_fill_positive)
            + int(self.relocation_reverse_direction_positive)
        )
        relocation_negative = (
            int(self.relocation_weak_corner_negative)
            + int(self.relocation_45_cut_negative)
            + int(self.relocation_slide_away_negative)
            + int(self.relocation_fill_behind_negative)
            + int(self.relocation_dunker_baseline_negative)
            + int(self.relocation_corner_fill_negative)
            + int(self.relocation_reverse_direction_negative)
        )

        # QB12 Decision Making
        qb12_positive = (
            int(self.qb12_strong_side_positive)
            + int(self.qb12_baseline_positive)
            + int(self.qb12_fill_behind_positive)
            + int(self.qb12_weak_side_positive)
            + int(self.qb12_roller_positive)
            + int(self.qb12_skip_pass_positive)
            + int(self.qb12_cutter_positive)
        )
        qb12_negative = (
            int(self.qb12_strong_side_negative)
            + int(self.qb12_baseline_negative)
            + int(self.qb12_fill_behind_negative)
            + int(self.qb12_weak_side_negative)
            + int(self.qb12_roller_negative)
            + int(self.qb12_skip_pass_negative)
            + int(self.qb12_cutter_negative)
        )

        bars: List[Scorecard.PlayerBar] = [
            Scorecard.PlayerBar(key='space_read', label='Space Read', positive=space_read_positive, negative=space_read_negative),
            Scorecard.PlayerBar(key='dm_catch', label='DM Catch', positive=dm_catch_positive, negative=dm_catch_negative),
            Scorecard.PlayerBar(key='driving', label='Driving', positive=driving_positive, negative=driving_negative),
            Scorecard.PlayerBar(key='qb12_dm', label='QB12 Decision Making', positive=qb12_positive, negative=qb12_negative),
            Scorecard.PlayerBar(key='positioning', label='Off Ball Positioning', positive=positioning_positive, negative=positioning_negative),
            Scorecard.PlayerBar(key='transition', label='Transition', positive=transition_positive, negative=transition_negative),
            Scorecard.PlayerBar(key='cutting_screening', label='Cutting & Screening', positive=cs_positive, negative=cs_negative),
            Scorecard.PlayerBar(key='relocation', label='Relocation', positive=relocation_positive, negative=relocation_negative),
        ]

        return bars
    
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
            data.get('game_id'),
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
            data.get('qb12_strong_side_positive', 0),
            data.get('qb12_strong_side_negative', 0),
            data.get('qb12_baseline_positive', 0),
            data.get('qb12_baseline_negative', 0),
            data.get('qb12_fill_behind_positive', 0),
            data.get('qb12_fill_behind_negative', 0),
            data.get('qb12_weak_side_positive', 0),
            data.get('qb12_weak_side_negative', 0),
            data.get('qb12_roller_positive', 0),
            data.get('qb12_roller_negative', 0),
            data.get('qb12_skip_pass_positive', 0),
            data.get('qb12_skip_pass_negative', 0),
            data.get('qb12_cutter_positive', 0),
            data.get('qb12_cutter_negative', 0),
            data.get('driving_paint_touch_positive', 0),
            data.get('driving_paint_touch_negative', 0),
            data.get('driving_physicality_positive', 0),
            data.get('driving_physicality_negative', 0),
            # Off Ball - Positioning
            data.get('offball_positioning_create_shape_positive', 0),
            data.get('offball_positioning_create_shape_negative', 0),
            data.get('offball_positioning_adv_awareness_positive', 0),
            data.get('offball_positioning_adv_awareness_negative', 0),
            # Off Ball - Transition
            data.get('transition_effort_pace_positive', 0),
            data.get('transition_effort_pace_negative', 0),
            # Cutting & Screening
            data.get('cs_denial_positive', 0),
            data.get('cs_denial_negative', 0),
            data.get('cs_movement_positive', 0),
            data.get('cs_movement_negative', 0),
            data.get('cs_body_to_body_positive', 0),
            data.get('cs_body_to_body_negative', 0),
            data.get('cs_screen_principle_positive', 0),
            data.get('cs_screen_principle_negative', 0),
            data.get('cs_cut_fill_positive', 0),
            data.get('cs_cut_fill_negative', 0),
            # Relocation
            data.get('relocation_weak_corner_positive', 0),
            data.get('relocation_weak_corner_negative', 0),
            data.get('relocation_45_cut_positive', 0),
            data.get('relocation_45_cut_negative', 0),
            data.get('relocation_slide_away_positive', 0),
            data.get('relocation_slide_away_negative', 0),
            data.get('relocation_fill_behind_positive', 0),
            data.get('relocation_fill_behind_negative', 0),
            data.get('relocation_dunker_baseline_positive', 0),
            data.get('relocation_dunker_baseline_negative', 0),
            data.get('relocation_corner_fill_positive', 0),
            data.get('relocation_corner_fill_negative', 0),
            data.get('relocation_reverse_direction_positive', 0),
            data.get('relocation_reverse_direction_negative', 0),
        )
    
    def __str__(self) -> str:
        """String representation of the scorecard."""
        return f"Scorecard({self.to_dict()})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the scorecard."""
        return f"Scorecard({self.to_dict()})"
    
    def __eq__(self, other) -> bool:
        """Check if two scorecards are equal."""
        if not isinstance(other, Scorecard):
            return False
        return self.to_dict() == other.to_dict()
    
    def __hash__(self) -> int:
        """Hash the scorecard for use in sets and as dictionary keys."""
        # Hash generated from the tuple of sorted items for stability
        items = tuple(sorted(self.to_dict().items()))
        return hash(items)