#!/bin/bash
# Run all test cases for team statistics

echo "=" | head -c 70; echo
echo "🧪 RUNNING ALL TEAM STATISTICS TESTS"
echo "=" | head -c 70; echo
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Backend API Tests
echo -e "${YELLOW}📡 Running Backend API Tests...${NC}"
echo
python3 testApp1/tests/test_team_statistics_api.py
BACKEND_EXIT=$?

echo
echo "=" | head -c 70; echo
echo

if [ $BACKEND_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Backend tests passed!${NC}"
else
    echo -e "${RED}❌ Backend tests failed!${NC}"
fi

echo
echo "=" | head -c 70; echo
echo
echo -e "${YELLOW}📋 Frontend Tests${NC}"
echo
echo "To run frontend tests:"
echo "1. Open your browser and navigate to: http://localhost:5000/analytics-dashboard"
echo "2. Open the browser console (F12 → Console tab)"
echo "3. Copy and paste the contents of: testApp1/tests/test_frontend_display.js"
echo "   OR visit: http://localhost:5000/static/js/test_frontend_display.js"
echo "4. The tests will run automatically"
echo
echo "Alternatively, you can run:"
echo "  curl http://localhost:5000/static/js/test_frontend_display.js | node"
echo

echo "=" | head -c 70; echo
echo "✅ Test execution complete!"
echo "=" | head -c 70; echo

