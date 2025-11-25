#!/bin/bash
# Script to process new CSV files and add scores to player dashboard
# This calls the Flask API endpoint to process all CSV files

echo "🚀 Processing CSV files and calculating scores..."
echo ""

# Try to call the API endpoint
response=$(curl -s -X POST http://localhost:5000/api/cog-scores/process-all-csvs \
  -H "Content-Type: application/json" 2>&1)

if [ $? -eq 0 ]; then
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
    echo "✅ Done! Check the player dashboard to see the new scores."
else
    echo "❌ Error: Could not connect to Flask server."
    echo ""
    echo "Please start the Flask app first:"
    echo "  cd testApp1 && python3 run_app.py"
    echo ""
    echo "Then run this script again, or call the endpoint directly:"
    echo "  curl -X POST http://localhost:5000/api/cog-scores/process-all-csvs"
fi

