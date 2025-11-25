/**
 * Test cases for Chart Line Toggle Functionality
 * These tests verify that the toggle lines feature works correctly on the analytics dashboard
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

// Test suite
class ChartToggleTests {
    constructor() {
        this.results = [];
    }

    // Test 1: Check if toggle menu elements exist
    testToggleMenuExists() {
        const testName = 'Toggle menu elements exist';
        try {
            const menu = document.getElementById('chartLineMenu');
            const list = document.getElementById('chartLineList');
            const toggleAll = document.getElementById('toggleAllLines');
            const toggleButton = document.querySelector('button[onclick*="chartLineMenu"]');
            
            const menuExists = menu !== null;
            const listExists = list !== null;
            const toggleAllExists = toggleAll !== null;
            const toggleButtonExists = toggleButton !== null;
            
            const passed = menuExists && listExists && toggleAllExists && toggleButtonExists;
            const details = `Menu: ${menuExists}, List: ${listExists}, ToggleAll: ${toggleAllExists}, Button: ${toggleButtonExists}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 2: Check if toggle functions are defined
    testToggleFunctionsExist() {
        const testName = 'Toggle functions are defined';
        try {
            const functions = [
                'getChartInstance',
                'toggleChartLine',
                'toggleAllChartLines',
                'populateChartLineMenu',
                'updateToggleAllState',
                'syncCheckboxState'
            ];
            
            const missing = [];
            functions.forEach(func => {
                if (typeof window[func] !== 'function') {
                    missing.push(func);
                }
            });
            
            const passed = missing.length === 0;
            const details = missing.length > 0 ? `Missing: ${missing.join(', ')}` : 'All functions exist';
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 3: Check if chart instance can be retrieved
    testGetChartInstance() {
        const testName = 'Chart instance can be retrieved';
        try {
            if (typeof getChartInstance !== 'function') {
                this.results.push({ test: testName, passed: false, details: 'getChartInstance function not found' });
                return logTest(testName, false, 'getChartInstance function not found');
            }
            
            const chart = getChartInstance();
            const passed = chart !== null && chart !== undefined;
            const details = passed ? `Chart found with ${chart.data?.datasets?.length || 0} datasets` : 'Chart not found';
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 4: Check if menu is populated when chart exists
    testMenuPopulated() {
        const testName = 'Menu is populated with chart datasets';
        try {
            const chart = getChartInstance();
            const container = document.getElementById('chartLineList');
            
            if (!chart) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return logTest(testName, false, 'Chart not available');
            }
            
            if (!container) {
                this.results.push({ test: testName, passed: false, details: 'Container not found' });
                return logTest(testName, false, 'Container not found');
            }
            
            const datasetCount = chart.data?.datasets?.length || 0;
            const menuItemCount = container.querySelectorAll('.chart-line-item').length;
            
            const passed = datasetCount > 0 && menuItemCount === datasetCount;
            const details = `Datasets: ${datasetCount}, Menu items: ${menuItemCount}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 5: Test individual line toggle
    testIndividualToggle() {
        const testName = 'Individual line toggle works';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available or no datasets' });
                return logTest(testName, false, 'Chart not available or no datasets');
            }
            
            const firstIndex = 0;
            const initialMeta = chart.getDatasetMeta(firstIndex);
            const initialHidden = initialMeta?.hidden === true;
            
            // Toggle the line
            const toggleResult = toggleChartLine(firstIndex, !initialHidden);
            
            if (!toggleResult) {
                this.results.push({ test: testName, passed: false, details: 'toggleChartLine returned false' });
                return logTest(testName, false, 'toggleChartLine returned false');
            }
            
            // Check if state changed
            const newMeta = chart.getDatasetMeta(firstIndex);
            const newHidden = newMeta?.hidden === true;
            const stateChanged = initialHidden !== newHidden;
            
            // Restore original state
            toggleChartLine(firstIndex, !initialHidden);
            
            const passed = stateChanged;
            const details = stateChanged ? 'State changed correctly' : 'State did not change';
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 6: Test toggle all functionality
    testToggleAll() {
        const testName = 'Toggle all lines works';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available or no datasets' });
                return logTest(testName, false, 'Chart not available or no datasets');
            }
            
            // Get initial states
            const initialStates = chart.data.datasets.map((ds, idx) => {
                const meta = chart.getDatasetMeta(idx);
                return meta?.hidden === true;
            });
            
            // Toggle all to hidden
            const hideResult = toggleAllChartLines(false);
            if (!hideResult) {
                this.results.push({ test: testName, passed: false, details: 'toggleAllChartLines(false) returned false' });
                return logTest(testName, false, 'toggleAllChartLines(false) returned false');
            }
            
            // Check if all are hidden
            const allHidden = chart.data.datasets.every((ds, idx) => {
                const meta = chart.getDatasetMeta(idx);
                return meta?.hidden === true;
            });
            
            // Toggle all back to visible
            toggleAllChartLines(true);
            
            // Check if all are visible
            const allVisible = chart.data.datasets.every((ds, idx) => {
                const meta = chart.getDatasetMeta(idx);
                return meta?.hidden !== true;
            });
            
            const passed = allHidden && allVisible;
            const details = `Hide all: ${allHidden}, Show all: ${allVisible}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 7: Test checkbox synchronization
    testCheckboxSync() {
        const testName = 'Checkbox state syncs with chart';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available or no datasets' });
                return logTest(testName, false, 'Chart not available or no datasets');
            }
            
            const firstIndex = 0;
            const checkbox = document.getElementById(`chartLine-${firstIndex}`);
            
            if (!checkbox) {
                this.results.push({ test: testName, passed: false, details: 'Checkbox not found' });
                return logTest(testName, false, 'Checkbox not found');
            }
            
            // Get initial states
            const initialMeta = chart.getDatasetMeta(firstIndex);
            const initialHidden = initialMeta?.hidden === true;
            const initialChecked = checkbox.checked;
            
            // Toggle via function
            toggleChartLine(firstIndex, !initialHidden);
            
            // Check if checkbox updated
            const newChecked = checkbox.checked;
            const synced = newChecked === !initialHidden;
            
            // Restore
            toggleChartLine(firstIndex, !initialHidden);
            
            const passed = synced;
            const details = synced ? 'Checkbox synced correctly' : 'Checkbox did not sync';
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 8: Test toggle all checkbox state
    testToggleAllCheckbox() {
        const testName = 'Toggle all checkbox reflects state';
        try {
            const toggleAll = document.getElementById('toggleAllLines');
            if (!toggleAll) {
                this.results.push({ test: testName, passed: false, details: 'Toggle all checkbox not found' });
                return logTest(testName, false, 'Toggle all checkbox not found');
            }
            
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return logTest(testName, false, 'Chart not available');
            }
            
            // Set all to visible
            toggleAllChartLines(true);
            updateToggleAllState();
            const allVisibleState = toggleAll.checked;
            
            // Set all to hidden
            toggleAllChartLines(false);
            updateToggleAllState();
            const allHiddenState = !toggleAll.checked;
            
            // Restore
            toggleAllChartLines(true);
            updateToggleAllState();
            
            const passed = allVisibleState && allHiddenState;
            const details = `Visible state: ${allVisibleState}, Hidden state: ${allHiddenState}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 9: Test toggle works after chart recreation (category change)
    testToggleAfterRecreation() {
        const testName = 'Toggle works after chart recreation';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return logTest(testName, false, 'Chart not available');
            }
            
            // Store original dataset count
            const originalCount = chart.data.datasets.length;
            
            // Simulate chart recreation by calling populateChartLineMenu
            if (typeof populateChartLineMenu === 'function') {
                const populateResult = populateChartLineMenu(true);
                
                if (!populateResult) {
                    this.results.push({ test: testName, passed: false, details: 'populateChartLineMenu failed' });
                    return logTest(testName, false, 'populateChartLineMenu failed');
                }
                
                // Try to toggle after repopulation
                const firstIndex = 0;
                const toggleResult = toggleChartLine(firstIndex, false);
                
                if (!toggleResult) {
                    this.results.push({ test: testName, passed: false, details: 'Toggle failed after recreation' });
                    return logTest(testName, false, 'Toggle failed after recreation');
                }
                
                // Check if toggle actually worked
                const meta = chart.getDatasetMeta(firstIndex);
                const hidden = meta?.hidden === true;
                
                // Restore state
                toggleChartLine(firstIndex, true);
                
                const passed = hidden;
                const details = hidden ? 'Toggle worked after recreation' : 'Toggle did not work after recreation';
                
                this.results.push({ test: testName, passed, details });
                return logTest(testName, passed, details);
            } else {
                this.results.push({ test: testName, passed: false, details: 'populateChartLineMenu not found' });
                return logTest(testName, false, 'populateChartLineMenu not found');
            }
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 10: Test multiple rapid toggles don't break functionality
    testRapidToggles() {
        const testName = 'Multiple rapid toggles work correctly';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return logTest(testName, false, 'Chart not available');
            }
            
            const firstIndex = 0;
            let allSucceeded = true;
            const iterations = 5;
            
            // Rapidly toggle multiple times
            for (let i = 0; i < iterations; i++) {
                const visible = i % 2 === 0;
                const result = toggleChartLine(firstIndex, visible);
                if (!result) {
                    allSucceeded = false;
                    break;
                }
            }
            
            if (!allSucceeded) {
                this.results.push({ test: testName, passed: false, details: 'One or more rapid toggles failed' });
                return logTest(testName, false, 'One or more rapid toggles failed');
            }
            
            // Verify chart is still functional
            const meta = chart.getDatasetMeta(firstIndex);
            const canGetMeta = meta !== null && meta !== undefined;
            
            // Restore to visible
            toggleChartLine(firstIndex, true);
            
            const passed = allSucceeded && canGetMeta;
            const details = passed ? `${iterations} rapid toggles succeeded` : 'Chart state corrupted';
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Test 11: Test toggle all then individual toggle works correctly (edge case)
    testToggleAllThenIndividual() {
        const testName = 'Individual toggle works after Toggle All';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length < 2) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available or insufficient datasets' });
                return logTest(testName, false, 'Chart not available or insufficient datasets');
            }
            
            // Step 1: Toggle all to hidden
            const toggleAllResult = toggleAllChartLines(false);
            if (!toggleAllResult) {
                this.results.push({ test: testName, passed: false, details: 'Toggle all failed' });
                return logTest(testName, false, 'Toggle all failed');
            }
            
            // Verify all are hidden
            const allHidden = chart.data.datasets.every((ds, idx) => {
                const meta = chart.getDatasetMeta(idx);
                return meta?.hidden === true;
            });
            
            if (!allHidden) {
                // Restore state
                toggleAllChartLines(true);
                this.results.push({ test: testName, passed: false, details: 'Not all datasets were hidden' });
                return logTest(testName, false, 'Not all datasets were hidden');
            }
            
            // Step 2: Toggle individual line back to visible
            const firstIndex = 0;
            const individualResult = toggleChartLine(firstIndex, true);
            if (!individualResult) {
                // Restore state
                toggleAllChartLines(true);
                this.results.push({ test: testName, passed: false, details: 'Individual toggle failed after toggle all' });
                return logTest(testName, false, 'Individual toggle failed after toggle all');
            }
            
            // Verify first line is now visible
            const firstMeta = chart.getDatasetMeta(firstIndex);
            const firstVisible = firstMeta?.hidden !== true;
            
            // Verify other lines are still hidden
            const othersHidden = chart.data.datasets.every((ds, idx) => {
                if (idx === firstIndex) return true; // Skip the one we made visible
                const meta = chart.getDatasetMeta(idx);
                return meta?.hidden === true;
            });
            
            // Step 3: Toggle another individual line
            const secondIndex = 1;
            const secondResult = toggleChartLine(secondIndex, true);
            const secondMeta = chart.getDatasetMeta(secondIndex);
            const secondVisible = secondMeta?.hidden !== true;
            
            // Restore all to visible
            toggleAllChartLines(true);
            
            const passed = firstVisible && othersHidden && secondResult && secondVisible;
            const details = passed 
                ? 'Individual toggles worked correctly after Toggle All'
                : `First: ${firstVisible}, Others hidden: ${othersHidden}, Second: ${secondVisible}`;
            
            this.results.push({ test: testName, passed, details });
            return logTest(testName, passed, details);
        } catch (error) {
            // Attempt to restore state
            try {
                toggleAllChartLines(true);
            } catch (restoreError) {
                console.error('Failed to restore state:', restoreError);
            }
            this.results.push({ test: testName, passed: false, details: error.message });
            return logTest(testName, false, error.message);
        }
    }

    // Run all tests
    runAll() {
        console.log('\n=== Chart Line Toggle Tests ===\n');
        
        // Core functionality tests
        this.testToggleMenuExists();
        this.testToggleFunctionsExist();
        this.testGetChartInstance();
        this.testMenuPopulated();
        this.testIndividualToggle();
        this.testToggleAll();
        this.testCheckboxSync();
        this.testToggleAllCheckbox();
        
        // Edge case tests (new)
        this.testToggleAfterRecreation();
        this.testRapidToggles();
        this.testToggleAllThenIndividual();
        
        const passed = this.results.filter(r => r.passed).length;
        const total = this.results.length;
        const percentage = Math.round((passed / total) * 100);
        
        console.log(`\n=== Results: ${passed}/${total} passed (${percentage}%) ===\n`);
        
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
    window.ChartToggleTests = ChartToggleTests;
}

// Auto-run if in browser console
if (typeof window !== 'undefined' && window.location) {
    // Only auto-run if on analytics dashboard page
    if (window.location.pathname.includes('analytics')) {
        setTimeout(() => {
            const tests = new ChartToggleTests();
            window.chartToggleTestResults = tests.runAll();
        }, 2000); // Wait for chart to load
    }
}

