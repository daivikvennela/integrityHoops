#!/usr/bin/env python3
"""
Startup script for the CSV ETL Processor Web Application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting CSV ETL Processor Web Application...")
    print("📁 Upload directory:", app.config['UPLOAD_FOLDER'])
    print("📁 Processed directory:", app.config['PROCESSED_FOLDER'])
    print("🌐 Access the application at: http://localhost:5001")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1) 