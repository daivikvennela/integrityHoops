/**
 * Frontend Display Test Cases
 * Tests that data is correctly displayed in the browser
 * 
 * Run this in the browser console on the /analytics-dashboard page
 */

(function() {
    'use strict';
    
    console.log("=".repeat(70));
    console.log("🧪 FRONTEND DISPLAY TEST SUITE");
    console.log("=".repeat(70));
    console.log();
    
    const tests = {
        passed: 0,
        failed: 0,
        results: []
    };
    
    function test(name, condition, message) {
        if (condition) {
            tests.passed++;
            tests.results.push({ name, status: 'PASS', message });
            console.log(`✅ ${name}: ${message || 'PASSED'}`);
        } else {
            tests.failed++;
            tests.results.push({ name, status: 'FAIL', message });
            console.error(`❌ ${name}: ${message || 'FAILED'}`);
        }
    }
    
    // Test 1: Check API endpoint is accessible
    async function test_01_api_accessible() {
        console.log("\n📡 Test 1: API Endpoint Accessibility");
        try {
            const response = await fetch('/api/team-statistics');
            const data = await response.json();
            
            test("API Returns Success", data.success === true, 
                `API returned success: ${data.success}`);
            
            test("API Has Statistics", Array.isArray(data.statistics), 
                `Statistics is array: ${Array.isArray(data.statistics)}`);
            
            test("API Has Overall Scores", typeof data.overall_scores === 'object', 
                `Overall scores is object: ${typeof data.overall_scores === 'object'}`);
            
            test("API Has Game Info", typeof data.game_info === 'object', 
                `Game info is object: ${typeof data.game_info === 'object'}`);
            
            return data;
        } catch (error) {
            test("API Accessible", false, `Error: ${error.message}`);
            return null;
        }
    }
    
    // Test 2: Check data contains 6 games
    async function test_02_six_games_present() {
        console.log("\n📊 Test 2: Six Games Present");
        try {
            const response = await fetch('/api/team-statistics');
            const data = await response.json();
            
            if (!data.success) {
                test("Six Games Present", false, "API did not return success");
                return;
            }
            
            const uniqueDates = new Set();
            if (data.statistics && Array.isArray(data.statistics)) {
                data.statistics.forEach(stat => {
                    uniqueDates.add(stat.date);
                });
            }
            
            const overallScoresCount = data.overall_scores ? Object.keys(data.overall_scores).length : 0;
            const gameInfoCount = data.game_info ? Object.keys(data.game_info).length : 0;
            
            test("Statistics Has Dates", uniqueDates.size > 0, 
                `Found ${uniqueDates.size} unique dates in statistics`);
            
            test("Overall Scores Has 6 Games", overallScoresCount >= 6, 
                `Found ${overallScoresCount} games in overall_scores (expected 6+)`);
            
            test("Game Info Has 6 Games", gameInfoCount >= 6, 
                `Found ${gameInfoCount} games in game_info (expected 6+)`);
            
            if (overallScoresCount > 0) {
                console.log("\n   Games found:");
                Object.keys(data.overall_scores).sort().forEach(date => {
                    const info = data.game_info[date] || {};
                    const opponent = info.opponent || 'Unknown';
                    const score = data.overall_scores[date];
                    console.log(`     • ${date} vs ${opponent}: ${score.toFixed(2)}%`);
                });
            }
            
            return {
                uniqueDates: uniqueDates.size,
                overallScoresCount,
                gameInfoCount
            };
        } catch (error) {
            test("Six Games Present", false, `Error: ${error.message}`);
            return null;
        }
    }
    
    // Test 3: Check chart element exists
    function test_03_chart_element_exists() {
        console.log("\n📈 Test 3: Chart Element Exists");
        
        const chartCanvas = document.getElementById('teamStatisticsChart');
        test("Chart Canvas Exists", chartCanvas !== null, 
            chartCanvas ? "Chart canvas found" : "Chart canvas not found");
        
        const categorySelect = document.getElementById('statisticsCategory');
        test("Category Select Exists", categorySelect !== null, 
            categorySelect ? "Category select found" : "Category select not found");
        
        const overallScoresList = document.getElementById('overallScoresList');
        test("Overall Scores List Exists", overallScoresList !== null, 
            overallScoresList ? "Overall scores list found" : "Overall scores list not found");
        
        return {
            chartCanvas: chartCanvas !== null,
            categorySelect: categorySelect !== null,
            overallScoresList: overallScoresList !== null
        };
    }
    
    // Test 4: Check Chart.js is loaded
    function test_04_chartjs_loaded() {
        console.log("\n📊 Test 4: Chart.js Library Loaded");
        
        const chartJsLoaded = typeof Chart !== 'undefined';
        test("Chart.js Loaded", chartJsLoaded, 
            chartJsLoaded ? "Chart.js is available" : "Chart.js not found");
        
        return chartJsLoaded;
    }
    
    // Test 5: Check chart instance exists
    function test_05_chart_instance_exists() {
        console.log("\n🎨 Test 5: Chart Instance Exists");
        
        // Try to find chart instance in window or global scope
        // The chart might be stored in a closure, so we check the canvas
        const chartCanvas = document.getElementById('teamStatisticsChart');
        
        if (!chartCanvas) {
            test("Chart Instance Exists", false, "Chart canvas not found");
            return false;
        }
        
        // Check if chart has been rendered (has width/height)
        const hasDimensions = chartCanvas.width > 0 && chartCanvas.height > 0;
        test("Chart Has Dimensions", hasDimensions, 
            hasDimensions ? `Chart dimensions: ${chartCanvas.width}x${chartCanvas.height}` : "Chart has no dimensions");
        
        // Check if there's a Chart.js instance (might be stored in data attribute or closure)
        const chartData = chartCanvas.getContext('2d');
        test("Chart Context Available", chartData !== null, 
            chartData ? "Chart context available" : "Chart context not available");
        
        return hasDimensions;
    }
    
    // Test 6: Check overall scores list is populated
    async function test_06_overall_scores_list_populated() {
        console.log("\n📋 Test 6: Overall Scores List Populated");
        
        const overallScoresList = document.getElementById('overallScoresList');
        if (!overallScoresList) {
            test("Overall Scores List Populated", false, "Overall scores list element not found");
            return false;
        }
        
        // Wait a bit for async loading
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const hasContent = overallScoresList.innerHTML.trim().length > 0;
        const buttonCount = overallScoresList.querySelectorAll('button').length;
        
        test("Overall Scores List Has Content", hasContent, 
            hasContent ? `List has content (${buttonCount} buttons)` : "List is empty");
        
        test("Overall Scores List Has 6 Buttons", buttonCount >= 6, 
            `Found ${buttonCount} score buttons (expected 6+)`);
        
        if (buttonCount > 0) {
            console.log("\n   Score buttons found:");
            overallScoresList.querySelectorAll('button').forEach((btn, idx) => {
                console.log(`     ${idx + 1}. ${btn.textContent.trim()}`);
            });
        }
        
        return {
            hasContent,
            buttonCount
        };
    }
    
    // Test 7: Force refresh and verify
    async function test_07_force_refresh() {
        console.log("\n🔄 Test 7: Force Refresh Functionality");
        
        try {
            const response = await fetch('/api/team-statistics?force_recalculate=true&_t=' + Date.now());
            const data = await response.json();
            
            test("Force Refresh Returns Success", data.success === true, 
                `Force refresh returned success: ${data.success}`);
            
            if (data.success) {
                const overallScoresCount = data.overall_scores ? Object.keys(data.overall_scores).length : 0;
                test("Force Refresh Has 6 Games", overallScoresCount >= 6, 
                    `Force refresh found ${overallScoresCount} games`);
                
                if (data.diagnostics) {
                    console.log("\n   Diagnostics:");
                    console.log(`     • Files found: ${data.diagnostics.files_found || 0}`);
                    console.log(`     • Files processed: ${data.diagnostics.files_processed || 0}`);
                    console.log(`     • Data points: ${data.diagnostics.data_points || 0}`);
                }
            }
            
            return data;
        } catch (error) {
            test("Force Refresh", false, `Error: ${error.message}`);
            return null;
        }
    }
    
    // Run all tests
    async function runAllTests() {
        console.log("\n🚀 Starting Frontend Display Tests...\n");
        
        await test_01_api_accessible();
        await test_02_six_games_present();
        test_03_chart_element_exists();
        test_04_chartjs_loaded();
        test_05_chart_instance_exists();
        await test_06_overall_scores_list_populated();
        await test_07_force_refresh();
        
        // Print summary
        console.log("\n" + "=".repeat(70));
        console.log("📊 TEST SUMMARY");
        console.log("=".repeat(70));
        console.log(`✅ Passed: ${tests.passed}`);
        console.log(`❌ Failed: ${tests.failed}`);
        console.log(`📈 Total: ${tests.passed + tests.failed}`);
        console.log(`📊 Success Rate: ${((tests.passed / (tests.passed + tests.failed)) * 100).toFixed(1)}%`);
        console.log("=".repeat(70));
        
        if (tests.failed === 0) {
            console.log("\n🎉 All tests passed!");
        } else {
            console.log("\n⚠️  Some tests failed. Check the output above for details.");
        }
        
        return tests;
    }
    
    // Export for manual execution
    window.runFrontendTests = runAllTests;
    
    // Auto-run if on analytics dashboard page
    if (window.location.pathname.includes('analytics-dashboard')) {
        console.log("📍 Detected analytics dashboard page. Running tests...\n");
        runAllTests();
    } else {
        console.log("ℹ️  Not on analytics dashboard page. Call runFrontendTests() manually.");
    }
})();

