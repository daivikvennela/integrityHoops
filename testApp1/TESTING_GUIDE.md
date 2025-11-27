# CSV Processing Pipeline Testing Guide

## Overview

This guide covers testing the complete CSV processing workflow, including file validation, preprocessing, database import, and notification system.

## Test Structure

The test suite is organized into four main categories:

1. **CSV Preprocessor Tests** - Tests CSV splitting by Row column
2. **Game Validator Tests** - Tests duplicate detection and validation
3. **CSV to Database Importer Tests** - Tests complete import workflow
4. **Pipeline Integration Tests** - Tests end-to-end workflow

## Running Tests

### Option 1: Run All Tests with Enhanced Reporter

```bash
cd /Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1
python tests/run_pipeline_tests.py
```

This will run all test suites with detailed reporting including:
- Test progress for each suite
- Pass/fail status for individual tests
- Duration metrics
- Final summary with statistics

### Option 2: Run Individual Test Suite

```bash
cd /Users/daivikvennela/workspace/testApp/IntegrityHoops/testApp1
python -m unittest tests.test_csv_pipeline.TestCSVPreprocessor -v
```

Available test classes:
- `TestCSVPreprocessor`
- `TestGameValidator`
- `TestCSVToDatabaseImporter`
- `TestPipelineIntegration`

### Option 3: Run Specific Test

```bash
python -m unittest tests.test_csv_pipeline.TestCSVPreprocessor.test_split_by_row -v
```

## Test Coverage

### CSV Preprocessor Tests

| Test | Description |
|------|-------------|
| `test_filename_parsing` | Validates parsing game metadata from filename |
| `test_game_id_generation` | Verifies deterministic game_id creation |
| `test_csv_loading` | Tests CSV file loading |
| `test_split_by_row` | Validates splitting CSV by Row column |

### Game Validator Tests

| Test | Description |
|------|-------------|
| `test_csv_file_validation` | Tests file format validation |
| `test_filename_parsing` | Tests filename metadata extraction |
| `test_duplicate_detection` | Verifies duplicate game prevention |

### CSV to Database Importer Tests

| Test | Description |
|------|-------------|
| `test_import_mega_csv` | Tests importing mega CSV with team and players |
| `test_duplicate_game_prevention` | Verifies duplicate upload blocking |

### Pipeline Integration Tests

| Test | Description |
|------|-------------|
| `test_complete_workflow` | End-to-end test of entire pipeline |

## Notification System

### How Notifications Work

The upload workflow provides real-time notifications at each step:

1. **Step 1**: File validation
2. **Step 2**: Validation success
3. **Step 3**: Game processing starts
4. **Step 4**: Team data processed (with cog score)
5. **Step 5**: Player data processed (count and names)
6. **Step 6**: Database storage complete
7. **Step 7**: Final success message

### Notification Types

- **Info** (blue): Informational updates
- **Success** (green): Successful completion of a step
- **Warning** (yellow): Non-critical issues
- **Error** (red): Failures and errors

### Testing Notifications

#### Via Web Interface:

1. Start the Flask app:
   ```bash
   python main.py
   ```

2. Navigate to http://localhost:5000/database-viz

3. Upload a CSV file:
   - Drag and drop onto the upload zone, OR
   - Click "Browse Files" button

4. Watch notifications appear in real-time

#### Expected Notification Flow (Success):

```
ℹ️ Step 1: Validating file: 10.12.25 MIA v ORL.csv
✓ Step 2: File validated successfully
ℹ️ Step 3: Processing game: 10.12.25 vs ORL
✓ Step 4: Team data processed - Cog Score: 75.3
✓ Step 5: Processed 2 players: Jimmy Butler, Bam Adebayo
✓ Step 6: Game abc123def4567890 saved to database
✓ Step 7: Import complete! Game ID: abc123def4567890
```

#### Expected Notification Flow (Duplicate):

```
ℹ️ Step 1: Validating file: 10.12.25 MIA v ORL.csv
✗ Step 2: Validation failed: Game already exists for 10.12.25 vs ORL
```

#### Expected Notification Flow (Invalid File):

```
ℹ️ Step 1: Validating file: invalid.csv
✗ Step 2: Validation failed: Cannot parse game date and opponent from filename
```

## Manual Testing Scenarios

### Scenario 1: Upload Valid Mega CSV

**File**: `10.12.25 MIA v ORL.csv`
**Content**: Team rows + player rows

**Expected Result**:
- ✓ File uploads successfully
- ✓ Notifications show each processing step
- ✓ Game appears in games table
- ✓ Players appear in players table
- ✓ Analytics dashboard updates with new stats

### Scenario 2: Upload Duplicate Game

**File**: Same file as Scenario 1

**Expected Result**:
- ✗ Upload rejected
- ✗ Error notification: "Game already exists"
- ✓ No database changes

### Scenario 3: Upload Invalid File

**File**: `invalid_format.csv`

**Expected Result**:
- ✗ Upload rejected
- ✗ Error notification about filename format
- ✓ No database changes

### Scenario 4: Drag and Drop

**Action**: Drag CSV file onto upload zone

**Expected Result**:
- ✓ Drag zone highlights during drag
- ✓ File processes on drop
- ✓ Notifications appear

### Scenario 5: Upload Team-Only CSV

**File**: CSV with only "Miami Heat" rows

**Expected Result**:
- ✓ File uploads successfully
- ✓ Team scorecard created
- ℹ️ No players processed (0 players)
- ✓ Game still appears in database

## Verifying Database State

After upload, verify database contents:

```bash
sqlite3 basketball.db

# List all games
SELECT * FROM games;

# List all players
SELECT * FROM players;

# List scorecards for a specific game
SELECT * FROM scorecards WHERE game_id = 'YOUR_GAME_ID';

# Get team cog scores
SELECT * FROM team_cog_scores WHERE game_id = 'YOUR_GAME_ID';

# Get player cog scores
SELECT * FROM player_cog_scores WHERE game_id = 'YOUR_GAME_ID';
```

## Performance Benchmarks

Expected processing times (approximate):

| File Size | Rows | Players | Expected Time |
|-----------|------|---------|---------------|
| Small | 50-100 | 1-2 | < 2 seconds |
| Medium | 100-200 | 3-5 | 2-5 seconds |
| Large | 200-500 | 5-10 | 5-10 seconds |
| Very Large | 500+ | 10+ | 10-20 seconds |

## Troubleshooting

### Tests Failing

1. **Database locked error**:
   - Close any database browser tools
   - Delete `test.db` files in temp directories

2. **Import errors**:
   - Ensure you're running from the correct directory
   - Check Python path includes project root

3. **Module not found**:
   - Verify virtual environment is activated
   - Run `pip install -r requirements.txt`

### Upload Failing

1. **File not uploading**:
   - Check file size (< 50MB recommended)
   - Verify CSV format is correct
   - Check console for JavaScript errors

2. **Notifications not appearing**:
   - Check browser console for errors
   - Verify API endpoint is responding
   - Check Flask logs for backend errors

3. **Duplicate game error (unexpected)**:
   - Verify game_id generation is deterministic
   - Check database for existing game with same date/opponent
   - Clear database if needed for testing: `rm basketball.db`

## CI/CD Integration

To integrate tests into CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run CSV Pipeline Tests
  run: |
    python tests/run_pipeline_tests.py
```

Exit codes:
- `0`: All tests passed
- `1`: Some tests failed

## Next Steps

After verifying all tests pass:

1. ✅ Test with actual game CSV files
2. ✅ Verify analytics dashboard updates
3. ✅ Test player management dashboard
4. ✅ Test PDF export functionality
5. ✅ Test player comparison features

## Support

For issues or questions:
1. Check Flask application logs
2. Review browser console for frontend errors
3. Run tests with `-v` flag for verbose output
4. Check database state with SQLite browser

