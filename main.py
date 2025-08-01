#!/usr/bin/env python3
"""
Main entry point for the Basketball Cognitive Performance Dashboard
"""

import os
import sys

# Add the testApp1 directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'testApp1'))

from app import app

if __name__ == '__main__':
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting Basketball Cognitive Performance Dashboard...")
    print("📁 Upload directory:", app.config['UPLOAD_FOLDER'])
    print("📁 Processed directory:", app.config['PROCESSED_FOLDER'])
    print("🌐 Access the application at: http://localhost:5002")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1) 