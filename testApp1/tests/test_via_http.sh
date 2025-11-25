#!/bin/bash
# HTTP-based test script for Team Statistics API
# Run this while your Flask app is running

BASE_URL="${1:-http://localhost:5000}"

echo "=" | head -c 70; echo
echo "🧪 TEAM STATISTICS HTTP TEST SUITE"
echo "=" | head -c 70; echo
echo "Testing: $BASE_URL"
echo

PASSED=0
FAILED=0

test() {
    local name="$1"
    local condition="$2"
    local message="$3"
    
    if eval "$condition"; then
        PASSED=$((PASSED + 1))
        echo "✅ $name: $message"
        return 0
    else
        FAILED=$((FAILED + 1))
        echo "❌ $name: $message"
        return 1
    fi
}

# Test 1: API Endpoint Accessible
echo "📡 Test 1: API Endpoint Accessibility"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/team-statistics")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

test "API Returns 200" "[ $http_code -eq 200 ]" "HTTP $http_code"

if [ $http_code -eq 200 ]; then
    success=$(echo "$body" | grep -o '"success":[^,}]*' | cut -d: -f2 | tr -d ' ')
    test "Response Has Success Field" "[ \"$success\" = \"true\" ]" "success=$success"
fi

echo

# Test 2: Check for 6 games
echo "📊 Test 2: Six Games Present"
response=$(curl -s "$BASE_URL/api/team-statistics?force_recalculate=true")
overall_count=$(echo "$response" | grep -o '"overall_scores":{[^}]*}' | grep -o '"[0-9-]*":' | wc -l | tr -d ' ')

test "Has Overall Scores" "[ $overall_count -gt 0 ]" "Found $overall_count games"

if [ $overall_count -ge 6 ]; then
    test "Has 6+ Games" "true" "Found $overall_count games (expected 6+)"
    echo "   Games found:"
    echo "$response" | grep -o '"[0-9-]*":[0-9.]*' | head -6 | while read line; do
        date=$(echo "$line" | cut -d: -f1 | tr -d '"')
        score=$(echo "$line" | cut -d: -f2)
        echo "     • $date: $score%"
    done
else
    test "Has 6+ Games" "false" "Found only $overall_count games (expected 6+)"
fi

echo

# Test 3: Check statistics data
echo "📋 Test 3: Statistics Data Structure"
response=$(curl -s "$BASE_URL/api/team-statistics")
has_statistics=$(echo "$response" | grep -q '"statistics"' && echo "true" || echo "false")
has_overall=$(echo "$response" | grep -q '"overall_scores"' && echo "true" || echo "false")
has_game_info=$(echo "$response" | grep -q '"game_info"' && echo "true" || echo "false")

test "Has Statistics Field" "[ \"$has_statistics\" = \"true\" ]" "statistics field present"
test "Has Overall Scores Field" "[ \"$has_game_info\" = \"true\" ]" "overall_scores field present"
test "Has Game Info Field" "[ \"$has_game_info\" = \"true\" ]" "game_info field present"

echo

# Test 4: Force Recalculate
echo "🔄 Test 4: Force Recalculate Works"
response=$(curl -s "$BASE_URL/api/team-statistics?force_recalculate=true")
source=$(echo "$response" | grep -o '"source":"[^"]*"' | cut -d: -f2 | tr -d '"')

if [ "$source" = "csv_calculated" ]; then
    test "Force Recalculate Works" "true" "Triggered CSV calculation"
    
    # Extract diagnostics if available
    files_found=$(echo "$response" | grep -o '"files_found":[0-9]*' | cut -d: -f2)
    files_processed=$(echo "$response" | grep -o '"files_processed":[0-9]*' | cut -d: -f2)
    
    if [ -n "$files_found" ]; then
        echo "   • Files found: $files_found"
    fi
    if [ -n "$files_processed" ]; then
        echo "   • Files processed: $files_processed"
    fi
else
    test "Force Recalculate Works" "false" "Source: $source (expected csv_calculated)"
fi

echo

# Summary
echo "=" | head -c 70; echo
echo "📊 TEST SUMMARY"
echo "=" | head -c 70; echo
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
TOTAL=$((PASSED + FAILED))
if [ $TOTAL -gt 0 ]; then
    SUCCESS_RATE=$(echo "scale=1; $PASSED * 100 / $TOTAL" | bc)
    echo "📈 Success Rate: ${SUCCESS_RATE}%"
fi
echo "=" | head -c 70; echo

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Check the output above."
    exit 1
fi

