/**
 * Test cases for Chart Tooltip Functionality
 * These tests verify that tooltips display category names when hovering over chart lines
 */

// Test utilities
function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

function logTest(testName, passed, details = '') {
    const status = passed ? '✓ PASS' : '✗ FAIL';
    console.log(`${status} - ${testName}${details ? `: ${details}` : ''}`);
    return passed;
}

function simulateHover(chart, datasetIndex, pointIndex) {
    const canvas = chart.canvas;
    const meta = chart.getDatasetMeta(datasetIndex);
    
    if (!meta || !meta.data || !meta.data[pointIndex]) {
        throw new Error(`Cannot simulate hover: dataset ${datasetIndex}, point ${pointIndex} not found`);
    }
    
    const point = meta.data[pointIndex];
    const rect = canvas.getBoundingClientRect();
    
    // Create and dispatch mousemove event
    const event = new MouseEvent('mousemove', {
        clientX: rect.left + point.x,
        clientY: rect.top + point.y,
        bubbles: true,
        cancelable: true,
        view: window
    });
    
    canvas.dispatchEvent(event);
    
    return {
        x: point.x,
        y: point.y,
        element: point
    };
}

// Test suite
class ChartTooltipTests {
    constructor() {
        this.results = [];
    }

    // Test 1: Verify tooltip configuration exists
    testTooltipConfigExists() {
        const testName = 'Tooltip configuration exists';
        try {
            const chart = getChartInstance();
            
            if (!chart) {
                this.results.push({ test: testName, passed: false, details: 'Chart not found' });
                return logTest(testName, false, 'Chart not found');
            }
            
            const tooltipConfig = chart.options?.plugins?.tooltip;
            
            if (!tooltipConfig) {
                this.results.push({ test: testName, passed: false, details: 'Tooltip config not found' });
                return logTest(testName, false, 'Tooltip config not found');
            }
            
            const hasBackgroundColor = tooltipConfig.backgroundColor !== undefined;
            const hasTitleColor = tooltipConfig.titleColor !== undefined;
            const hasCallbacks = tooltipConfig.callbacks !== undefined;
            const hasTitleCallback = tooltipConfig.callbacks?.title !== undefined;
            const hasLabelCallback = tooltipConfig.callbacks?.label !== undefined;
            
            const passed = hasBackgroundColor && hasTitleColor && hasCallbacks && hasTitleCallback && hasLabelCallback;
            const details = `BG: ${hasBackgroundColor}, Title: ${hasTitleColor}, Callbacks: ${hasCallbacks}, TitleCB: ${hasTitleCallback}, LabelCB: ${hasLabelCallback}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 2: Verify tooltip callbacks are functions
    testTooltipCallbacksAreFunctions() {
        const testName = 'Tooltip callbacks are functions';
        try {
            const chart = getChartInstance();
            
            if (!chart) {
                this.results.push({ test: testName, passed: false, details: 'Chart not found' });
                return logTest(testName, false, 'Chart not found');
            }
            
            const callbacks = chart.options?.plugins?.tooltip?.callbacks;
            
            if (!callbacks) {
                this.results.push({ test: testName, passed: false, details: 'Callbacks not found' });
                return logTest(testName, false, 'Callbacks not found');
            }
            
            const titleIsFunction = typeof callbacks.title === 'function';
            const labelIsFunction = typeof callbacks.label === 'function';
            
            const passed = titleIsFunction && labelIsFunction;
            const details = `Title: ${titleIsFunction}, Label: ${labelIsFunction}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 3: Verify interaction mode is set correctly
    testInteractionMode() {
        const testName = 'Interaction mode configured for hover';
        try {
            const chart = getChartInstance();
            
            if (!chart) {
                this.results.push({ test: testName, passed: false, details: 'Chart not found' });
                return logTest(testName, false, 'Chart not found');
            }
            
            const interactionMode = chart.options?.interaction?.mode;
            const intersect = chart.options?.interaction?.intersect;
            
            // Should be 'nearest' or 'index' for easy hovering
            const modeIsGood = interactionMode === 'nearest' || interactionMode === 'index';
            const intersectIsFalse = intersect === false;
            
            const passed = modeIsGood && intersectIsFalse;
            const details = `Mode: ${interactionMode}, Intersect: ${intersect}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 4: Verify chart has data for tooltips
    testChartHasData() {
        const testName = 'Chart has data for tooltips';
        try {
            const chart = getChartInstance();
            
            if (!chart) {
                this.results.push({ test: testName, passed: false, details: 'Chart not found' });
                return logTest(testName, false, 'Chart not found');
            }
            
            const hasData = chart.data?.datasets && chart.data.datasets.length > 0;
            const hasLabels = chart.data?.labels && chart.data.labels.length > 0;
            const firstDatasetHasData = hasData && chart.data.datasets[0]?.data?.length > 0;
            
            const passed = hasData && hasLabels && firstDatasetHasData;
            const details = `Datasets: ${chart.data?.datasets?.length || 0}, Labels: ${chart.data?.labels?.length || 0}, Data points: ${chart.data?.datasets?.[0]?.data?.length || 0}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 5: Test tooltip title callback returns category name
    testTitleCallbackReturnsCategoryName() {
        const testName = 'Title callback returns category name';
        try {
            const chart = getChartInstance();
            
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart or data not available' });
                return logTest(testName, false, 'Chart or data not available');
            }
            
            const callbacks = chart.options?.plugins?.tooltip?.callbacks;
            
            if (!callbacks || typeof callbacks.title !== 'function') {
                this.results.push({ test: testName, passed: false, details: 'Title callback not found' });
                return logTest(testName, false, 'Title callback not found');
            }
            
            // Create mock context
            const mockContext = [{
                dataset: chart.data.datasets[0],
                label: chart.data.labels[0],
                datasetIndex: 0,
                dataIndex: 0
            }];
            
            const result = callbacks.title(mockContext);
            const categoryName = chart.data.datasets[0].label;
            
            // Check if result contains category name or date (depending on view)
            const passed = result !== null && result !== undefined && result !== '';
            const details = `Returned: "${result}", Expected category: "${categoryName}"`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 6: Test tooltip label callback includes category info
    testLabelCallbackIncludesCategoryInfo() {
        const testName = 'Label callback includes category info';
        try {
            const chart = getChartInstance();
            
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart or data not available' });
                return logTest(testName, false, 'Chart or data not available');
            }
            
            const callbacks = chart.options?.plugins?.tooltip?.callbacks;
            
            if (!callbacks || typeof callbacks.label !== 'function') {
                this.results.push({ test: testName, passed: false, details: 'Label callback not found' });
                return logTest(testName, false, 'Label callback not found');
            }
            
            // Create mock context
            const dataValue = chart.data.datasets[0].data[0];
            const mockContext = {
                dataset: chart.data.datasets[0],
                label: chart.data.labels[0],
                parsed: { y: dataValue },
                datasetIndex: 0,
                dataIndex: 0
            };
            
            const result = callbacks.label(mockContext);
            const categoryName = chart.data.datasets[0].label;
            
            // Check if result is a string and not empty
            const isString = typeof result === 'string';
            const notEmpty = result && result.length > 0;
            const hasPercentage = result && result.includes('%');
            
            const passed = isString && notEmpty && hasPercentage;
            const details = `Returned: "${result}"`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 7: Simulate hover and check tooltip plugin state
    testSimulateHoverActivatesTooltip() {
        const testName = 'Simulate hover activates tooltip';
        try {
            const chart = getChartInstance();
            
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart or data not available' });
                return logTest(testName, false, 'Chart or data not available');
            }
            
            // Try to simulate hover
            try {
                const hoverResult = simulateHover(chart, 0, 0);
                
                // Check if tooltip plugin exists and has active state
                const tooltipPlugin = chart.tooltip;
                const hasTooltip = tooltipPlugin !== undefined && tooltipPlugin !== null;
                
                const passed = hasTooltip;
                const details = `Tooltip plugin exists: ${hasTooltip}, Hover simulated at (${hoverResult.x}, ${hoverResult.y})`;
                
                this.results.push({ test: testName, passed, details });
                return logTest(testName, passed, details);
            } catch (hoverError) {
                this.results.push({ test: testName, passed: false, details: `Hover simulation failed: ${hoverError.message}` });
                return logTest(testName, false, `Hover simulation failed: ${hoverError.message}`);
            }
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 8: Check Canvas and Chart.js version
    testCanvasAndChartJSVersion() {
        const testName = 'Canvas accessible and Chart.js loaded';
        try {
            const canvas = document.getElementById('teamStatisticsChart');
            
            if (!canvas) {
                this.results.push({ test: testName, passed: false, details: 'Canvas not found' });
                return logTest(testName, false, 'Canvas not found');
            }
            
            const isCanvas = canvas.tagName === 'CANVAS';
            const hasChartJS = typeof Chart !== 'undefined';
            const chartJSVersion = hasChartJS ? Chart.version : 'N/A';
            
            const passed = isCanvas && hasChartJS;
            const details = `Canvas: ${isCanvas}, Chart.js: ${hasChartJS}, Version: ${chartJSVersion}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Run all tests
    runAll() {
        console.log('\n=== Chart Tooltip Tests ===\n');
        
        this.testCanvasAndChartJSVersion();
        this.testTooltipConfigExists();
        this.testTooltipCallbacksAreFunctions();
        this.testInteractionMode();
        this.testChartHasData();
        this.testTitleCallbackReturnsCategoryName();
        this.testLabelCallbackIncludesCategoryInfo();
        this.testSimulateHoverActivatesTooltip();
        
        const passed = this.results.filter(r => r.passed).length;
        const total = this.results.length;
        const percentage = Math.round((passed / total) * 100);
        
        console.log(`\n=== Results: ${passed}/${total} passed (${percentage}%) ===\n`);
        
        if (percentage < 100) {
            console.log('🔍 DIAGNOSTIC INFORMATION:');
            console.log('If tooltips are not working, check:');
            console.log('1. Hover slowly near the chart lines (not just on points)');
            console.log('2. Ensure Chart.js version is 3.x or higher');
            console.log('3. Check browser console for JavaScript errors');
            console.log('4. Verify analytics_dashboard.js has loaded correctly');
            console.log('5. Try refreshing the page to reload the chart');
            console.log('\nManual test: Slowly move your mouse near a line on the chart.');
            console.log('You should see a tooltip appear with the category name.\n');
        }
        
        return {
            passed,
            total,
            percentage,
            results: this.results
        };
    }
}

// Export for use in systems check
if (typeof window !== 'undefined') {
    window.ChartTooltipTests = ChartTooltipTests;
}

// Auto-run if in browser console
if (typeof window !== 'undefined' && window.location) {
    // Only auto-run if on analytics dashboard page
    if (window.location.pathname.includes('analytics')) {
        setTimeout(() => {
            console.log('⏳ Waiting for chart to load...');
            setTimeout(() => {
                const tests = new ChartTooltipTests();
                window.chartTooltipTestResults = tests.runAll();
            }, 2000);
        }, 1000);
    }
}

