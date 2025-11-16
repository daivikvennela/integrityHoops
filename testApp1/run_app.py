import os
import sys
import argparse
from src.core.app import app

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Basketball Cognitive Performance Dashboard')
    parser.add_argument('--port', type=int, help='Port to run the server on')
    args = parser.parse_args()
    
    # Get port from command-line argument, environment variable, or default to 8000
    port = args.port or int(os.environ.get('PORT', 8000))
    
    print(f"🌐 Starting server on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port)
