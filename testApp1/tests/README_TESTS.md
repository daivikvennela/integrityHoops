# Team Statistics Test Suite

This directory contains comprehensive test cases to verify that team statistics data is being calculated and displayed correctly.

## Test Files

### 1. `test_team_statistics_flask.py`
Flask-based unit tests that test the API endpoints directly.
**Requires:** Flask app context, pandas, and other dependencies

**Run:**
```bash
python3 testApp1/tests/test_team_statistics_flask.py
```

### 2. `test_via_http.sh`
HTTP-based integration tests that test the API via HTTP requests.
**Requires:** Flask app running, curl

**Run:**
```bash
# Make sure Flask app is running first
cd testApp1 && python3 run_app.py

# In another terminal:
./testApp1/tests/test_via_http.sh
# Or specify custom URL:
./testApp1/tests/test_via_http.sh http://localhost:5000
```

### 3. `test_frontend_display.js`
Browser-based frontend tests that verify data display in the UI.
**Requires:** Browser on analytics dashboard page

**Run:**
1. Open browser and navigate to: `http://localhost:5000/analytics-dashboard`
2. Open browser console (F12 → Console tab)
3. Copy and paste the contents of `testApp1/tests/test_frontend_display.js`
4. Tests will run automatically

Or load it directly:
```javascript
// In browser console:
fetch('/static/js/test_frontend_display.js')
  .then(r => r.text())
  .then(eval);
```

## Test Coverage

### Backend Tests
- ✅ CSV files exist and are readable
- ✅ CSV files can be parsed (dates, opponents)
- ✅ Scores can be calculated from CSV files
- ✅ Data is stored in database correctly
- ✅ API returns correct data structure
- ✅ 6 games are present in database

### API Tests
- ✅ API endpoint is accessible (200 status)
- ✅ API returns success=true
- ✅ API has statistics, overall_scores, game_info fields
- ✅ Force recalculation works
- ✅ Category filtering works

### Frontend Tests
- ✅ API endpoint accessible from browser
- ✅ Chart element exists
- ✅ Chart.js library loaded
- ✅ Chart instance created
- ✅ Overall scores list populated
- ✅ 6 games displayed

## Quick Test Checklist

1. **Backend Processing:**
   ```bash
   ./testApp1/tests/test_via_http.sh
   ```

2. **Frontend Display:**
   - Open `/analytics-dashboard` in browser
   - Open console (F12)
   - Run `test_frontend_display.js`

3. **Manual Verification:**
   - Check browser console for: "📊 Found 6 unique games"
   - Check chart shows 6 data points
   - Check "Overall Cog Scores" section shows 6 buttons

## Expected Results

- ✅ 6 CSV files processed
- ✅ 6 unique game dates in database
- ✅ 6 overall scores calculated
- ✅ 6 points on chart
- ✅ 6 buttons in overall scores list

## Troubleshooting

If tests fail:

1. **Backend not processing CSV files:**
   - Check CSV files exist in `testcases/test_csvs/`
   - Check Flask app logs for errors
   - Try calling `/api/team-statistics?force_recalculate=true`

2. **Frontend not displaying data:**
   - Check browser console for errors
   - Verify API returns data: `curl http://localhost:5000/api/team-statistics`
   - Click "Refresh Data" button
   - Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)

3. **Database issues:**
   - Check database file exists: `src/core/data/basketball.db`
   - Verify database has data: Check `team_statistics` table
   - Try force recalculation to rebuild database

