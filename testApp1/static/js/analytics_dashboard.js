(function() {
  'use strict';

  const chartEl = document.getElementById('cogChart');
  if (!chartEl) return;

  const chart = echarts.init(chartEl, null, { renderer: 'canvas' });

  function setChart(labels, scores, gameResults = {}) {
    // Get accent color from current theme
    const isHeatTheme = document.body.classList.contains('theme-heat');
    const accentColor = isHeatTheme ? '#F9423A' : '#a855f7';
    const accentColorLight = isHeatTheme ? '#FF5349' : '#c084fc';
    const accentColorFaded = isHeatTheme ? 'rgba(249,66,58,0.06)' : 'rgba(168,85,247,0.06)';
    
      // Create data array with individual item styles for win/loss coloring
      const dataWithColors = scores.map((score, index) => {
        const label = labels[index];
        // Try to get date from stored points
        let dateIso = null;
        
        if (window.__cogPoints__ && window.__cogPoints__[index]) {
          const point = window.__cogPoints__[index];
          // Use date_iso if available (preferred), otherwise extract from timestamp
          if (point.date_iso) {
            dateIso = point.date_iso;
          } else if (point.timestamp) {
            const dt = new Date(point.timestamp * 1000);
            dateIso = dt.toISOString().split('T')[0]; // YYYY-MM-DD
          }
        }
      
      // Determine color based on win/loss
      let pointColor = accentColor;  // Default
      let borderColor = accentColorLight;
      
      if (dateIso && gameResults[dateIso]) {
        if (gameResults[dateIso] === 'win') {
          pointColor = '#00ff00';  // Green for win
          borderColor = '#00cc00';
        } else if (gameResults[dateIso] === 'loss') {
          pointColor = '#F9423A';  // Red for loss
          borderColor = '#FF5349';
        }
      }
      
      return {
        value: score,
        itemStyle: {
          color: pointColor,
          borderColor: borderColor,
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: pointColor
        }
      };
    });
    
    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0, 0, 0, 0.9)',
        borderColor: accentColor,
        borderWidth: 2,
        textStyle: {
          color: '#fff',
          fontSize: 14
        },
        formatter: function(params) {
          const param = params[0];
          const index = param.dataIndex;
          let resultText = '';
          
          // Try to get win/loss info
          if (window.__cogPoints__ && window.__cogPoints__[index]) {
            const point = window.__cogPoints__[index];
            let dateIso = null;
            // Use date_iso if available (preferred), otherwise extract from timestamp
            if (point.date_iso) {
              dateIso = point.date_iso;
            } else if (point.timestamp) {
              const dt = new Date(point.timestamp * 1000);
              dateIso = dt.toISOString().split('T')[0];
            }
            
            if (dateIso && gameResults[dateIso]) {
              const result = gameResults[dateIso];
              resultText = result === 'win' 
                ? '<div style="color: #00ff00; font-weight: 600; margin-top: 4px;">✓ WIN</div>'
                : '<div style="color: #F9423A; font-weight: 600; margin-top: 4px;">✗ LOSS</div>';
            }
          }
          
          return `
            <div style="padding: 8px;">
              <div style="font-weight: 700; font-size: 16px; color: ${accentColor}; margin-bottom: 8px;">
                ${param.name}
              </div>
              <div style="font-size: 24px; font-weight: 800; color: ${accentColor}; text-shadow: 0 0 10px ${accentColor};">
                ${param.value}%
              </div>
              <div style="margin-top: 6px; font-size: 12px; color: rgba(255,255,255,0.7);">
                Cognitive Score
              </div>
              ${resultText}
            </div>
          `;
        }
      },
      grid: { left: 40, right: 20, top: 30, bottom: 40 },
      // Ensure programmatic dataZoom exists for slider control
      dataZoom: [
        { type: 'slider', show: false, start: 0, end: 100, xAxisIndex: 0 }
      ],
      xAxis: {
        type: 'category',
        data: labels,
        axisLine: { lineStyle: { color: accentColor } },
        axisLabel: { color: '#F5F5F5' }
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100,
        axisLine: { lineStyle: { color: accentColor } },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
        axisLabel: { 
          color: '#F5F5F5',
          formatter: '{value}%'
        }
      },
      series: [{
        type: 'line',
        data: dataWithColors,  // Use data array with individual colors
        smooth: true,
        symbol: 'circle',
        symbolSize: 10,
        lineStyle: { color: accentColor, width: 3 },
        emphasis: {
          itemStyle: {
            symbolSize: 16,
            borderWidth: 3,
            shadowBlur: 20
          }
        },
        areaStyle: { color: accentColorFaded }
      }]
    };
    chart.setOption(option);

    // Initialize slider after first chart paint
    const container = document.getElementById('vizPrecisionSlider');
    if (container && window.IntegrityHoopsSlider && !container.dataset.bound) {
      const initialPrecision = parseInt(localStorage.getItem('analyticsPrecision') || '40', 10);
      window.IntegrityHoopsSlider.create({
        chart,
        container,
        initialPrecision,
        anchor: 'end'
      });
      container.dataset.bound = '1';
    }
  }

  async function loadTeamSeries() {
    const res = await fetch('/api/cog-scores?level=team&team=Heat');
    const json = await res.json();
    if (!json.success) return;
    const labels = json.points.map(p => p.label);
    const scores = json.points.map(p => p.score);
    const gameResults = json.game_results || {};  // Get win/loss data
    // stash ids for click deletion
    window.__cogPoints__ = json.points;
    setChart(labels, scores, gameResults);
  }

  function toEpoch(dateStr) {
    // dateStr in YYYY-MM-DD
    const d = new Date(dateStr + 'T00:00:00');
    return Math.floor(d.getTime() / 1000);
  }

  // Delete point on click (team series for now)
  chart.on('click', async function (params) {
    try {
      if (!window.__cogPoints__) return;
      const idx = params.dataIndex;
      const point = window.__cogPoints__[idx];
      if (!point) return;
      const isHeatTheme = document.body.classList.contains('theme-heat');
      const accent = isHeatTheme ? '#F9423A' : '#a855f7';
      const scoreFormatted = typeof point.score === 'number' ? point.score.toFixed(5) : point.score;
      const label = point.label + ' → ' + scoreFormatted + '%';
      const ok = window.confirm('Delete point\n' + label + ' ?');
      if (!ok) return;
      // Team delete for now
      const del = await fetch('/api/cog-scores/team/' + point.id, { method: 'DELETE' });
      const resp = await del.json();
      if (resp && resp.success) {
        await loadTeamSeries();
      } else {
        alert('Failed to delete point');
      }
    } catch (e) {
      // swallow
    }
  });

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return res.json();
  }

  // Team form
  const teamSubmit = document.getElementById('teamSubmit');
  if (teamSubmit) {
    teamSubmit.addEventListener('click', async () => {
      const date = document.getElementById('teamDate').value;
      const score = parseInt(document.getElementById('teamScore').value, 10);
      const team = document.getElementById('teamName').value.trim();
      const opponent = document.getElementById('teamOpponent').value.trim();
      const note = document.getElementById('teamNote').value.trim();
      if (!date || isNaN(score) || !team || !opponent) return;
      const resp = await postJSON('/api/cog-scores/team', {
        game_date: toEpoch(date), team, opponent, score, note
      });
      if (resp.success) {
        // refresh chart
        await loadTeamSeries();
        // close modal
        document.querySelector('#teamModal .btn-close')?.click();
      }
    });
  }

  // Player form
  const playerSubmit = document.getElementById('playerSubmit');
  if (playerSubmit) {
    playerSubmit.addEventListener('click', async () => {
      const date = document.getElementById('playerDate').value;
      const score = parseInt(document.getElementById('playerScore').value, 10);
      const player_name = document.getElementById('playerName').value.trim();
      const team = document.getElementById('playerTeam').value.trim();
      const opponent = document.getElementById('playerOpponent').value.trim();
      const note = document.getElementById('playerNote').value.trim();
      if (!date || isNaN(score) || !player_name) return;
      const resp = await postJSON('/api/cog-scores/player', {
        game_date: toEpoch(date), player_name, team, opponent, score, note
      });
      if (resp.success) {
        // For now, keep team series; future: toggle to player series
        await loadTeamSeries();
        document.querySelector('#playerModal .btn-close')?.click();
      }
    });
  }

  // 2K/Madden Style Score Reveal Animation
  function showScoreReveal(data) {
    const modal = new bootstrap.Modal(document.getElementById('scoreRevealModal'));
    
    // Extract game info
    const gameName = data.metadata.game || 'Game';
    const gameDate = data.metadata.game_date || '';
    const score = Math.round(data.overall_score);
    
    console.log('=== Score Reveal Data ===');
    console.log('Game Name:', gameName);
    console.log('Game Date:', gameDate);
    console.log('Score:', score);
    console.log('Full Data:', data);
    
    // Calculate totals
    let totalPositives = 0;
    let totalNegatives = 0;
    for (const skill in data.breakdown) {
      totalPositives += data.breakdown[skill].positive;
      totalNegatives += data.breakdown[skill].negative;
    }
    const totalPlays = totalPositives + totalNegatives;
    
    // Set initial values
    document.getElementById('revealGameTitle').textContent = gameName.toUpperCase();
    document.getElementById('revealGameDate').textContent = gameDate;
    document.getElementById('revealScoreValue').textContent = '0';
    document.getElementById('revealScoreBar').style.width = '0%';
    document.getElementById('revealPositives').textContent = '0';
    document.getElementById('revealNegatives').textContent = '0';
    document.getElementById('revealTotal').textContent = '0';
    
    // Determine rank based on score
    let rank = 'NEEDS IMPROVEMENT';
    if (score >= 90) rank = '🔥 LEGENDARY 🔥';
    else if (score >= 80) rank = '⭐ ELITE PERFORMANCE ⭐';
    else if (score >= 70) rank = 'GREAT EXECUTION';
    else if (score >= 50) rank = 'AVERAGE';
    
    document.getElementById('revealRank').textContent = rank;
    
    // Show modal
    modal.show();
    
    // Animate after modal is shown
    setTimeout(() => {
      // Animate score counter
      animateValue('revealScoreValue', 0, score, 2000);
      
      // Animate progress bar
      document.getElementById('revealScoreBar').style.width = score + '%';
      
      // Animate stats with delay
      setTimeout(() => {
        animateValue('revealPositives', 0, totalPositives, 1500);
        animateValue('revealNegatives', 0, totalNegatives, 1500);
        animateValue('revealTotal', 0, totalPlays, 1500);
      }, 500);
    }, 300);
    
    // Fix close button - remove any previous handlers and add new one
    const closeBtn = document.getElementById('scoreRevealCloseBtn');
    if (closeBtn) {
      const newCloseBtn = closeBtn.cloneNode(true);
      closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
      
      newCloseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Close button clicked');
        modal.hide();
      });
    }
    
    // Pre-fill input form with auto-extracted values
    // Parse date from game name with improved logic
    let suggestedDate = new Date(); // default to today
    
    // Try multiple date formats
    // Format 1: MM.DD.YY (e.g., "10.06.25")
    const dateMatch1 = gameName.match(/(\d{2})\.(\d{2})\.(\d{2})/);
    // Format 2: MM-DD-YY
    const dateMatch2 = gameName.match(/(\d{2})-(\d{2})-(\d{2})/);
    // Format 3: YYYY-MM-DD
    const dateMatch3 = gameName.match(/(\d{4})-(\d{2})-(\d{2})/);
    
    if (dateMatch1) {
      const [_, month, day, year] = dateMatch1;
      const fullYear = 2000 + parseInt(year, 10);
      suggestedDate = new Date(fullYear, parseInt(month, 10) - 1, parseInt(day, 10));
      console.log(`Auto-extracted date (MM.DD.YY): ${month}.${day}.${year}`);
    } else if (dateMatch2) {
      const [_, month, day, year] = dateMatch2;
      const fullYear = 2000 + parseInt(year, 10);
      suggestedDate = new Date(fullYear, parseInt(month, 10) - 1, parseInt(day, 10));
      console.log(`Auto-extracted date (MM-DD-YY): ${month}-${day}-${year}`);
    } else if (dateMatch3) {
      const [_, year, month, day] = dateMatch3;
      suggestedDate = new Date(parseInt(year, 10), parseInt(month, 10) - 1, parseInt(day, 10));
      console.log(`Auto-extracted date (YYYY-MM-DD): ${year}-${month}-${day}`);
    } else {
      console.warn('Could not parse date from game name, using today');
    }
    
    // Extract team and opponent from game name with improved regex
    let suggestedTeam = 'Heat';
    let suggestedOpponent = 'Unknown';
    
    // Try multiple patterns:
    // Pattern 1: "Heat v Bucks" or "Heat vs Bucks"
    const vsMatch1 = gameName.match(/([A-Za-z]+)\s+v(?:s)?\s+([A-Za-z]+)/i);
    // Pattern 2: "Heat @ Bucks" or "Heat at Bucks"
    const vsMatch2 = gameName.match(/([A-Za-z]+)\s+(?:@|at)\s+([A-Za-z]+)/i);
    
    if (vsMatch1) {
      suggestedTeam = vsMatch1[1];
      suggestedOpponent = vsMatch1[2];
      console.log(`Auto-extracted teams: ${suggestedTeam} vs ${suggestedOpponent}`);
    } else if (vsMatch2) {
      suggestedTeam = vsMatch2[1];
      suggestedOpponent = vsMatch2[2];
      console.log(`Auto-extracted teams: ${suggestedTeam} vs ${suggestedOpponent}`);
    } else {
      console.warn('Could not extract teams from game name');
    }
    
    // Format date as YYYY-MM-DD for input field
    const dateStr = suggestedDate.toISOString().split('T')[0];
    
    // Pre-fill the input fields
    document.getElementById('revealDateInput').value = dateStr;
    document.getElementById('revealTeamInput').value = suggestedTeam;
    document.getElementById('revealOpponentInput').value = suggestedOpponent;
    
    // Add Cog Score button handler - now shows form first, then saves
    const addBtn = document.getElementById('addToDashboardBtn');
    if (!addBtn) {
      console.error('Add to Dashboard button not found!');
      return;
    }
    
    // Clone and replace to remove all previous event listeners
    const newAddBtn = addBtn.cloneNode(true);
    addBtn.parentNode.replaceChild(newAddBtn, addBtn);
    
    let formShown = false;
    
    newAddBtn.addEventListener('click', async () => {
      // First click: show the form for manual input
      if (!formShown) {
        document.getElementById('revealInputForm').style.display = 'block';
        newAddBtn.innerHTML = '<i class="fas fa-save"></i> Save to Dashboard';
        formShown = true;
        console.log('Input form displayed - verify and click Save');
        return;
      }
      
      // Second click: save with manual input values
      console.log('=== Save to Dashboard Clicked ===');
      
      // Get manual input values
      const dateInput = document.getElementById('revealDateInput').value;
      const teamInput = document.getElementById('revealTeamInput').value.trim();
      const opponentInput = document.getElementById('revealOpponentInput').value.trim();
      
      // Validate inputs
      if (!dateInput || !teamInput || !opponentInput) {
        alert('Please fill in all fields (Date, Team, Opponent)');
        return;
      }
      
      // Convert date to epoch timestamp
      const gameDate = new Date(dateInput + 'T00:00:00');
      const gameTimestamp = Math.floor(gameDate.getTime() / 1000);
      
      const csvFile = data.metadata.csv_file || 'Unknown file';
      const note = `CSV Upload - ${csvFile}`;
      
      const payload = {
        game_date: gameTimestamp,
        team: teamInput,
        opponent: opponentInput,
        score: score,
        source: 'CSV Upload',
        note: note
      };
      
      console.log('=== Sending to API ===');
      console.log('Manual Input - Date:', dateInput, '-> Timestamp:', gameTimestamp);
      console.log('Manual Input - Team:', teamInput);
      console.log('Manual Input - Opponent:', opponentInput);
      console.log('Payload:', payload);
      
      // Disable button while processing
      newAddBtn.disabled = true;
      newAddBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
      
      try {
        // Use same postJSON helper as manual forms
        const resp = await postJSON('/api/cog-scores/team', payload);
        
        console.log('=== API Response ===');
        console.log('Response:', resp);
        
        if (resp && resp.success) {
          console.log('✅ Score saved successfully!');
          
          // Refresh chart using same method as manual forms
          await loadTeamSeries();
          console.log('Chart refreshed');
          
          // Refresh the scores list table
          if (window.refreshScoresList) {
            await window.refreshScoresList();
            console.log('Scores list refreshed');
          }
          
          // Close modal
          modal.hide();
          
          // Show success message
          alert('✅ Score added to dashboard successfully!');
        } else {
          const errorMsg = resp?.error || 'Unknown error - check console for details';
          console.error('❌ API returned error:', errorMsg);
          alert('Error adding score: ' + errorMsg);
          // Re-enable button
          newAddBtn.disabled = false;
          newAddBtn.innerHTML = '<i class="fas fa-save"></i> Save to Dashboard';
        }
      } catch (error) {
        console.error('❌ Exception during save:', error);
        alert('Failed to add score to dashboard. Check console for details.');
        // Re-enable button
        newAddBtn.disabled = false;
        newAddBtn.innerHTML = '<i class="fas fa-save"></i> Save to Dashboard';
      }
    });
  }

  // Animate number counting up
  function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    const range = end - start;
    const increment = range / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
        current = end;
        clearInterval(timer);
      }
      element.textContent = Math.round(current);
    }, 16);
  }

  // Initial load with seeded Heat data
  loadTeamSeries();
  
  // Load scores list
  refreshScoresList();
  
  // Trigger team statistics API call to ensure sync runs (this will sync overall scores to analytics dashboard)
  // This ensures games from team statistics are available in the main analytics chart
  fetch('/api/team-statistics?use_database=true&force_recalculate=false')
    .then(res => res.json())
    .then(data => {
      if (data.success && data.overall_scores) {
        console.log('Team statistics loaded, sync should have run. Games available:', Object.keys(data.overall_scores).length);
        // Reload the analytics chart to show newly synced games
        loadTeamSeries();
      }
    })
    .catch(err => {
      console.error('Error triggering team statistics sync:', err);
    });
})();

// Refresh scores list (global function)
async function refreshScoresList() {
  try {
    const res = await fetch('/api/cog-scores?level=team&team=Heat');
    const json = await res.json();
    
    if (!json.success || !json.points) {
      document.getElementById('scoresTableBody').innerHTML = '<tr><td colspan="5" class="text-center">Error loading scores</td></tr>';
      return;
    }
    
    const tbody = document.getElementById('scoresTableBody');
    
    if (json.points.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center">No scores yet</td></tr>';
      return;
    }
    
    tbody.innerHTML = json.points.map(point => {
      const date = new Date(point.timestamp * 1000).toLocaleDateString();
      const scoreFormatted = typeof point.score === 'number' ? point.score.toFixed(5) : point.score;
      return `
        <tr>
          <td>${point.date}</td>
          <td>${point.label}</td>
          <td><strong style="color: #F9423A;">${scoreFormatted}%</strong></td>
          <td><span class="badge bg-secondary">${point.source || 'Manual'}</span></td>
          <td>
            <button class="btn btn-sm btn-danger" onclick="deleteScoreFromList(${point.id})">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>
      `;
    }).join('');
    
  } catch (e) {
    console.error('Error loading scores list:', e);
    document.getElementById('scoresTableBody').innerHTML = '<tr><td colspan="5" class="text-center">Error loading scores</td></tr>';
  }
}

// Delete score from list
async function deleteScoreFromList(scoreId) {
  if (!confirm('Delete this score?')) return;
  
  try {
    const res = await fetch(`/api/cog-scores/team/${scoreId}`, { method: 'DELETE' });
    const json = await res.json();
    
    if (json.success) {
      await refreshScoresList();
      // Reload the chart by calling the IIFE function's loadTeamSeries
      // Since loadTeamSeries is defined inside the IIFE, we need to reload the page or expose it
      location.reload();
    } else {
      alert('Failed to delete score');
    }
  } catch (e) {
    console.error('Error deleting score:', e);
    alert('Failed to delete score');
  }
}

// Team Statistics Chart
(function() {
  'use strict';
  
  const chartCanvas = document.getElementById('teamStatisticsChart');
  const categorySelect = document.getElementById('statisticsCategory');
  
  if (!chartCanvas || !categorySelect) return;
  
  let statisticsChart = null;
  let mousemoveHandler = null;
  let mouseleaveHandler = null;
  let chartZoomedOut = false; // Track zoom state
  
  // Category colors - High contrast palette for better visibility
  const categoryColors = {
    'Cutting & Screening': '#FF1744',      // Bright red
    'DM Catch': '#00E5FF',                  // Bright cyan
    'Finishing': '#FFD700',                 // Gold
    'Footwork': '#00FF88',                  // Bright green
    'Passing': '#FF6B00',                   // Bright orange
    'Positioning': '#9C27B0',               // Bright purple
    'QB12 DM': '#FF00FF',                   // Magenta
    'Relocation': '#00BCD4',                // Cyan-blue
    'Space Read': '#FF9800',                 // Orange
    'Transition': '#2196F3'                 // Bright blue
  };
  
  async function loadTeamStatistics(category = '', forceRefresh = false) {
    try {
      // Add timestamp to prevent caching, and force_recalculate if needed
      const timestamp = new Date().getTime();
      const forceParam = forceRefresh ? '&force_recalculate=true' : '';
      const url = category 
        ? `/api/team-statistics?category=${encodeURIComponent(category)}&_t=${timestamp}${forceParam}`
        : `/api/team-statistics?_t=${timestamp}${forceParam}`;
      
      console.log('Loading team statistics from:', url);
      const response = await fetch(url);
      const data = await response.json();
      
      console.log('API Response:', data);
      console.log('Overall scores from API:', data.overall_scores);
      console.log('Game info from API:', data.game_info);
      
      // Remove any existing error messages
      if (chartCanvas && chartCanvas.parentElement) {
        const existingErrors = chartCanvas.parentElement.querySelectorAll('.chart-error-message');
        existingErrors.forEach(err => err.remove());
      }
      
      // Check for API errors
      if (!data.success) {
        console.error('Failed to load statistics:', data.error);
        if (chartCanvas && chartCanvas.parentElement) {
          const errorMsg = document.createElement('div');
          errorMsg.className = 'chart-error-message alert alert-danger';
          errorMsg.style.cssText = 'background: rgba(249,66,58,0.2); border: 1px solid rgba(249,66,58,0.5); color: #fff; padding: 15px; margin: 10px 0;';
          errorMsg.textContent = `Error loading statistics: ${data.error || 'Unknown error'}`;
          chartCanvas.parentElement.insertBefore(errorMsg, chartCanvas);
        }
        return;
      }
      
      // Check for warnings (files processed but no data)
      if (data.warning) {
        console.warn('Team statistics warning:', data.warning);
        if (chartCanvas && chartCanvas.parentElement) {
          const warningMsg = document.createElement('div');
          warningMsg.className = 'chart-error-message alert alert-warning';
          warningMsg.style.cssText = 'background: rgba(249,66,58,0.1); border: 1px solid rgba(249,66,58,0.3); color: #fff; padding: 15px; margin: 10px 0;';
          warningMsg.innerHTML = `<strong>Warning:</strong> ${data.warning}<br>`;
          if (data.diagnostics && data.diagnostics.errors && data.diagnostics.errors.length > 0) {
            warningMsg.innerHTML += '<small>Errors: ' + data.diagnostics.errors.join('; ') + '</small>';
          }
          chartCanvas.parentElement.insertBefore(warningMsg, chartCanvas);
        }
      }
      
      // Log diagnostics if available
      if (data.diagnostics) {
        console.log('Team statistics diagnostics:', data.diagnostics);
      }
      
      // Log unique games count
      if (data.overall_scores) {
        const uniqueGames = Object.keys(data.overall_scores).length;
        console.log(`📊 Found ${uniqueGames} unique games in overall_scores:`, Object.keys(data.overall_scores));
        if (uniqueGames !== 6) {
          console.warn(`⚠️ Expected 6 games but found ${uniqueGames}. Games:`, Object.keys(data.overall_scores));
        } else {
          console.log('✅ All 6 games found!');
        }
      }
      
      // Check if we have statistics data
      if (!data.statistics || data.statistics.length === 0) {
        console.warn('No statistics data available');
        if (chartCanvas && chartCanvas.parentElement) {
          const errorMsg = document.createElement('div');
          errorMsg.className = 'chart-error-message alert alert-warning';
          errorMsg.style.cssText = 'background: rgba(249,66,58,0.1); border: 1px solid rgba(249,66,58,0.3); color: #fff; padding: 15px; margin: 10px 0;';
          let msg = 'No statistics data available. ';
          if (data.diagnostics) {
            msg += `Found ${data.diagnostics.files_found} CSV files, processed ${data.diagnostics.files_processed}. `;
          }
          msg += 'Please check that CSV files contain the expected cognitive performance columns.';
          errorMsg.textContent = msg;
          chartCanvas.parentElement.insertBefore(errorMsg, chartCanvas);
        }
        return;
      }
      
      // Update chart
      try {
      updateStatisticsChart(
        data.statistics,
        category,
        data.overall_scores || {},
        data.game_info || {},
        data.game_results || {}  // Add game results (win/loss)
      );

        // Update overall scores list under the chart (pass chart instance for toggle functionality)
        updateOverallScoresList(data.overall_scores || {}, data.game_info || {}, statisticsChart);
      } catch (chartError) {
        console.error('Error updating chart:', chartError);
        if (chartCanvas && chartCanvas.parentElement) {
          const existingErrors = chartCanvas.parentElement.querySelectorAll('.chart-error-message');
          existingErrors.forEach(err => err.remove());
          
          const errorMsg = document.createElement('div');
          errorMsg.className = 'chart-error-message alert alert-danger';
          errorMsg.style.cssText = 'background: rgba(249,66,58,0.2); border: 1px solid rgba(249,66,58,0.5); color: #fff; padding: 15px; margin: 10px 0;';
          errorMsg.textContent = 'Error generating chart. Please refresh the page and try again.';
          chartCanvas.parentElement.insertBefore(errorMsg, chartCanvas);
        }
      }
    } catch (error) {
      console.error('Error loading team statistics:', error);
      if (chartCanvas && chartCanvas.parentElement) {
        const existingErrors = chartCanvas.parentElement.querySelectorAll('.chart-error-message');
        existingErrors.forEach(err => err.remove());
        
        const errorMsg = document.createElement('div');
        errorMsg.className = 'chart-error-message alert alert-danger';
        errorMsg.style.cssText = 'background: rgba(249,66,58,0.2); border: 1px solid rgba(249,66,58,0.5); color: #fff; padding: 15px; margin: 10px 0;';
        errorMsg.textContent = 'Error loading statistics. Please refresh the page and try again.';
        chartCanvas.parentElement.insertBefore(errorMsg, chartCanvas);
      }
    }
  }

  // Render overall cognitive scores list beneath the chart
  function updateOverallScoresList(overallScores = {}, gameInfo = {}, chartInstance = null) {
    console.log('updateOverallScoresList called with:', { overallScores, gameInfo, chartInstance });
    const container = document.getElementById('overallScoresList');
    console.log('Overall scores container found:', container);
    if (!container) {
      console.error('overallScoresList container not found!');
      return;
    }

    const entries = Object.keys(overallScores)
      .sort() // sort by ISO date
      .map(dateIso => {
        const score = overallScores[dateIso];
        const info = gameInfo[dateIso] || {};
        const dateLabel = (info.date_string ? info.date_string.replace(/\./g, '/') : dateIso);
        const opponent = info.opponent ? ` vs ${info.opponent}` : '';
        return { dateIso, dateLabel, opponent, score };
      });

    if (entries.length === 0) {
      container.innerHTML = '';
      return;
    }

    // Build interactive, button-like badges with toggle state
    const html = [
      '<div class="d-flex flex-wrap gap-2 align-items-center mb-2">',
      '<span style="color:#F9423A; font-weight:700; margin-right:6px;">Overall Cog Scores:</span>'
    ];
    entries.forEach(({ dateIso, dateLabel, opponent, score }) => {
      const label = `${dateLabel}${opponent}: ${score.toFixed(5)}%`;
      html.push(
        `<button type="button" class="ih-score-toggle" data-date="${dateIso}" style="
            cursor:pointer; background:#111; color:#fff; padding:8px 10px; border-radius:8px;
            border:1px solid rgba(249,66,58,0.3); transition:all .15s ease;">
            ${label}
         </button>`
      );
    });
    html.push('</div>');

    container.innerHTML = html.join('');

    // Attach click handlers to toggle overall scores dataset on chart
    const buttons = container.querySelectorAll('.ih-score-toggle');
    buttons.forEach(btn => {
      btn.addEventListener('click', function() {
        if (!chartInstance || !statisticsChart) return;
        
        // Find the overall scores dataset index
        const overallDatasetIndex = statisticsChart.data.datasets.findIndex(ds => ds.label === 'Overall Cog Score');
        if (overallDatasetIndex === -1) return;
        
        // Toggle the dataset visibility
        const meta = statisticsChart.getDatasetMeta(overallDatasetIndex);
        if (meta) {
          const isCurrentlyHidden = meta.hidden === true;
          meta.hidden = !isCurrentlyHidden;
          statisticsChart.update();
          
          // Update button visual state
          if (isCurrentlyHidden) {
            // Show - turn ON neon
          this.setAttribute('data-active', '1');
          this.style.boxShadow = '0 0 12px rgba(249,66,58,0.9), 0 0 24px rgba(249,66,58,0.5)';
          this.style.borderColor = '#F9423A';
          this.style.color = '#FCEAE9';
          } else {
            // Hide - turn OFF neon
            this.setAttribute('data-active', '0');
            this.style.boxShadow = 'none';
            this.style.borderColor = 'rgba(249,66,58,0.3)';
            this.style.color = '#fff';
          }
        }
      });
    });
    
    // Initialize button states based on chart visibility
    if (statisticsChart && buttons.length > 0) {
      const overallDatasetIndex = statisticsChart.data.datasets.findIndex(ds => ds.label === 'Overall Cog Score');
      if (overallDatasetIndex !== -1) {
        const meta = statisticsChart.getDatasetMeta(overallDatasetIndex);
        const isHidden = meta && meta.hidden === true;
        buttons.forEach(btn => {
          if (!isHidden) {
            btn.setAttribute('data-active', '1');
            btn.style.boxShadow = '0 0 12px rgba(249,66,58,0.9), 0 0 24px rgba(249,66,58,0.5)';
            btn.style.borderColor = '#F9423A';
            btn.style.color = '#FCEAE9';
          }
        });
      }
    }
  }
  
  // Render custom toggle buttons for chart datasets
  function renderCategoryToggleButtons(chartInstance) {
    // Check if chartInstance exists
    if (!chartInstance) {
      console.warn('renderCategoryToggleButtons: chartInstance is null');
      return;
    }
    
    // Get container
    const container = document.getElementById('statisticsDatasetToggles');
    if (!container) {
      console.warn('renderCategoryToggleButtons: container not found');
      return;
    }
    
    // Check if datasets exist
    if (!chartInstance.data || !chartInstance.data.datasets || chartInstance.data.datasets.length === 0) {
      console.warn('renderCategoryToggleButtons: no datasets found');
      return;
    }
    
    console.log('renderCategoryToggleButtons: rendering buttons for', chartInstance.data.datasets.length, 'datasets');
    
    // Clear existing content
    container.innerHTML = '';
    
    // Iterate through datasets
    chartInstance.data.datasets.forEach((dataset, index) => {
      try {
        // Get visibility state
        const meta = chartInstance.getDatasetMeta(index);
        const isVisible = meta.hidden !== true;
      
      // Get color
      const color = dataset.borderColor || '#CCCCCC';
      
      // Check theme
      const isHeatTheme = document.body.classList.contains('theme-heat');
      
      // Create button element
      const button = document.createElement('button');
      button.className = 'btn btn-sm';
      button.setAttribute('data-dataset-index', index);
      
      // Set button styles based on visibility state
      const borderColor = isVisible 
        ? (isHeatTheme ? '#F9423A' : 'rgba(168, 85, 247, 0.8)')
        : 'rgba(255,255,255,0.3)';
      const borderWidth = isVisible ? '2px' : '1px';
      const opacity = isVisible ? '1' : '0.4';
      
      button.style.cssText = `
        background: rgba(0,0,0,0.8);
        color: #fff;
        border: ${borderWidth} solid ${borderColor};
        opacity: ${opacity};
        margin: 4px;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
      `;
      
      // Add color indicator span
      const colorIndicator = document.createElement('span');
      colorIndicator.style.cssText = `
        display: inline-block;
        width: 12px;
        height: 12px;
        background: ${color};
        border-radius: 2px;
        margin-right: 6px;
        vertical-align: middle;
      `;
      button.appendChild(colorIndicator);
      
      // Add label text
      const label = document.createTextNode(dataset.label);
      button.appendChild(label);
      
      // Add click handler
      button.addEventListener('click', function() {
        const idx = parseInt(this.getAttribute('data-dataset-index'));
        if (isNaN(idx)) {
          console.warn('Toggle button missing dataset index');
          return;
        }
        
        // Prefer the global toggleChartLine helper so checkbox/menu state stays in sync
        const currentlyVisible = chartInstance.isDatasetVisible(idx);
        const nextVisible = !currentlyVisible;
        
        if (typeof toggleChartLine === 'function') {
          toggleChartLine(idx, nextVisible);
        } else {
          chartInstance.setDatasetVisibility(idx, nextVisible);
        chartInstance.update('none');
        }
        
        // Re-render buttons to refresh styles and order
        renderCategoryToggleButtons(chartInstance);
      });
      
      // Add hover effect
      button.addEventListener('mouseenter', function() {
        this.style.opacity = '0.8';
        this.style.transform = 'scale(1.05)';
      });
      
      button.addEventListener('mouseleave', function() {
        const idx = parseInt(this.getAttribute('data-dataset-index'));
        const meta = chartInstance.getDatasetMeta(idx);
        const isVisible = meta.hidden !== true;
        this.style.opacity = isVisible ? '1' : '0.4';
        this.style.transform = 'scale(1)';
      });
      
      // Append button to container
      container.appendChild(button);
      } catch (error) {
        console.error('Error creating button for dataset', index, ':', error);
      }
    });
    
    console.log('renderCategoryToggleButtons: created', container.children.length, 'buttons');
  }
  
  // Watchdog timer to monitor and reset toggle buttons if they're not working
  let toggleWatchdogTimer = null;
  let lastToggleCheck = Date.now();
  
  function initToggleWatchdog() {
    // Clear existing timer if any
    if (toggleWatchdogTimer) {
      clearInterval(toggleWatchdogTimer);
    }
    
    console.log('Toggle Watchdog: Started - checking every 60 seconds');
    
    // Check every 60 seconds (1 minute)
    toggleWatchdogTimer = setInterval(() => {
      try {
        console.log('Toggle Watchdog: Running health check...');
        
        // Check if toggle container exists
        const container = document.getElementById('statisticsDatasetToggles');
        if (!container) {
          console.warn('Toggle Watchdog: Container not found, skipping check');
          return;
        }
        
        // Check if statisticsChart exists
        if (!statisticsChart) {
          console.warn('Toggle Watchdog: Chart not initialized, skipping check');
          return;
        }
        
        // Check if chart has datasets
        if (!statisticsChart.data || !statisticsChart.data.datasets || statisticsChart.data.datasets.length === 0) {
          console.warn('Toggle Watchdog: No datasets found, skipping check');
          return;
        }
        
        // Check if toggle buttons exist
        const buttons = container.querySelectorAll('button[data-dataset-index]');
        const expectedButtons = statisticsChart.data.datasets.length;
        
        console.log(`Toggle Watchdog: Found ${buttons.length} buttons, expected ${expectedButtons}`);
        
        // If buttons don't match datasets, re-render
        if (buttons.length !== expectedButtons) {
          console.warn('Toggle Watchdog: Button count mismatch - re-rendering toggles');
          renderCategoryToggleButtons(statisticsChart);
          return;
        }
        
        // Check if buttons are functional by testing click event listeners
        let workingButtons = 0;
        buttons.forEach((button, index) => {
          // Check if button has click listener by checking if it has the data attribute
          if (button.hasAttribute('data-dataset-index')) {
            workingButtons++;
          }
        });
        
        console.log(`Toggle Watchdog: ${workingButtons}/${buttons.length} buttons appear functional`);
        
        // If less than 50% of buttons are working, re-render
        if (workingButtons < buttons.length * 0.5) {
          console.warn('Toggle Watchdog: Less than 50% of buttons functional - re-rendering toggles');
          renderCategoryToggleButtons(statisticsChart);
          return;
        }
        
        // Check if buttons are visible
        if (container.offsetParent === null) {
          console.warn('Toggle Watchdog: Container is hidden');
        }
        
        // All checks passed
        console.log('Toggle Watchdog: All checks passed - toggles are healthy');
        lastToggleCheck = Date.now();
        
      } catch (error) {
        console.error('Toggle Watchdog: Error during health check:', error);
        // Try to re-render on error
        try {
          if (statisticsChart) {
            renderCategoryToggleButtons(statisticsChart);
          }
        } catch (renderError) {
          console.error('Toggle Watchdog: Failed to re-render toggles:', renderError);
        }
      }
    }, 60000); // Check every 60 seconds
    
    // Also add a manual reset function to window
    window.resetToggleButtons = function() {
      console.log('Manual toggle reset requested');
      if (statisticsChart) {
        renderCategoryToggleButtons(statisticsChart);
        console.log('Toggle buttons manually reset');
      } else {
        console.warn('Cannot reset toggles: chart not initialized');
      }
    };
  }
  
  // Force re-render toggles function that can be called anytime
  window.forceReinitToggleButtons = function() {
    console.log('🔧 Force re-initializing toggle buttons...');
    
    const container = document.getElementById('statisticsDatasetToggles');
    if (!container) {
      console.error('❌ Toggle container not found');
      return false;
    }
    
    if (!statisticsChart) {
      console.error('❌ Chart not initialized');
      return false;
    }
    
    // Clear container
    container.innerHTML = '';
    
    // Re-render
    renderCategoryToggleButtons(statisticsChart);
    
    console.log('✅ Toggle buttons force re-initialized');
    return true;
  };
  
  // Start watchdog when page loads
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        initToggleWatchdog();
        // Force check after 2 seconds
        setTimeout(() => {
          console.log('🔄 Running initial toggle check...');
          if (statisticsChart) {
            renderCategoryToggleButtons(statisticsChart);
          }
        }, 2000);
      });
    } else {
      initToggleWatchdog();
      // Force check immediately
      setTimeout(() => {
        console.log('🔄 Running initial toggle check...');
        if (statisticsChart) {
          renderCategoryToggleButtons(statisticsChart);
        }
      }, 2000);
    }
  }
  
  function updateStatisticsChart(statistics, category, overallScores = {}, gameInfo = {}, gameResults = {}) {
    const ctx = chartCanvas.getContext('2d');
    const overlay = document.getElementById('categoryHoverOverlay');
    const cardBody = chartCanvas.parentElement;
    
    // Validate input
    if (!statistics || !Array.isArray(statistics) || statistics.length === 0) {
      console.error('No statistics data available');
      return;
    }
    
    // Remove old event listeners if they exist
    if (mousemoveHandler) {
      chartCanvas.removeEventListener('mousemove', mousemoveHandler);
      mousemoveHandler = null;
    }
    if (mouseleaveHandler) {
      chartCanvas.removeEventListener('mouseleave', mouseleaveHandler);
      mouseleaveHandler = null;
    }
    
    // Destroy existing chart if it exists
    if (statisticsChart) {
      statisticsChart.destroy();
      statisticsChart = null;
    }
    
    // Set canvas background to black via CSS
    chartCanvas.style.backgroundColor = '#000000';
    
    // Filter statistics by category if one is selected
    let filteredStatistics = statistics;
    if (category && category.trim() !== '') {
      // Filter to only show the selected category
      filteredStatistics = statistics.filter(s => s.category === category);
      console.log(`Filtering for category "${category}": ${filteredStatistics.length} records found out of ${statistics.length} total`);
      
      // Check if filtered result is empty
      if (!filteredStatistics || filteredStatistics.length === 0) {
        console.warn(`No data found for category: ${category}`);
        if (chartCanvas && chartCanvas.parentElement) {
          const errorMsg = document.createElement('div');
          errorMsg.className = 'chart-error-message alert alert-warning';
          errorMsg.style.cssText = 'background: rgba(249,66,58,0.1); border: 1px solid rgba(249,66,58,0.3); color: #fff; padding: 15px; margin: 10px 0;';
          errorMsg.textContent = `No data found for category: ${category}`;
          chartCanvas.parentElement.insertBefore(errorMsg, chartCanvas);
        }
        return;
      }
      
      // Verify all filtered statistics belong to the selected category
      const invalidCategories = filteredStatistics.filter(s => s.category !== category);
      if (invalidCategories.length > 0) {
        console.warn(`Warning: Found ${invalidCategories.length} records with incorrect category`);
      }
    } else {
      console.log(`Showing all categories: ${filteredStatistics.length} total records`);
    }
    
    // Group data by date from filtered statistics
    // Sort dates chronologically (ISO format YYYY-MM-DD sorts correctly as strings)
    const dates = [...new Set(filteredStatistics.map(s => s.date))].sort();
    
    // X-axis labels: dates only (prefer date_string MM.DD.YY -> MM/DD/YY)
    const formattedDates = dates.map(date => {
      const info = gameInfo[date];
      if (info && info.date_string) {
        // Convert MM.DD.YY to MM/DD/YY format
        return String(info.date_string).replace(/\./g, '/');
      }
      // Fallback: format from ISO date
      const d = new Date(date);
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const year = String(d.getFullYear()).slice(-2);
      return `${month}/${day}/${year}`;
    });
    
    if (category && category.trim() !== '') {
      // Single category view - use already filtered statistics
      // Double-check that we only have data for the selected category
      const categoryData = filteredStatistics
        .filter(s => s.category === category) // Ensure we only have the selected category
        .sort((a, b) => a.date.localeCompare(b.date));
      
      console.log(`Single category view for "${category}": ${categoryData.length} data points`);

      // Use dates from the selected category only
      const catDates = [...new Set(categoryData.map(s => s.date))].sort();
      const catFormattedDates = catDates.map(date => {
        const info = gameInfo[date];
        if (info && info.date_string) {
          return String(info.date_string).replace(/\./g, '/');
        }
        const d = new Date(date);
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const year = String(d.getFullYear()).slice(-2);
        return `${month}/${day}/${year}`;
      });

      const percentages = catDates.map(date => {
        const point = categoryData.find(d => d.date === date);
        return point ? point.percentage : null;
      });

      const lineColor = categoryColors[category] || '#CCCCCC';

      // Color code points based on win/loss
      const pointColors = catDates.map(date => {
        const result = gameResults[date];
        if (result === 'win') {
          return '#00ff00';  // Green for win
        } else if (result === 'loss') {
          return '#F9423A';  // Red for loss
        }
        return lineColor;  // Default color if result unknown
      });

      // Create overall scores dataset overlay
      const overallScoresData = catDates.map(date => {
        return overallScores[date] || null;
      });
      
      // Color code overall scores points based on win/loss
      const overallPointColors = catDates.map(date => {
        const result = gameResults[date];
        if (result === 'win') {
          return '#00ff00';  // Green for win
        } else if (result === 'loss') {
          return '#F9423A';  // Red for loss
        }
        return '#F9423A';  // Default red if result unknown
      });

      // Build datasets array with category and overall scores
      const datasets = [
        {
            label: category,
            data: percentages,
            borderColor: lineColor,
            backgroundColor: lineColor + '20',
            borderWidth: 4,
            fill: true,
            tension: 0.4,
            pointRadius: 6,
            pointHoverRadius: 9,
            pointBackgroundColor: pointColors,  // Array of colors for each point
            pointBorderColor: '#000',
            pointBorderWidth: 2.5
        }
      ];

      // Add overall scores overlay if available
      console.log('Single category - Overall scores available:', overallScores);
      console.log('Single category - Cat dates:', catDates);
      if (Object.keys(overallScores).length > 0) {
        console.log('Adding overall scores to single category view');
        datasets.push({
          label: 'Overall Cog Score',
          data: overallScoresData,
          borderColor: '#F9423A',
          backgroundColor: '#F9423A20',
          borderWidth: 3,
          borderDash: [5, 5],
          fill: false,
          tension: 0.4,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointBackgroundColor: '#F9423A',
          pointBorderColor: '#000',
          pointBorderWidth: 2
        });
        console.log('Added overall scores dataset. Total datasets:', datasets.length);
      } else {
        console.warn('No overall scores available for single category view');
      }

      // Update slider if it exists
      if (window.teamStatsSlider && typeof window.teamStatsSlider.updateOriginalData === 'function') {
        // Store reference to update after chart creation
        const updateSliderAfterCreation = true;
      }
      
      // Calculate chart dimensions - support both 4-game view and zoomed-out view (single category)
      const container = document.getElementById('teamStatsChartContainer');
      const wrapper = document.getElementById('teamStatsChartWrapper');
      const totalGames = catFormattedDates.length;
      const gamesPerView = chartZoomedOut ? totalGames : 4;
      
      // Get container width
      const containerWidth = container ? container.offsetWidth || container.clientWidth : 1200;
      
      // Calculate width per game
      const widthPerGame = containerWidth / gamesPerView;
      const totalChartWidth = chartZoomedOut ? containerWidth : (totalGames * widthPerGame);
      
      // Set wrapper width to accommodate all games
      if (wrapper) {
        if (chartZoomedOut) {
          // When zoomed out, fit all games in container width
          wrapper.style.width = '100%';
          wrapper.style.minWidth = '100%';
        } else {
          // When zoomed in, use calculated width for scrolling
          wrapper.style.width = totalChartWidth + 'px';
          wrapper.style.minWidth = '100%';
        }
      }
      
      // Configure chart width
      const chartWidth = chartZoomedOut ? containerWidth : totalChartWidth;
      
      try {
        statisticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: catFormattedDates,
          datasets: datasets
        },
        options: {
          responsive: chartZoomedOut, // Make responsive when zoomed out
          maintainAspectRatio: false,
          devicePixelRatio: 2,
          backgroundColor: '#000000',  // Black background for plot
          interaction: {
            mode: 'point',
            intersect: false
          },
          hover: {
            mode: 'point',
            intersect: false
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              enabled: true,
              backgroundColor: 'rgba(0, 0, 0, 0.95)',
              titleColor: '#F9423A',
              bodyColor: '#fff',
              borderColor: '#F9423A',
              borderWidth: 2,
              padding: 15,
              displayColors: true,
              boxWidth: 10,
              boxHeight: 10,
              titleFont: {
                size: 16,
                weight: 'bold'
              },
              bodyFont: {
                size: 14
              },
              callbacks: {
                title: function(context) {
                  // Show the category name prominently as the title
                  const categoryName = context[0].dataset.label || 'Category';
                  return '📊 ' + categoryName;
                },
                label: function(context) {
                  // Show the value and date
                  const value = context.parsed.y.toFixed(2);
                  const date = context.label;
                  return `Score: ${value}% on ${date}`;
                }
              }
            }
          },
          scales: {
            x: {
              ticks: {
                color: '#fff',
                font: {
                  size: 12
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              }
            },
            y: {
              ticks: {
                color: '#fff',
                font: {
                  size: 12
                },
                callback: function(value) {
                  return value + '%';
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              min: 0,
              max: 100
            }
          },
          animation: {
            onComplete: function() {
              // Draw overall cog scores above each game date
              const chart = this.chart;
              const ctx = chart.ctx;
              const meta = chart.getDatasetMeta(0);
              
              ctx.save();
              ctx.font = 'bold 12px Arial';
              ctx.fillStyle = '#F9423A';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'bottom';
              
              // Get x-axis scale for positioning
              const xScale = chart.scales.x;
              const chartArea = chart.chartArea;
              
              catDates.forEach((date, index) => {
                const overallScore = overallScores[date];
                if (overallScore !== undefined) {
                  const x = xScale.getPixelForValue(index);
                  const y = chartArea.top - 15; // Position above chart area
                  
                  ctx.fillText(`Overall: ${overallScore.toFixed(4)}%`, x, y);
                }
              });
              
              ctx.restore();
            }
          }
        }
      });
      
      // Set canvas dimensions explicitly for single category view
      if (statisticsChart && statisticsChart.canvas) {
        if (chartZoomedOut) {
          // When zoomed out, use responsive sizing
          statisticsChart.canvas.style.width = '100%';
          statisticsChart.canvas.style.height = '700px';
          statisticsChart.canvas.style.maxWidth = '100%';
        } else {
          // When zoomed in, use explicit dimensions
          statisticsChart.canvas.style.width = chartWidth + 'px';
          statisticsChart.canvas.style.height = '700px';
          statisticsChart.canvas.width = chartWidth;
          statisticsChart.canvas.height = 700;
        }
        statisticsChart.resize();
      }
      } catch (error) {
        console.error('Error creating chart for single category:', error);
        return;
      }
      
      // Initialize slider after chart is fully rendered
      setTimeout(() => {
        const sliderContainer = document.getElementById('teamStatsPrecisionSlider');
        console.log('Attempting to initialize slider:', {
          container: !!sliderContainer,
          sliderLib: !!window.IntegrityHoopsSlider,
          createFn: !!window.IntegrityHoopsSlider?.createForChartJS,
          chart: !!statisticsChart,
          chartData: statisticsChart?.data,
          labelsCount: statisticsChart?.data?.labels?.length,
          datasetsCount: statisticsChart?.data?.datasets?.length,
          bound: sliderContainer?.dataset.bound
        });
        
        if (sliderContainer && window.IntegrityHoopsSlider && window.IntegrityHoopsSlider.createForChartJS && statisticsChart && statisticsChart.data && statisticsChart.data.labels && statisticsChart.data.labels.length > 0 && !sliderContainer.dataset.bound) {
          const initialPrecision = parseInt(localStorage.getItem('teamStatsPrecision') || '40', 10);
          console.log('Creating slider with precision:', initialPrecision);
          try {
            window.teamStatsSlider = window.IntegrityHoopsSlider.createForChartJS({
              chart: statisticsChart,
              container: sliderContainer,
              initialPrecision,
              anchor: 'end'
            });
            sliderContainer.dataset.bound = '1';
            console.log('Slider created successfully:', window.teamStatsSlider);
          } catch (error) {
            console.error('Error creating slider:', error);
            console.error('Error stack:', error.stack);
          }
        } else {
          console.warn('Slider initialization skipped:', {
            container: !!sliderContainer,
            sliderLib: !!window.IntegrityHoopsSlider,
            createFn: !!window.IntegrityHoopsSlider?.createForChartJS,
            chart: !!statisticsChart,
            hasData: !!statisticsChart?.data,
            hasLabels: !!statisticsChart?.data?.labels,
            labelsLength: statisticsChart?.data?.labels?.length,
            bound: sliderContainer?.dataset.bound
          });
        }
      }, 100);
      
      // Update overall scores list with chart instance for toggle functionality
      updateOverallScoresList(overallScores, gameInfo, statisticsChart);
      
      // Populate chart line menu for toggle functionality
      // Ensure populateChartLineMenu is called after chart is fully initialized
      if (typeof populateChartLineMenu === 'function') {
        setTimeout(() => {
          try {
            populateChartLineMenu();
          } catch (error) {
            console.error('Error populating chart line menu:', error);
          }
        }, 300);
      }
      
      // Render custom toggle buttons for datasets (use setTimeout to ensure chart is fully initialized)
      setTimeout(() => {
        console.log('📊 Rendering toggle buttons...');
        renderCategoryToggleButtons(statisticsChart);
        
        // Double-check after another delay
        setTimeout(() => {
          const container = document.getElementById('statisticsDatasetToggles');
          const buttons = container ? container.querySelectorAll('button[data-dataset-index]').length : 0;
          console.log(`🔍 Verification: ${buttons} toggle buttons rendered`);
          
          if (buttons === 0 && statisticsChart) {
            console.warn('⚠️ No buttons found, re-rendering...');
            renderCategoryToggleButtons(statisticsChart);
          }
        }, 500);
      }, 100);

      // Canvas hover to show dataset label near cursor with enhanced tooltip and button highlighting
      let lastHoveredDatasetIndex = -1;
      mousemoveHandler = function(ev) {
        if (!overlay || !statisticsChart) return;
        
        // Remove glow from previously hovered button
        if (lastHoveredDatasetIndex >= 0) {
          const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
          if (prevButton) {
            prevButton.classList.remove('toggle-button-neon-glow');
            prevButton.style.color = '';
          }
        }
        
            const chartArea = statisticsChart.chartArea;
            const canvasPos = Chart.helpers.getRelativePosition(ev, statisticsChart);
            const x = canvasPos.x;
            const y = canvasPos.y;
            
        // Check if cursor is within chart area
        if (x < chartArea.left || x > chartArea.right || 
            y < chartArea.top || y > chartArea.bottom) {
          overlay.style.display = 'none';
          if (lastHoveredDatasetIndex >= 0) {
            const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
            if (prevButton) {
              prevButton.classList.remove('toggle-button-neon-glow');
              prevButton.style.color = '';
            }
            lastHoveredDatasetIndex = -1;
          }
          return;
        }
        
        // Try multiple detection methods to catch all points
        let foundPoint = null;
        let foundDataset = null;
        let foundValue = null;
        let foundDateLabel = null;
        
        // Method 1: Try 'nearest' mode with larger threshold
        const nearestPoints = statisticsChart.getElementsAtEventForMode(ev, 'nearest', { intersect: false, threshold: 50 }, true);
        if (nearestPoints && nearestPoints.length > 0) {
          const point = nearestPoints[0];
          const dsIndex = point.datasetIndex;
          const dataset = statisticsChart.data.datasets[dsIndex];
          if (dataset && !dataset.hidden) {
            const dataIndex = point.index;
            const value = dataset.data[dataIndex];
            if (value !== null && value !== undefined) {
              foundPoint = point;
              foundDataset = dataset;
              foundValue = value;
              foundDateLabel = statisticsChart.data.labels[dataIndex];
            }
          }
        }
        
        // Method 2: If not found, try 'index' mode
        if (!foundPoint) {
          const indexPoints = statisticsChart.getElementsAtEventForMode(ev, 'index', { intersect: false }, true);
          if (indexPoints && indexPoints.length > 0) {
            // Find the closest visible dataset
            for (const point of indexPoints) {
              const dsIndex = point.datasetIndex;
              const dataset = statisticsChart.data.datasets[dsIndex];
              if (dataset && !dataset.hidden) {
                const dataIndex = point.index;
                const value = dataset.data[dataIndex];
                if (value !== null && value !== undefined) {
                  foundPoint = point;
                  foundDataset = dataset;
                  foundValue = value;
                  foundDateLabel = statisticsChart.data.labels[dataIndex];
                  break;
                }
              }
            }
          }
        }
        
        // Method 3: Calculate distance to all visible lines and find closest
        if (!foundPoint) {
          let closestDistance = Infinity;
          let closestDatasetIndex = -1;
          let closestDataIndex = -1;
          
          const xScale = statisticsChart.scales.x;
          
          // First, determine which x-axis index we're closest to based on x position
          let closestXIndex = -1;
          let closestXDistance = Infinity;
          
          if (xScale && statisticsChart.data.labels) {
            statisticsChart.data.labels.forEach((label, idx) => {
              const labelX = xScale.getPixelForValue(idx);
              const distance = Math.abs(x - labelX);
              if (distance < closestXDistance) {
                closestXDistance = distance;
                closestXIndex = idx;
              }
            });
          }
          
          statisticsChart.data.datasets.forEach((dataset, dsIdx) => {
            if (dataset.hidden) return;
            
            const meta = statisticsChart.getDatasetMeta(dsIdx);
            if (!meta || !meta.data) return;
            
            // Check each point in this dataset
            meta.data.forEach((point, idx) => {
              if (point.skip) return;
              
              const pointX = point.x;
              const pointY = point.y;
              
              // Calculate distance from cursor to point
              const distance = Math.sqrt(Math.pow(x - pointX, 2) + Math.pow(y - pointY, 2));
              
              if (distance < closestDistance && distance < 50) {
                const value = dataset.data[idx];
                if (value !== null && value !== undefined) {
                  closestDistance = distance;
                  closestDatasetIndex = dsIdx;
                  closestDataIndex = idx;
                }
              }
            });
          });
          
          if (closestDatasetIndex >= 0) {
            foundDataset = statisticsChart.data.datasets[closestDatasetIndex];
            foundValue = foundDataset.data[closestDataIndex];
            // Use the x-axis label for the closest x position
            if (closestXIndex >= 0 && statisticsChart.data.labels[closestXIndex]) {
              foundDateLabel = statisticsChart.data.labels[closestXIndex];
            } else {
              foundDateLabel = statisticsChart.data.labels[closestDataIndex];
            }
            foundPoint = { datasetIndex: closestDatasetIndex, index: closestDataIndex };
          } else if (closestXIndex >= 0) {
            // If we can't find a point but we know the x position, use that
            // Find the first visible dataset with data at this index
            for (let dsIdx = 0; dsIdx < statisticsChart.data.datasets.length; dsIdx++) {
              const dataset = statisticsChart.data.datasets[dsIdx];
              if (dataset.hidden) continue;
              
              const value = dataset.data[closestXIndex];
              if (value !== null && value !== undefined) {
                foundDataset = dataset;
                foundValue = value;
                foundDateLabel = statisticsChart.data.labels[closestXIndex];
                foundPoint = { datasetIndex: dsIdx, index: closestXIndex };
                break;
              }
            }
          }
        }
        
        // If we found a point, show tooltip and highlight button
        if (foundPoint && foundDataset) {
          const label = foundDataset.label;
          const dsIndex = foundPoint.datasetIndex;
          
          // Determine x-axis label based on x position if not already set
          if (!foundDateLabel) {
            const xScale = statisticsChart.scales.x;
            if (xScale && statisticsChart.data.labels) {
              // Find closest x-axis label based on cursor x position
              let closestXIndex = -1;
              let closestXDistance = Infinity;
              statisticsChart.data.labels.forEach((lbl, idx) => {
                const labelX = xScale.getPixelForValue(idx);
                const distance = Math.abs(x - labelX);
                if (distance < closestXDistance) {
                  closestXDistance = distance;
                  closestXIndex = idx;
                }
              });
              if (closestXIndex >= 0) {
                foundDateLabel = statisticsChart.data.labels[closestXIndex];
              }
            }
          }
          
          // Update tooltip content
          const categoryNameEl = document.getElementById('hoverCategoryName');
          const dateEl = document.getElementById('hoverDate');
          const valueEl = document.getElementById('hoverValue');
          
          if (categoryNameEl) categoryNameEl.textContent = label || 'Unknown';
          if (dateEl) dateEl.textContent = `📅 ${foundDateLabel || 'N/A'}`;
          if (valueEl) valueEl.textContent = `📊 ${foundValue.toFixed(2)}%`;
          
          // Set tooltip border color to match line color (subtle glow)
          const lineColor = foundDataset.borderColor || '#F9423A';
          overlay.style.borderColor = lineColor;
          overlay.style.boxShadow = `0 0 8px ${lineColor}50, 0 0 15px ${lineColor}25`;
          
          // Position tooltip to follow cursor
          const rect = cardBody.getBoundingClientRect();
          overlay.style.display = 'block';
          overlay.style.left = (ev.clientX - rect.left + 20) + 'px';
          overlay.style.top = (ev.clientY - rect.top - 80) + 'px';
          
          // Highlight corresponding toggle button with neon glow
          const toggleButton = document.querySelector(`button[data-dataset-index="${dsIndex}"]`);
          if (toggleButton) {
            toggleButton.classList.add('toggle-button-neon-glow');
            toggleButton.style.color = lineColor;
            lastHoveredDatasetIndex = dsIndex;
          }
        } else {
          // No point found - hide tooltip and remove glow
        overlay.style.display = 'none';
          if (lastHoveredDatasetIndex >= 0) {
            const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
            if (prevButton) {
              prevButton.classList.remove('toggle-button-neon-glow');
              prevButton.style.color = '';
            }
            lastHoveredDatasetIndex = -1;
          }
        }
      };
      chartCanvas.addEventListener('mousemove', mousemoveHandler);
      
      mouseleaveHandler = function() {
        if (overlay) overlay.style.display = 'none';
        // Remove glow from any hovered button
        if (lastHoveredDatasetIndex >= 0) {
          const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
          if (prevButton) {
            prevButton.classList.remove('toggle-button-neon-glow');
            prevButton.style.color = '';
          }
          lastHoveredDatasetIndex = -1;
        }
      };
      chartCanvas.addEventListener('mouseleave', mouseleaveHandler);
    } else {
      // All categories view - use filtered statistics (which will be all when no category selected)
      const categories = [...new Set(filteredStatistics.map(s => s.category))];
      
      // Color code points based on win/loss for all categories
      const pointColors = dates.map(date => {
        const result = gameResults[date];
        if (result === 'win') {
          return '#00ff00';  // Green for win
        } else if (result === 'loss') {
          return '#F9423A';  // Red for loss
        }
        return null;  // Will use default color if result unknown
      });
      
      const datasets = categories.map(cat => {
        const categoryData = filteredStatistics
          .filter(s => s.category === cat)
          .sort((a, b) => a.date.localeCompare(b.date));
        
        const percentages = dates.map(date => {
          const point = categoryData.find(d => d.date === date);
          return point ? point.percentage : null;
        });
        
        const lineColor = categoryColors[cat] || '#CCCCCC';
        return {
          label: cat,
          data: percentages,
          borderColor: lineColor,
          backgroundColor: lineColor + '20',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 8,
          pointBackgroundColor: pointColors.map(color => color || lineColor),  // Use win/loss colors or default
          pointBorderColor: '#000',
          pointBorderWidth: 2
        };
      });
      
      // Add overall scores dataset overlay if available
        console.log('Overall scores available:', overallScores);
        console.log('Dates array:', dates);
        if (Object.keys(overallScores).length > 0) {
          const overallScoresData = dates.map(date => {
            const score = overallScores[date] || null;
            console.log(`Date ${date}: score = ${score}`);
            return score;
          });
          
          // Color code overall scores points based on win/loss
          const overallPointColors = dates.map(date => {
            const result = gameResults[date];
            if (result === 'win') {
              return '#00ff00';  // Green for win
            } else if (result === 'loss') {
              return '#F9423A';  // Red for loss
            }
            return '#F9423A';  // Default red if result unknown
          });
          
          console.log('Overall scores data array:', overallScoresData);
          datasets.push({
            label: 'Overall Cog Score',
            data: overallScoresData,
            borderColor: '#F9423A',
            backgroundColor: '#F9423A20',
            borderWidth: 3,
            borderDash: [5, 5],
            fill: false,
            tension: 0.4,
            pointRadius: 6,
            pointHoverRadius: 8,
            pointBackgroundColor: overallPointColors,  // Array of colors for each point
            pointBorderColor: '#000',
            pointBorderWidth: 2
          });
        console.log('Added overall scores dataset. Total datasets:', datasets.length);
      } else {
        console.warn('No overall scores available to add to chart');
      }
      
      // Calculate chart dimensions - support both 4-game view and zoomed-out view
      const container = document.getElementById('teamStatsChartContainer');
      const wrapper = document.getElementById('teamStatsChartWrapper');
      const totalGames = formattedDates.length;
      const gamesPerView = chartZoomedOut ? totalGames : 4;
      
      // Get container width
      const containerWidth = container ? container.offsetWidth || container.clientWidth : 1200;
      
      // Calculate width per game
      const widthPerGame = containerWidth / gamesPerView;
      const totalChartWidth = chartZoomedOut ? containerWidth : (totalGames * widthPerGame);
      
      // Set wrapper width to accommodate all games
      if (wrapper) {
        if (chartZoomedOut) {
          // When zoomed out, fit all games in container width
          wrapper.style.width = '100%';
          wrapper.style.minWidth = '100%';
        } else {
          // When zoomed in, use calculated width for scrolling
          wrapper.style.width = totalChartWidth + 'px';
          wrapper.style.minWidth = '100%';
        }
      }
      
      // Configure chart width
      const chartWidth = chartZoomedOut ? containerWidth : totalChartWidth;
      
      try {
      statisticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: formattedDates,
          datasets: datasets
        },
        options: {
          responsive: chartZoomedOut, // Make responsive when zoomed out
          maintainAspectRatio: false,
          devicePixelRatio: 2,
          interaction: {
            mode: 'point',
            intersect: false
          },
          hover: {
            mode: 'point',
            intersect: false
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              enabled: true,
              backgroundColor: 'rgba(0, 0, 0, 0.95)',
              titleColor: '#F9423A',
              bodyColor: '#fff',
              borderColor: '#F9423A',
              borderWidth: 2,
              padding: 15,
              displayColors: true,
              boxWidth: 10,
              boxHeight: 10,
              titleFont: {
                size: 16,
                weight: 'bold'
              },
              bodyFont: {
                size: 14
              },
              callbacks: {
                title: function(context) {
                  // Show the date as the title
                  return '📅 ' + (context[0].label || 'Date');
                },
                label: function(context) {
                  // Show category name and value prominently
                  const categoryName = context.dataset.label;
                  const value = context.parsed.y.toFixed(2);
                  return `📊 ${categoryName}: ${value}%`;
                },
                afterLabel: function(context) {
                  // Add color indicator matching the line
                  return '';
                }
              }
            }
          },
          scales: {
            x: {
              ticks: {
                color: '#fff',
                font: {
                  size: 11
                },
                maxRotation: 45,
                minRotation: 0
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              title: {
                display: false
              }
            },
            y: {
              ticks: {
                color: '#fff',
                font: {
                  size: 11
                },
                callback: function(value) {
                  return value + '%';
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              min: 0,
              max: 100
            }
          },
          animation: {
            onComplete: function() {
              // Draw overall cog scores above each game date
              const chart = this.chart;
              const ctx = chart.ctx;
              
              ctx.save();
              ctx.font = 'bold 12px Arial';
              ctx.fillStyle = '#F9423A';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'bottom';
              
              // Get x-axis scale to position labels
              const xScale = chart.scales.x;
              const chartArea = chart.chartArea;
              
              dates.forEach((date, index) => {
                const overallScore = overallScores[date];
                if (overallScore !== undefined) {
                  const x = xScale.getPixelForValue(index);
                  const y = chartArea.top - 10; // Position above chart area
                  
                  ctx.fillText(`Overall: ${overallScore.toFixed(4)}%`, x, y);
                }
              });
              
              ctx.restore();
              
              // Set canvas dimensions after chart is rendered
              if (chart.canvas) {
                if (chartZoomedOut) {
                  // When zoomed out, let Chart.js handle responsive sizing
                  chart.resize();
                } else {
                  // When zoomed in, set explicit dimensions
                  chart.canvas.width = chartWidth;
                  chart.canvas.height = 700;
                  chart.resize();
                }
              }
            }
          }
        }
      });
      
      // Set canvas dimensions explicitly
      if (statisticsChart && statisticsChart.canvas) {
        if (chartZoomedOut) {
          // When zoomed out, use responsive sizing
          statisticsChart.canvas.style.width = '100%';
          statisticsChart.canvas.style.height = '700px';
          statisticsChart.canvas.style.maxWidth = '100%';
        } else {
          // When zoomed in, use explicit dimensions
          statisticsChart.canvas.style.width = chartWidth + 'px';
          statisticsChart.canvas.style.height = '700px';
          statisticsChart.canvas.width = chartWidth;
          statisticsChart.canvas.height = 700;
        }
        statisticsChart.resize();
      }
      } catch (error) {
        console.error('Error creating chart for all categories:', error);
        return;
      }
      
      // Initialize slider after chart is fully rendered
      setTimeout(() => {
        const sliderContainer = document.getElementById('teamStatsPrecisionSlider');
        console.log('Attempting to initialize slider:', {
          container: !!sliderContainer,
          sliderLib: !!window.IntegrityHoopsSlider,
          createFn: !!window.IntegrityHoopsSlider?.createForChartJS,
          chart: !!statisticsChart,
          chartData: statisticsChart?.data,
          labelsCount: statisticsChart?.data?.labels?.length,
          datasetsCount: statisticsChart?.data?.datasets?.length,
          bound: sliderContainer?.dataset.bound
        });
        
        if (sliderContainer && window.IntegrityHoopsSlider && window.IntegrityHoopsSlider.createForChartJS && statisticsChart && statisticsChart.data && statisticsChart.data.labels && statisticsChart.data.labels.length > 0 && !sliderContainer.dataset.bound) {
          const initialPrecision = parseInt(localStorage.getItem('teamStatsPrecision') || '40', 10);
          console.log('Creating slider with precision:', initialPrecision);
          try {
            window.teamStatsSlider = window.IntegrityHoopsSlider.createForChartJS({
              chart: statisticsChart,
              container: sliderContainer,
              initialPrecision,
              anchor: 'end'
            });
            sliderContainer.dataset.bound = '1';
            console.log('Slider created successfully:', window.teamStatsSlider);
          } catch (error) {
            console.error('Error creating slider:', error);
            console.error('Error stack:', error.stack);
          }
        } else {
          console.warn('Slider initialization skipped:', {
            container: !!sliderContainer,
            sliderLib: !!window.IntegrityHoopsSlider,
            createFn: !!window.IntegrityHoopsSlider?.createForChartJS,
            chart: !!statisticsChart,
            hasData: !!statisticsChart?.data,
            hasLabels: !!statisticsChart?.data?.labels,
            labelsLength: statisticsChart?.data?.labels?.length,
            bound: sliderContainer?.dataset.bound
          });
        }
      }, 100);
      
      // Update overall scores list with chart instance for toggle functionality
      updateOverallScoresList(overallScores, gameInfo, statisticsChart);
      
      // Populate chart line menu for toggle functionality
      // Ensure populateChartLineMenu is called after chart is fully initialized
      if (typeof populateChartLineMenu === 'function') {
        setTimeout(() => {
          try {
            populateChartLineMenu();
          } catch (error) {
            console.error('Error populating chart line menu:', error);
          }
        }, 300);
      }
      
      // Render custom toggle buttons for datasets (use setTimeout to ensure chart is fully initialized)
      setTimeout(() => {
        console.log('📊 Rendering toggle buttons for all categories view...');
        renderCategoryToggleButtons(statisticsChart);
        
        // Double-check after another delay
        setTimeout(() => {
          const container = document.getElementById('statisticsDatasetToggles');
          const buttons = container ? container.querySelectorAll('button[data-dataset-index]').length : 0;
          console.log(`🔍 Verification: ${buttons} toggle buttons rendered`);
          
          if (buttons === 0 && statisticsChart) {
            console.warn('⚠️ No buttons found, re-rendering...');
            renderCategoryToggleButtons(statisticsChart);
          }
        }, 500);
      }, 100);
      
      // Add hover support for all categories view with enhanced tooltip and button highlighting
      let lastHoveredDatasetIndex = -1;
      mousemoveHandler = function(ev) {
        if (!overlay || !statisticsChart) return;
        
        // Remove glow from previously hovered button
        if (lastHoveredDatasetIndex >= 0) {
          const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
          if (prevButton) {
            prevButton.classList.remove('toggle-button-neon-glow');
            prevButton.style.color = '';
          }
        }
        
            const chartArea = statisticsChart.chartArea;
            const canvasPos = Chart.helpers.getRelativePosition(ev, statisticsChart);
            const x = canvasPos.x;
            const y = canvasPos.y;
            
        // Check if cursor is within chart area
        if (x < chartArea.left || x > chartArea.right || 
            y < chartArea.top || y > chartArea.bottom) {
          overlay.style.display = 'none';
          if (lastHoveredDatasetIndex >= 0) {
            const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
            if (prevButton) {
              prevButton.classList.remove('toggle-button-neon-glow');
              prevButton.style.color = '';
            }
            lastHoveredDatasetIndex = -1;
          }
          return;
        }
        
        // Try multiple detection methods to catch all points
        let foundPoint = null;
        let foundDataset = null;
        let foundValue = null;
        let foundDateLabel = null;
        
        // Method 1: Try 'nearest' mode with larger threshold
        const nearestPoints = statisticsChart.getElementsAtEventForMode(ev, 'nearest', { intersect: false, threshold: 50 }, true);
        if (nearestPoints && nearestPoints.length > 0) {
          const point = nearestPoints[0];
          const dsIndex = point.datasetIndex;
          const dataset = statisticsChart.data.datasets[dsIndex];
          if (dataset && !dataset.hidden) {
            const dataIndex = point.index;
            const value = dataset.data[dataIndex];
            if (value !== null && value !== undefined) {
              foundPoint = point;
              foundDataset = dataset;
              foundValue = value;
              foundDateLabel = statisticsChart.data.labels[dataIndex];
            }
          }
        }
        
        // Method 2: If not found, try 'index' mode
        if (!foundPoint) {
          const indexPoints = statisticsChart.getElementsAtEventForMode(ev, 'index', { intersect: false }, true);
          if (indexPoints && indexPoints.length > 0) {
            // Find the closest visible dataset
            for (const point of indexPoints) {
              const dsIndex = point.datasetIndex;
              const dataset = statisticsChart.data.datasets[dsIndex];
              if (dataset && !dataset.hidden) {
                const dataIndex = point.index;
                const value = dataset.data[dataIndex];
                if (value !== null && value !== undefined) {
                  foundPoint = point;
                  foundDataset = dataset;
                  foundValue = value;
                  foundDateLabel = statisticsChart.data.labels[dataIndex];
                  break;
                }
              }
            }
          }
        }
        
        // Method 3: Calculate distance to all visible lines and find closest
        if (!foundPoint) {
          let closestDistance = Infinity;
          let closestDatasetIndex = -1;
          let closestDataIndex = -1;
          
          const xScale = statisticsChart.scales.x;
          const yScale = statisticsChart.scales.y;
          
          // First, determine which x-axis index we're closest to based on x position
          let closestXIndex = -1;
          let closestXDistance = Infinity;
          
          if (xScale && statisticsChart.data.labels) {
            statisticsChart.data.labels.forEach((label, idx) => {
              const labelX = xScale.getPixelForValue(idx);
              const distance = Math.abs(x - labelX);
              if (distance < closestXDistance) {
                closestXDistance = distance;
                closestXIndex = idx;
              }
            });
          }
          
          statisticsChart.data.datasets.forEach((dataset, dsIdx) => {
            if (dataset.hidden) return;
            
            const meta = statisticsChart.getDatasetMeta(dsIdx);
            if (!meta || !meta.data) return;
            
            // Check each point in this dataset
            meta.data.forEach((point, idx) => {
              if (point.skip) return;
              
              const pointX = point.x;
              const pointY = point.y;
              
              // Calculate distance from cursor to point
              const distance = Math.sqrt(Math.pow(x - pointX, 2) + Math.pow(y - pointY, 2));
              
              if (distance < closestDistance && distance < 50) {
                const value = dataset.data[idx];
                if (value !== null && value !== undefined) {
                  closestDistance = distance;
                  closestDatasetIndex = dsIdx;
                  closestDataIndex = idx;
                }
              }
            });
          });
          
          if (closestDatasetIndex >= 0) {
            foundDataset = statisticsChart.data.datasets[closestDatasetIndex];
            foundValue = foundDataset.data[closestDataIndex];
            // Use the x-axis label for the closest x position
            if (closestXIndex >= 0 && statisticsChart.data.labels[closestXIndex]) {
              foundDateLabel = statisticsChart.data.labels[closestXIndex];
            } else {
              foundDateLabel = statisticsChart.data.labels[closestDataIndex];
            }
            foundPoint = { datasetIndex: closestDatasetIndex, index: closestDataIndex };
          } else if (closestXIndex >= 0) {
            // If we can't find a point but we know the x position, use that
            // Find the first visible dataset with data at this index
            for (let dsIdx = 0; dsIdx < statisticsChart.data.datasets.length; dsIdx++) {
              const dataset = statisticsChart.data.datasets[dsIdx];
              if (dataset.hidden) continue;
              
              const value = dataset.data[closestXIndex];
              if (value !== null && value !== undefined) {
                foundDataset = dataset;
                foundValue = value;
                foundDateLabel = statisticsChart.data.labels[closestXIndex];
                foundPoint = { datasetIndex: dsIdx, index: closestXIndex };
                break;
              }
            }
          }
        }
        
        // If we found a point, show tooltip and highlight button
        if (foundPoint && foundDataset) {
          const label = foundDataset.label;
          const dsIndex = foundPoint.datasetIndex;
          
          // Determine x-axis label based on x position if not already set
          if (!foundDateLabel) {
            const xScale = statisticsChart.scales.x;
            if (xScale && statisticsChart.data.labels) {
              // Find closest x-axis label based on cursor x position
              let closestXIndex = -1;
              let closestXDistance = Infinity;
              statisticsChart.data.labels.forEach((lbl, idx) => {
                const labelX = xScale.getPixelForValue(idx);
                const distance = Math.abs(x - labelX);
                if (distance < closestXDistance) {
                  closestXDistance = distance;
                  closestXIndex = idx;
                }
              });
              if (closestXIndex >= 0) {
                foundDateLabel = statisticsChart.data.labels[closestXIndex];
              }
            }
          }
          
          // Update tooltip content
          const categoryNameEl = document.getElementById('hoverCategoryName');
          const dateEl = document.getElementById('hoverDate');
          const valueEl = document.getElementById('hoverValue');
          
          if (categoryNameEl) categoryNameEl.textContent = label || 'Unknown';
          if (dateEl) dateEl.textContent = `📅 ${foundDateLabel || 'N/A'}`;
          if (valueEl) valueEl.textContent = `📊 ${foundValue.toFixed(2)}%`;
          
          // Set tooltip border color to match line color
          const lineColor = foundDataset.borderColor || '#F9423A';
          overlay.style.borderColor = lineColor;
          overlay.style.boxShadow = `0 0 10px ${lineColor}60, 0 0 20px ${lineColor}30`;
          
          // Position tooltip to follow cursor
          const rect = cardBody.getBoundingClientRect();
          overlay.style.display = 'block';
          overlay.style.left = (ev.clientX - rect.left + 20) + 'px';
          overlay.style.top = (ev.clientY - rect.top - 80) + 'px';
          
          // Highlight corresponding toggle button with neon glow
          const toggleButton = document.querySelector(`button[data-dataset-index="${dsIndex}"]`);
          if (toggleButton) {
            toggleButton.classList.add('toggle-button-neon-glow');
            toggleButton.style.color = lineColor;
            lastHoveredDatasetIndex = dsIndex;
          }
        } else {
          // No point found - hide tooltip and remove glow
        overlay.style.display = 'none';
          if (lastHoveredDatasetIndex >= 0) {
            const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
            if (prevButton) {
              prevButton.classList.remove('toggle-button-neon-glow');
              prevButton.style.color = '';
            }
            lastHoveredDatasetIndex = -1;
          }
        }
      };
      chartCanvas.addEventListener('mousemove', mousemoveHandler);
      
      mouseleaveHandler = function() {
        if (overlay) overlay.style.display = 'none';
        // Remove glow from any hovered button
        if (lastHoveredDatasetIndex >= 0) {
          const prevButton = document.querySelector(`button[data-dataset-index="${lastHoveredDatasetIndex}"]`);
          if (prevButton) {
            prevButton.classList.remove('toggle-button-neon-glow');
            prevButton.style.color = '';
          }
          lastHoveredDatasetIndex = -1;
        }
      };
      chartCanvas.addEventListener('mouseleave', mouseleaveHandler);
    }
  }
  
  // Global function to refresh team statistics (called from HTML button)
  window.refreshTeamStatistics = function() {
    console.log('🔄 Refreshing team statistics with force recalculation...');
    const selectedCategory = categorySelect.value || '';
    loadTeamStatistics(selectedCategory, true); // true = force refresh
  };
  
  // Global function to toggle chart zoom (called from HTML button)
  window.toggleChartZoom = function() {
    // Toggle zoom state
    chartZoomedOut = !chartZoomedOut;
    
    // Update button text and icon
    const zoomBtn = document.getElementById('zoomOutBtn');
    if (zoomBtn) {
      if (chartZoomedOut) {
        zoomBtn.innerHTML = '<i class="fas fa-search-plus me-1"></i>Zoom In';
        zoomBtn.title = 'Zoom in to see 4 games at a time';
      } else {
        zoomBtn.innerHTML = '<i class="fas fa-search-minus me-1"></i>Zoom Out';
        zoomBtn.title = 'Zoom out to see all games';
      }
    }
    
    // Reload the chart with new zoom state
    console.log('🔍 Toggling chart zoom:', chartZoomedOut ? 'Zoomed Out (all games)' : 'Zoomed In (4 games)');
    const selectedCategory = categorySelect.value || '';
    loadTeamStatistics(selectedCategory, false);
  };
  
  // Load statistics on page load
  loadTeamStatistics();
  
  // Systems Check Functions
  async function runSystemsCheck() {
    const container = document.getElementById('systemsCheckContainer');
    if (!container) return;
    
    container.innerHTML = '<div class="text-center text-muted py-2"><i class="fas fa-spinner fa-spin"></i> Running systems check...</div>';
    
    try {
      const response = await fetch('/systems-check/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: window.location.origin })
      });
      
      const data = await response.json();
      
      if (data.success) {
        displaySystemsCheck(data.data);
      } else {
        container.innerHTML = `<div class="alert alert-danger">Error: ${data.error || 'Unknown error'}</div>`;
      }
    } catch (error) {
      container.innerHTML = `<div class="alert alert-danger">Error running systems check: ${error.message}</div>`;
    }
  }
  
  function displaySystemsCheck(results) {
    const container = document.getElementById('systemsCheckContainer');
    if (!container) return;
    
    // Determine status color
    let statusColor = '#F9423A'; // unhealthy
    let statusClass = 'status-unhealthy';
    if (results.score >= 80) {
      statusColor = '#00ff00';
      statusClass = 'status-healthy';
    } else if (results.score >= 50) {
      statusColor = '#ffa500';
      statusClass = 'status-degraded';
    }
    
    let html = `
      <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">System Health Score</div>
        <div style="font-size: 3rem; font-weight: 900; color: ${statusColor}; text-shadow: 0 0 20px ${statusColor}80; margin: 10px 0;">
          ${results.score}%
        </div>
        <span class="status-badge ${statusClass}" style="display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">
          ${results.status}
        </span>
      </div>
      
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 20px;">
        <div style="background: rgba(249,66,58,0.1); border: 1px solid rgba(249,66,58,0.3); border-radius: 8px; padding: 10px; text-align: center;">
          <div style="font-size: 1.5rem; font-weight: 700; color: #F9423A;">${results.total_checks}</div>
          <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Total</div>
        </div>
        <div style="background: rgba(0,255,0,0.1); border: 1px solid rgba(0,255,0,0.3); border-radius: 8px; padding: 10px; text-align: center;">
          <div style="font-size: 1.5rem; font-weight: 700; color: #00ff00;">${results.passed}</div>
          <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Passed</div>
        </div>
        <div style="background: rgba(255,165,0,0.1); border: 1px solid rgba(255,165,0,0.3); border-radius: 8px; padding: 10px; text-align: center;">
          <div style="font-size: 1.5rem; font-weight: 700; color: #ffa500;">${results.warnings}</div>
          <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Warnings</div>
        </div>
        <div style="background: rgba(249,66,58,0.1); border: 1px solid rgba(249,66,58,0.3); border-radius: 8px; padding: 10px; text-align: center;">
          <div style="font-size: 1.5rem; font-weight: 700; color: #F9423A;">${results.failed + results.errors}</div>
          <div style="font-size: 0.75rem; color: rgba(255,255,255,0.6);">Failed</div>
        </div>
      </div>
      
      <div style="max-height: 400px; overflow-y: auto;">
    `;
    
    results.checks.forEach(check => {
      let statusColor = '#F9423A';
      let statusBg = 'rgba(249,66,58,0.1)';
      let statusBorder = 'rgba(249,66,58,0.3)';
      
      if (check.status === 'pass') {
        statusColor = '#00ff00';
        statusBg = 'rgba(0,255,0,0.1)';
        statusBorder = 'rgba(0,255,0,0.3)';
      } else if (check.status === 'warn') {
        statusColor = '#ffa500';
        statusBg = 'rgba(255,165,0,0.1)';
        statusBorder = 'rgba(255,165,0,0.3)';
      } else if (check.status === 'error') {
        statusColor = '#808080';
        statusBg = 'rgba(128,128,128,0.1)';
        statusBorder = 'rgba(128,128,128,0.3)';
      }
      
      html += `
        <div style="background: #000; border: 1px solid ${statusBorder}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: 600; color: #fff;">${check.name}</div>
            <span style="padding: 4px 12px; border-radius: 15px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; background: ${statusBg}; color: ${statusColor}; border: 1px solid ${statusBorder};">
              ${check.status}
            </span>
          </div>
          <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: ${check.details && check.details.length > 0 ? '8px' : '0'};">
            ${check.message}
          </div>
          ${check.details && check.details.length > 0 ? `
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
              ${check.details.map(detail => `<div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; font-family: monospace; padding: 2px 0;">${detail}</div>`).join('')}
            </div>
          ` : ''}
        </div>
      `;
    });
    
    html += '</div>';
    container.innerHTML = html;
  }
  
  // Run systems check on page load
  if (document.getElementById('systemsCheckContainer')) {
    runSystemsCheck();
  }
  
  // Handle category selector change - ensure it works properly
  categorySelect.addEventListener('change', function() {
    const selectedCategory = this.value;
    console.log('Category changed to:', selectedCategory || 'All Categories');
    
    // Clear any existing chart and buttons before loading new data
    if (statisticsChart) {
      statisticsChart.destroy();
      statisticsChart = null;
    }
    
    // Reset slider binding so it can be reinitialized
    const sliderContainer = document.getElementById('teamStatsPrecisionSlider');
    if (sliderContainer) {
      sliderContainer.dataset.bound = '0';
      sliderContainer.innerHTML = '';
    }
    
    // Clear toggle buttons container
    const toggleContainer = document.getElementById('statisticsDatasetToggles');
    if (toggleContainer) {
      toggleContainer.innerHTML = '';
    }
    
    // Clear overall scores list
    const scoresList = document.getElementById('overallScoresList');
    if (scoresList) {
      scoresList.innerHTML = '';
    }
    
    // Load statistics for the selected category (empty string = all categories)
    loadTeamStatistics(selectedCategory || '');
  });

  // Leaderboard Functions
  let leaderboardData = [];
  let currentSortColumn = 'overall';
  let currentSortDirection = 'desc'; // 'asc' or 'desc'
  
  async function loadLeaderboard() {
    try {
      const response = await fetch('/api/team-statistics');
      const data = await response.json();
      
      if (!data.success || !data.statistics) {
        document.getElementById('leaderboardBody').innerHTML = 
          '<tr><td colspan="10" class="text-center text-muted">No data available</td></tr>';
        return;
      }
      
      // Transform statistics array into games-by-categories matrix
      const gamesMap = new Map();
      const categories = new Set();
      
      // Process all statistics
      data.statistics.forEach(stat => {
        const date = stat.date;
        if (!gamesMap.has(date)) {
          gamesMap.set(date, {
            date: date,
            date_string: stat.date_string || date,
            opponent: stat.opponent || 'Unknown',
            overall: data.overall_scores?.[date] || 0,
            categories: {}
          });
        }
        
        const game = gamesMap.get(date);
        game.categories[stat.category] = stat.percentage;
        categories.add(stat.category);
      });
      
      // Convert to array and sort by overall score (default)
      leaderboardData = Array.from(gamesMap.values());
      sortLeaderboardData('overall', 'desc');
      
      // Render the table
      renderLeaderboard(Array.from(categories).sort());
      
    } catch (error) {
      console.error('Error loading leaderboard:', error);
      document.getElementById('leaderboardBody').innerHTML = 
        '<tr><td colspan="10" class="text-center text-danger">Error loading leaderboard</td></tr>';
    }
  }
  
  function sortLeaderboardData(column, direction) {
    leaderboardData.sort((a, b) => {
      let aVal, bVal;
      
      if (column === 'date') {
        aVal = new Date(a.date);
        bVal = new Date(b.date);
      } else if (column === 'opponent') {
        aVal = a.opponent.toLowerCase();
        bVal = b.opponent.toLowerCase();
      } else if (column === 'overall') {
        aVal = a.overall || 0;
        bVal = b.overall || 0;
      } else {
        // Category column
        aVal = a.categories[column] || 0;
        bVal = b.categories[column] || 0;
      }
      
      if (direction === 'asc') {
        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
      } else {
        return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
      }
    });
  }
  
  function sortLeaderboard(column) {
    // Toggle direction if same column, otherwise default to desc
    if (currentSortColumn === column) {
      currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      currentSortColumn = column;
      currentSortDirection = 'desc';
    }
    
    sortLeaderboardData(column, currentSortDirection);
    
    // Re-render with updated sort indicators
    const categories = Array.from(new Set(leaderboardData.flatMap(g => Object.keys(g.categories)))).sort();
    renderLeaderboard(categories);
  }
  
  function renderLeaderboard(categories) {
    const header = document.getElementById('leaderboardHeader');
    const body = document.getElementById('leaderboardBody');
    
    // Build header row
    let headerHTML = `
      <tr>
        <th style="cursor: pointer;" onclick="sortLeaderboard('rank')">
          Rank ${getSortIcon('rank')}
        </th>
        <th style="cursor: pointer;" onclick="sortLeaderboard('date')">
          Date ${getSortIcon('date')}
        </th>
        <th style="cursor: pointer;" onclick="sortLeaderboard('opponent')">
          Opponent ${getSortIcon('opponent')}
        </th>
        <th style="cursor: pointer;" onclick="sortLeaderboard('overall')">
          Overall ${getSortIcon('overall')}
        </th>
    `;
    
    categories.forEach(cat => {
      headerHTML += `
        <th class="category-column" style="cursor: pointer;" onclick="sortLeaderboard('${cat}')">
          ${cat} ${getSortIcon(cat)}
        </th>
      `;
    });
    
    headerHTML += '</tr>';
    header.innerHTML = headerHTML;
    
    // Build body rows
    let bodyHTML = '';
    leaderboardData.forEach((game, index) => {
      const rank = index + 1;
      const dateStr = game.date_string || game.date;
      const opponent = game.opponent || 'Unknown';
      const overall = game.overall || 0;
      
      // Format date for display
      let displayDate = dateStr;
      try {
        const date = new Date(game.date);
        displayDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      } catch (e) {
        // Keep original if parsing fails
      }
      
      bodyHTML += `
        <tr>
          <td><strong>#${rank}</strong></td>
          <td>${displayDate}</td>
          <td>${opponent}</td>
          <td><strong>${overall.toFixed(2)}%</strong></td>
      `;
      
      categories.forEach(cat => {
        const value = game.categories[cat] || 0;
        const colorClass = getPercentageColorClass(value);
        bodyHTML += `
          <td class="category-column ${colorClass}">${value.toFixed(2)}%</td>
        `;
      });
      
      bodyHTML += '</tr>';
    });
    
    if (bodyHTML === '') {
      bodyHTML = '<tr><td colspan="' + (4 + categories.length) + '" class="text-center text-muted">No games found</td></tr>';
    }
    
    body.innerHTML = bodyHTML;
  }
  
  function getSortIcon(column) {
    if (currentSortColumn !== column) {
      return '<i class="fas fa-sort text-muted"></i>';
    }
    return currentSortDirection === 'asc' 
      ? '<i class="fas fa-sort-up text-warning"></i>' 
      : '<i class="fas fa-sort-down text-warning"></i>';
  }
  
  function getPercentageColorClass(value) {
    if (value >= 80) return 'text-success';
    if (value >= 60) return 'text-info';
    if (value >= 40) return 'text-warning';
    return 'text-danger';
  }
  
  // Make functions globally accessible
  window.loadLeaderboard = loadLeaderboard;
  window.sortLeaderboard = sortLeaderboard;
  
  // Load leaderboard on page load
  if (document.getElementById('leaderboardTable')) {
    loadLeaderboard();
  }

  // Games Dashboard Functions
  async function loadGamesDashboard() {
    const container = document.getElementById('gamesDashboardContainer');
    if (!container) return;

    try {
      container.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-spinner fa-spin"></i> Loading games...</div>';
      
      const response = await fetch('/api/games-dashboard');
      const data = await response.json();
      
      if (!data.success) {
        container.innerHTML = `<div class="alert alert-danger">Error loading games: ${data.error || 'Unknown error'}</div>`;
        return;
      }
      
      renderGamesDashboard(data.games || []);
    } catch (error) {
      console.error('Error loading games dashboard:', error);
      container.innerHTML = `<div class="alert alert-danger">Error loading games dashboard. Please refresh the page.</div>`;
    }
  }

  function renderGamesDashboard(games) {
    const container = document.getElementById('gamesDashboardContainer');
    if (!container) return;

    if (games.length === 0) {
      container.innerHTML = '<div class="text-center text-muted py-4">No games found in database.</div>';
      return;
    }

    // Category colors for display
    const categoryColors = {
      'Space Read': '#FF9800',                 // Orange
      'DM Catch': '#00E5FF',                   // Bright cyan
      'Driving': '#2196F3',                    // Bright blue
      'Finishing': '#FFD700',                  // Gold
      'Footwork': '#00FF88',                   // Bright green
      'Passing': '#FF6B00',                    // Bright orange
      'Positioning': '#9C27B0',                // Bright purple
      'QB12 DM': '#FF00FF',                    // Magenta
      'Relocation': '#00BCD4',                 // Cyan-blue
      'Cutting & Screening': '#FF1744',        // Bright red
      'Transition': '#2196F3'                 // Bright blue
    };

    let html = '<div class="table-responsive"><table class="table table-dark table-hover">';
    html += '<thead><tr>';
    html += '<th>Date</th>';
    html += '<th>Opponent</th>';
    html += '<th>Overall Score</th>';
    html += '<th>Categories</th>';
    html += '</tr></thead><tbody>';

    games.forEach(game => {
      const dateStr = game.date_string || new Date(game.date * 1000).toLocaleDateString();
      const overallScore = game.overall_score !== null && game.overall_score !== undefined 
        ? game.overall_score.toFixed(4) + '%' 
        : 'N/A';
      
      // Build category breakdown
      let categoriesHtml = '';
      if (game.categories && Object.keys(game.categories).length > 0) {
        const categoryItems = Object.entries(game.categories)
          .map(([cat, score]) => {
            const color = categoryColors[cat] || '#CCCCCC';
            return `<span class="badge" style="background-color: ${color}; margin: 2px; color: #000; font-weight: bold;">${cat}: ${score.toFixed(4)}%</span>`;
          })
          .join('');
        categoriesHtml = `<div class="d-flex flex-wrap">${categoryItems}</div>`;
      } else {
        categoriesHtml = '<span class="text-muted">No category data</span>';
      }

      html += '<tr>';
      html += `<td><strong>${dateStr}</strong></td>`;
      html += `<td>${game.opponent || 'Unknown'}</td>`;
      html += `<td><span class="badge" style="background-color: #F9423A; color: #fff; font-size: 1em; padding: 6px 12px;">${overallScore}</span></td>`;
      html += `<td>${categoriesHtml}</td>`;
      html += '</tr>';
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
  }

  // Load games dashboard on page load
  loadGamesDashboard();
  
  // Export Premium Report functionality
  const exportBtn = document.getElementById('exportPremiumReportBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', async function() {
      try {
        // Disable button and show loading
        exportBtn.disabled = true;
        const originalText = exportBtn.innerHTML;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading Chart...';
        
        // Ensure chart exists - if not, load it first
        if (!statisticsChart) {
          console.log('Chart not found, loading statistics...');
          await loadTeamStatistics(categorySelect.value || '');
          // Wait a bit for chart to render
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Check again after loading - if still no chart, there's likely no data
        if (!statisticsChart) {
          // Try to get data first to see if there's any
          const testUrl = categorySelect.value 
            ? `/api/team-statistics?category=${encodeURIComponent(categorySelect.value)}`
            : '/api/team-statistics';
          const testResponse = await fetch(testUrl);
          const testData = await testResponse.json();
          
          if (!testData.success || !testData.statistics || testData.statistics.length === 0) {
            alert('No statistics data available to export. Please upload game CSV files first using the "Clear & Rebuild" feature or upload files via SmartDash.');
            exportBtn.disabled = false;
            exportBtn.innerHTML = originalText;
            return;
          }
          
          // If we have data but no chart, try one more time
          await loadTeamStatistics(categorySelect.value || '');
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          if (!statisticsChart) {
            alert('Unable to generate chart. Please refresh the page and try again.');
            exportBtn.disabled = false;
            exportBtn.innerHTML = originalText;
            return;
          }
        }
        
        if (!chartCanvas) {
          alert('Chart canvas not found. Please refresh the page.');
          exportBtn.disabled = false;
          exportBtn.innerHTML = originalText;
          return;
        }
        
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Report...';
        
        // Capture chart as high-resolution image
        // Note: Chart.js doesn't support DPI parameter, but we can scale the canvas
        const originalWidth = chartCanvas.width;
        const originalHeight = chartCanvas.height;
        const scale = 2; // 2x for higher resolution
        
        // Temporarily scale canvas for export
        chartCanvas.width = originalWidth * scale;
        chartCanvas.height = originalHeight * scale;
        statisticsChart.resize();
        await new Promise(resolve => setTimeout(resolve, 100)); // Wait for resize
        const chartImage = statisticsChart.toBase64Image('image/png');
        
        // Restore original size
        chartCanvas.width = originalWidth;
        chartCanvas.height = originalHeight;
        statisticsChart.resize();
        
        // Get current statistics data
        const category = categorySelect.value || '';
        const url = category 
          ? `/api/team-statistics?category=${encodeURIComponent(category)}`
          : '/api/team-statistics';
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (!data.success || !data.statistics) {
          throw new Error(data.error || 'Failed to load statistics data');
        }
        
        // Calculate analytics insights
        const insights = calculateInsights(data.statistics, data.overall_scores || {}, data.game_info || {});
        
        // Send to backend for PDF generation
        const exportResponse = await fetch('/api/team-statistics/export-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chart_image: chartImage,
            statistics: data.statistics,
            overall_scores: data.overall_scores || {},
            game_info: data.game_info || {},
            category: category,
            insights: insights
          })
        });
        
        if (!exportResponse.ok) {
          throw new Error('Failed to generate PDF');
        }
        
        // Download the PDF
        const blob = await exportResponse.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `heat_team_statistics_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(blobUrl);
        document.body.removeChild(a);
        
        alert('✅ Premium report generated successfully!');
      } catch (error) {
        console.error('Error exporting report:', error);
        alert('Error generating report: ' + error.message);
      } finally {
        exportBtn.disabled = false;
        const originalText = '<i class="fas fa-file-pdf me-2"></i>Export Premium Report';
        exportBtn.innerHTML = originalText;
      }
    });
  }
  
  // Calculate insights from statistics data
  function calculateInsights(statistics, overallScores, gameInfo) {
    const insights = {
      top_categories: [],
      weak_categories: [],
      improving_categories: [],
      declining_categories: [],
      stats_summary: {},
      trends: []
    };
    
    // Group by category
    const categoryData = {};
    statistics.forEach(stat => {
      if (!categoryData[stat.category]) {
        categoryData[stat.category] = [];
      }
      categoryData[stat.category].push(stat);
    });
    
    // Calculate averages and trends for each category
    Object.keys(categoryData).forEach(cat => {
      const data = categoryData[cat].sort((a, b) => a.date.localeCompare(b.date));
      const percentages = data.map(d => d.percentage);
      const avg = percentages.reduce((a, b) => a + b, 0) / percentages.length;
      
      // Calculate trend (improving if last > first)
      const trend = percentages.length > 1 ? percentages[percentages.length - 1] - percentages[0] : 0;
      
      insights.stats_summary[cat] = {
        average: avg.toFixed(5),
        min: Math.min(...percentages).toFixed(5),
        max: Math.max(...percentages).toFixed(5),
        trend: trend.toFixed(5),
        count: percentages.length
      };
      
      if (trend > 2) {
        insights.improving_categories.push({ category: cat, trend: trend.toFixed(5), average: avg.toFixed(5) });
      } else if (trend < -2) {
        insights.declining_categories.push({ category: cat, trend: trend.toFixed(5), average: avg.toFixed(5) });
      }
    });
    
    // Sort by average to find top and weak categories
    const sortedByAvg = Object.keys(categoryData).map(cat => ({
      category: cat,
      average: parseFloat(insights.stats_summary[cat].average)
    })).sort((a, b) => b.average - a.average);
    
    insights.top_categories = sortedByAvg.slice(0, 3).map(c => ({ 
      category: c.category, 
      average: c.average.toFixed(5) 
    }));
    insights.weak_categories = sortedByAvg.slice(-3).reverse().map(c => ({ 
      category: c.category, 
      average: c.average.toFixed(5) 
    }));
    
    // Overall scores trend
    const overallDates = Object.keys(overallScores).sort();
    if (overallDates.length > 1) {
      const firstScore = overallScores[overallDates[0]];
      const lastScore = overallScores[overallDates[overallDates.length - 1]];
      insights.overall_trend = (lastScore - firstScore).toFixed(5);
      insights.overall_average = (Object.values(overallScores).reduce((a, b) => a + b, 0) / Object.values(overallScores).length).toFixed(5);
    }
    
    return insights;
  }
})();

/**
 * Advanced Visualization Modules (Temporal, Pressure, Team Insights)
 */
(function() {
  const modeButtons = document.querySelectorAll('[data-analytics-mode]');
  const sections = {
    standard: document.getElementById('standardAnalyticsSection'),
    temporal: document.getElementById('temporalSection'),
    pressure: document.getElementById('pressureSection'),
    'team-insights': document.getElementById('teamInsightsSection')
  };
  
  let activeMode = 'standard';
  let temporalCache = null;
  let pressureCache = null;
  let insightsCache = null;
  
  function setMode(mode) {
    if (!sections.standard) {
      return;
    }
    activeMode = mode;
    Object.entries(sections).forEach(([key, el]) => {
      if (!el) return;
      if (key === 'standard') {
        el.style.display = (mode === 'standard') ? 'block' : 'none';
      } else {
        el.style.display = (mode === key) ? 'block' : 'none';
      }
    });
    
    modeButtons.forEach(btn => {
      const btnMode = btn.getAttribute('data-analytics-mode');
      btn.classList.toggle('active', btnMode === mode);
    });
    
    if (mode === 'temporal') {
      loadTemporalVisualization();
    } else if (mode === 'pressure') {
      loadPressureVisualization();
    } else if (mode === 'team-insights') {
      loadTeamInsights();
    }
  }
  
  function getPhaseColor(phase) {
    const colors = {
      Early: '#00bcd4',
      Middle: '#ff9800',
      Late: '#F9423A',
      Unknown: '#9e9e9e'
    };
    return colors[phase] || '#9e9e9e';
  }
  
  async function loadTemporalVisualization(force = false) {
    if (temporalCache && !force) {
      renderTemporalChart(temporalCache);
      return;
    }
    try {
      const res = await fetch('/api/analytics/time-series');
      const json = await res.json();
      if (!json.success) {
        showTemporalMessage('Unable to load temporal analytics.');
        return;
      }
      temporalCache = json.events || [];
      renderTemporalChart(temporalCache);
    } catch (err) {
      console.error('Temporal analytics error', err);
      showTemporalMessage('Unexpected error loading temporal analytics.');
    }
  }
  
  function showTemporalMessage(message) {
    const insightsEl = document.getElementById('temporalInsights');
    const chartEl = document.getElementById('temporalChart');
    if (chartEl && window.Plotly) {
      Plotly.purge(chartEl);
    }
    if (insightsEl) {
      insightsEl.textContent = message;
    }
  }
  
  function renderTemporalChart(events) {
    const chartEl = document.getElementById('temporalChart');
    const insightsEl = document.getElementById('temporalInsights');
    if (!chartEl || !window.Plotly) {
      return;
    }
    
    const scoredEvents = (events || []).filter(ev => typeof ev.cognitive_score === 'number');
    if (!scoredEvents.length) {
      showTemporalMessage('No possession data available yet. Import a CSV to unlock temporal analytics.');
      return;
    }
    
    const quarters = Array.from(new Set(scoredEvents.map(ev => ev.quarter || 'All')));
    if (!quarters.includes('All')) {
      quarters.unshift('All');
    }
    const baseTrace = {
      x: scoredEvents.map(ev => ev.timestamp ?? scoredEvents.indexOf(ev)),
      y: scoredEvents.map(ev => ev.cognitive_score),
      mode: 'markers',
      marker: {
        color: scoredEvents.map(ev => getPhaseColor(ev.shot_clock_phase)),
        size: 10,
        line: { width: 1, color: '#ffffff' }
      },
      text: scoredEvents.map(ev => {
        const phase = ev.shot_clock_phase || 'Unknown';
        const outcome = ev.shot_outcome || 'N/A';
        const timeLabel = typeof ev.timestamp === 'number'
          ? `${(ev.timestamp / 60).toFixed(1)} min`
          : `Event ${scoredEvents.indexOf(ev) + 1}`;
        return `${timeLabel}<br>Phase: ${phase}<br>Score: ${ev.cognitive_score.toFixed(1)}<br>Outcome: ${outcome}`;
      }),
      hoverinfo: 'text'
    };
    
    const frames = quarters.map(q => {
      const subset = q === 'All' ? scoredEvents : scoredEvents.filter(ev => ev.quarter === q);
      return {
        name: q,
        data: [{
          x: subset.map(ev => ev.timestamp ?? scoredEvents.indexOf(ev)),
          y: subset.map(ev => ev.cognitive_score),
          mode: 'markers',
          marker: {
            color: subset.map(ev => getPhaseColor(ev.shot_clock_phase)),
            size: 11,
            line: { width: 1, color: '#ffffff' }
          },
          text: subset.map(ev => {
            const phase = ev.shot_clock_phase || 'Unknown';
            const outcome = ev.shot_outcome || 'N/A';
            const timeLabel = typeof ev.timestamp === 'number'
              ? `${(ev.timestamp / 60).toFixed(1)} min`
              : `Event ${scoredEvents.indexOf(ev) + 1}`;
            return `${timeLabel}<br>Phase: ${phase}<br>Score: ${ev.cognitive_score?.toFixed(1) ?? '—'}<br>Outcome: ${outcome}`;
          })
        }]
      };
    });
    
    const sliderSteps = frames.map(frame => ({
      label: frame.name,
      method: 'animate',
      args: [[frame.name], { mode: 'immediate', transition: { duration: 0 }, frame: { duration: 450, redraw: true } }]
    }));
    
    const layout = {
      paper_bgcolor: '#000',
      plot_bgcolor: '#000',
      font: { color: '#fff' },
      xaxis: {
        title: 'Timeline (seconds)',
        color: '#fff'
      },
      yaxis: {
        title: 'Cognitive Score',
        range: [0, 100],
        color: '#fff'
      },
      updatemenus: [{
        type: 'buttons',
        showactive: false,
        x: 0.05,
        y: 1.15,
        buttons: [
          {
            label: 'Play',
            method: 'animate',
            args: [null, { fromcurrent: true, transition: { duration: 200 }, frame: { duration: 450, redraw: true } }]
          },
          {
            label: 'Pause',
            method: 'animate',
            args: [[null], { mode: 'immediate', transition: { duration: 0 }, frame: { duration: 0 } }]
          }
        ]
      }],
      sliders: [{
        pad: { l: 80, t: 35 },
        currentvalue: { visible: true, prefix: 'Quarter: ', font: { color: '#fff', size: 14 } },
        steps: sliderSteps
      }]
    };
    
    Plotly.newPlot(chartEl, [baseTrace], layout, { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d'] })
      .then(() => {
        if (frames.length > 0) {
          Plotly.addFrames(chartEl, frames);
        }
      });
    
    if (insightsEl) {
      const latePhase = scoredEvents.filter(ev => ev.shot_clock_phase === 'Late');
      const lateAvg = latePhase.length ? latePhase.reduce((sum, ev) => sum + ev.cognitive_score, 0) / latePhase.length : null;
      const earlyPhase = scoredEvents.filter(ev => ev.shot_clock_phase === 'Early');
      const earlyAvg = earlyPhase.length ? earlyPhase.reduce((sum, ev) => sum + ev.cognitive_score, 0) / earlyPhase.length : null;
      let text = '';
      if (lateAvg !== null && earlyAvg !== null) {
        const delta = (lateAvg - earlyAvg).toFixed(1);
        text = `Late clock possessions average ${lateAvg.toFixed(1)} vs ${earlyAvg.toFixed(1)} early clock (${delta} net change).`;
      } else {
        text = 'Insufficient data for clock-phase comparison.';
      }
      insightsEl.textContent = text;
    }
  }
  
  async function loadPressureVisualization(force = false) {
    if (pressureCache && !force) {
      renderPressureHeatmap(pressureCache);
      return;
    }
    try {
      const res = await fetch('/api/analytics/pressure-summary');
      const json = await res.json();
      if (!json.success) {
        renderPressureHeatmap({ phases: [], quarter_grid: [] });
        return;
      }
      pressureCache = json;
      renderPressureHeatmap(json);
    } catch (err) {
      console.error('Pressure summary error', err);
    }
  }
  
  function renderPressureHeatmap(summary) {
    const container = document.getElementById('pressureHeatmap');
    const insightsEl = document.getElementById('pressureInsights');
    if (!container || !window.Plotly) return;
    
    const phases = ['Early', 'Middle', 'Late', 'Unknown'];
    const order = ['Q1', 'Q2', 'Q3', 'Q4', 'OT', 'Q?'];
    const quarterSet = new Set(summary.quarter_grid?.map(item => item.quarter || 'Q?'));
    const quarters = Array.from(quarterSet).sort((a, b) => order.indexOf(a) - order.indexOf(b));
    if (!quarters.length) {
      container.innerHTML = '<div class="text-muted">No shot clock data available yet.</div>';
      if (insightsEl) {
        insightsEl.textContent = '';
      }
      return;
    }
    
    const z = phases.map(phase => quarters.map(q => {
      const match = (summary.quarter_grid || []).find(item => item.quarter === q && item.phase === phase);
      return match ? (match.avg_score ?? 0) : 0;
    }));
    
    const text = phases.map(phase => quarters.map(q => {
      const match = (summary.quarter_grid || []).find(item => item.quarter === q && item.phase === phase);
      if (!match) return `Phase: ${phase}<br>${q}<br>No data`;
      return `Phase: ${phase}<br>${q}<br>Avg Score: ${match.avg_score?.toFixed(1) ?? '—'}<br>Possessions: ${match.possessions}`;
    }));
    
    Plotly.newPlot(container, [{
      z,
      x: quarters,
      y: phases,
      type: 'heatmap',
      colorscale: 'Jet',
      hoverinfo: 'text',
      text
    }], {
      paper_bgcolor: '#000',
      plot_bgcolor: '#000',
      font: { color: '#fff' },
      xaxis: { title: 'Quarter', color: '#fff' },
      yaxis: { title: 'Shot Clock Phase', color: '#fff' },
      margin: { t: 40, r: 20, b: 40, l: 80 }
    }, { responsive: true, displaylogo: false });
    
    if (insightsEl && summary.phases) {
      const sorted = [...summary.phases].sort((a, b) => (b.avg_score || 0) - (a.avg_score || 0));
      if (sorted.length) {
        const best = sorted[0];
        const worst = sorted[sorted.length - 1];
        const diff = ((best.avg_score || 0) - (worst.avg_score || 0)).toFixed(1);
        insightsEl.innerHTML = `
          <div>Most efficient phase: <strong>${best.phase}</strong> (${(best.avg_score || 0).toFixed(1)}).</div>
          <div>Gap to ${worst.phase}: ${diff} pts.</div>
        `;
      } else {
        insightsEl.textContent = '';
      }
    }
  }
  
  async function loadTeamInsights(force = false) {
    if (insightsCache && !force) {
      renderTeamInsights(insightsCache);
      return;
    }
    try {
      const res = await fetch('/api/analytics/team-insights');
      const json = await res.json();
      if (!json.success) {
        return;
      }
      insightsCache = json;
      renderTeamInsights(json);
    } catch (err) {
      console.error('Team insights error', err);
    }
  }
  
  function renderTeamInsights(data) {
    if (!window.Plotly) return;
    renderRadarChart(data.radar || {});
    renderSynergyMatrix(data.synergy || {});
    renderEpaWaterfall(data.epa || {});
    renderCoachInsights(data);
  }
  
  function renderRadarChart(radarData) {
    const container = document.getElementById('teamRadarChart');
    if (!container || !radarData.labels || !radarData.labels.length) return;
    Plotly.newPlot(container, [{
      type: 'scatterpolar',
      r: radarData.team_average || [],
      theta: radarData.labels,
      fill: 'toself',
      name: 'Heat',
      line: { color: '#F9423A' }
    }, {
      type: 'scatterpolar',
      r: radarData.opponent_pressure || [],
      theta: radarData.labels,
      fill: 'toself',
      name: 'Opponent Pressure',
      line: { color: '#00bcd4' }
    }], {
      polar: {
        bgcolor: '#000',
        radialaxis: { visible: true, range: [0, 100], color: '#fff' },
        angularaxis: { color: '#fff' }
      },
      paper_bgcolor: '#000',
      legend: { orientation: 'h', x: 0.1, y: -0.2 }
    }, { responsive: true, displaylogo: false });
  }
  
  function renderSynergyMatrix(synergy) {
    const container = document.getElementById('synergyMatrix');
    if (!container || !synergy.players || !synergy.players.length || !window.Plotly) return;
    Plotly.newPlot(container, [{
      z: synergy.matrix || [],
      x: synergy.players,
      y: synergy.players,
      type: 'heatmap',
      colorscale: 'Viridis',
      hoverongaps: false,
      hovertemplate: 'Lineup: %{y} + %{x}<br>Avg Score: %{z:.1f}<extra></extra>'
    }], {
      paper_bgcolor: '#000',
      plot_bgcolor: '#000',
      font: { color: '#fff' },
      margin: { t: 10 }
    }, { responsive: true, displaylogo: false });
  }
  
  function renderEpaWaterfall(epa) {
    const container = document.getElementById('epaWaterfallChart');
    if (!container || !epa.stages || !epa.stages.length || !window.Plotly) return;
    
    const x = ['Baseline'].concat(epa.stages.map(stage => stage.label)).concat(['Result']);
    const measures = ['absolute']
      .concat(Array(epa.stages.length).fill('relative'))
      .concat(['total']);
    const y = [epa.baseline || 50]
      .concat(epa.stages.map(stage => stage.delta || 0))
      .concat([epa.final || epa.baseline || 50]);
    
    Plotly.newPlot(container, [{
      type: 'waterfall',
      x,
      y,
      measure: measures,
      decreasing: { marker: { color: '#F9423A' } },
      increasing: { marker: { color: '#00ff00' } },
      totals: { marker: { color: '#2196f3' } },
      connector: { line: { color: '#ffffff' } }
    }], {
      paper_bgcolor: '#000',
      plot_bgcolor: '#000',
      font: { color: '#fff' },
      margin: { t: 10 }
    }, { responsive: true, displaylogo: false });
  }
  
  function renderCoachInsights(data) {
    const list = document.getElementById('coachInsightsList');
    if (!list) return;
    const insights = [];
    if (data.epa && Array.isArray(data.epa.insights)) {
      insights.push(...data.epa.insights);
    }
    const synergy = data.synergy;
    if (synergy && synergy.players && synergy.matrix) {
      let bestPair = null;
      let bestScore = -Infinity;
      synergy.players.forEach((player, i) => {
        synergy.players.forEach((partner, j) => {
          if (i >= j) return;
          const value = synergy.matrix[i][j];
          if (value !== null && value !== undefined && value > bestScore) {
            bestScore = value;
            bestPair = `${player} + ${partner}`;
          }
        });
      });
      if (bestPair) {
        insights.push(`Top synergy pairing: ${bestPair} (${bestScore.toFixed(1)})`);
      }
    }
    
    if (!insights.length) {
      list.innerHTML = '<div class="text-muted">No insights yet.</div>';
      return;
    }
    
    list.innerHTML = `<ul class="mb-0">${insights.map(item => `<li>${item}</li>`).join('')}</ul>`;
  }
  
  if (modeButtons.length) {
    modeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-analytics-mode');
        setMode(mode);
      });
    });
  }
  
  setMode('standard');
  
  window.refreshAdvancedVisualizations = function() {
    temporalCache = null;
    pressureCache = null;
    insightsCache = null;
    if (activeMode !== 'standard') {
      setMode(activeMode);
    }
  };
})();

/**
 * Auto-refresh analytics when new game is uploaded
 */
(function() {
  // Listen for new game uploads from database-viz page
  window.addEventListener('newGameUploaded', function(event) {
    console.log('New game uploaded, refreshing analytics...', event.detail);
    
    // Reload team statistics
    if (typeof loadTeamStatistics === 'function') {
      loadTeamStatistics('', true);
    }
    
    // Reload team series/scores
    if (typeof loadTeamSeries === 'function') {
      loadTeamSeries();
    }
    
    if (typeof refreshAdvancedVisualizations === 'function') {
      refreshAdvancedVisualizations();
    }
    
    // Show notification
    showNotificationBanner('New game data imported! Dashboard updated.', 'success');
  });
  
  // Check localStorage on page load for recent uploads
  if (typeof loadTeamStatistics === 'function') {
    const lastUpload = localStorage.getItem('lastGameUpload');
    if (lastUpload) {
      try {
        const uploadData = JSON.parse(lastUpload);
        const uploadTime = uploadData.timestamp;
        const now = Date.now();
        
        // If upload was within last 5 minutes, show notification
        if (now - uploadTime < 5 * 60 * 1000) {
          setTimeout(() => {
            showNotificationBanner(
              `Recent upload detected: ${uploadData.date} vs ${uploadData.opponent}`, 
              'info'
            );
          }, 1000);
        }
      } catch (e) {
        console.error('Error parsing lastGameUpload:', e);
      }
    }
  }
  
  function showNotificationBanner(message, type = 'info') {
    const banner = document.createElement('div');
    banner.className = `alert alert-${type === 'success' ? 'success' : 'info'}`;
    banner.style.cssText = `
      position: fixed;
      top: 80px;
      right: 20px;
      z-index: 9999;
      background: ${type === 'success' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(59, 130, 246, 0.2)'};
      border: 2px solid ${type === 'success' ? '#10B981' : '#3B82F6'};
      color: #fff;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      animation: slideInRight 0.3s ease;
    `;
    banner.innerHTML = `
      <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
      ${message}
    `;
    
    document.body.appendChild(banner);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      banner.style.animation = 'slideOutRight 0.3s ease';
      setTimeout(() => banner.remove(), 300);
    }, 5000);
  }
})();


// Clear & Rebuild (Testcases) handler
(function() {
  const btn = document.getElementById('confirmClearRebuildBtn');
  const statusEl = document.getElementById('clearRebuildStatus');
  if (!btn) return;

  async function runResetAndReseed() {
    try {
      statusEl.textContent = 'Resetting existing cog scores...';
      btn.disabled = true;

      // Reset
      const resetRes = await fetch('/api/cog-scores/reset', { method: 'POST' });
      const resetJson = await resetRes.json();
      if (!resetJson.success) {
        statusEl.textContent = 'Error during reset: ' + (resetJson.error || 'Unknown error');
        btn.disabled = false;
        return;
      }

      statusEl.textContent = 'Calculating and seeding from testcases...';
      // Reseed
      const reseedRes = await fetch('/api/cog-scores/reseed-from-testcases', { method: 'POST' });
      const reseedJson = await reseedRes.json();
      if (!reseedJson.success) {
        statusEl.textContent = 'Error during reseed: ' + (reseedJson.error || 'Unknown error');
        btn.disabled = false;
        return;
      }

      statusEl.textContent = 'Done. Refreshing...';
      // Reload to refresh charts and lists
      setTimeout(() => { window.location.reload(); }, 500);
    } catch (e) {
      statusEl.textContent = 'Unexpected error: ' + e;
      btn.disabled = false;
    }
  }

  btn.addEventListener('click', runResetAndReseed);
})();

