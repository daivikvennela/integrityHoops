"""
Cognitive Score Calculator
Calculates cognitive performance scores from basketball game CSV data.
"""

import pandas as pd
import json
from typing import Dict, Tuple, Optional
import os


class CogScoreCalculator:
    """
    Calculates cognitive scores from basketball performance CSV files.
    
    The score is calculated as: positives / (positives + negatives) * 100
    Result ranges from 0% (all negative) to 100% (all positive)
    """
    
    # Cognitive skill columns to analyze
    COG_COLUMNS = [
        'Cutting & Screeing',  # Note: typo in CSV header
        'DM Catch',
        'Driving',
        'Finishing',
        'Footwork',
        'Passing',
        'Positioning',
        'QB12 DM',
        'Relocation',
        'Space Read',
        'Transition'
    ]
    
    def __init__(self, csv_path: str):
        """
        Initialize calculator with CSV file path.
        
        Args:
            csv_path: Path to the CSV file containing game data
        """
        self.csv_path = csv_path
        self.df = None
        self.game_name = None
        self.game_date = None
        
    def load_csv(self) -> pd.DataFrame:
        """Load and return the CSV data."""
        # Simple approach - let pandas handle it
        try:
            self.df = pd.read_csv(self.csv_path, low_memory=False)
        except Exception as e:
            # If that fails, try with different encoding
            try:
                self.df = pd.read_csv(self.csv_path, encoding='latin-1', low_memory=False)
            except Exception as e2:
                raise Exception(f"Failed to read CSV file: {str(e2)}")
        
        # Extract game name and date from first row's Timeline column
        if not self.df.empty and 'Timeline' in self.df.columns:
            self.game_name = self.df['Timeline'].iloc[0]
            # Extract date from game name (e.g., "10.04.25 Heat v Bucks Team")
            import re
            date_match = re.match(r'(\d{2}\.\d{2}\.\d{2})', self.game_name)
            if date_match:
                self.game_date = date_match.group(1)
        
        return self.df
    
    def calculate_column_score(self, column_name: str) -> Dict:
        """
        Calculate cognitive score for a single column.
        
        Args:
            column_name: Name of the cognitive column to analyze
            
        Returns:
            Dictionary with positive, negative, total counts and calculated score
        """
        if self.df is None:
            self.load_csv()
        
        # Handle missing column
        if column_name not in self.df.columns:
            return {
                'positive': 0,
                'negative': 0,
                'total': 0,
                'score': 0.0
            }
        
        # Count +ve and -ve occurrences in the column
        # Using str.count to handle multiple entries in same cell (e.g., "+ve X, +ve Y")
        positives = self.df[column_name].fillna('').astype(str).str.count(r'\+ve').sum()
        negatives = self.df[column_name].fillna('').astype(str).str.count(r'-ve').sum()
        total = positives + negatives
        
        # Calculate score
        if total > 0:
            score = (positives / total) * 100
        else:
            score = 0.0
        
        return {
            'positive': int(positives),
            'negative': int(negatives),
            'total': int(total),
            'score': round(score, 2)
        }
    
    def calculate_all_scores(self) -> Tuple[Dict, float]:
        """
        Calculate cognitive scores for all columns.
        
        Returns:
            Tuple of (scores_dict, overall_score)
            - scores_dict: Dictionary with breakdown per cognitive skill
            - overall_score: Average score across all skills
        """
        if self.df is None:
            self.load_csv()
        
        scores = {}
        
        for col in self.COG_COLUMNS:
            scores[col] = self.calculate_column_score(col)
        
        # Calculate overall score as average of all column scores
        valid_scores = [s['score'] for s in scores.values() if s['total'] > 0]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        
        return scores, round(overall_score, 2)
    
    def get_full_report(self) -> Dict:
        """
        Generate a complete cognitive score report.
        
        Returns:
            Dictionary containing overall score, breakdown, and metadata
        """
        scores, overall = self.calculate_all_scores()
        
        return {
            'overall_score': overall,
            'breakdown': scores,
            'metadata': {
                'game': self.game_name or os.path.basename(self.csv_path),
                'game_date': self.game_date,
                'total_instances': len(self.df) if self.df is not None else 0,
                'csv_file': os.path.basename(self.csv_path)
            }
        }
    
    def print_report(self):
        """Print a formatted report to console."""
        report = self.get_full_report()
        
        print("\n" + "="*70)
        print(f"COGNITIVE SCORE REPORT: {report['metadata']['game']}")
        print("="*70)
        print(f"\nOverall Cognitive Score: {report['overall_score']:.2f}%")
        print(f"Total Instances: {report['metadata']['total_instances']}")
        print("\n" + "-"*70)
        print(f"{'Cognitive Skill':<25} {'Positive':>10} {'Negative':>10} {'Total':>10} {'Score':>10}")
        print("-"*70)
        
        for skill, data in report['breakdown'].items():
            print(f"{skill:<25} {data['positive']:>10} {data['negative']:>10} {data['total']:>10} {data['score']:>9.2f}%")
        
        print("="*70 + "\n")
    
    def save_report_json(self, output_path: str):
        """
        Save report as JSON file.
        
        Args:
            output_path: Path where JSON report should be saved
        """
        report = self.get_full_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {output_path}")


def calculate_cog_score(csv_path: str) -> Tuple[Dict, float]:
    """
    Convenience function to calculate cognitive scores from a CSV file.
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Tuple of (scores_dict, overall_score)
    """
    calculator = CogScoreCalculator(csv_path)
    return calculator.calculate_all_scores()


if __name__ == "__main__":
    # Test with sample file if run directly
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        print("Usage: python cog_score_calculator.py <csv_file>")
        sys.exit(1)
    
    calculator = CogScoreCalculator(csv_file)
    calculator.print_report()

