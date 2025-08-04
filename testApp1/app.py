import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import logging
from custom_etl_processor import StatisticalDataProcessor
from basketball_cognitive_processor import BasketballCognitiveProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
    """ScoreCard Plus dashboard with specific data file"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            flash('File not found')
            return redirect(url_for('scorecard_plus'))
        
        # Load the processed data
        df = pd.read_csv(file_path)
        
        # Extract comprehensive performance data using the new calculation functions
        processor = BasketballCognitiveProcessor()
        scorecard_metrics = processor.calculate_scorecard_plus_metrics(df)
        
        # Get the original CSV filename for display
        original_filename = filename.replace('processed_cognitive_', '').replace('.csv', '')
        
        return render_template('scorecard_plus.html', 
                             filename=filename,
                             original_filename=original_filename,
                             scorecard_metrics=scorecard_metrics,
                             df=df)
        
    except Exception as e:
        flash(f'Error loading data: {str(e)}')
        return redirect(url_for('scorecard_plus'))

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
    
    return render_template('smartdash.html', latest_file=latest_file, processed_files=processed_files)

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
            return render_template('smartdash_results.html', 
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
            return redirect(url_for('smartdash'))
    
    flash('Invalid file type. Please upload a CSV or Excel file.')
    return redirect(url_for('smartdash'))

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