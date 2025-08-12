"""
Custom ETL Processor for Statistical Data from PDFs
This module provides specialized processing for various types of statistical data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class StatisticalDataProcessor:
    """Specialized processor for statistical data from PDFs"""
    
    def __init__(self):
        self.supported_stats_types = [
            'basketball_stats',
            'financial_data', 
            'sports_analytics',
            'performance_metrics',
            'survey_data',
            'time_series_data'
        ]
    
    def detect_data_type(self, df):
        """Automatically detect the type of statistical data"""
        columns = [col.lower() for col in df.columns]
        
        # Basketball/Football stats detection
        if any(word in ' '.join(columns) for word in ['points', 'rebounds', 'assists', 'steals', 'blocks', 'fg%', '3p%', 'ft%']):
            return 'basketball_stats'
        
        # Financial data detection
        if any(word in ' '.join(columns) for word in ['revenue', 'profit', 'sales', 'income', 'expenses', 'balance']):
            return 'financial_data'
        
        # Sports analytics
        if any(word in ' '.join(columns) for word in ['wins', 'losses', 'record', 'games', 'season', 'team']):
            return 'sports_analytics'
        
        # Performance metrics
        if any(word in ' '.join(columns) for word in ['performance', 'efficiency', 'rating', 'score', 'grade']):
            return 'performance_metrics'
        
        # Survey data
        if any(word in ' '.join(columns) for word in ['survey', 'response', 'rating', 'satisfaction', 'feedback']):
            return 'survey_data'
        
        # Time series
        if any(word in ' '.join(columns) for word in ['date', 'time', 'period', 'quarter', 'year', 'month']):
            return 'time_series_data'
        
        return 'general_stats'
    
    def process_basketball_stats(self, df):
        """Process basketball statistics data"""
        processed_df = df.copy()
        
        # Calculate advanced metrics
        if all(col in processed_df.columns for col in ['Points', 'Games_Played']):
            processed_df['Points_Per_Game'] = processed_df['Points'] / processed_df['Games_Played']
        
        if all(col in processed_df.columns for col in ['Field_Goals_Made', 'Field_Goals_Attempted']):
            processed_df['FG_Percentage'] = (processed_df['Field_Goals_Made'] / processed_df['Field_Goals_Attempted'] * 100).round(2)
        
        if all(col in processed_df.columns for col in ['Three_Point_Made', 'Three_Point_Attempted']):
            processed_df['3P_Percentage'] = (processed_df['Three_Point_Made'] / processed_df['Three_Point_Attempted'] * 100).round(2)
        
        if all(col in processed_df.columns for col in ['Free_Throws_Made', 'Free_Throws_Attempted']):
            processed_df['FT_Percentage'] = (processed_df['Free_Throws_Made'] / processed_df['Free_Throws_Attempted'] * 100).round(2)
        
        # Calculate efficiency metrics
        if all(col in processed_df.columns for col in ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks']):
            processed_df['Total_Impact'] = processed_df['Points'] + processed_df['Rebounds'] + processed_df['Assists'] + processed_df['Steals'] + processed_df['Blocks']
        
        # Add performance categories
        if 'Points_Per_Game' in processed_df.columns:
            processed_df['Scoring_Category'] = pd.cut(
                processed_df['Points_Per_Game'], 
                bins=[0, 10, 20, 30, 100], 
                labels=['Low Scorer', 'Average Scorer', 'High Scorer', 'Elite Scorer']
            )
        
        return processed_df
    
    def process_financial_data(self, df):
        """Process financial data"""
        processed_df = df.copy()
        
        # Calculate growth rates
        numeric_columns = processed_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if 'revenue' in col.lower() or 'sales' in col.lower() or 'income' in col.lower():
                processed_df[f'{col}_Growth_Rate'] = processed_df[col].pct_change() * 100
        
        # Calculate ratios
        if all(col in processed_df.columns for col in ['Revenue', 'Expenses']):
            processed_df['Profit_Margin'] = ((processed_df['Revenue'] - processed_df['Expenses']) / processed_df['Revenue'] * 100).round(2)
        
        # Add financial health indicators
        if 'Revenue' in processed_df.columns:
            processed_df['Revenue_Category'] = pd.qcut(
                processed_df['Revenue'], 
                q=4, 
                labels=['Low Revenue', 'Medium Revenue', 'High Revenue', 'Very High Revenue']
            )
        
        return processed_df
    
    def process_sports_analytics(self, df):
        """Process sports analytics data"""
        processed_df = df.copy()
        
        # Calculate win percentage
        if all(col in processed_df.columns for col in ['Wins', 'Losses']):
            processed_df['Win_Percentage'] = (processed_df['Wins'] / (processed_df['Wins'] + processed_df['Losses']) * 100).round(2)
        
        # Calculate point differential
        if all(col in processed_df.columns for col in ['Points_For', 'Points_Against']):
            processed_df['Point_Differential'] = processed_df['Points_For'] - processed_df['Points_Against']
        
        # Add performance tiers
        if 'Win_Percentage' in processed_df.columns:
            processed_df['Performance_Tier'] = pd.cut(
                processed_df['Win_Percentage'],
                bins=[0, 40, 50, 60, 100],
                labels=['Poor', 'Below Average', 'Above Average', 'Excellent']
            )
        
        return processed_df
    
    def process_performance_metrics(self, df):
        """Process performance metrics data"""
        processed_df = df.copy()
        
        # Normalize scores (0-100 scale)
        numeric_columns = processed_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if 'score' in col.lower() or 'rating' in col.lower() or 'performance' in col.lower():
                min_val = processed_df[col].min()
                max_val = processed_df[col].max()
                if max_val > min_val:
                    processed_df[f'{col}_Normalized'] = ((processed_df[col] - min_val) / (max_val - min_val) * 100).round(2)
        
        # Calculate composite scores
        score_columns = [col for col in numeric_columns if 'score' in col.lower()]
        if len(score_columns) > 1:
            processed_df['Composite_Score'] = processed_df[score_columns].mean(axis=1).round(2)
        
        return processed_df
    
    def process_survey_data(self, df):
        """Process survey data"""
        processed_df = df.copy()
        
        # Calculate response rates
        if 'Response' in processed_df.columns:
            processed_df['Response_Rate'] = (processed_df['Response'].notna().sum() / len(processed_df) * 100).round(2)
        
        # Calculate satisfaction scores
        rating_columns = [col for col in processed_df.columns if 'rating' in col.lower() or 'satisfaction' in col.lower()]
        if rating_columns:
            processed_df['Average_Rating'] = processed_df[rating_columns].mean(axis=1).round(2)
        
        # Add sentiment analysis
        if 'Comments' in processed_df.columns:
            processed_df['Comment_Length'] = processed_df['Comments'].str.len()
            processed_df['Has_Comments'] = processed_df['Comments'].notna()
        
        return processed_df
    
    def process_time_series_data(self, df):
        """Process time series data"""
        processed_df = df.copy()
        
        # Convert date columns
        date_columns = [col for col in processed_df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_columns:
            try:
                processed_df[col] = pd.to_datetime(processed_df[col])
            except:
                pass
        
        # Calculate trends
        numeric_columns = processed_df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in date_columns:
                processed_df[f'{col}_Trend'] = processed_df[col].diff()
                processed_df[f'{col}_Moving_Average'] = processed_df[col].rolling(window=3, min_periods=1).mean()
        
        return processed_df
    
    def add_summary_statistics(self, df):
        """Add summary statistics for the dataset"""
        summary_stats = {}
        
        # Basic statistics
        summary_stats['total_rows'] = len(df)
        summary_stats['total_columns'] = len(df.columns)
        summary_stats['missing_values'] = df.isnull().sum().sum()
        summary_stats['completeness_percentage'] = ((len(df) * len(df.columns) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100).round(2)
        
        # Column statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            summary_stats['numeric_columns'] = list(numeric_columns)
            summary_stats['numeric_summary'] = df[numeric_columns].describe().to_dict()
        
        # Categorical statistics
        categorical_columns = df.select_dtypes(include=['object']).columns
        if len(categorical_columns) > 0:
            summary_stats['categorical_columns'] = list(categorical_columns)
            summary_stats['categorical_summary'] = {}
            for col in categorical_columns:
                summary_stats['categorical_summary'][col] = df[col].value_counts().to_dict()
        
        return summary_stats
    
    def process_data(self, df, processing_options=None):
        """Main processing function"""
        if processing_options is None:
            processing_options = {}
        
        # Detect data type
        data_type = self.detect_data_type(df)
        logger.info(f"Detected data type: {data_type}")
        
        # Apply type-specific processing
        if data_type == 'basketball_stats':
            df = self.process_basketball_stats(df)
        elif data_type == 'financial_data':
            df = self.process_financial_data(df)
        elif data_type == 'sports_analytics':
            df = self.process_sports_analytics(df)
        elif data_type == 'performance_metrics':
            df = self.process_performance_metrics(df)
        elif data_type == 'survey_data':
            df = self.process_survey_data(df)
        elif data_type == 'time_series_data':
            df = self.process_time_series_data(df)
        
        # Apply general processing options
        if processing_options.get('remove_duplicates'):
            df = df.drop_duplicates()
        
        if processing_options.get('fill_missing'):
            # Handle categorical columns properly
            for col in df.columns:
                if df[col].dtype.name == 'category':
                    # Add 'N/A' to categories if it doesn't exist
                    if 'N/A' not in df[col].cat.categories:
                        df[col] = df[col].cat.add_categories(['N/A'])
                    df[col] = df[col].fillna('N/A')
                else:
                    df[col] = df[col].fillna('N/A')
        
        if processing_options.get('add_timestamp'):
            df['processed_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add data type and summary
        df.attrs['data_type'] = data_type
        df.attrs['summary_stats'] = self.add_summary_statistics(df)
        
        return df

def create_sample_basketball_stats():
    """Create sample basketball statistics data"""
    sample_data = {
        'Player_Name': ['LeBron James', 'Stephen Curry', 'Kevin Durant', 'Giannis Antetokounmpo', 'Nikola Jokic'],
        'Team': ['Lakers', 'Warriors', 'Suns', 'Bucks', 'Nuggets'],
        'Games_Played': [67, 69, 71, 73, 75],
        'Points': [1800, 2100, 1950, 2200, 2050],
        'Rebounds': [450, 320, 380, 550, 680],
        'Assists': [520, 480, 420, 380, 620],
        'Steals': [85, 95, 75, 90, 110],
        'Blocks': [45, 25, 55, 80, 60],
        'Field_Goals_Made': [650, 720, 680, 750, 780],
        'Field_Goals_Attempted': [1200, 1350, 1250, 1400, 1450],
        'Three_Point_Made': [120, 280, 180, 90, 110],
        'Three_Point_Attempted': [350, 750, 450, 280, 320],
        'Free_Throws_Made': [380, 320, 410, 510, 380],
        'Free_Throws_Attempted': [450, 380, 480, 620, 450]
    }
    
    return pd.DataFrame(sample_data)

if __name__ == "__main__":
    # Test the processor
    processor = StatisticalDataProcessor()
    sample_df = create_sample_basketball_stats()
    
    print("Sample Basketball Stats:")
    print(sample_df.head())
    print("\n" + "="*50 + "\n")
    
    processed_df = processor.process_data(sample_df, {
        'remove_duplicates': True,
        'fill_missing': True,
        'add_timestamp': True
    })
    
    print("Processed Basketball Stats:")
    print(processed_df.head())
    print(f"\nData Type: {processed_df.attrs.get('data_type')}")
    print(f"Summary Stats: {processed_df.attrs.get('summary_stats')}") 