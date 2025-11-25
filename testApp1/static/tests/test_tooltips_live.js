/**
 * Live Tooltip Diagnostic - Run in browser console
 * Paste this entire script into the console on /analytics-dashboard
 */

function runLiveTooltipDiagnostic() {
console.log('🔍 === TOOLTIP DIAGNOSTIC START ===');

// Test 1: Check if Chart.js is loaded
console.log('\n1️⃣ Chart.js Check:');
if (typeof Chart === 'undefined') {
    console.error('❌ Chart.js is NOT loaded!');
} else {
    console.log('✅ Chart.js loaded, version:', Chart.version);
}

// Test 2: Check if chart instance exists
console.log('\n2️⃣ Chart Instance Check:');
const chart = getChartInstance();
if (!chart) {
    console.error('❌ Chart instance NOT found!');
    console.log('Try: window.statisticsChart or check if chart is created');
} else {
    console.log('✅ Chart instance found');
    console.log('   Chart type:', chart.config.type);
    console.log('   Datasets:', chart.data.datasets.length);
    console.log('   Data points:', chart.data.labels.length);
}

// Test 3: Check tooltip configuration
console.log('\n3️⃣ Tooltip Configuration Check:');
if (chart && chart.options && chart.options.plugins && chart.options.plugins.tooltip) {
    const tooltipConfig = chart.options.plugins.tooltip;
    console.log('✅ Tooltip config exists:');
    console.log('   Enabled:', tooltipConfig.enabled);
    console.log('   Background:', tooltipConfig.backgroundColor);
    console.log('   Has title callback:', typeof tooltipConfig.callbacks?.title === 'function');
    console.log('   Has label callback:', typeof tooltipConfig.callbacks?.label === 'function');
    console.log('   Title font size:', tooltipConfig.titleFont?.size);
    console.log('   Body font size:', tooltipConfig.bodyFont?.size);
} else {
    console.error('❌ Tooltip configuration NOT found!');
}

// Test 4: Check interaction configuration
console.log('\n4️⃣ Interaction Configuration Check:');
if (chart && chart.options && chart.options.interaction) {
    console.log('✅ Interaction config:');
    console.log('   Mode:', chart.options.interaction.mode);
    console.log('   Intersect:', chart.options.interaction.intersect);
}
if (chart && chart.options && chart.options.hover) {
    console.log('✅ Hover config:');
    console.log('   Mode:', chart.options.hover.mode);
    console.log('   Intersect:', chart.options.hover.intersect);
}

// Test 5: Check canvas element
console.log('\n5️⃣ Canvas Element Check:');
const canvas = document.getElementById('teamStatisticsChart');
if (!canvas) {
    console.error('❌ Canvas element NOT found!');
} else {
    console.log('✅ Canvas found:');
    console.log('   Width:', canvas.width);
    console.log('   Height:', canvas.height);
    console.log('   Visible:', canvas.offsetParent !== null);
    console.log('   Position:', canvas.getBoundingClientRect());
}

// Test 6: Test tooltip callbacks manually
console.log('\n6️⃣ Manual Callback Test:');
if (chart && chart.data.datasets.length > 0) {
    try {
        const mockContext = [{
            dataset: chart.data.datasets[0],
            label: chart.data.labels[0],
            parsed: { y: 75.5 },
            datasetIndex: 0,
            dataIndex: 0
        }];
        
        const titleResult = chart.options.plugins.tooltip.callbacks.title(mockContext);
        const labelContext = {
            dataset: chart.data.datasets[0],
            label: chart.data.labels[0],
            parsed: { y: 75.5 },
            datasetIndex: 0,
            dataIndex: 0
        };
        const labelResult = chart.options.plugins.tooltip.callbacks.label(labelContext);
        
        console.log('✅ Callbacks work:');
        console.log('   Title output:', titleResult);
        console.log('   Label output:', labelResult);
    } catch (error) {
        console.error('❌ Callback test failed:', error);
    }
}

// Test 7: Try to manually trigger tooltip
console.log('\n7️⃣ Manual Tooltip Trigger Test:');
if (chart && canvas) {
    console.log('Attempting to trigger tooltip on first data point...');
    
    try {
        const meta = chart.getDatasetMeta(0);
        if (meta && meta.data && meta.data.length > 0) {
            const point = meta.data[0];
            const rect = canvas.getBoundingClientRect();
            
            // Simulate mousemove event
            const event = new MouseEvent('mousemove', {
                clientX: rect.left + point.x,
                clientY: rect.top + point.y,
                bubbles: true,
                cancelable: true
            });
            
            canvas.dispatchEvent(event);
            
            console.log('✅ Hover event dispatched at:', {
                x: rect.left + point.x,
                y: rect.top + point.y
            });
            console.log('   Move your mouse away and back to the chart to see if tooltip appears');
        } else {
            console.error('❌ No data points to trigger tooltip');
        }
    } catch (error) {
        console.error('❌ Failed to trigger tooltip:', error);
    }
}

// Test 8: Check for JavaScript errors
console.log('\n8️⃣ Console Errors Check:');
console.log('Check above for any JavaScript errors (red text)');
console.log('Common issues:');
console.log('   - Chart.js not loaded');
console.log('   - Canvas element missing');
console.log('   - Tooltip config overridden');
console.log('   - CSS z-index hiding tooltip');

// Test 9: Check Chart.js tooltip plugin
console.log('\n9️⃣ Tooltip Plugin Check:');
if (chart && chart.tooltip) {
    console.log('✅ Tooltip plugin exists on chart');
    console.log('   Tooltip object:', chart.tooltip);
} else {
    console.error('❌ Tooltip plugin NOT found on chart!');
}

console.log('\n🔍 === DIAGNOSTIC COMPLETE ===\n');
console.log('📝 SUMMARY:');
console.log('If tooltips still don\'t work after all tests pass:');
console.log('1. Try refreshing the page (Ctrl+F5 or Cmd+Shift+R)');
console.log('2. Clear browser cache');
console.log('3. Try a different browser');
console.log('4. Check if any browser extensions are blocking tooltips');
console.log('5. Hover SLOWLY over the chart points');
console.log('\n💡 TIP: Tooltips should appear when you hover over the colored dots on the lines\n');
}

// Auto-run on load if on analytics dashboard
if (typeof window !== 'undefined' && window.location && window.location.pathname.includes('analytics')) {
    // Wait for page to fully load
    if (document.readyState === 'complete') {
        setTimeout(runLiveTooltipDiagnostic, 3000);
    } else {
        window.addEventListener('load', () => {
            setTimeout(runLiveTooltipDiagnostic, 3000);
        });
    }
}

