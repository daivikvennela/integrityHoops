# Analytics Dashboard & Cognitive Score Calculator - MECE Test Cases

## Test Suite Overview
**System Under Test**: Analytics Dashboard, Cognitive Score Calculator, Score Reveal Animation  
**Test Framework**: MECE (Mutually Exclusive, Collectively Exhaustive)  
**Last Updated**: October 14, 2025

---

## 1. COGNITIVE SCORE CALCULATION TESTS

### 1.1 Formula Validation Tests
**Category**: Core Calculation Logic

#### TC-1.1.1: Basic Score Calculation
- **Input**: CSV with 100 positives, 50 negatives
- **Expected**: Score = (100 / 150) * 100 = 66.67%
- **Priority**: P0 - Critical

#### TC-1.1.2: All Positive Scenario
- **Input**: CSV with 200 positives, 0 negatives
- **Expected**: Score = 100%
- **Priority**: P0 - Critical

#### TC-1.1.3: All Negative Scenario
- **Input**: CSV with 0 positives, 150 negatives
- **Expected**: Score = 0%
- **Priority**: P0 - Critical

#### TC-1.1.4: Equal Positive/Negative
- **Input**: CSV with 75 positives, 75 negatives
- **Expected**: Score = 50%
- **Priority**: P1 - High

#### TC-1.1.5: No Data Scenario
- **Input**: CSV with 0 positives, 0 negatives (empty column)
- **Expected**: Score = 0%, no division by zero error
- **Priority**: P0 - Critical

#### TC-1.1.6: Decimal Precision
- **Input**: CSV with 67 positives, 33 negatives
- **Expected**: Score = 67.00% (rounded to 2 decimals)
- **Priority**: P2 - Medium

---

### 1.2 CSV Parsing Tests
**Category**: Data Input Processing

#### TC-1.2.1: Valid CSV Format
- **Input**: Standard Heat vs Bucks CSV with all columns
- **Expected**: Successfully parses all 11 cognitive columns
- **Priority**: P0 - Critical

#### TC-1.2.2: Missing Cognitive Column
- **Input**: CSV missing "Footwork" column
- **Expected**: Returns 0 score for missing column, continues processing
- **Priority**: P1 - High

#### TC-1.2.3: Multiple +ve/-ve in Single Cell
- **Input**: Cell contains "+ve Driving: Paint Touch, +ve Driving: Physicality"
- **Expected**: Counts 2 positives correctly
- **Priority**: P0 - Critical

#### TC-1.2.4: Empty Cells
- **Input**: CSV with many empty cells in cognitive columns
- **Expected**: Ignores empty cells, processes only filled ones
- **Priority**: P1 - High

#### TC-1.2.5: Special Characters in Data
- **Input**: CSV with commas, quotes, special chars in cognitive entries
- **Expected**: Correctly parses without breaking
- **Priority**: P1 - High

#### TC-1.2.6: Large CSV File
- **Input**: CSV with 5000+ rows
- **Expected**: Processes within 5 seconds, returns accurate score
- **Priority**: P2 - Medium

#### TC-1.2.7: Malformed CSV
- **Input**: CSV with inconsistent column counts
- **Expected**: Returns error message, doesn't crash
- **Priority**: P1 - High

---

### 1.3 Date Extraction Tests
**Category**: Metadata Processing

#### TC-1.3.1: Standard Date Format
- **Input**: Timeline = "10.06.25 Heat v Bucks Team"
- **Expected**: Extracts date = "10.06.25"
- **Priority**: P0 - Critical

#### TC-1.3.2: Missing Date
- **Input**: Timeline = "Heat v Bucks Team" (no date)
- **Expected**: game_date = null, doesn't crash
- **Priority**: P1 - High

#### TC-1.3.3: Different Date Format
- **Input**: Timeline = "2025-10-06 Heat v Bucks"
- **Expected**: Attempts extraction, handles gracefully if fails
- **Priority**: P2 - Medium

#### TC-1.3.4: Invalid Date
- **Input**: Timeline = "99.99.99 Heat v Bucks"
- **Expected**: Extracts string but doesn't crash on conversion
- **Priority**: P2 - Medium

---

### 1.4 Per-Category Score Tests
**Category**: Individual Cognitive Skills

#### TC-1.4.1: All 11 Categories Calculated
- **Input**: Valid CSV with data in all columns
- **Expected**: Returns breakdown with all 11 cognitive skills
- **Priority**: P0 - Critical

#### TC-1.4.2: Category with High Score
- **Input**: "Driving" column with 99 positives, 1 negative
- **Expected**: Driving score = 99%
- **Priority**: P1 - High

#### TC-1.4.3: Category with Low Score
- **Input**: "Footwork" column with 12 positives, 51 negatives
- **Expected**: Footwork score = 19.05%
- **Priority**: P1 - High

#### TC-1.4.4: Overall Score Calculation
- **Input**: Multiple categories with varying scores
- **Expected**: Overall = average of all category scores
- **Priority**: P0 - Critical

---

## 2. API ENDPOINT TESTS

### 2.1 CSV Upload Endpoint Tests
**Category**: `/api/cog-scores/calculate-from-csv`

#### TC-2.1.1: Successful Upload
- **Input**: POST with valid CSV file
- **Expected**: 200 status, returns JSON with overall_score and breakdown
- **Priority**: P0 - Critical

#### TC-2.1.2: No File Provided
- **Input**: POST with empty file field
- **Expected**: 400 status, error message "No file provided"
- **Priority**: P0 - Critical

#### TC-2.1.3: Invalid File Type
- **Input**: POST with .txt or .pdf file
- **Expected**: 400 status, error message "Invalid file type"
- **Priority**: P1 - High

#### TC-2.1.4: File Too Large
- **Input**: POST with 20MB CSV file (exceeds 16MB limit)
- **Expected**: 413 status, error message about file size
- **Priority**: P1 - High

#### TC-2.1.5: Corrupted CSV
- **Input**: POST with corrupted/unreadable CSV
- **Expected**: 500 status, error message, doesn't crash server
- **Priority**: P1 - High

#### TC-2.1.6: Concurrent Uploads
- **Input**: 5 simultaneous CSV uploads
- **Expected**: All process successfully, no race conditions
- **Priority**: P2 - Medium

---

### 2.2 Add Score to Dashboard Tests
**Category**: `/api/cog-scores/team`

#### TC-2.2.1: Successful Score Addition
- **Input**: POST with valid game_date, team, opponent, score
- **Expected**: 200 status, score added to database, appears on chart
- **Priority**: P0 - Critical

#### TC-2.2.2: Missing Required Fields
- **Input**: POST without team or opponent
- **Expected**: 400 status, error message about required fields
- **Priority**: P1 - High

#### TC-2.2.3: Invalid Date Format
- **Input**: POST with non-epoch timestamp
- **Expected**: 400 status or handles conversion gracefully
- **Priority**: P1 - High

#### TC-2.2.4: Duplicate Score Entry
- **Input**: POST same game twice
- **Expected**: Either updates existing or creates duplicate (document behavior)
- **Priority**: P2 - Medium

#### TC-2.2.5: Score Out of Range
- **Input**: POST with score = 150% or -20%
- **Expected**: Accepts value (or validates 0-100 range)
- **Priority**: P2 - Medium

---

### 2.3 Get Scores Endpoint Tests
**Category**: `/api/cog-scores`

#### TC-2.3.1: Get Team Scores
- **Input**: GET with ?level=team&team=Heat
- **Expected**: Returns array of Heat team scores
- **Priority**: P0 - Critical

#### TC-2.3.2: Get Player Scores
- **Input**: GET with ?level=player&player_name=John
- **Expected**: Returns array of John's scores
- **Priority**: P1 - High

#### TC-2.3.3: Empty Results
- **Input**: GET for team with no data
- **Expected**: Returns empty array, not error
- **Priority**: P1 - High

#### TC-2.3.4: Invalid Query Parameters
- **Input**: GET with ?level=invalid
- **Expected**: Returns error or defaults to team level
- **Priority**: P2 - Medium

---

## 3. SCORE REVEAL ANIMATION TESTS

### 3.1 Modal Display Tests
**Category**: UI/UX - Score Reveal

#### TC-3.1.1: Modal Opens
- **Input**: Upload CSV successfully
- **Expected**: Score reveal modal appears automatically
- **Priority**: P0 - Critical

#### TC-3.1.2: Game Title Display
- **Input**: CSV with game "10.04.25 Heat v Bucks Team"
- **Expected**: Modal shows "10.04.25 HEAT V BUCKS TEAM" in uppercase
- **Priority**: P1 - High

#### TC-3.1.3: Game Date Display
- **Input**: CSV with date "10.06.25"
- **Expected**: Modal shows "10.06.25" below title
- **Priority**: P1 - High

#### TC-3.1.4: Score Counter Animation
- **Input**: Final score = 65%
- **Expected**: Counter animates from 0 to 65 over 2 seconds
- **Priority**: P1 - High

#### TC-3.1.5: Progress Bar Animation
- **Input**: Final score = 65%
- **Expected**: Bar fills from 0% to 65% width smoothly
- **Priority**: P1 - High

#### TC-3.1.6: Stats Counter Animation
- **Input**: 1245 positives, 600 negatives, 1845 total
- **Expected**: All three stats count up simultaneously
- **Priority**: P1 - High

---

### 3.2 Rank Display Tests
**Category**: Performance Ranking

#### TC-3.2.1: Legendary Rank
- **Input**: Score = 92%
- **Expected**: Displays "🔥 LEGENDARY 🔥"
- **Priority**: P1 - High

#### TC-3.2.2: Elite Performance Rank
- **Input**: Score = 85%
- **Expected**: Displays "⭐ ELITE PERFORMANCE ⭐"
- **Priority**: P1 - High

#### TC-3.2.3: Great Execution Rank
- **Input**: Score = 72%
- **Expected**: Displays "GREAT EXECUTION"
- **Priority**: P1 - High

#### TC-3.2.4: Average Rank
- **Input**: Score = 55%
- **Expected**: Displays "AVERAGE"
- **Priority**: P1 - High

#### TC-3.2.5: Needs Improvement Rank
- **Input**: Score = 40%
- **Expected**: Displays "NEEDS IMPROVEMENT"
- **Priority**: P1 - High

#### TC-3.2.6: Boundary Testing - 90%
- **Input**: Score = 90%
- **Expected**: Displays "🔥 LEGENDARY 🔥" (inclusive)
- **Priority**: P2 - Medium

#### TC-3.2.7: Boundary Testing - 80%
- **Input**: Score = 80%
- **Expected**: Displays "⭐ ELITE PERFORMANCE ⭐" (inclusive)
- **Priority**: P2 - Medium

---

### 3.3 Add to Dashboard Button Tests
**Category**: Data Integration

#### TC-3.3.1: Button Click Success
- **Input**: Click "ADD TO DASHBOARD" after score reveal
- **Expected**: Score added to chart, modal closes, success alert shown
- **Priority**: P0 - Critical

#### TC-3.3.2: Date Extraction for API
- **Input**: Game name "10.06.25 Heat v Bucks"
- **Expected**: Converts to epoch timestamp correctly
- **Priority**: P0 - Critical

#### TC-3.3.3: Team/Opponent Extraction
- **Input**: Game name "Heat v Bucks Team"
- **Expected**: Extracts team="Heat", opponent="Bucks"
- **Priority**: P1 - High

#### TC-3.3.4: Chart Refresh
- **Input**: Add score to dashboard
- **Expected**: Chart reloads with new data point visible
- **Priority**: P0 - Critical

#### TC-3.3.5: API Failure Handling
- **Input**: Network error during add
- **Expected**: Shows error alert, doesn't close modal
- **Priority**: P1 - High

#### TC-3.3.6: Duplicate Prevention
- **Input**: Click "ADD TO DASHBOARD" twice quickly
- **Expected**: Only adds once or handles gracefully
- **Priority**: P2 - Medium

---

## 4. CHART VISUALIZATION TESTS

### 4.1 Chart Display Tests
**Category**: ECharts Integration

#### TC-4.1.1: Chart Renders
- **Input**: Page load with existing data
- **Expected**: Line chart displays with all data points
- **Priority**: P0 - Critical

#### TC-4.1.2: Empty Chart
- **Input**: No data in database
- **Expected**: Shows empty chart or placeholder message
- **Priority**: P1 - High

#### TC-4.1.3: Single Data Point
- **Input**: Only one score in database
- **Expected**: Chart displays single point correctly
- **Priority**: P2 - Medium

#### TC-4.1.4: Multiple Data Points
- **Input**: 10+ scores in database
- **Expected**: Chart shows trend line through all points
- **Priority**: P0 - Critical

---

### 4.2 Tooltip Tests
**Category**: Hover Interactions

#### TC-4.2.1: Tooltip Appears on Hover
- **Input**: Hover over data point
- **Expected**: Tooltip appears with dark background and red border
- **Priority**: P0 - Critical

#### TC-4.2.2: Tooltip Content
- **Input**: Hover over point with score 65%
- **Expected**: Shows game name, "65%", and "Cognitive Score" label
- **Priority**: P0 - Critical

#### TC-4.2.3: Tooltip Styling
- **Input**: Hover over point
- **Expected**: Large score (24px), red glow effect, proper formatting
- **Priority**: P1 - High

#### TC-4.2.4: Tooltip Theme Adaptation
- **Input**: Switch to Miami Heat theme, hover point
- **Expected**: Tooltip border changes to Heat red
- **Priority**: P2 - Medium

#### TC-4.2.5: Multiple Points Hover
- **Input**: Hover over different points quickly
- **Expected**: Tooltip updates smoothly without lag
- **Priority**: P2 - Medium

---

### 4.3 Point Interaction Tests
**Category**: Visual Feedback

#### TC-4.3.1: Point Hover Effect
- **Input**: Hover over data point
- **Expected**: Point enlarges from 10px to 16px
- **Priority**: P1 - High

#### TC-4.3.2: Point Glow Effect
- **Input**: Hover over data point
- **Expected**: Glow shadow intensifies (shadowBlur 10 → 20)
- **Priority**: P1 - High

#### TC-4.3.3: Point Unhover
- **Input**: Move mouse away from point
- **Expected**: Point returns to normal size and glow
- **Priority**: P2 - Medium

---

### 4.4 Axis Tests
**Category**: Chart Configuration

#### TC-4.4.1: Y-Axis Range
- **Input**: Chart with various scores
- **Expected**: Y-axis shows 0-100% range
- **Priority**: P1 - High

#### TC-4.4.2: Y-Axis Labels
- **Input**: Chart display
- **Expected**: Y-axis labels show percentage symbols (e.g., "50%")
- **Priority**: P1 - High

#### TC-4.4.3: X-Axis Labels
- **Input**: Multiple games on chart
- **Expected**: X-axis shows game names/dates clearly
- **Priority**: P1 - High

#### TC-4.4.4: Axis Color Theme
- **Input**: Default theme
- **Expected**: Axes use purple accent color
- **Priority**: P2 - Medium

#### TC-4.4.5: Axis Color - Heat Theme
- **Input**: Miami Heat theme active
- **Expected**: Axes use red accent color
- **Priority**: P2 - Medium

---

## 5. THEME INTEGRATION TESTS

### 5.1 Default Theme Tests
**Category**: Purple Neon Theme

#### TC-5.1.1: Chart Colors
- **Input**: Default theme active
- **Expected**: Line color = #a855f7 (purple)
- **Priority**: P1 - High

#### TC-5.1.2: Tooltip Border
- **Input**: Default theme, hover point
- **Expected**: Tooltip border = purple
- **Priority**: P2 - Medium

#### TC-5.1.3: Score Reveal Modal
- **Input**: Upload CSV in default theme
- **Expected**: Modal uses purple accents (not red)
- **Priority**: P2 - Medium

---

### 5.2 Miami Heat Theme Tests
**Category**: Red Neon Theme

#### TC-5.2.1: Chart Colors
- **Input**: Heat theme active
- **Expected**: Line color = #F9423A (red)
- **Priority**: P1 - High

#### TC-5.2.2: Tooltip Border
- **Input**: Heat theme, hover point
- **Expected**: Tooltip border = red
- **Priority**: P2 - Medium

#### TC-5.2.3: Score Reveal Modal
- **Input**: Upload CSV in Heat theme
- **Expected**: Modal uses red accents throughout
- **Priority**: P1 - High

#### TC-5.2.4: Theme Switch During Session
- **Input**: Switch theme while viewing analytics
- **Expected**: Chart colors update immediately
- **Priority**: P2 - Medium

---

## 6. ERROR HANDLING TESTS

### 6.1 Network Error Tests
**Category**: Resilience

#### TC-6.1.1: Upload Timeout
- **Input**: Upload CSV with simulated network timeout
- **Expected**: Shows error message, doesn't hang UI
- **Priority**: P1 - High

#### TC-6.1.2: Server 500 Error
- **Input**: Trigger server error during calculation
- **Expected**: Returns 500 with error message, doesn't crash
- **Priority**: P1 - High

#### TC-6.1.3: Offline Mode
- **Input**: Disconnect network, try upload
- **Expected**: Shows "Failed to process" error
- **Priority**: P2 - Medium

---

### 6.2 Data Validation Tests
**Category**: Input Sanitization

#### TC-6.2.1: SQL Injection Attempt
- **Input**: CSV with SQL injection strings
- **Expected**: Safely handles, doesn't execute SQL
- **Priority**: P0 - Critical

#### TC-6.2.2: XSS Attempt
- **Input**: CSV with `<script>` tags in data
- **Expected**: Escapes HTML, doesn't execute scripts
- **Priority**: P0 - Critical

#### TC-6.2.3: Extremely Long Strings
- **Input**: CSV with 10,000 character strings
- **Expected**: Handles gracefully, doesn't crash
- **Priority**: P2 - Medium

---

## 7. PERFORMANCE TESTS

### 7.1 Load Time Tests
**Category**: Speed & Efficiency

#### TC-7.1.1: Small CSV Processing
- **Input**: 100-row CSV
- **Expected**: Processes in < 1 second
- **Priority**: P1 - High

#### TC-7.1.2: Medium CSV Processing
- **Input**: 1000-row CSV (like Heat v Bucks)
- **Expected**: Processes in < 3 seconds
- **Priority**: P1 - High

#### TC-7.1.3: Large CSV Processing
- **Input**: 5000-row CSV
- **Expected**: Processes in < 10 seconds
- **Priority**: P2 - Medium

#### TC-7.1.4: Animation Performance
- **Input**: Score reveal modal opens
- **Expected**: Animations run at 60fps, no jank
- **Priority**: P2 - Medium

#### TC-7.1.5: Chart Render Time
- **Input**: Load chart with 50 data points
- **Expected**: Renders in < 2 seconds
- **Priority**: P2 - Medium

---

### 7.2 Memory Tests
**Category**: Resource Management

#### TC-7.2.1: Multiple Uploads
- **Input**: Upload 10 CSVs sequentially
- **Expected**: Memory doesn't leak, stays stable
- **Priority**: P2 - Medium

#### TC-7.2.2: Temp File Cleanup
- **Input**: Upload CSV
- **Expected**: Temp file deleted after processing
- **Priority**: P1 - High

---

## 8. INTEGRATION TESTS

### 8.1 End-to-End Workflow Tests
**Category**: Complete User Journey

#### TC-8.1.1: Full Upload to Dashboard Flow
- **Steps**:
  1. Navigate to analytics dashboard
  2. Upload Heat v Bucks CSV
  3. View score reveal animation
  4. Click "ADD TO DASHBOARD"
  5. Verify score appears on chart
- **Expected**: Complete flow works without errors
- **Priority**: P0 - Critical

#### TC-8.1.2: Multiple Games Upload
- **Steps**:
  1. Upload Game 1 CSV
  2. Add to dashboard
  3. Upload Game 2 CSV
  4. Add to dashboard
  5. Verify both appear on chart
- **Expected**: Both games visible, chronologically ordered
- **Priority**: P0 - Critical

#### TC-8.1.3: Manual Entry vs CSV Upload
- **Steps**:
  1. Manually add score via form
  2. Upload CSV and add
  3. Verify both on chart
- **Expected**: Both methods work, data consistent
- **Priority**: P1 - High

---

### 8.2 Database Integration Tests
**Category**: Data Persistence

#### TC-8.2.1: Score Persists After Refresh
- **Input**: Add score, refresh page
- **Expected**: Score still visible on chart
- **Priority**: P0 - Critical

#### TC-8.2.2: Score Persists After Server Restart
- **Input**: Add score, restart Flask app
- **Expected**: Score still in database and visible
- **Priority**: P1 - High

---

## 9. BROWSER COMPATIBILITY TESTS

### 9.1 Modern Browser Tests
**Category**: Cross-Browser Support

#### TC-9.1.1: Chrome/Edge (Chromium)
- **Input**: Run all tests in Chrome
- **Expected**: All features work perfectly
- **Priority**: P0 - Critical

#### TC-9.1.2: Firefox
- **Input**: Run all tests in Firefox
- **Expected**: All features work, animations smooth
- **Priority**: P1 - High

#### TC-9.1.3: Safari
- **Input**: Run all tests in Safari
- **Expected**: Backdrop blur works, animations smooth
- **Priority**: P1 - High

---

### 9.2 Mobile Browser Tests
**Category**: Responsive Design

#### TC-9.2.1: Mobile Chrome
- **Input**: Access on mobile Chrome
- **Expected**: Layout responsive, touch interactions work
- **Priority**: P2 - Medium

#### TC-9.2.2: Mobile Safari
- **Input**: Access on iPhone Safari
- **Expected**: Backdrop blur works, animations smooth
- **Priority**: P2 - Medium

---

## 10. ACCESSIBILITY TESTS

### 10.1 Keyboard Navigation Tests
**Category**: A11y Compliance

#### TC-10.1.1: Tab Navigation
- **Input**: Use Tab key to navigate
- **Expected**: Can reach all interactive elements
- **Priority**: P2 - Medium

#### TC-10.1.2: Modal Keyboard Control
- **Input**: Press Escape in score reveal modal
- **Expected**: Modal closes (if not backdrop static)
- **Priority**: P2 - Medium

---

### 10.2 Screen Reader Tests
**Category**: A11y Compliance

#### TC-10.2.1: Chart Accessibility
- **Input**: Use screen reader on chart
- **Expected**: Announces data points meaningfully
- **Priority**: P3 - Low

#### TC-10.2.2: Modal Accessibility
- **Input**: Use screen reader on score reveal
- **Expected**: Announces score and stats
- **Priority**: P3 - Low

---

## TEST EXECUTION CHECKLIST

### Pre-Release Testing
- [ ] All P0 tests pass (Critical)
- [ ] 95%+ of P1 tests pass (High)
- [ ] 80%+ of P2 tests pass (Medium)
- [ ] Known P3 issues documented (Low)

### Regression Testing (After Changes)
- [ ] Re-run all P0 tests
- [ ] Re-run affected P1/P2 tests
- [ ] Verify no new issues introduced

### Performance Baseline
- [ ] Small CSV: < 1s
- [ ] Medium CSV (1000 rows): < 3s
- [ ] Large CSV (5000 rows): < 10s
- [ ] Chart render: < 2s
- [ ] Animation: 60fps

---

## TEST DATA SETS

### Provided Test Files
1. **10.06.25 Heat v Bucks (1).csv** - Standard test file (992 rows)
2. **Empty CSV** - 0 data rows (create)
3. **Small CSV** - 10 rows (create)
4. **Large CSV** - 5000 rows (create)
5. **Malformed CSV** - Missing columns (create)
6. **Special Chars CSV** - Edge case data (create)

---

## DEFECT TRACKING

### Critical Issues (P0)
- [ ] None currently identified

### High Priority Issues (P1)
- [ ] None currently identified

### Medium Priority Issues (P2)
- [ ] None currently identified

### Known Limitations
- CSV upload limited to 16MB
- Supports only CSV file format (not Excel directly)
- Date extraction assumes MM.DD.YY format

---

## NOTES

**Test Environment**:
- OS: macOS 24.1.0
- Python: 3.13
- Flask: Latest
- Browser: Chrome/Safari latest

**Last Test Run**: [Date]  
**Test Coverage**: [%]  
**Pass Rate**: [%]

---

**Document Version**: 1.0  
**Created**: October 14, 2025  
**Owner**: IntegrityHoops QA Team

