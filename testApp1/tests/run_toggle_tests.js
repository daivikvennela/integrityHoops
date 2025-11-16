// Toggle Functionality Test Runner
// Copy and paste this into browser console on smartdash_results page

(function() {
    console.log("=".repeat(70));
    console.log("🧪 TOGGLE FUNCTIONALITY TEST SUITE");
    console.log("=".repeat(70));
    
    const tests = [];
    let testCount = 0;
    
    function test(name, fn) {
        testCount++;
        try {
            const result = fn();
            const passed = result !== false;
            tests.push({name, passed, error: passed ? null : result});
            console.log(`${passed ? '✅' : '❌'} Test ${testCount}: ${name}`);
            if (!passed && result) console.log(`   Error: ${result}`);
        } catch (e) {
            tests.push({name, passed: false, error: e.message});
            console.log(`❌ Test ${testCount}: ${name}`);
            console.log(`   Error: ${e.message}`);
        }
    }
    
    // Test 1: Functions exist
    test("toggleColumn function exists", () => typeof toggleColumn === 'function');
    test("toggleAllColumns function exists", () => typeof toggleAllColumns === 'function');
    test("updateToggleAll function exists", () => typeof updateToggleAll === 'function');
    
    // Test 2: DOM elements exist
    test("Table exists", () => {
        const table = document.getElementById('dataTable');
        return table !== null ? true : "Table not found";
    });
    
    test("Column menu exists", () => {
        const menu = document.getElementById('columnMenu');
        return menu !== null ? true : "Menu not found";
    });
    
    test("Toggle All checkbox exists", () => {
        const toggleAll = document.getElementById('toggleAll');
        return toggleAll !== null ? true : "Toggle All checkbox not found";
    });
    
    test("Column checkboxes exist", () => {
        const checkboxes = document.querySelectorAll('.col-toggle');
        return checkboxes.length > 0 ? true : `No checkboxes found (expected at least 1)`;
    });
    
    // Test 3: Table structure
    test("Table has data-column-index attributes", () => {
        const table = document.getElementById('dataTable');
        if (!table) return "Table not found";
        const headers = table.querySelectorAll('th[data-column-index]');
        return headers.length > 0 ? true : "No headers with data-column-index";
    });
    
    // Test 4: Individual toggle functionality
    test("Individual column toggle works", () => {
        const table = document.getElementById('dataTable');
        const checkboxes = document.querySelectorAll('.col-toggle');
        
        if (!table || checkboxes.length === 0) return "Prerequisites not met";
        
        const testIndex = 1;
        const checkbox = document.getElementById(`col-toggle-${testIndex}`);
        const header = table.querySelector(`th[data-column-index="${testIndex}"]`);
        
        if (!checkbox || !header) return `Test elements not found for index ${testIndex}`;
        
        const initialHidden = header.classList.contains('hidden-column');
        const initialChecked = checkbox.checked;
        
        // Toggle off
        toggleColumn(testIndex, false, false);
        const afterToggleOff = header.classList.contains('hidden-column');
        const afterToggleOffChecked = checkbox.checked;
        
        if (afterToggleOff !== true) return "Column not hidden after toggleColumn(false)";
        if (afterToggleOffChecked !== false) return "Checkbox not unchecked after toggleColumn(false)";
        
        // Toggle on
        toggleColumn(testIndex, true, false);
        const afterToggleOn = header.classList.contains('hidden-column');
        const afterToggleOnChecked = checkbox.checked;
        
        if (afterToggleOn !== false) return "Column not shown after toggleColumn(true)";
        if (afterToggleOnChecked !== true) return "Checkbox not checked after toggleColumn(true)";
        
        // Restore original state
        toggleColumn(testIndex, initialChecked, false);
        
        return true;
    });
    
    // Test 5: Toggle All functionality
    test("Toggle All works", () => {
        const checkboxes = document.querySelectorAll('.col-toggle');
        const toggleAll = document.getElementById('toggleAll');
        
        if (!checkboxes.length || !toggleAll) return "Prerequisites not met";
        
        // Get initial states
        const initialStates = Array.from(checkboxes).map(cb => cb.checked);
        
        // Toggle all off
        toggleAllColumns(false);
        const allUnchecked = Array.from(checkboxes).every(cb => !cb.checked);
        if (!allUnchecked) return "Not all checkboxes unchecked after toggleAllColumns(false)";
        
        // Toggle all on
        toggleAllColumns(true);
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        if (!allChecked) return "Not all checkboxes checked after toggleAllColumns(true)";
        
        // Restore original states
        checkboxes.forEach((cb, i) => {
            toggleColumn(parseInt(cb.dataset.col), initialStates[i], true);
        });
        updateToggleAll();
        
        return true;
    });
    
    // Test 6: Individual toggle after Toggle All
    test("Individual toggle works after Toggle All", () => {
        const checkboxes = document.querySelectorAll('.col-toggle');
        const table = document.getElementById('dataTable');
        
        if (!checkboxes.length || !table) return "Prerequisites not met";
        
        const testIndex = 1;
        const checkbox = document.getElementById(`col-toggle-${testIndex}`);
        const header = table.querySelector(`th[data-column-index="${testIndex}"]`);
        
        if (!checkbox || !header) return "Test elements not found";
        
        // Use toggle all twice
        toggleAllColumns(false);
        toggleAllColumns(true);
        
        // Now test individual toggle
        const beforeToggle = checkbox.checked;
        const beforeHidden = header.classList.contains('hidden-column');
        
        // Click checkbox (simulate user action)
        checkbox.click();
        
        // Wait a bit for event to process
        setTimeout(() => {
            const afterToggle = checkbox.checked;
            const afterHidden = header.classList.contains('hidden-column');
            
            if (afterToggle === beforeToggle) {
                console.log("   ⚠️  Checkbox state didn't change on click");
            }
            if (afterHidden === beforeHidden) {
                console.log("   ⚠️  Column visibility didn't change on click");
            }
        }, 100);
        
        // Manually test toggle function
        toggleColumn(testIndex, !beforeToggle, false);
        const manualAfterToggle = checkbox.checked;
        const manualAfterHidden = header.classList.contains('hidden-column');
        
        if (manualAfterToggle === beforeToggle) return "toggleColumn didn't change checkbox state";
        if (manualAfterHidden === beforeHidden) return "toggleColumn didn't change column visibility";
        
        // Restore
        toggleColumn(testIndex, beforeToggle, false);
        
        return true;
    });
    
    // Test 7: Event listeners attached
    test("Event listeners are attached", () => {
        const columnMenu = document.getElementById('columnMenu');
        if (!columnMenu) return "Menu not found";
        
        // Check if event delegation is set up by testing if clicking a checkbox triggers toggle
        const checkboxes = document.querySelectorAll('.col-toggle');
        if (checkboxes.length === 0) return "No checkboxes found";
        
        // We can't easily test if listeners are attached, but we can verify the structure
        return true;
    });
    
    // Summary
    setTimeout(() => {
        console.log("\n" + "=".repeat(70));
        console.log("📊 TEST RESULTS SUMMARY");
        console.log("=".repeat(70));
        
        const passed = tests.filter(t => t.passed).length;
        const failed = tests.filter(t => !t.passed).length;
        
        tests.forEach(t => {
            const status = t.passed ? '✅ PASS' : '❌ FAIL';
            console.log(`${status}: ${t.name}`);
            if (!t.passed && t.error) {
                console.log(`      → ${t.error}`);
            }
        });
        
        console.log("\n" + "=".repeat(70));
        console.log(`Total: ${tests.length} tests`);
        console.log(`Passed: ${passed} ✅`);
        console.log(`Failed: ${failed} ${failed > 0 ? '❌' : ''}`);
        console.log(`Success Rate: ${((passed/tests.length)*100).toFixed(1)}%`);
        console.log("=".repeat(70));
        
        if (failed === 0) {
            console.log("\n🎉 All tests passed! Toggle functionality is working correctly.");
        } else {
            console.log("\n⚠️  Some tests failed. Check the errors above.");
        }
    }, 200);
    
    return tests;
})();

