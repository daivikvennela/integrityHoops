#!/usr/bin/env python3
"""
Startup script for the Basketball Cognitive Performance Dashboard
"""

import os
import sys
from src.core.app import app

def main():
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting Basketball Cognitive Performance Dashboard...")
    print("📁 Upload directory:", app.config['UPLOAD_FOLDER'])
    print("📁 Processed directory:", app.config['PROCESSED_FOLDER'])
    print("🌐 Access the application at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
