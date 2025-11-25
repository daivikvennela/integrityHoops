/**
 * Integration Tests for Chart Line Toggle Functionality
 * These tests simulate actual user interactions with the toggle menu
 */

// Test utilities
function waitFor(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function simulateClick(element) {
    if (!element) {
        throw new Error('Element not found for click simulation');
    }
    const event = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
    });
    element.dispatchEvent(event);
}

function simulateChange(checkbox, checked) {
    if (!checkbox) {
        throw new Error('Checkbox not found for change simulation');
    }
    checkbox.checked = checked;
    const event = new Event('change', {
        bubbles: true,
        cancelable: true
    });
    checkbox.dispatchEvent(event);
}

// Integration test suite
class ChartToggleIntegrationTests {
    constructor() {
        this.results = [];
    }

    log(testName, passed, details = '') {
        const status = passed ? '✓ PASS' : '✗ FAIL';
        console.log(`${status} - ${testName}${details ? `: ${details}` : ''}`);
        return passed;
    }

    // Test 1: Toggle menu opens and closes
    async testMenuOpenClose() {
        const testName = 'Toggle menu opens and closes';
        try {
            const button = document.querySelector('button[onclick*="chartLineMenu"]');
            const menu = document.getElementById('chartLineMenu');
            
            if (!button || !menu) {
                this.results.push({ test: testName, passed: false, details: 'Button or menu not found' });
                return this.log(testName, false, 'Button or menu not found');
            }
            
            // Open menu
            simulateClick(button);
            await waitFor(100);
            const isOpen = menu.classList.contains('show');
            
            // Close menu
            simulateClick(button);
            await waitFor(100);
            const isClosed = !menu.classList.contains('show');
            
            const passed = isOpen && isClosed;
            const details = `Open: ${isOpen}, Closed: ${isClosed}`;
            
            this.results.push({ test: testName, passed, details });
            return this.log(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return this.log(testName, false, error.message);
        }
    }

    // Test 2: User clicks individual checkbox
    async testUserClicksCheckbox() {
        const testName = 'User clicks individual checkbox';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return this.log(testName, false, 'Chart not available');
            }
            
            const firstIndex = 0;
            const checkbox = document.getElementById(`chartLine-${firstIndex}`);
            
            if (!checkbox) {
                this.results.push({ test: testName, passed: false, details: 'Checkbox not found' });
                return this.log(testName, false, 'Checkbox not found');
            }
            
            // Get initial state
            const initialChecked = checkbox.checked;
            const initialMeta = chart.getDatasetMeta(firstIndex);
            const initialHidden = initialMeta?.hidden === true;
            
            // Simulate user clicking checkbox
            simulateChange(checkbox, !initialChecked);
            await waitFor(100);
            
            // Check if chart updated
            const newMeta = chart.getDatasetMeta(firstIndex);
            const newHidden = newMeta?.hidden === true;
            const stateChanged = initialHidden !== newHidden;
            
            // Restore
            simulateChange(checkbox, initialChecked);
            await waitFor(100);
            
            const passed = stateChanged;
            const details = stateChanged ? 'Chart updated correctly' : 'Chart did not update';
            
            this.results.push({ test: testName, passed, details });
            return this.log(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return this.log(testName, false, error.message);
        }
    }

    // Test 3: User clicks Toggle All then individual checkboxes
    async testToggleAllThenIndividualClicks() {
        const testName = 'User clicks Toggle All then individual checkboxes';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length < 2) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available or insufficient datasets' });
                return this.log(testName, false, 'Chart not available or insufficient datasets');
            }
            
            const toggleAll = document.getElementById('toggleAllLines');
            if (!toggleAll) {
                this.results.push({ test: testName, passed: false, details: 'Toggle All not found' });
                return this.log(testName, false, 'Toggle All not found');
            }
            
            // Step 1: User clicks Toggle All to uncheck (hide all)
            simulateChange(toggleAll, false);
            await waitFor(150);
            
            // Verify all lines are hidden
            const allHidden = chart.data.datasets.every((ds, idx) => {
                const meta = chart.getDatasetMeta(idx);
                return meta?.hidden === true;
            });
            
            if (!allHidden) {
                // Restore
                simulateChange(toggleAll, true);
                this.results.push({ test: testName, passed: false, details: 'Not all lines hidden after Toggle All' });
                return this.log(testName, false, 'Not all lines hidden after Toggle All');
            }
            
            // Step 2: User clicks individual checkbox to show one line
            const firstCheckbox = document.getElementById('chartLine-0');
            if (!firstCheckbox) {
                simulateChange(toggleAll, true);
                this.results.push({ test: testName, passed: false, details: 'First checkbox not found' });
                return this.log(testName, false, 'First checkbox not found');
            }
            
            simulateChange(firstCheckbox, true);
            await waitFor(150);
            
            // Verify first line is visible
            const firstMeta = chart.getDatasetMeta(0);
            const firstVisible = firstMeta?.hidden !== true;
            
            // Step 3: User clicks second individual checkbox
            const secondCheckbox = document.getElementById('chartLine-1');
            if (!secondCheckbox) {
                simulateChange(toggleAll, true);
                this.results.push({ test: testName, passed: false, details: 'Second checkbox not found' });
                return this.log(testName, false, 'Second checkbox not found');
            }
            
            simulateChange(secondCheckbox, true);
            await waitFor(150);
            
            // Verify second line is visible
            const secondMeta = chart.getDatasetMeta(1);
            const secondVisible = secondMeta?.hidden !== true;
            
            // Restore all to visible
            simulateChange(toggleAll, true);
            await waitFor(150);
            
            const passed = allHidden && firstVisible && secondVisible;
            const details = passed 
                ? 'All steps worked correctly'
                : `Hidden: ${allHidden}, First: ${firstVisible}, Second: ${secondVisible}`;
            
            this.results.push({ test: testName, passed, details });
            return this.log(testName, passed, details);
        } catch (error) {
            // Restore state
            try {
                const toggleAll = document.getElementById('toggleAllLines');
                if (toggleAll) simulateChange(toggleAll, true);
            } catch (restoreError) {
                console.error('Failed to restore state:', restoreError);
            }
            this.results.push({ test: testName, passed: false, details: error.message });
            return this.log(testName, false, error.message);
        }
    }

    // Test 4: Toggle persistence across category changes
    async testTogglePersistenceAcrossCategories() {
        const testName = 'Toggle persists across category changes';
        try {
            // This test simulates changing categories (which recreates the chart)
            // We can't actually trigger a category change in a unit test,
            // but we can test that populateChartLineMenu properly rebuilds the menu
            
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return this.log(testName, false, 'Chart not available');
            }
            
            // Hide first line
            const firstIndex = 0;
            toggleChartLine(firstIndex, false);
            await waitFor(100);
            
            // Verify it's hidden
            let meta = chart.getDatasetMeta(firstIndex);
            const wasHidden = meta?.hidden === true;
            
            // Simulate chart recreation by forcing menu repopulation
            if (typeof populateChartLineMenu === 'function') {
                populateChartLineMenu(true);
                await waitFor(150);
                
                // Check if the checkbox still reflects the hidden state
                const checkbox = document.getElementById(`chartLine-${firstIndex}`);
                const checkboxReflectsState = checkbox && checkbox.checked === false;
                
                // Restore
                toggleChartLine(firstIndex, true);
                await waitFor(100);
                
                const passed = wasHidden && checkboxReflectsState;
                const details = passed 
                    ? 'State persisted correctly'
                    : `Hidden: ${wasHidden}, Checkbox: ${checkboxReflectsState}`;
                
                this.results.push({ test: testName, passed, details });
                return this.log(testName, passed, details);
            } else {
                this.results.push({ test: testName, passed: false, details: 'populateChartLineMenu not found' });
                return this.log(testName, false, 'populateChartLineMenu not found');
            }
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return this.log(testName, false, error.message);
        }
    }

    // Test 5: Rapid user interactions don't break functionality
    async testRapidUserInteractions() {
        const testName = 'Rapid user interactions work correctly';
        try {
            const chart = getChartInstance();
            if (!chart || !chart.data?.datasets || chart.data.datasets.length === 0) {
                this.results.push({ test: testName, passed: false, details: 'Chart not available' });
                return this.log(testName, false, 'Chart not available');
            }
            
            const firstCheckbox = document.getElementById('chartLine-0');
            if (!firstCheckbox) {
                this.results.push({ test: testName, passed: false, details: 'Checkbox not found' });
                return this.log(testName, false, 'Checkbox not found');
            }
            
            let allSucceeded = true;
            const iterations = 5;
            
            // Rapidly toggle checkbox
            for (let i = 0; i < iterations; i++) {
                try {
                    simulateChange(firstCheckbox, i % 2 === 0);
                    await waitFor(50); // Shorter delay to test rapid interactions
                } catch (toggleError) {
                    allSucceeded = false;
                    console.error('Toggle failed on iteration', i, toggleError);
                    break;
                }
            }
            
            // Verify chart is still functional
            const meta = chart.getDatasetMeta(0);
            const canGetMeta = meta !== null && meta !== undefined;
            
            // Restore to checked
            simulateChange(firstCheckbox, true);
            await waitFor(100);
            
            const passed = allSucceeded && canGetMeta;
            const details = passed 
                ? `${iterations} rapid interactions succeeded`
                : 'Functionality degraded after rapid interactions';
            
            this.results.push({ test: testName, passed, details });
            return this.log(testName, passed, details);
        } catch (error) {
            this.results.push({ test: testName, passed: false, details: error.message });
            return this.log(testName, false, error.message);
        }
    }

    // Run all integration tests
    async runAll() {
        console.log('\n=== Chart Line Toggle Integration Tests ===\n');
        
        await this.testMenuOpenClose();
        await this.testUserClicksCheckbox();
        await this.testToggleAllThenIndividualClicks();
        await this.testTogglePersistenceAcrossCategories();
        await this.testRapidUserInteractions();
        
        const passed = this.results.filter(r => r.passed).length;
        const total = this.results.length;
        const percentage = Math.round((passed / total) * 100);
        
        console.log(`\n=== Integration Results: ${passed}/${total} passed (${percentage}%) ===\n`);
        
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
    window.ChartToggleIntegrationTests = ChartToggleIntegrationTests;
}

// Auto-run if in browser console
if (typeof window !== 'undefined' && window.location) {
    // Only auto-run if on analytics dashboard page
    if (window.location.pathname.includes('analytics')) {
        setTimeout(async () => {
            const tests = new ChartToggleIntegrationTests();
            window.chartToggleIntegrationTestResults = await tests.runAll();
        }, 3000); // Wait longer for chart to fully load
    }
}

