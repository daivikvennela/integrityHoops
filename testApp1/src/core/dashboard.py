from flask import Blueprint, render_template, flash, redirect, url_for
import os
import pandas as pd
from src.processors.basketball_cognitive_processor import BasketballCognitiveProcessor

dashboard_bp = Blueprint('dashboard_bp', __name__)

PROCESSED_FOLDER = 'data/processed'

@dashboard_bp.route('/scorecard-plus/<filename>')
def scorecard_plus_with_data(filename):
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('scorecard_plus'))

        df = pd.read_csv(file_path)
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
        return redirect(url_for('scorecard_plus'))

@dashboard_bp.route('/scorecard-plus/<filename>/refresh')
def scorecard_plus_refresh(filename):
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('dashboard_bp.scorecard_plus_with_data', filename=filename))

        df = pd.read_csv(file_path)
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
        return redirect(url_for('dashboard_bp.scorecard_plus_with_data', filename=filename))