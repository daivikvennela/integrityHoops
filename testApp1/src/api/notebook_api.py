"""
Notebook API Blueprint
Handles ML notebook routes and API endpoints
"""

import os
import logging
import json
from flask import Blueprint, render_template, request, jsonify, current_app, session
from werkzeug.utils import secure_filename
from src.core.kernel_manager import kernel_manager
from src.processors.ml_notebook_processor import MLNotebookProcessor

logger = logging.getLogger(__name__)

# Create Blueprint
notebook_api = Blueprint('notebook_api', __name__, url_prefix='/api/notebook')
notebook_bp = Blueprint('notebook', __name__)


# Helper function to get or create session kernel
def get_session_kernel():
    """Get or create a kernel for the current user session"""
    if 'kernel_session_id' not in session:
        session['kernel_session_id'] = kernel_manager.create_kernel()
    return session['kernel_session_id']


@notebook_bp.route('/ml-notebook')
def ml_notebook():
    """Main ML Notebook interface page"""
    try:
        # Initialize kernel for this session
        kernel_session_id = get_session_kernel()
        
        # Get list of available CSV files
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'data/uploads')
        csv_files = []
        
        if os.path.exists(upload_folder):
            for file in os.listdir(upload_folder):
                if file.endswith('.csv'):
                    csv_files.append(file)
        
        return render_template(
            'ml_notebook.html',
            kernel_session_id=kernel_session_id,
            csv_files=csv_files
        )
        
    except Exception as e:
        logger.error(f"Error loading ML notebook page: {e}")
        return f"Error loading notebook: {str(e)}", 500


@notebook_api.route('/execute', methods=['POST'])
def execute_code():
    """
    Execute Python code in the kernel.
    
    Request JSON:
    {
        "code": "print('Hello, World!')",
        "timeout": 60  # optional
    }
    
    Response JSON:
    {
        "success": true,
        "output": "...",
        "error": "...",
        "display_data": [...],
        "execution_count": 1
    }
    """
    try:
        data = request.get_json()
        code = data.get('code', '')
        timeout = data.get('timeout', 60)
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'No code provided'
            }), 400
        
        # Get kernel for this session
        kernel_session_id = get_session_kernel()
        
        # Execute code
        result = kernel_manager.execute_code(kernel_session_id, code, timeout)
        
        # Format output for display
        processor = MLNotebookProcessor(current_app.config.get('UPLOAD_FOLDER', 'data/uploads'))
        formatted_result = processor.format_output_for_display(result)
        
        return jsonify(formatted_result)
        
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'output': '',
            'display_data': []
        }), 500


@notebook_api.route('/upload-csv', methods=['POST'])
def upload_csv():
    """
    Upload a CSV file and load it into the kernel.
    
    Response JSON:
    {
        "success": true,
        "filename": "data.csv",
        "dataframe_info": {...},
        "load_code": "df = pd.read_csv(...)"
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Only CSV files are supported'
            }), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'data/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Get DataFrame info
        processor = MLNotebookProcessor(upload_folder)
        df_info = processor.load_csv_to_dataframe(file_path)
        
        if not df_info.get('success'):
            return jsonify(df_info), 400
        
        # Generate load code
        load_code = processor.generate_csv_load_code(file_path, variable_name='df')
        
        # Execute load code in kernel
        kernel_session_id = get_session_kernel()
        execution_result = kernel_manager.execute_code(kernel_session_id, load_code, timeout=30)
        
        if not execution_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Failed to load CSV into kernel',
                'details': execution_result.get('error', '')
            }), 500
        
        return jsonify({
            'success': True,
            'filename': filename,
            'dataframe_info': df_info,
            'load_code': load_code,
            'execution_output': execution_result.get('output', '')
        })
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notebook_api.route('/load-template', methods=['POST'])
def load_template():
    """
    Load a notebook template.
    
    Request JSON:
    {
        "template": "linear_regression" | "data_exploration" | "blank"
    }
    
    Response JSON:
    {
        "success": true,
        "cells": [...]
    }
    """
    try:
        data = request.get_json()
        template_name = data.get('template', 'blank')
        
        processor = MLNotebookProcessor(current_app.config.get('UPLOAD_FOLDER', 'data/uploads'))
        
        if template_name == 'linear_regression':
            cells = processor.create_linear_regression_template()
        elif template_name == 'data_exploration':
            cells = processor.create_data_exploration_template()
        elif template_name == 'blank':
            cells = processor.create_blank_template()
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown template: {template_name}'
            }), 400
        
        return jsonify({
            'success': True,
            'cells': cells,
            'template_name': template_name
        })
        
    except Exception as e:
        logger.error(f"Error loading template: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notebook_api.route('/kernel/status', methods=['GET'])
def kernel_status():
    """
    Get kernel status for current session.
    
    Response JSON:
    {
        "exists": true,
        "is_alive": true,
        "created_at": 1234567890,
        "last_activity": 1234567890
    }
    """
    try:
        kernel_session_id = session.get('kernel_session_id')
        
        if not kernel_session_id:
            return jsonify({
                'exists': False,
                'message': 'No kernel session found'
            })
        
        status = kernel_manager.get_kernel_status(kernel_session_id)
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting kernel status: {e}")
        return jsonify({
            'exists': False,
            'error': str(e)
        }), 500


@notebook_api.route('/kernel/restart', methods=['POST'])
def restart_kernel():
    """
    Restart the kernel for current session.
    
    Response JSON:
    {
        "success": true,
        "kernel_session_id": "..."
    }
    """
    try:
        # Stop old kernel if exists
        old_kernel_id = session.get('kernel_session_id')
        if old_kernel_id:
            kernel_manager.stop_kernel(old_kernel_id)
        
        # Create new kernel
        new_kernel_id = kernel_manager.create_kernel()
        session['kernel_session_id'] = new_kernel_id
        
        return jsonify({
            'success': True,
            'kernel_session_id': new_kernel_id,
            'message': 'Kernel restarted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error restarting kernel: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notebook_api.route('/save-notebook', methods=['POST'])
def save_notebook():
    """
    Save notebook cells as .ipynb file.
    
    Request JSON:
    {
        "cells": [...],
        "filename": "my_notebook.ipynb"
    }
    
    Response JSON:
    {
        "success": true,
        "filepath": "..."
    }
    """
    try:
        data = request.get_json()
        cells = data.get('cells', [])
        filename = data.get('filename', 'notebook.ipynb')
        
        if not filename.endswith('.ipynb'):
            filename += '.ipynb'
        
        # Create notebooks directory if it doesn't exist
        notebooks_dir = os.path.join(
            current_app.root_path,
            '..',
            'notebooks',
            'saved'
        )
        os.makedirs(notebooks_dir, exist_ok=True)
        
        output_path = os.path.join(notebooks_dir, secure_filename(filename))
        
        processor = MLNotebookProcessor(current_app.config.get('UPLOAD_FOLDER', 'data/uploads'))
        success = processor.save_notebook_as_ipynb(cells, output_path)
        
        if success:
            return jsonify({
                'success': True,
                'filepath': output_path,
                'filename': filename
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save notebook'
            }), 500
        
    except Exception as e:
        logger.error(f"Error saving notebook: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notebook_api.route('/list-csv-files', methods=['GET'])
def list_csv_files():
    """
    List available CSV files in upload folder.
    
    Response JSON:
    {
        "success": true,
        "files": ["file1.csv", "file2.csv", ...]
    }
    """
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'data/uploads')
        csv_files = []
        
        if os.path.exists(upload_folder):
            for file in os.listdir(upload_folder):
                if file.endswith('.csv'):
                    file_path = os.path.join(upload_folder, file)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    csv_files.append({
                        'filename': file,
                        'size_mb': round(file_size, 2)
                    })
        
        return jsonify({
            'success': True,
            'files': csv_files
        })
        
    except Exception as e:
        logger.error(f"Error listing CSV files: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notebook_api.route('/csv-info/<filename>', methods=['GET'])
def get_csv_info(filename):
    """
    Get information about a specific CSV file.
    
    Response JSON:
    {
        "success": true,
        "info": {...}
    }
    """
    try:
        filename = secure_filename(filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'data/uploads')
        file_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        processor = MLNotebookProcessor(upload_folder)
        df_info = processor.load_csv_to_dataframe(file_path)
        
        return jsonify({
            'success': True,
            'info': df_info
        })
        
    except Exception as e:
        logger.error(f"Error getting CSV info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

