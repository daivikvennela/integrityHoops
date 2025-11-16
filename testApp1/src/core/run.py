#!/usr/bin/env python3
"""
Startup script for the Basketball Cognitive Performance Dashboard
"""

import os
import sys
import argparse
from src.core.app import app

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Basketball Cognitive Performance Dashboard')
    parser.add_argument('--port', type=int, help='Port to run the server on')
    args = parser.parse_args()
    
    # Get port from command-line argument, environment variable, or default to 8000
    port = args.port or int(os.environ.get('PORT', 8000))
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    print("🚀 Starting Basketball Cognitive Performance Dashboard...")
    print("📁 Upload directory:", app.config['UPLOAD_FOLDER'])
    print("📁 Processed directory:", app.config['PROCESSED_FOLDER'])
    print(f"🌐 Access the application at: http://localhost:{port}")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
