# Chart Tooltip Test Instructions

## Problem
Tooltips showing category names when hovering over chart lines are not appearing.

## Test Case Created
Created `test_chart_tooltips.js` with 8 diagnostic tests to identify the issue.

## How to Run the Test

### Option 1: Automatic (Recommended)
1. Navigate to: `http://localhost:5000/analytics-dashboard`
2. Wait 3 seconds for the page to load
3. Open browser console (F12 → Console tab)
4. Look for test results automatically printed

### Option 2: Manual
1. Navigate to: `http://localhost:5000/analytics-dashboard`
2. Open browser console (F12 → Console tab)
3. Run:
```javascript
const tests = new ChartTooltipTests();
const results = tests.runAll();
```

## Test Cases

1. **Canvas accessible and Chart.js loaded** - Verifies basic setup
2. **Tooltip configuration exists** - Checks if tooltip config is present
3. **Tooltip callbacks are functions** - Verifies callbacks are defined
4. **Interaction mode configured for hover** - Checks hover settings
5. **Chart has data for tooltips** - Verifies chart has data to display
6. **Title callback returns category name** - Tests title generation
7. **Label callback includes category info** - Tests label generation
8. **Simulate hover activates tooltip** - Tests actual hover behavior

## Expected Results

All 8 tests should pass (100%).

If tests fail, the console will show:
- Which specific test failed
- Details about why it failed
- Diagnostic suggestions

## Manual Verification

After running tests, manually verify tooltips:

1. Slowly move your mouse **near** (not on) a chart line
2. Tooltip should appear showing:
   - **Title**: Category name (e.g., "DM Catch") OR Date (depending on chart view)
   - **Body**: Score percentage and additional info
3. Tooltip should have:
   - Black background with red border
   - Red title text
   - White body text
   - Color indicator matching the line

## Common Issues

### Issue 1: Tooltip config not applied
**Symptom**: Tests 2-3 fail  
**Solution**: Check if `analytics_dashboard.js` loaded correctly

### Issue 2: Chart has no data
**Symptom**: Test 4 fails  
**Solution**: Ensure CSV files are processed and data is in database

### Issue 3: Interaction mode wrong
**Symptom**: Test 3 fails, tooltips don't appear when hovering near lines  
**Solution**: Verify `interaction.mode` is set to 'nearest' and `intersect: false`

### Issue 4: Chart.js version incompatibility
**Symptom**: Test 1 shows old Chart.js version  
**Solution**: Update Chart.js to version 3.x or higher

## Debugging Commands

In browser console:

```javascript
// Check if chart exists
const chart = getChartInstance();
console.log('Chart:', chart);

// Check tooltip config
console.log('Tooltip config:', chart?.options?.plugins?.tooltip);

// Check interaction mode
console.log('Interaction:', chart?.options?.interaction);

// Check if datasets have labels
chart?.data?.datasets?.forEach((ds, i) => {
    console.log(`Dataset ${i}: ${ds.label}`);
});

// Force hover simulation (replace indexes as needed)
const canvas = chart.canvas;
const meta = chart.getDatasetMeta(0);
const point = meta.data[0];
const event = new MouseEvent('mousemove', {
    clientX: canvas.getBoundingClientRect().left + point.x,
    clientY: canvas.getBoundingClientRect().top + point.y,
    bubbles: true
});
canvas.dispatchEvent(event);
```

## Files Modified

- `testApp1/tests/test_chart_tooltips.js` - New test suite
- `testApp1/static/tests/test_chart_tooltips.js` - Copy for web serving
- `testApp1/templates/analytics_dashboard.html` - Added test script loading
- `testApp1/static/js/analytics_dashboard.js` - Enhanced tooltip configuration

## Next Steps

1. Run the test suite
2. Review which tests pass/fail
3. Check console for error messages
4. Manually test hovering over chart lines
5. Report back with test results

If all tests pass but tooltips still don't appear visually, the issue may be:
- CSS z-index conflicts
- Canvas rendering issues
- Browser-specific behavior
- Need to clear browser cache

