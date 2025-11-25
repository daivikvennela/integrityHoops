# Column/Line Toggle Test Cases

## Overview
Comprehensive test suite for column toggle functionality in tables (smartdash_results) and line toggle functionality in charts (analytics_dashboard).

**Last Updated:** 2025-01-25  
**Test Coverage:** Table columns, Chart lines, Toggle All, State synchronization, Edge cases, Integration tests  
**Test Count:** 16 automated tests (11 unit + 5 integration)  
**Systems Check:** Integrated  
**Status:** ✅ All tests passing

---

## Test Environment Setup

### Prerequisites
- Flask app running on `http://localhost:8081`
- Browser with developer console access
- Test data available (CSV files for smartdash, team statistics for analytics)

### Test Pages
- **Table Toggle:** `/smartdash-results/<filename>` or `/smartdash`
- **Chart Toggle:** `/analytics-dashboard`

---

## Test Cases

### TABLE COLUMN TOGGLE TESTS

#### TC-TABLE-01: Toggle Button Exists
**Priority:** P0 - Critical  
**Description:** Verify toggle button is present on smartdash results page

**Steps:**
1. Navigate to `/smartdash-results/<filename>`
2. Locate "Toggle Columns" button

**Expected Result:**
- Button exists in DOM
- Button is visible and clickable
- Button has correct text: "Toggle Columns"

**Pass Criteria:**
```javascript
const btn = document.querySelector('button[onclick*="columnMenu"]');
assert(btn !== null);
```

---

#### TC-TABLE-02: Menu Opens on Button Click
**Priority:** P0 - Critical  
**Description:** Verify menu appears when toggle button is clicked

**Steps:**
1. Click "Toggle Columns" button
2. Observe menu appearance

**Expected Result:**
- Menu element becomes visible
- Menu has class "show"
- Menu contains checkboxes

**Pass Criteria:**
```javascript
btn.click();
const menu = document.getElementById('columnMenu');
assert(menu.classList.contains('show'));
```

---

#### TC-TABLE-03: Checkboxes Exist for All Columns
**Priority:** P0 - Critical  
**Description:** Verify checkboxes exist for each table column

**Steps:**
1. Open toggle menu
2. Count checkboxes

**Expected Result:**
- Checkboxes exist for all columns (including row number)
- Checkbox count matches column count
- Each checkbox has correct label

**Pass Criteria:**
```javascript
const checkboxes = document.querySelectorAll('.col-toggle');
const headers = document.querySelectorAll('th[data-column-index]');
assert(checkboxes.length === headers.length);
```

---

#### TC-TABLE-04: Individual Column Toggle Works
**Priority:** P0 - Critical  
**Description:** Verify clicking checkbox hides/shows corresponding column

**Steps:**
1. Open toggle menu
2. Uncheck a column checkbox
3. Verify column is hidden
4. Check the checkbox
5. Verify column is visible

**Expected Result:**
- Column header and cells get `hidden-column` class when unchecked
- Column header and cells lose `hidden-column` class when checked
- Visual update is immediate

**Pass Criteria:**
```javascript
const colIndex = 1;
const header = document.querySelector(`th[data-column-index="${colIndex}"]`);
toggleColumn(colIndex, false);
assert(header.classList.contains('hidden-column'));
toggleColumn(colIndex, true);
assert(!header.classList.contains('hidden-column'));
```

---

#### TC-TABLE-05: Toggle All Functionality
**Priority:** P0 - Critical  
**Description:** Verify "Toggle All" checkbox controls all columns

**Steps:**
1. Open toggle menu
2. Uncheck "Toggle All"
3. Verify all columns hidden
4. Check "Toggle All"
5. Verify all columns visible

**Expected Result:**
- All individual checkboxes update
- All columns hide/show together
- Toggle All checkbox reflects state (checked/unchecked/indeterminate)

**Pass Criteria:**
```javascript
const toggleAll = document.getElementById('toggleAll');
const checkboxes = document.querySelectorAll('.col-toggle');

toggleAllColumns(false);
assert(Array.from(checkboxes).every(cb => !cb.checked));

toggleAllColumns(true);
assert(Array.from(checkboxes).every(cb => cb.checked));
```

---

#### TC-TABLE-06: Checkbox State Syncs with Column Visibility
**Priority:** P1 - High  
**Description:** Verify checkbox state matches column visibility state

**Steps:**
1. Manually hide a column via `toggleColumn()`
2. Check checkbox state
3. Manually show column
4. Check checkbox state again

**Expected Result:**
- Checkbox checked state matches column visibility
- No desync between checkbox and column state

**Pass Criteria:**
```javascript
const colIndex = 1;
const checkbox = document.getElementById(`col-toggle-${colIndex}`);
const header = document.querySelector(`th[data-column-index="${colIndex}"]`);

toggleColumn(colIndex, false);
assert(!checkbox.checked && header.classList.contains('hidden-column'));

toggleColumn(colIndex, true);
assert(checkbox.checked && !header.classList.contains('hidden-column'));
```

---

#### TC-TABLE-07: Menu Closes on Outside Click
**Priority:** P2 - Medium  
**Description:** Verify menu closes when clicking outside

**Steps:**
1. Open toggle menu
2. Click outside menu area
3. Verify menu closes

**Expected Result:**
- Menu loses "show" class
- Menu becomes hidden

**Pass Criteria:**
```javascript
menu.classList.add('show');
// Simulate outside click
document.body.click();
assert(!menu.classList.contains('show'));
```

---

### CHART LINE TOGGLE TESTS

#### TC-CHART-01: Toggle Button Exists
**Priority:** P0 - Critical  
**Description:** Verify toggle button exists on analytics dashboard

**Steps:**
1. Navigate to `/analytics-dashboard`
2. Locate "Toggle Lines" button

**Expected Result:**
- Button exists in DOM
- Button is visible
- Button has correct text: "Toggle Lines"

**Pass Criteria:**
```javascript
const btn = document.querySelector('button[onclick*="chartLineMenu"]');
assert(btn !== null);
```

---

#### TC-CHART-02: Chart Menu Populates with Datasets
**Priority:** P0 - Critical  
**Description:** Verify menu populates with checkboxes for each chart dataset

**Steps:**
1. Wait for chart to load
2. Open toggle menu
3. Verify checkboxes exist

**Expected Result:**
- Menu contains checkboxes
- Checkbox count matches dataset count
- Each checkbox has color indicator and label

**Pass Criteria:**
```javascript
const chart = getChartInstance();
const checkboxes = document.querySelectorAll('.chart-line-toggle');
assert(checkboxes.length === chart.data.datasets.length);
```

---

#### TC-CHART-03: Individual Line Toggle Works
**Priority:** P0 - Critical  
**Description:** Verify clicking checkbox hides/shows chart line

**Steps:**
1. Open toggle menu
2. Uncheck a line checkbox
3. Verify line disappears from chart
4. Check the checkbox
5. Verify line reappears

**Expected Result:**
- Chart dataset meta `hidden` property updates
- Chart re-renders
- Line visibility matches checkbox state

**Pass Criteria:**
```javascript
const chart = getChartInstance();
const datasetIndex = 0;
const meta = chart.getDatasetMeta(datasetIndex);

toggleChartLine(datasetIndex, false);
assert(chart.getDatasetMeta(datasetIndex).hidden === true);

toggleChartLine(datasetIndex, true);
assert(chart.getDatasetMeta(datasetIndex).hidden !== true);
```

---

#### TC-CHART-04: Toggle All Chart Lines
**Priority:** P0 - Critical  
**Description:** Verify "Toggle All" controls all chart lines

**Steps:**
1. Open toggle menu
2. Uncheck "Toggle All"
3. Verify all lines hidden
4. Check "Toggle All"
5. Verify all lines visible

**Expected Result:**
- All dataset metas update
- All checkboxes update
- Chart re-renders

**Pass Criteria:**
```javascript
const chart = getChartInstance();
toggleAllChartLines(false);
const allHidden = chart.data.datasets.every((ds, i) => 
    chart.getDatasetMeta(i).hidden === true
);
assert(allHidden);

toggleAllChartLines(true);
const allVisible = chart.data.datasets.every((ds, i) => 
    chart.getDatasetMeta(i).hidden !== true
);
assert(allVisible);
```

---

#### TC-CHART-05: Checkbox State Syncs with Chart State
**Priority:** P1 - High  
**Description:** Verify checkbox state matches chart line visibility

**Steps:**
1. Toggle a line via `toggleChartLine()`
2. Check corresponding checkbox state
3. Verify they match

**Expected Result:**
- Checkbox checked state matches line visibility
- No desync

**Pass Criteria:**
```javascript
const chart = getChartInstance();
const datasetIndex = 0;
const checkbox = document.getElementById(`chartLine-${datasetIndex}`);

toggleChartLine(datasetIndex, false);
assert(!checkbox.checked && chart.getDatasetMeta(datasetIndex).hidden === true);

toggleChartLine(datasetIndex, true);
assert(checkbox.checked && chart.getDatasetMeta(datasetIndex).hidden !== true);
```

---

#### TC-CHART-06: Menu Updates When Chart Data Changes
**Priority:** P2 - Medium  
**Description:** Verify menu refreshes when chart category changes

**Steps:**
1. Open toggle menu
2. Change category dropdown
3. Verify menu updates with new datasets

**Expected Result:**
- Menu repopulates with new datasets
- Old checkboxes removed
- New checkboxes added

**Pass Criteria:**
```javascript
const initialCount = document.querySelectorAll('.chart-line-toggle').length;
// Change category
categorySelect.value = 'DM Catch';
categorySelect.dispatchEvent(new Event('change'));
// Wait for chart update
setTimeout(() => {
    const newCount = document.querySelectorAll('.chart-line-toggle').length;
    assert(newCount > 0); // Menu should repopulate
}, 2000);
```

---

## Edge Cases

#### TC-EDGE-01: Individual Toggles Work After Toggle All
**Priority:** P0 - Critical  
**Description:** Verify individual checkboxes still work after using "Toggle All"

**Steps:**
1. Open toggle menu
2. Click "Toggle All" to hide all columns/lines
3. Click "Toggle All" again to show all columns/lines
4. Try toggling individual checkboxes
5. Verify individual toggles work correctly

**Expected Result:**
- Individual checkboxes respond to clicks after toggleAll
- Columns/lines toggle correctly
- No state corruption
- Checkbox states remain synchronized

**Pass Criteria:**
```javascript
// Test table toggle
const toggleAll = document.getElementById('toggleAll');
const firstCheckbox = document.getElementById('col-toggle-1');
const firstHeader = document.querySelector('th[data-column-index="1"]');

// Use toggle all
toggleAllColumns(false);
toggleAllColumns(true);

// Now test individual toggle
const initialState = firstCheckbox.checked;
firstCheckbox.click();
const afterClick = firstCheckbox.checked;
assert(afterClick !== initialState, "Individual toggle should work");
assert(firstHeader.classList.contains('hidden-column') !== afterClick, 
       "Column visibility should match checkbox state");

// Test chart toggle
const chartToggleAll = document.getElementById('toggleAllLines');
const chartFirstCheckbox = document.getElementById('chartLine-0');
const chart = getChartInstance();

if (chart && chartToggleAll && chartFirstCheckbox) {
    toggleAllChartLines(false);
    toggleAllChartLines(true);
    
    const chartInitialState = chartFirstCheckbox.checked;
    chartFirstCheckbox.click();
    const chartAfterClick = chartFirstCheckbox.checked;
    assert(chartAfterClick !== chartInitialState, "Chart toggle should work");
    assert(chart.getDatasetMeta(0).hidden !== chartAfterClick, 
           "Chart line visibility should match checkbox");
}
```

**Bug Fixed:** Individual toggles were breaking after toggleAll due to state synchronization issues. Fixed by:
- Adding `skipUpdateToggleAll` parameter to prevent recursive updates
- Ensuring checkbox state is updated in `toggleColumn` function
- Batching operations in `toggleAllColumns` to avoid race conditions

---

#### TC-EDGE-02: No Data Scenario
**Priority:** P1 - High  
**Description:** Verify toggle works when table/chart has no data

**Expected Result:**
- No errors thrown
- Menu still opens
- Toggle functions handle empty state gracefully

---

#### TC-EDGE-03: Single Column/Line
**Priority:** P2 - Medium  
**Description:** Verify toggle works with only one column/line

**Expected Result:**
- Toggle still works
- Toggle All still functions
- No errors

---

#### TC-EDGE-04: Rapid Toggle Clicks
**Priority:** P2 - Medium  
**Description:** Verify system handles rapid checkbox clicks

**Expected Result:**
- No race conditions
- State remains consistent
- No visual glitches

---

#### TC-EDGE-05: Toggle All Then Individual Toggle Sequence
**Priority:** P0 - Critical  
**Description:** Verify complex toggle sequences work correctly

**Steps:**
1. Click Toggle All to hide all
2. Click individual checkbox to show one line
3. Click another individual checkbox
4. Verify both work correctly

**Expected Result:**
- Individual toggles work after Toggle All
- State stays synchronized
- Chart updates correctly

**Pass Criteria:**
```javascript
const chart = getChartInstance();
toggleAllChartLines(false);
// All should be hidden
assert(chart.data.datasets.every((ds, i) => chart.getDatasetMeta(i).hidden === true));

// Show first line
toggleChartLine(0, true);
assert(chart.getDatasetMeta(0).hidden !== true);

// Show second line
toggleChartLine(1, true);
assert(chart.getDatasetMeta(1).hidden !== true);
```

---

#### TC-EDGE-06: Toggle After Chart Recreation
**Priority:** P1 - High  
**Description:** Verify toggle works after chart is recreated (e.g., category change)

**Steps:**
1. Load chart with data
2. Toggle some lines
3. Change category to recreate chart
4. Wait for chart to load
5. Try toggling lines again

**Expected Result:**
- populateChartLineMenu() is called after chart recreation
- Toggle functions still work
- No stale references to old chart
- Menu repopulates with new datasets

**Pass Criteria:**
```javascript
const chart = getChartInstance();
if (!chart) return false;

// Force menu repopulation (simulates chart recreation)
const populateResult = populateChartLineMenu(true);
assert(populateResult === true, 'populateChartLineMenu should succeed');

// Try toggling after repopulation
const toggleResult = toggleChartLine(0, false);
assert(toggleResult === true, 'Toggle should work after recreation');

const meta = chart.getDatasetMeta(0);
assert(meta.hidden === true, 'Chart should be hidden');
```

**Implementation Details:**
- `populateChartLineMenu()` accepts `forceUpdate` parameter
- Throttling prevents duplicate menu updates (100ms window)
- Event listeners are reattached when menu is repopulated
- Chart watcher monitors dataset count changes

---

#### TC-EDGE-07: Multiple Rapid Toggles
**Priority:** P2 - Medium  
**Description:** Verify system handles rapid consecutive toggles without errors

**Steps:**
1. Toggle same line on/off rapidly 5+ times
2. Verify each toggle succeeds
3. Verify chart state is consistent
4. Verify no errors in console

**Expected Result:**
- All toggle operations complete successfully
- Final state is deterministic
- Chart remains functional
- No memory leaks or stale references

**Pass Criteria:**
```javascript
const chart = getChartInstance();
let allSucceeded = true;
const iterations = 5;

for (let i = 0; i < iterations; i++) {
    const visible = i % 2 === 0;
    const result = toggleChartLine(0, visible);
    if (!result) {
        allSucceeded = false;
        break;
    }
}

assert(allSucceeded === true, 'All rapid toggles should succeed');

// Verify chart is still functional
const meta = chart.getDatasetMeta(0);
assert(meta !== null && meta !== undefined, 'Chart meta should be accessible');
```

**Implementation Details:**
- Toggle functions include try-catch for error handling
- Chart.update() is wrapped in error handling
- Each toggle returns true/false for success/failure
- State validation before and after operations

---

#### TC-EDGE-08: Toggle All Then Multiple Individual Toggles
**Priority:** P0 - Critical  
**Description:** Verify the most common bug: individual toggles failing after Toggle All

**Steps:**
1. Click Toggle All to hide all lines
2. Verify all lines are hidden
3. Click first individual checkbox to show
4. Verify first line is visible
5. Click second individual checkbox to show
6. Verify second line is visible
7. Verify other lines remain hidden

**Expected Result:**
- All lines hide when Toggle All is unchecked
- First line shows when its checkbox is checked
- Second line shows when its checkbox is checked
- Other lines remain hidden
- Toggle All checkbox updates to indeterminate state

**Pass Criteria:**
```javascript
const chart = getChartInstance();

// Step 1: Toggle All to hide
toggleAllChartLines(false);
const allHidden = chart.data.datasets.every((ds, i) => 
    chart.getDatasetMeta(i).hidden === true
);
assert(allHidden === true, 'All lines should be hidden');

// Step 2: Show first line
toggleChartLine(0, true);
const firstVisible = chart.getDatasetMeta(0).hidden !== true;
assert(firstVisible === true, 'First line should be visible');

// Step 3: Verify others still hidden (except first)
const othersHidden = chart.data.datasets.every((ds, i) => {
    if (i === 0) return true; // Skip first
    return chart.getDatasetMeta(i).hidden === true;
});
assert(othersHidden === true, 'Other lines should remain hidden');

// Step 4: Show second line
toggleChartLine(1, true);
const secondVisible = chart.getDatasetMeta(1).hidden !== true;
assert(secondVisible === true, 'Second line should be visible');

// Step 5: Verify state consistency
const checkbox0 = document.getElementById('chartLine-0');
const checkbox1 = document.getElementById('chartLine-1');
assert(checkbox0.checked === true, 'First checkbox should be checked');
assert(checkbox1.checked === true, 'Second checkbox should be checked');

// Step 6: Verify Toggle All is indeterminate
const toggleAll = document.getElementById('toggleAllLines');
assert(toggleAll.indeterminate === true, 'Toggle All should be indeterminate');
```

**Bug History:**
- Original issue: Individual toggles stopped working after Toggle All
- Root cause: Recursive function calls and state synchronization
- Solution: Direct state updates in toggleAllChartLines(), proper event handling

---

**Steps:**
1. Toggle All OFF
2. Toggle individual column ON
3. Toggle All ON
4. Toggle individual column OFF
5. Verify states are correct throughout

**Expected Result:**
- Each operation works independently
- State remains consistent
- Toggle All reflects correct indeterminate state when mixed

**Pass Criteria:**
```javascript
// Complex sequence test
toggleAllColumns(false);
assert(Array.from(document.querySelectorAll('.col-toggle')).every(cb => !cb.checked));

toggleColumn(1, true);
const checkboxes = document.querySelectorAll('.col-toggle');
const toggleAll = document.getElementById('toggleAll');
assert(toggleAll.indeterminate === true, "Should be indeterminate when mixed");

toggleAllColumns(true);
assert(Array.from(checkboxes).every(cb => cb.checked));

toggleColumn(1, false);
assert(toggleAll.indeterminate === true, "Should be indeterminate again");
```

---

## Performance Tests

#### TC-PERF-01: Large Dataset Performance
**Priority:** P2 - Medium  
**Description:** Verify toggle performance with many columns (50+)

**Expected Result:**
- Toggle response time < 100ms
- No UI freezing
- Smooth animations

---

## Browser Compatibility

#### TC-BROWSER-01: Chrome/Edge
**Priority:** P0 - Critical  
**Status:** ✅ Tested

#### TC-BROWSER-02: Firefox
**Priority:** P1 - High  
**Status:** ⏳ Pending

#### TC-BROWSER-03: Safari
**Priority:** P1 - High  
**Status:** ⏳ Pending

---

## Test Execution

### Automated Tests

#### Python/Selenium Tests
```bash
# Run Python test suite (requires selenium)
python testApp1/tests/test_column_toggle.py
```

#### JavaScript Unit Tests
Load in browser console on `/analytics-dashboard`:
```html
<!-- Option 1: Load test scripts -->
<script src="/static/tests/test_chart_toggle.js"></script>
<script src="/static/tests/test_chart_toggle_integration.js"></script>
```

Or directly in console:
```javascript
// Load and run unit tests
const testScript = document.createElement('script');
testScript.src = '/static/tests/test_chart_toggle.js';
document.head.appendChild(testScript);

// After loading, run tests
setTimeout(() => {
    const tests = new ChartToggleTests();
    window.chartToggleTestResults = tests.runAll();
}, 1000);
```

#### Integration Tests
```javascript
// Load and run integration tests (in browser console)
const integrationScript = document.createElement('script');
integrationScript.src = '/static/tests/test_chart_toggle_integration.js';
document.head.appendChild(integrationScript);

setTimeout(async () => {
    const tests = new ChartToggleIntegrationTests();
    window.chartToggleIntegrationTestResults = await tests.runAll();
}, 2000);
```

### Manual Tests
1. Open `testApp1/tests/test_column_toggle_manual.html` in browser
2. Follow instructions to run tests in console
3. Or copy test functions directly into browser console

### Quick Test Commands
```javascript
// In browser console on smartdash results page
testTableToggle();

// In browser console on analytics dashboard
testChartToggle();

// Run all unit tests
if (window.ChartToggleTests) {
    const tests = new ChartToggleTests();
    const results = tests.runAll();
    console.log(`Results: ${results.passed}/${results.total} passed (${results.percentage}%)`);
}

// Run all integration tests
if (window.ChartToggleIntegrationTests) {
    const tests = new ChartToggleIntegrationTests();
    tests.runAll().then(results => {
        console.log(`Integration: ${results.passed}/${results.total} passed (${results.percentage}%)`);
    });
}
```

### Systems Check Integration

The chart toggle tests are integrated into the systems check dashboard:

1. **Automated Check**: The systems check automatically verifies:
   - Test files exist (`tests/test_chart_toggle.js`, `tests/test_chart_toggle_integration.js`)
   - Analytics dashboard page loads
   - Toggle HTML elements are present
   - Toggle functions are defined
   - Menu container exists

2. **View Results**:
   ```
   Navigate to: /analytics-dashboard
   Scroll to bottom: Systems Check widget
   Look for: "Chart Toggle Functionality" check
   ```

3. **API Access**:
   ```bash
   curl http://localhost:5000/systems-check/api/run
   ```

4. **Check Details**:
   - ✓ Pass: All 6 required elements present
   - ⚠ Warn: 4-5 elements present (partial functionality)
   - ✗ Fail: < 4 elements present

### Test File Locations

```
testApp1/
├── tests/
│   ├── test_chart_toggle.js              # Unit tests (11 test cases)
│   ├── test_chart_toggle_integration.js   # Integration tests (5 test cases)
│   ├── test_column_toggle.py              # Selenium tests
│   ├── test_column_toggle_manual.html     # Manual test runner
│   └── COLUMN_TOGGLE_TEST_CASES.md        # This document
├── systems_check/
│   ├── check_runner.py                    # Includes check_chart_toggle_functionality()
│   └── api.py                             # Systems check API
└── templates/
    └── analytics_dashboard.html           # Toggle implementation
```

---

## Test Results Template

```
Test Run Date: YYYY-MM-DD
Browser: Chrome/Firefox/Safari
Version: X.X.X

TABLE TESTS:
✅ TC-TABLE-01: Toggle Button Exists
✅ TC-TABLE-02: Menu Opens on Button Click
✅ TC-TABLE-03: Checkboxes Exist for All Columns
✅ TC-TABLE-04: Individual Column Toggle Works
✅ TC-TABLE-05: Toggle All Functionality
✅ TC-TABLE-06: Checkbox State Syncs
✅ TC-TABLE-07: Menu Closes on Outside Click

CHART TESTS:
✅ TC-CHART-01: Toggle Button Exists
✅ TC-CHART-02: Chart Menu Populates
✅ TC-CHART-03: Individual Line Toggle Works
✅ TC-CHART-04: Toggle All Chart Lines
✅ TC-CHART-05: Checkbox State Syncs
✅ TC-CHART-06: Menu Updates When Chart Changes

Results: 13/13 passed (100%)
```

---

## Recent Fixes and Improvements

### 2025-01 - Major Toggle Refactor
**Issue**: Individual toggles stopped working after using "Toggle All"

**Root Causes Identified**:
1. Missing return statement in `getChartInstance()` function
2. Recursive function calls causing state corruption
3. Race conditions in checkbox state updates
4. Timing issues with menu population after chart recreation

**Solutions Implemented**:
1. **Fixed `getChartInstance()`**:
   - Added proper return statement
   - Added fallback to global `statisticsChart` variable
   - Improved error handling

2. **Improved `toggleChartLine()`**:
   - Added comprehensive try-catch error handling
   - Added parameter validation (type, range checks)
   - Added detailed console warnings for debugging
   - Returns true/false for testability
   - Updates checkbox state synchronously

3. **Improved `toggleAllChartLines()`**:
   - Removed recursive calls to `toggleChartLine()`
   - Direct state updates for all datasets
   - Success/failure counting for diagnostics
   - Batch chart update (single update() call)
   - Comprehensive error handling

4. **Enhanced `populateChartLineMenu()`**:
   - Added `forceUpdate` parameter for chart recreation scenarios
   - Throttling to prevent duplicate updates (100ms window)
   - Uses `dataset.index` data attribute instead of parsing IDs
   - Improved event listener management
   - Empty dataset handling

5. **Improved State Synchronization**:
   - `updateToggleAllState()` properly reflects mixed states (indeterminate)
   - `syncCheckboxState()` syncs checkboxes with chart meta
   - Chart watcher monitors dataset count changes (500ms interval)
   - Event propagation control with `e.stopPropagation()`

### Test Coverage Improvements
- Added 3 new edge case tests (TC-09, TC-10, TC-11)
- Created integration test suite (5 tests)
- Integrated into systems check
- Total: 11 unit tests + 5 integration tests = 16 automated tests

### Performance Improvements
- Throttled menu updates to reduce overhead
- Single chart.update() call in batch operations
- Early returns for invalid state

---

## Known Issues

**None currently** - All critical bugs have been resolved.

### Previously Resolved Issues
- ✅ Individual toggles breaking after Toggle All (2025-01)
- ✅ Chart instance not accessible (missing return statement, 2025-01)
- ✅ Race conditions in state updates (2025-01)
- ✅ Menu not updating after chart recreation (2025-01)

---

## Future Enhancements

### High Priority
- [ ] Add keyboard shortcuts (Ctrl+T to toggle menu, Space to toggle)
- [ ] Persist toggle state in localStorage across page reloads
- [ ] Add "Show Only" mode (show one, hide all others)

### Medium Priority
- [ ] Add animation for show/hide transitions
- [ ] Add tooltips showing line/column details on hover
- [ ] Add search/filter in toggle menu for large datasets
- [ ] Add "Invert Selection" button

### Low Priority
- [ ] Add drag-and-drop reordering of lines/columns
- [ ] Add color picker for customizing line colors
- [ ] Export toggle state configuration
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)

