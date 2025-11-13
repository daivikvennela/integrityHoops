from flask import Blueprint, render_template, flash, redirect, url_for
import os
import pandas as pd
import numpy as np
from src.processors.basketball_cognitive_processor import BasketballCognitiveProcessor

dashboard_bp = Blueprint('dashboard_bp', __name__)

PROCESSED_FOLDER = 'data/processed'
TEST_CSVS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'testcases', 'test_csvs')

def transform_csv_to_processor_format(df):
    """Transform CSV with individual category columns to processor format with Row/BREAKDOWN"""
    # Check if already in processor format (has BREAKDOWN column and Row contains category names)
    if 'BREAKDOWN' in df.columns and df['Row'].str.contains('Space Read|DM Catch|Driving', na=False).any():
        return df
    
    # Category columns to process
    category_columns = {
        'Space Read': 'Space Read',
        'DM Catch': 'DM Catch',
        'Driving': 'Driving',
        'Finishing': 'Finishing',
        'Footwork': 'Footwork',
        'Passing': 'Passing',
        'Positioning': 'Positioning',
        'QB12 DM': 'QB12 Decision Making',
        'Relocation': 'Relocation',
        'Cutting & Screeing': 'Cutting & Screening',
        'Transition': 'Transition'
    }
    
    # Create list to store transformed rows
    transformed_rows = []
    
    # Keep all original columns for metadata
    base_columns = [col for col in df.columns if col not in category_columns.keys()]
    
    # Process each row
    for idx, row in df.iterrows():
        # Add base row data
        base_data = {col: row[col] for col in base_columns}
        
        # Process each category column
        for col_name, row_name in category_columns.items():
            if col_name in df.columns and pd.notna(row[col_name]) and str(row[col_name]).strip():
                # Create a new row for this category
                new_row = base_data.copy()
                new_row['Row'] = row_name
                new_row['BREAKDOWN'] = str(row[col_name])
                transformed_rows.append(new_row)
    
    # Create new DataFrame
    if transformed_rows:
        # Ensure all columns exist
        all_columns = base_columns + ['Row', 'BREAKDOWN']
        for row in transformed_rows:
            for col in all_columns:
                if col not in row:
                    row[col] = None
        
        return pd.DataFrame(transformed_rows)
    else:
        # If no transformations, return original
        return df

@dashboard_bp.route('/scorecard-plus/<filename>')
def scorecard_plus_with_data(filename):
    try:
        # Try test_csvs first, then fall back to processed folder
        test_csv_path = os.path.join(TEST_CSVS_FOLDER, filename)
        processed_path = os.path.join(PROCESSED_FOLDER, filename)
        
        if os.path.exists(test_csv_path):
            file_path = test_csv_path
        elif os.path.exists(processed_path):
            file_path = processed_path
        else:
            flash('File not found')
            return redirect(url_for('scorecard_plus'))

        # Read CSV, skipping the "Table 1" header row if present
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            skip_rows = 1 if first_line == 'Table 1' else 0
        df = pd.read_csv(file_path, low_memory=False, skiprows=skip_rows)
        
        # Transform CSV format if needed (individual columns -> Row/BREAKDOWN format)
        df = transform_csv_to_processor_format(df)
        
        processor = BasketballCognitiveProcessor()
        scorecard_metrics = processor.calculate_scorecard_plus_metrics(df)
        player_stats = processor.build_player_stats(df)
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')

        return render_template('neon_dashboard.html',
                               filename=filename,
                               original_filename=original_filename,
                               scorecard_metrics=scorecard_metrics,
                               player_stats=player_stats,
                               df=df)
    except Exception as e:
        flash(f'Error loading data: {str(e)}')
        import traceback
        print(f"Error traceback: {traceback.format_exc()}")
        return redirect(url_for('scorecard_plus'))

@dashboard_bp.route('/scorecard-plus/<filename>/refresh')
def scorecard_plus_refresh(filename):
    try:
        # Try test_csvs first, then fall back to processed folder
        test_csv_path = os.path.join(TEST_CSVS_FOLDER, filename)
        processed_path = os.path.join(PROCESSED_FOLDER, filename)
        
        if os.path.exists(test_csv_path):
            file_path = test_csv_path
        elif os.path.exists(processed_path):
            file_path = processed_path
        else:
            flash('File not found')
            return redirect(url_for('dashboard_bp.scorecard_plus_with_data', filename=filename))

        # Read CSV, skipping the "Table 1" header row if present
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            skip_rows = 1 if first_line == 'Table 1' else 0
        df = pd.read_csv(file_path, low_memory=False, skiprows=skip_rows)
        
        # Transform CSV format if needed (individual columns -> Row/BREAKDOWN format)
        df = transform_csv_to_processor_format(df)
        
        processor = BasketballCognitiveProcessor()
        refreshed_df = df  # In this context we just reload; heavy reprocess is in app
        scorecard_metrics = processor.calculate_scorecard_plus_metrics(refreshed_df)
        player_stats = processor.build_player_stats(refreshed_df)

        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')

        flash('Dashboard refreshed with latest data!')
        return render_template('neon_dashboard.html',
                               filename=filename,
                               original_filename=original_filename,
                               scorecard_metrics=scorecard_metrics,
                               player_stats=player_stats,
                               df=refreshed_df,
                               refreshed=True)
    except Exception as e:
        flash(f'Error refreshing data: {str(e)}')
        import traceback
        print(f"Error traceback: {traceback.format_exc()}")
        return redirect(url_for('dashboard_bp.scorecard_plus_with_data', filename=filename))

@dashboard_bp.route('/scorecard-plus-latest')
def scorecard_plus_latest():
    """Route to automatically load the latest CSV from test_csvs"""
    try:
        if not os.path.exists(TEST_CSVS_FOLDER):
            flash('Test CSV folder not found')
            return redirect(url_for('scorecard_plus'))
        
        # Get all CSV files
        csv_files = [f for f in os.listdir(TEST_CSVS_FOLDER) if f.endswith('.csv')]
        if not csv_files:
            flash('No CSV files found in test_csvs')
            return redirect(url_for('scorecard_plus'))
        
        # Get the latest file by modification time
        latest_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(TEST_CSVS_FOLDER, x)))
        
        # Redirect to the regular route with the filename
        return redirect(url_for('dashboard_bp.scorecard_plus_with_data', filename=latest_file))
    except Exception as e:
        flash(f'Error finding latest file: {str(e)}')
        import traceback
        print(f"Error traceback: {traceback.format_exc()}")
        return redirect(url_for('scorecard_plus'))