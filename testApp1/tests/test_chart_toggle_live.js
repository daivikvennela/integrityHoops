/**
 * Live Chart Toggle Test - Run in browser console on /analytics-dashboard
 * This tests the actual functionality based on the test cases
 */

(function() {
    console.log("=".repeat(70));
    console.log("🧪 CHART LINE TOGGLE LIVE TEST");
    console.log("=".repeat(70));
    
    const results = [];
    
    function test(name, fn) {
        try {
            const result = fn();
            const passed = result !== false && result !== undefined;
            results.push({name, passed, error: passed ? null : result});
            console.log(`${passed ? '✅' : '❌'} ${name}`);
            if (!passed && result) console.log(`   Error: ${result}`);
        } catch (e) {
            results.push({name, passed: false, error: e.message});
            console.log(`❌ ${name}`);
            console.log(`   Error: ${e.message}`);
        }
    }
    
    // TC-01: Button exists
    test("TC-01: Toggle Lines button exists", () => {
        const btn = document.querySelector('button[onclick*="chartLineMenu"]');
        return btn !== null;
    });
    
    // TC-02: Menu exists
    test("TC-02: Chart line menu exists", () => {
        const menu = document.getElementById('chartLineMenu');
        return menu !== null;
    });
    
    // TC-03: Chart canvas exists
    test("TC-03: Chart canvas exists", () => {
        const canvas = document.getElementById('teamStatisticsChart');
        return canvas !== null;
    });
    
    // TC-04-06: Functions exist
    test("TC-04: getChartInstance function exists", () => typeof getChartInstance === 'function');
    test("TC-05: toggleChartLine function exists", () => typeof toggleChartLine === 'function');
    test("TC-06: toggleAllChartLines function exists", () => typeof toggleAllChartLines === 'function');
    
    // TC-07: Chart instance accessible
    test("TC-07: Chart instance accessible", () => {
        const chart = getChartInstance();
        return chart !== null;
    });
    
    // TC-08: Chart has datasets
    test("TC-08: Chart has datasets", () => {
        const chart = getChartInstance();
        return chart && chart.data && chart.data.datasets && chart.data.datasets.length > 0;
    });
    
    // TC-09: Menu populates with checkboxes
    test("TC-09: Menu populates with checkboxes", () => {
        const container = document.getElementById('chartLineList');
        const chart = getChartInstance();
        if (!chart || !container) return false;
        
        // Force populate if needed
        if (typeof populateChartLineMenu === 'function') {
            populateChartLineMenu();
        }
        
        const checkboxes = container.querySelectorAll('.chart-line-toggle');
        return checkboxes.length === chart.data.datasets.length;
    });
    
    // TC-10: Individual toggle works
    test("TC-10: Individual line toggle works", () => {
        const chart = getChartInstance();
        if (!chart || chart.data.datasets.length === 0) return "Chart not available";
        
        const checkbox = document.getElementById('chartLine-0');
        if (!checkbox) return "Checkbox not found";
        
        const initialChecked = checkbox.checked;
        const initialHidden = chart.getDatasetMeta(0).hidden === true;
        
        // Toggle off
        toggleChartLine(0, false);
        const afterToggleOff = chart.getDatasetMeta(0).hidden === true;
        const checkboxAfterOff = checkbox.checked === false;
        
        // Toggle on
        toggleChartLine(0, true);
        const afterToggleOn = chart.getDatasetMeta(0).hidden !== true;
        const checkboxAfterOn = checkbox.checked === true;
        
        // Restore
        toggleChartLine(0, initialChecked);
        
        return afterToggleOff && checkboxAfterOff && afterToggleOn && checkboxAfterOn;
    });
    
    // TC-11: Toggle All works
    test("TC-11: Toggle All works", () => {
        const chart = getChartInstance();
        if (!chart || chart.data.datasets.length === 0) return "Chart not available";
        
        const checkboxes = document.querySelectorAll('.chart-line-toggle');
        if (checkboxes.length === 0) return "No checkboxes found";
        
        // Get initial states
        const initialStates = Array.from(checkboxes).map(cb => cb.checked);
        
        // Toggle all off
        toggleAllChartLines(false);
        const allUnchecked = Array.from(checkboxes).every(cb => !cb.checked);
        const allHidden = chart.data.datasets.every((ds, i) => {
            const meta = chart.getDatasetMeta(i);
            return meta && meta.hidden === true;
        });
        
        // Toggle all on
        toggleAllChartLines(true);
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        const allVisible = chart.data.datasets.every((ds, i) => {
            const meta = chart.getDatasetMeta(i);
            return meta && meta.hidden !== true;
        });
        
        // Restore
        initialStates.forEach((state, i) => {
            toggleChartLine(i, state);
        });
        
        return allUnchecked && allHidden && allChecked && allVisible;
    });
    
    // TC-EDGE-01: Individual toggle after Toggle All
    test("TC-EDGE-01: Individual toggle works after Toggle All", () => {
        const chart = getChartInstance();
        if (!chart || chart.data.datasets.length === 0) return "Chart not available";
        
        const checkbox = document.getElementById('chartLine-0');
        if (!checkbox) return "Checkbox not found";
        
        // Use toggle all twice
        toggleAllChartLines(false);
        toggleAllChartLines(true);
        
        // Now test individual toggle
        const beforeToggle = checkbox.checked;
        const beforeHidden = chart.getDatasetMeta(0).hidden === true;
        
        // Toggle individual
        toggleChartLine(0, !beforeToggle);
        
        const afterToggle = checkbox.checked;
        const afterHidden = chart.getDatasetMeta(0).hidden === true;
        
        // Restore
        toggleChartLine(0, beforeToggle);
        
        return afterToggle !== beforeToggle && afterHidden !== beforeHidden;
    });
    
    // Summary
    setTimeout(() => {
        console.log("\n" + "=".repeat(70));
        console.log("📊 TEST RESULTS");
        console.log("=".repeat(70));
        
        const passed = results.filter(r => r.passed).length;
        const failed = results.filter(r => !r.passed).length;
        
        results.forEach(r => {
            const icon = r.passed ? '✅' : '❌';
            console.log(`${icon} ${r.name}`);
            if (!r.passed && r.error) {
                console.log(`   → ${r.error}`);
            }
        });
        
        console.log("\n" + "=".repeat(70));
        console.log(`Total: ${results.length} tests`);
        console.log(`Passed: ${passed} ✅`);
        console.log(`Failed: ${failed} ${failed > 0 ? '❌' : ''}`);
        console.log(`Success Rate: ${((passed/results.length)*100).toFixed(1)}%`);
        console.log("=".repeat(70));
        
        if (failed === 0) {
            console.log("\n🎉 All tests passed! Chart toggle is working correctly.");
        } else {
            console.log("\n⚠️  Some tests failed. Check errors above.");
        }
    }, 500);
    
    return results;
})();

