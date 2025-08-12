#!/usr/bin/env python3
"""
Scorecard Autofill Processor
Handles automatic calculation of scorecard attributes from basketball data.
"""

import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ScorecardAutofillProcessor:
    """
    Processor for automatically calculating scorecard attributes from basketball data.
    """
    
    def __init__(self):
        """Initialize the processor."""
        pass
    
    def calculate_space_read_metrics(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Calculate Space Read metrics from basketball data.
        
        Args:
            df (pd.DataFrame): Basketball data DataFrame
            
        Returns:
            Dict[str, int]: Dictionary containing calculated metrics
        """
        try:
            # Initialize metrics
            space_read_live_dribble = 0
            space_read_catch = 0
            
            # Check if 'Space Read' column exists (column 58)
            space_read_column = None
            
            # Try to find the Space Read column
            for col in df.columns:
                if 'Space Read' in str(col) or 'space read' in str(col).lower():
                    space_read_column = col
                    break
            
            if space_read_column is None:
                logger.warning("Space Read column not found in data")
                return {
                    'space_read_live_dribble': 0,
                    'space_read_catch': 0
                }
            
            # Count positive Space Read actions
            for value in df[space_read_column]:
                if pd.notna(value):  # Check if value is not NaN
                    value_str = str(value).strip()
                    
                    # Count Live Dribble actions
                    if '+ve Space Read: Live Dribble' in value_str:
                        space_read_live_dribble += 1
                    
                    # Count Catch actions
                    if '+ve Space Read: Catch' in value_str:
                        space_read_catch += 1
            
            logger.info(f"Calculated Space Read metrics: Live Dribble={space_read_live_dribble}, Catch={space_read_catch}")
            
            return {
                'space_read_live_dribble': space_read_live_dribble,
                'space_read_catch': space_read_catch
            }
            
        except Exception as e:
            logger.error(f"Error calculating Space Read metrics: {e}")
            return {
                'space_read_live_dribble': 0,
                'space_read_catch': 0
            }
    
    def autofill_scorecard_attributes(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Autofill all scorecard attributes from basketball data.
        
        Args:
            df (pd.DataFrame): Basketball data DataFrame
            
        Returns:
            Dict[str, Any]: Dictionary containing all calculated attributes
        """
        try:
            # Calculate Space Read metrics
            space_read_metrics = self.calculate_space_read_metrics(df)
            
            # Combine all metrics
            autofill_data = {
                **space_read_metrics,
                'total_actions': len(df),
                'data_columns': list(df.columns)
            }
            
            logger.info(f"Autofill completed: {autofill_data}")
            return autofill_data
            
        except Exception as e:
            logger.error(f"Error in autofill process: {e}")
            return {
                'space_read_live_dribble': 0,
                'space_read_catch': 0,
                'total_actions': 0,
                'data_columns': []
            }
    
    def validate_data_for_autofill(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate if the data is suitable for autofill processing.
        
        Args:
            df (pd.DataFrame): Basketball data DataFrame
            
        Returns:
            Dict[str, Any]: Validation results
        """
        try:
            validation_results = {
                'is_valid': True,
                'space_read_column_found': False,
                'total_rows': len(df),
                'columns_checked': []
            }
            
            # Check for Space Read column
            for col in df.columns:
                if 'Space Read' in str(col) or 'space read' in str(col).lower():
                    validation_results['space_read_column_found'] = True
                    validation_results['columns_checked'].append(col)
            
            if not validation_results['space_read_column_found']:
                validation_results['is_valid'] = False
                validation_results['warning'] = "Space Read column not found in data"
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'space_read_column_found': False,
                'total_rows': 0,
                'columns_checked': []
            } 