// Quick Diagnostic Test for Toggle Functionality
// Run this in browser console on smartdash_results page

function diagnosticTest() {
    console.log("🔍 Running Toggle Diagnostic Tests...\n");
    
    const results = [];
    
    // Test 1: Check if functions exist
    console.log("Test 1: Checking function existence...");
    const hasToggleColumn = typeof toggleColumn === 'function';
    const hasToggleAll = typeof toggleAllColumns === 'function';
    const hasUpdateToggleAll = typeof updateToggleAll === 'function';
    
    results.push({test: "toggleColumn function exists", pass: hasToggleColumn});
    results.push({test: "toggleAllColumns function exists", pass: hasToggleAll});
    results.push({test: "updateToggleAll function exists", pass: hasUpdateToggleAll});
    
    console.log(`  toggleColumn: ${hasToggleColumn ? '✅' : '❌'}`);
    console.log(`  toggleAllColumns: ${hasToggleAll ? '✅' : '❌'}`);
    console.log(`  updateToggleAll: ${hasUpdateToggleAll ? '✅' : '❌'}\n`);
    
    // Test 2: Check if table exists
    console.log("Test 2: Checking table structure...");
    const table = document.getElementById('dataTable');
    const hasTable = table !== null;
    results.push({test: "Table exists", pass: hasTable});
    
    if (table) {
        const headers = table.querySelectorAll('th[data-column-index]');
        const cells = table.querySelectorAll('td[data-column-index]');
        console.log(`  Table found: ✅`);
        console.log(`  Headers with data-column-index: ${headers.length}`);
        console.log(`  Cells with data-column-index: ${cells.length}\n`);
        results.push({test: "Table has data attributes", pass: headers.length > 0});
    } else {
        console.log(`  Table found: ❌\n`);
    }
    
    // Test 3: Check if checkboxes exist
    console.log("Test 3: Checking checkboxes...");
    const checkboxes = document.querySelectorAll('.col-toggle');
    const toggleAll = document.getElementById('toggleAll');
    
    results.push({test: "Checkboxes exist", pass: checkboxes.length > 0});
    results.push({test: "Toggle All checkbox exists", pass: toggleAll !== null});
    
    console.log(`  Individual checkboxes: ${checkboxes.length}`);
    console.log(`  Toggle All checkbox: ${toggleAll ? '✅' : '❌'}\n`);
    
    // Test 4: Test actual toggle functionality
    if (hasToggleColumn && table && checkboxes.length > 0) {
        console.log("Test 4: Testing toggle functionality...");
        
        const testColIndex = 1;
        const testHeader = table.querySelector(`th[data-column-index="${testColIndex}"]`);
        const testCheckbox = document.getElementById(`col-toggle-${testColIndex}`);
        
        if (testHeader && testCheckbox) {
            // Get initial state
            const initialHidden = testHeader.classList.contains('hidden-column');
            const initialChecked = testCheckbox.checked;
            
            console.log(`  Testing column ${testColIndex}:`);
            console.log(`    Initial hidden: ${initialHidden}`);
            console.log(`    Initial checked: ${initialChecked}`);
            
            // Try to toggle
            try {
                toggleColumn(testColIndex, !initialChecked);
                
                // Check result
                const afterHidden = testHeader.classList.contains('hidden-column');
                const afterChecked = testCheckbox.checked;
                
                console.log(`    After toggle hidden: ${afterHidden}`);
                console.log(`    After toggle checked: ${afterChecked}`);
                
                const visibilityChanged = (afterHidden !== initialHidden);
                const checkboxSynced = (afterChecked === !afterHidden);
                
                results.push({test: "Toggle changes visibility", pass: visibilityChanged});
                results.push({test: "Checkbox syncs with visibility", pass: checkboxSynced});
                
                console.log(`    Visibility changed: ${visibilityChanged ? '✅' : '❌'}`);
                console.log(`    Checkbox synced: ${checkboxSynced ? '✅' : '❌'}`);
                
                // Restore state
                toggleColumn(testColIndex, initialChecked);
                
            } catch (e) {
                console.log(`    Error: ${e.message}`);
                results.push({test: "Toggle executes without error", pass: false});
            }
        } else {
            console.log(`  Could not find test elements`);
            results.push({test: "Test elements found", pass: false});
        }
    }
    
    // Summary
    console.log("\n📊 Test Summary:");
    const passed = results.filter(r => r.pass).length;
    const total = results.length;
    
    results.forEach(r => {
        console.log(`  ${r.pass ? '✅' : '❌'} ${r.test}`);
    });
    
    console.log(`\nResults: ${passed}/${total} tests passed`);
    
    if (passed === total) {
        console.log("✅ All tests passed!");
    } else {
        console.log("❌ Some tests failed. Check the issues above.");
    }
    
    return results;
}

// Auto-run if in browser
if (typeof window !== 'undefined') {
    console.log("Run diagnosticTest() to test toggle functionality");
}

