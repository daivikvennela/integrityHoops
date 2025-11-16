# Column/Line Toggle Test Cases

## Overview
Test suite for column toggle functionality in tables (smartdash_results) and line toggle functionality in charts (analytics_dashboard).

**Last Updated:** 2025-01-XX  
**Test Coverage:** Table columns, Chart lines, Toggle All, State synchronization

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
```bash
# Run Python test suite (requires selenium)
python testApp1/tests/test_column_toggle.py
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

// Integration tests
testToggleIntegration();
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

## Known Issues

- None currently

## Future Enhancements

- [ ] Persist toggle state in localStorage
- [ ] Add keyboard shortcuts (Ctrl+T to toggle menu)
- [ ] Add animation for show/hide transitions
- [ ] Add tooltips for column/line names

