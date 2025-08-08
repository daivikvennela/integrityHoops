import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import logging
from src.processors.custom_etl_processor import StatisticalDataProcessor
from src.processors.basketball_cognitive_processor import BasketballCognitiveProcessor
from src.api.player_api import player_api
from src.api.player_management_dashboard import player_dashboard
from src.core.dashboard import dashboard_bp
from src.database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
app.secret_key = 'your-secret-key-here'

# Register blueprints
app.register_blueprint(player_api)
app.register_blueprint(player_dashboard)
app.register_blueprint(dashboard_bp)

# Configuration
UPLOAD_FOLDER = 'data/uploads'
PROCESSED_FOLDER = 'data/processed'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


 # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_csv_file(file_path):
    """Load CSV file and return DataFrame"""
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
        return df
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise

def scrape_company_data(company_name):
    """Scrape additional data for a company (example function)"""
    try:
        # This is a mock scraping function - in real implementation, you'd scrape actual websites
        # For demonstration, we'll return mock data
        mock_data = {
            'website': f"https://{company_name.lower().replace(' ', '')}.com",
            'industry': 'Technology',
            'employees': '1000-5000',
            'revenue': '$10M-$50M',
            'location': 'San Francisco, CA',
            'founded': '2010',
            'description': f'{company_name} is a leading technology company.'
        }
        return mock_data
    except Exception as e:
        logger.error(f"Error scraping data for {company_name}: {e}")
        return {}

def process_data_etl(df, processing_options):
    """ETL processing function with specialized basketball cognitive data processing"""
    try:
        # Initialize processors
        stats_processor = StatisticalDataProcessor()
        cognitive_processor = BasketballCognitiveProcessor()
        
        # Check if this is basketball cognitive performance data
        if cognitive_processor.detect_cognitive_data(df):
            logger.info("Detected basketball cognitive performance data - using specialized processor")
            
            # Process with cognitive processor
            processed_df, performance_summary_df = cognitive_processor.process_cognitive_data(df, processing_options)
            
            # Save both the detailed data and performance summary
            output_filename = f"processed_cognitive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            processed_df.to_csv(output_path, index=False)
            
            # Save performance summary
            summary_filename = f"performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            summary_path = os.path.join(app.config['PROCESSED_FOLDER'], summary_filename)
            performance_summary_df.to_csv(summary_path, index=False)
            
            # Store summary path in attributes for template access
            processed_df.attrs['performance_summary_path'] = summary_path
            
            return processed_df, output_path
            
        else:
            # Use general statistical processor
            logger.info("Using general statistical data processor")
            processed_df = stats_processor.process_data(df, processing_options)
            
            # Add additional scraping if requested
            if processing_options.get('scrape_additional_data'):
                # Add scraped data for each row (using PLAYER column if available, otherwise first column)
                scraped_data = []
                for index, row in processed_df.iterrows():
                    try:
                        # Try to use PLAYER column first, fallback to first column
                        if 'PLAYER' in row.index and pd.notna(row['PLAYER']):
                            identifier = str(row['PLAYER'])
                        elif len(row) > 0:
                            identifier = str(row.iloc[0])
                        else:
                            identifier = f"Entry_{index}"
                        
                        scraped_info = scrape_company_data(identifier)
                        scraped_data.append(scraped_info)
                    except Exception as e:
                        # If there's any error, add empty data
                        scraped_data.append({})
                
                # Add scraped data as new columns
                if scraped_data:
                    scraped_df = pd.DataFrame(scraped_data)
                    processed_df = pd.concat([processed_df, scraped_df], axis=1)
            
            # Load: Save processed data
            output_filename = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            processed_df.to_csv(output_path, index=False)
            
            return processed_df, output_path
        
    except Exception as e:
        logger.error(f"Error in ETL processing: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scorecard')
def scorecard():
    """ScoreCard dashboard route"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    return render_template('scorecard.html', latest_file=latest_file)

@app.route('/scorecard/<filename>')
def scorecard_with_data(filename):
    """ScoreCard dashboard with specific data file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('scorecard'))
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Extract performance data using the basketball cognitive processor
        processor = BasketballCognitiveProcessor()
        performance_data = processor.extract_performance_data(df)
        
        # Get the original CSV filename for display
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        
        return render_template('scorecard.html', 
                             filename=filename,
                             original_filename=original_filename,
                             performance_data=performance_data,
                             df=df)
        
    except Exception as e:
        flash(f'Error loading data: {str(e)}')
        return redirect(url_for('scorecard'))

@app.route('/scorecard-plus')
def scorecard_plus():
    """ScoreCard Plus comprehensive dashboard route"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    return render_template('scorecard_plus.html', latest_file=latest_file)

@app.route('/scorecard-plus/<filename>')
def scorecard_plus_with_data(filename):
    """Proxy route delegating to dashboard blueprint for backward compatibility"""
    return redirect(url_for('dashboard_bp.scorecard_plus_with_data', filename=filename))

@app.route('/scorecard-plus/<filename>/refresh')
def scorecard_plus_refresh(filename):
    """Refresh ScoreCard Plus dashboard by reprocessing the file"""
    try:
        # Get the original CSV file path
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        original_file_path = os.path.join('..', f'{original_filename}.csv')
        
        # Check if original file exists
        if not os.path.exists(original_file_path):
            flash('Original CSV file not found')
            return redirect(url_for('scorecard_plus_with_data', filename=filename))
        
        # Load and reprocess the original CSV file
        df = pd.read_csv(original_file_path)
        
        # Process the data with ETL
        processing_options = {
            'add_timestamp': True,
            'scrape_additional_data': False
        }
        
        # Use the cognitive processor to reprocess
        processor = BasketballCognitiveProcessor()
        if processor.detect_cognitive_data(df):
            processed_df, performance_summary_df = processor.process_cognitive_data(df, processing_options)
            
            # Save the reprocessed data
            output_filename = f"processed_cognitive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = os.path.join(PROCESSED_FOLDER, output_filename)
            processed_df.to_csv(output_path, index=False)
            
            # Calculate fresh ScoreCard Plus metrics
            scorecard_metrics = processor.calculate_scorecard_plus_metrics(processed_df)
            
            flash('Dashboard refreshed with latest data!')
            return render_template('scorecard_plus.html', 
                                 filename=output_filename,
                                 original_filename=original_filename,
                                 scorecard_metrics=scorecard_metrics,
                                 df=processed_df,
                                 refreshed=True)
        else:
            flash('File is not recognized as basketball cognitive data')
            return redirect(url_for('scorecard_plus_with_data', filename=filename))
        
    except Exception as e:
        flash(f'Error refreshing data: {str(e)}')
        return redirect(url_for('scorecard_plus_with_data', filename=filename))

@app.route('/players')
def players():
    """Player management page"""
    return render_template('players.html')

@app.route('/player-management')
def player_management():
    """Advanced Player Management Dashboard"""
    return render_template('player_management_dashboard.html')
def players():
    """Player management page"""
    return render_template('players.html')

@app.route('/smartdash')
def smartdash():
    """SmartDash dashboard route"""
    # Check if there are any processed cognitive performance files
    processed_files = []
    if os.path.exists(PROCESSED_FOLDER):
        for file in os.listdir(PROCESSED_FOLDER):
            if file.startswith('processed_cognitive_') and file.endswith('.csv'):
                processed_files.append(file)
    
    # Get the most recent file if available
    latest_file = None
    if processed_files:
        latest_file = max(processed_files, key=lambda x: os.path.getctime(os.path.join(PROCESSED_FOLDER, x)))
    
    # Check if a specific file was requested
    requested_file = request.args.get('file')
    if requested_file and requested_file in processed_files:
        return redirect(url_for('smartdash_with_data', filename=requested_file))
    
    # Get all players for the dropdown
    db_manager = DatabaseManager("data/basketball.db")
    # Ensure database has required columns
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(scorecards)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Add space_read_live_dribble if missing
            if "space_read_live_dribble" not in columns:
                cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble INTEGER DEFAULT 0")
                print("Added space_read_live_dribble column")
            
            # Add space_read_catch if missing
            if "space_read_catch" not in columns:
                cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch INTEGER DEFAULT 0")
                print("Added space_read_catch column")
            
            conn.commit()
            print("Database migration completed successfully")
    except Exception as e:
        print(f"Error during database migration: {e}")
    players = db_manager.get_all_players()
    
    return render_template('smartdash.html', 
                         latest_file=latest_file, 
                         processed_files=processed_files,
                         players=players)

@app.route('/smartdash/<filename>')
def smartdash_with_data(filename):
    """SmartDash dashboard with specific data file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('smartdash'))
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Extract smart dashboard metrics using the basketball cognitive processor
        processor = BasketballCognitiveProcessor()
        smart_metrics = processor.calculate_smart_dashboard_metrics(df)
        
        # Get the flattened tally table
        flattened_tally = processor.create_flattened_tally_table(df)
        
        # Get the original CSV filename for display
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        
        return render_template('smartdash.html', 
                             filename=filename,
                             original_filename=original_filename,
                             smart_metrics=smart_metrics,
                             flattened_tally=flattened_tally,
                             df=df)
        
    except Exception as e:
        flash(f'Error loading data: {str(e)}')
        return redirect(url_for('smartdash'))

@app.route('/smartdash-upload', methods=['POST'])
def smartdash_upload():
    """Handle file upload specifically for SmartDash with results table"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('smartdash'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('smartdash'))
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Load the file
            df = load_csv_file(file_path)
            
            # Get processing options
            processing_options = {
                'remove_duplicates': request.form.get('remove_duplicates') == 'on',
                'fill_missing': request.form.get('fill_missing') == 'on',
                'add_timestamp': request.form.get('add_timestamp') == 'on',
                'scrape_additional_data': False  # Disable for SmartDash
            }
            
            # Process the data
            processed_df, output_path = process_data_etl(df, processing_options)
            
            # Convert to JSON for display (same as main upload)
            data_json = processed_df.to_json(orient='records', date_format='iso')
            
            # Get data type and summary statistics
            data_type = getattr(processed_df, 'attrs', {}).get('data_type', 'general_stats')
            summary_stats = getattr(processed_df, 'attrs', {}).get('summary_stats', {})
            completeness = summary_stats.get('completeness_percentage', 100)
            performance_summary_path = getattr(processed_df, 'attrs', {}).get('performance_summary_path', None)
            
            # Check if this is basketball cognitive data
            processor = BasketballCognitiveProcessor()
            is_cognitive_data = processor.detect_cognitive_data(processed_df)
            
            if is_cognitive_data:
                data_type = 'basketball_cognitive_performance'
            
            flash('File uploaded and processed successfully!')
            
            # Get all players for the dropdown - using correct database path
            db_manager = DatabaseManager("data/basketball.db")
            # Ensure database has required columns
            try:
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(scorecards)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    # Add space_read_live_dribble if missing
                    if "space_read_live_dribble" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble INTEGER DEFAULT 0")
                        print("Added space_read_live_dribble column")
                    
                    # Add space_read_catch if missing
                    if "space_read_catch" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch INTEGER DEFAULT 0")
                        print("Added space_read_catch column")
                    
                    # Add driving_paint_touch_positive if missing
                    if "driving_paint_touch_positive" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_positive INTEGER DEFAULT 0")
                        print("Added driving_paint_touch_positive column")
                    
                    # Add driving_paint_touch_negative if missing
                    if "driving_paint_touch_negative" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_negative INTEGER DEFAULT 0")
                        print("Added driving_paint_touch_negative column")
                    
                    # Add driving_physicality_positive if missing
                    if "driving_physicality_positive" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_positive INTEGER DEFAULT 0")
                        print("Added driving_physicality_positive column")
                    
                    # Add driving_physicality_negative if missing
                    if "driving_physicality_negative" not in columns:
                        cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_negative INTEGER DEFAULT 0")
                        print("Added driving_physicality_negative column")
                    
                    conn.commit()
                    print("Database migration completed successfully")
            except Exception as e:
                print(f"Error during database migration: {e}")
            
            players = db_manager.get_all_players()
            
            return render_template('smartdash_results.html', 
                                 data=json.loads(data_json),
                                 columns=processed_df.columns.tolist(),
                                 filename=filename,
                                 output_path=output_path,
                                 data_type=data_type,
                                 completeness=completeness,
                                 summary_stats=summary_stats,
                                 performance_summary_path=performance_summary_path,
                                 players=players)
    
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('smartdash'))
    
    flash('Invalid file type. Please upload a CSV or Excel file.')
    return redirect(url_for('smartdash'))

@app.route('/create-scorecard', methods=['POST'])
def create_scorecard():
    """Create a new scorecard for a selected player"""
    try:
        from src.models.scorecard import Scorecard
        
        # Get form data
        # Accept either the select field (preferred) or legacy 'player_name'
        player_name = request.form.get('player_name') or request.form.get('player_dropdown') or request.form.get('player_name_display')
        date_created = int(datetime.now().timestamp())
        space_read_live_dribble = int(request.form.get('space_read_live_dribble', 0))
        space_read_catch = int(request.form.get('space_read_catch', 0))
        space_read_live_dribble_negative = int(request.form.get('space_read_live_dribble_negative', 0))
        space_read_catch_negative = int(request.form.get('space_read_catch_negative', 0))
        dm_catch_back_to_back_positive = int(request.form.get('dm_catch_back_to_back_positive', 0))
        dm_catch_back_to_back_negative = int(request.form.get('dm_catch_back_to_back_negative', 0))
        dm_catch_uncontested_shot_positive = int(request.form.get('dm_catch_uncontested_shot_positive', 0))
        dm_catch_uncontested_shot_negative = int(request.form.get('dm_catch_uncontested_shot_negative', 0))
        dm_catch_swing_positive = int(request.form.get('dm_catch_swing_positive', 0))
        dm_catch_swing_negative = int(request.form.get('dm_catch_swing_negative', 0))
        dm_catch_drive_pass_positive = int(request.form.get('dm_catch_drive_pass_positive', 0))
        dm_catch_drive_pass_negative = int(request.form.get('dm_catch_drive_pass_negative', 0))
        dm_catch_drive_swing_skip_pass_positive = int(request.form.get('dm_catch_drive_swing_skip_pass_positive', 0))
        dm_catch_drive_swing_skip_pass_negative = int(request.form.get('dm_catch_drive_swing_skip_pass_negative', 0))
        qb12_strong_side_positive = int(request.form.get('qb12_strong_side_positive', 0))
        qb12_strong_side_negative = int(request.form.get('qb12_strong_side_negative', 0))
        qb12_baseline_positive = int(request.form.get('qb12_baseline_positive', 0))
        qb12_baseline_negative = int(request.form.get('qb12_baseline_negative', 0))
        qb12_fill_behind_positive = int(request.form.get('qb12_fill_behind_positive', 0))
        qb12_fill_behind_negative = int(request.form.get('qb12_fill_behind_negative', 0))
        qb12_weak_side_positive = int(request.form.get('qb12_weak_side_positive', 0))
        qb12_weak_side_negative = int(request.form.get('qb12_weak_side_negative', 0))
        qb12_roller_positive = int(request.form.get('qb12_roller_positive', 0))
        qb12_roller_negative = int(request.form.get('qb12_roller_negative', 0))
        qb12_skip_pass_positive = int(request.form.get('qb12_skip_pass_positive', 0))
        qb12_skip_pass_negative = int(request.form.get('qb12_skip_pass_negative', 0))
        qb12_cutter_positive = int(request.form.get('qb12_cutter_positive', 0))
        qb12_cutter_negative = int(request.form.get('qb12_cutter_negative', 0))
        driving_paint_touch_positive = int(request.form.get('driving_paint_touch_positive', 0))
        driving_paint_touch_negative = int(request.form.get('driving_paint_touch_negative', 0))
        driving_physicality_positive = int(request.form.get('driving_physicality_positive', 0))
        driving_physicality_negative = int(request.form.get('driving_physicality_negative', 0))
        
        if not player_name:
            flash('Please select a player')
            return redirect(url_for('smartdash'))
        
        # Create scorecard with new attributes
        scorecard = Scorecard(
            player_name=player_name, 
            date_created=date_created,
            space_read_live_dribble=space_read_live_dribble,
            space_read_catch=space_read_catch,
            space_read_live_dribble_negative=space_read_live_dribble_negative,
            space_read_catch_negative=space_read_catch_negative,
            dm_catch_back_to_back_positive=dm_catch_back_to_back_positive,
            dm_catch_back_to_back_negative=dm_catch_back_to_back_negative,
            dm_catch_uncontested_shot_positive=dm_catch_uncontested_shot_positive,
            dm_catch_uncontested_shot_negative=dm_catch_uncontested_shot_negative,
            dm_catch_swing_positive=dm_catch_swing_positive,
            dm_catch_swing_negative=dm_catch_swing_negative,
            dm_catch_drive_pass_positive=dm_catch_drive_pass_positive,
            dm_catch_drive_pass_negative=dm_catch_drive_pass_negative,
            dm_catch_drive_swing_skip_pass_positive=dm_catch_drive_swing_skip_pass_positive,
            dm_catch_drive_swing_skip_pass_negative=dm_catch_drive_swing_skip_pass_negative,
            qb12_strong_side_positive=qb12_strong_side_positive,
            qb12_strong_side_negative=qb12_strong_side_negative,
            qb12_baseline_positive=qb12_baseline_positive,
            qb12_baseline_negative=qb12_baseline_negative,
            qb12_fill_behind_positive=qb12_fill_behind_positive,
            qb12_fill_behind_negative=qb12_fill_behind_negative,
            qb12_weak_side_positive=qb12_weak_side_positive,
            qb12_weak_side_negative=qb12_weak_side_negative,
            qb12_roller_positive=qb12_roller_positive,
            qb12_roller_negative=qb12_roller_negative,
            qb12_skip_pass_positive=qb12_skip_pass_positive,
            qb12_skip_pass_negative=qb12_skip_pass_negative,
            qb12_cutter_positive=qb12_cutter_positive,
            qb12_cutter_negative=qb12_cutter_negative,
            driving_paint_touch_positive=driving_paint_touch_positive,
            driving_paint_touch_negative=driving_paint_touch_negative,
            driving_physicality_positive=driving_physicality_positive,
            driving_physicality_negative=driving_physicality_negative
        )
        
        # Save to database
        db_manager = DatabaseManager("data/basketball.db")
        # Ensure database has required columns
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(scorecards)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Add space_read_live_dribble if missing
                if "space_read_live_dribble" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble INTEGER DEFAULT 0")
                    print("Added space_read_live_dribble column")
                
                # Add space_read_catch if missing
                if "space_read_catch" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch INTEGER DEFAULT 0")
                    print("Added space_read_catch column")
                
                # Add space_read_live_dribble_negative if missing
                if "space_read_live_dribble_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_live_dribble_negative INTEGER DEFAULT 0")
                    print("Added space_read_live_dribble_negative column")
                
                # Add space_read_catch_negative if missing
                if "space_read_catch_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN space_read_catch_negative INTEGER DEFAULT 0")
                    print("Added space_read_catch_negative column")
                
                # Add DM Catch columns if missing
                if "dm_catch_back_to_back_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_back_to_back_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_back_to_back_positive column")
                
                if "dm_catch_back_to_back_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_back_to_back_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_back_to_back_negative column")
                
                if "dm_catch_uncontested_shot_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_uncontested_shot_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_uncontested_shot_positive column")
                
                if "dm_catch_uncontested_shot_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_uncontested_shot_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_uncontested_shot_negative column")
                
                if "dm_catch_swing_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_swing_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_swing_positive column")
                
                if "dm_catch_swing_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_swing_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_swing_negative column")
                
                if "dm_catch_drive_pass_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_pass_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_pass_positive column")
                
                if "dm_catch_drive_pass_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_pass_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_pass_negative column")
                
                if "dm_catch_drive_swing_skip_pass_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_swing_skip_pass_positive INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_swing_skip_pass_positive column")
                
                if "dm_catch_drive_swing_skip_pass_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN dm_catch_drive_swing_skip_pass_negative INTEGER DEFAULT 0")
                    print("Added dm_catch_drive_swing_skip_pass_negative column")

                # Add QB12 columns if missing
                if "qb12_strong_side_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_strong_side_positive INTEGER DEFAULT 0")
                    print("Added qb12_strong_side_positive column")
                if "qb12_strong_side_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_strong_side_negative INTEGER DEFAULT 0")
                    print("Added qb12_strong_side_negative column")
                if "qb12_baseline_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_baseline_positive INTEGER DEFAULT 0")
                    print("Added qb12_baseline_positive column")
                if "qb12_baseline_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_baseline_negative INTEGER DEFAULT 0")
                    print("Added qb12_baseline_negative column")
                if "qb12_fill_behind_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_fill_behind_positive INTEGER DEFAULT 0")
                    print("Added qb12_fill_behind_positive column")
                if "qb12_fill_behind_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_fill_behind_negative INTEGER DEFAULT 0")
                    print("Added qb12_fill_behind_negative column")
                if "qb12_weak_side_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_weak_side_positive INTEGER DEFAULT 0")
                    print("Added qb12_weak_side_positive column")
                if "qb12_weak_side_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_weak_side_negative INTEGER DEFAULT 0")
                    print("Added qb12_weak_side_negative column")
                if "qb12_roller_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_roller_positive INTEGER DEFAULT 0")
                    print("Added qb12_roller_positive column")
                if "qb12_roller_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_roller_negative INTEGER DEFAULT 0")
                    print("Added qb12_roller_negative column")
                if "qb12_skip_pass_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_skip_pass_positive INTEGER DEFAULT 0")
                    print("Added qb12_skip_pass_positive column")
                if "qb12_skip_pass_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_skip_pass_negative INTEGER DEFAULT 0")
                    print("Added qb12_skip_pass_negative column")
                if "qb12_cutter_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_cutter_positive INTEGER DEFAULT 0")
                    print("Added qb12_cutter_positive column")
                if "qb12_cutter_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN qb12_cutter_negative INTEGER DEFAULT 0")
                    print("Added qb12_cutter_negative column")
                
                # Add driving_paint_touch_positive if missing
                if "driving_paint_touch_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_positive INTEGER DEFAULT 0")
                    print("Added driving_paint_touch_positive column")
                
                # Add driving_paint_touch_negative if missing
                if "driving_paint_touch_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_paint_touch_negative INTEGER DEFAULT 0")
                    print("Added driving_paint_touch_negative column")
                
                # Add driving_physicality_positive if missing
                if "driving_physicality_positive" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_positive INTEGER DEFAULT 0")
                    print("Added driving_physicality_positive column")
                
                # Add driving_physicality_negative if missing
                if "driving_physicality_negative" not in columns:
                    cursor.execute("ALTER TABLE scorecards ADD COLUMN driving_physicality_negative INTEGER DEFAULT 0")
                    print("Added driving_physicality_negative column")
                
                conn.commit()
                print("Database migration completed successfully")
        except Exception as e:
            print(f"Error during database migration: {e}")
        success = db_manager.create_scorecard(scorecard)
        
        if success:
            flash(f'Scorecard created successfully for {player_name}!')
        else:
            flash(f'Failed to create scorecard for {player_name}')
            
        return redirect(url_for('smartdash'))
        
    except Exception as e:
        logger.error(f"Error creating scorecard: {e}")
        flash(f'Error creating scorecard: {str(e)}')
        return redirect(url_for('smartdash'))

@app.route('/autofill-scorecard', methods=['POST'])
def autofill_scorecard():
    """Autofill scorecard attributes from uploaded data"""
    try:
        from src.processors.scorecard_autofill_processor import ScorecardAutofillProcessor
        
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{filename}")
            file.save(file_path)
            
            # Load the file
            df = load_csv_file(file_path)
            
            # Process with autofill processor
            processor = ScorecardAutofillProcessor()
            autofill_data = processor.autofill_scorecard_attributes(df)
            
            # Clean up temp file
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'autofill_data': autofill_data
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error in autofill: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Load the file
            df = load_csv_file(file_path)
            
            # Get processing options
            processing_options = {
                'remove_duplicates': request.form.get('remove_duplicates') == 'on',
                'fill_missing': request.form.get('fill_missing') == 'on',
                'add_timestamp': request.form.get('add_timestamp') == 'on',
                'scrape_additional_data': request.form.get('scrape_additional_data') == 'on'
            }
            
            # Process the data
            processed_df, output_path = process_data_etl(df, processing_options)
            
            # Convert to JSON for display
            data_json = processed_df.to_json(orient='records', date_format='iso')
            
            # Get data type and summary statistics
            data_type = getattr(processed_df, 'attrs', {}).get('data_type', 'general_stats')
            summary_stats = getattr(processed_df, 'attrs', {}).get('summary_stats', {})
            completeness = summary_stats.get('completeness_percentage', 100)
            performance_summary_path = getattr(processed_df, 'attrs', {}).get('performance_summary_path', None)
            
            flash('File uploaded and processed successfully!')
            return render_template('results.html', 
                                 data=json.loads(data_json),
                                 columns=processed_df.columns.tolist(),
                                 filename=filename,
                                 output_path=output_path,
                                 data_type=data_type,
                                 completeness=completeness,
                                 summary_stats=summary_stats,
                                 performance_summary_path=performance_summary_path)
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for processing data"""
    try:
        data = request.get_json()
        csv_data = data.get('csv_data')
        processing_options = data.get('processing_options', {})
        
        # Convert CSV string to DataFrame
        df = pd.read_csv(pd.StringIO(csv_data))
        
        # Process the data
        processed_df, output_path = process_data_etl(df, processing_options)
        
        return jsonify({
            'success': True,
            'data': processed_df.to_dict('records'),
            'columns': processed_df.columns.tolist(),
            'output_path': output_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081) 