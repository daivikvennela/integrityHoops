(function() {
  'use strict';

  const chartEl = document.getElementById('cogChart');
  if (!chartEl) return;

  const chart = echarts.init(chartEl, null, { renderer: 'canvas' });

  function setChart(labels, scores) {
    // Get accent color from current theme
    const isHeatTheme = document.body.classList.contains('theme-heat');
    const accentColor = isHeatTheme ? '#F9423A' : '#a855f7';
    const accentColorLight = isHeatTheme ? '#FF5349' : '#c084fc';
    const accentColorFaded = isHeatTheme ? 'rgba(249,66,58,0.06)' : 'rgba(168,85,247,0.06)';
    
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
        data: scores,
        smooth: true,
        symbol: 'circle',
        symbolSize: 10,
        lineStyle: { color: accentColor, width: 3 },
        itemStyle: { 
          color: accentColor, 
          borderColor: accentColorLight, 
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: accentColor
        },
        emphasis: {
          itemStyle: {
            symbolSize: 16,
            borderWidth: 3,
            shadowBlur: 20,
            shadowColor: accentColor
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
    // stash ids for click deletion
    window.__cogPoints__ = json.points;
    setChart(labels, scores);
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
  
  async function loadTeamStatistics(category = '') {
    try {
      const url = category 
        ? `/api/team-statistics?category=${encodeURIComponent(category)}`
        : '/api/team-statistics';
      
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
        data.game_info || {}
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
        const meta = chartInstance.getDatasetMeta(idx);
        meta.hidden = meta.hidden === null ? true : null;
        chartInstance.update('none');
        // Re-render buttons to update visual state
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
  
  function updateStatisticsChart(statistics, category, overallScores = {}, gameInfo = {}) {
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

      // Create overall scores dataset overlay
      const overallScoresData = catDates.map(date => {
        return overallScores[date] || null;
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
            pointBackgroundColor: lineColor,
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

      try {
        statisticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: catFormattedDates,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          backgroundColor: '#000000',  // Black background for plot
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
              titleColor: '#F9423A',
              bodyColor: '#fff',
              borderColor: '#F9423A',
              borderWidth: 2,
              padding: 12,
              callbacks: {
                label: function(context) {
                  return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}%`;
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
      } catch (error) {
        console.error('Error creating chart for single category:', error);
        return;
      }
      
      // Update overall scores list with chart instance for toggle functionality
      updateOverallScoresList(overallScores, gameInfo, statisticsChart);
      
      // Populate chart line menu for toggle functionality
      if (typeof populateChartLineMenu === 'function') {
        setTimeout(() => {
          populateChartLineMenu();
        }, 200);
      }
      
      // Render custom toggle buttons for datasets (use setTimeout to ensure chart is fully initialized)
      setTimeout(() => {
        renderCategoryToggleButtons(statisticsChart);
      }, 100);

      // Canvas hover to show dataset label near cursor - improved for line detection
      mousemoveHandler = function(ev) {
        if (!overlay || !statisticsChart) return;
        
        // Use 'index' mode to find nearest point, then check if we're close to the line
        const points = statisticsChart.getElementsAtEventForMode(ev, 'index', { intersect: false }, true);
        
        if (points && points.length > 0) {
          const point = points[0];
          const dsIndex = point.datasetIndex;
          const label = statisticsChart.data.datasets[dsIndex]?.label;
          
          if (label) {
            // Check if we're within reasonable distance from the line (more lenient)
            const meta = statisticsChart.getDatasetMeta(dsIndex);
            const index = point.index;
            
            // Calculate distance from cursor to line segment
            const chartArea = statisticsChart.chartArea;
            const xScale = statisticsChart.scales.x;
            const yScale = statisticsChart.scales.y;
            
            const canvasPos = Chart.helpers.getRelativePosition(ev, statisticsChart);
            const x = canvasPos.x;
            const y = canvasPos.y;
            
            // Check if we're within chart area and near any point
            if (x >= chartArea.left && x <= chartArea.right && 
                y >= chartArea.top && y <= chartArea.bottom) {
              // Show overlay for any point in the dataset
            overlay.style.display = 'block';
            overlay.textContent = label;
            const rect = cardBody.getBoundingClientRect();
            overlay.style.left = (ev.clientX - rect.left + 12) + 'px';
            overlay.style.top = (ev.clientY - rect.top + 12) + 'px';
              return;
            }
          }
        }
        
        // Fallback: try 'nearest' mode with more lenient detection
        const nearestPoints = statisticsChart.getElementsAtEventForMode(ev, 'nearest', { intersect: false, threshold: 30 }, true);
        if (nearestPoints && nearestPoints.length > 0) {
          const dsIndex = nearestPoints[0].datasetIndex;
          const label = statisticsChart.data.datasets[dsIndex]?.label;
          if (label) {
            overlay.style.display = 'block';
            overlay.textContent = label;
            const rect = cardBody.getBoundingClientRect();
            overlay.style.left = (ev.clientX - rect.left + 12) + 'px';
            overlay.style.top = (ev.clientY - rect.top + 12) + 'px';
            return;
          }
        }
        
        overlay.style.display = 'none';
      };
      chartCanvas.addEventListener('mousemove', mousemoveHandler);
      
      mouseleaveHandler = function() {
        if (overlay) overlay.style.display = 'none';
      };
      chartCanvas.addEventListener('mouseleave', mouseleaveHandler);
    } else {
      // All categories view - use filtered statistics (which will be all when no category selected)
      const categories = [...new Set(filteredStatistics.map(s => s.category))];
      
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
          pointBackgroundColor: lineColor,
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
          pointBackgroundColor: '#F9423A',
          pointBorderColor: '#000',
          pointBorderWidth: 2
        });
        console.log('Added overall scores dataset. Total datasets:', datasets.length);
      } else {
        console.warn('No overall scores available to add to chart');
      }
      
      try {
      statisticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: formattedDates,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
              titleColor: '#F9423A',
              bodyColor: '#fff',
              borderColor: '#F9423A',
              borderWidth: 2,
              padding: 12,
              callbacks: {
                label: function(context) {
                  return `${context.dataset.label}: ${context.parsed.y.toFixed(4)}%`;
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
            }
          }
        }
      });
      } catch (error) {
        console.error('Error creating chart for all categories:', error);
        return;
      }
      
      // Update overall scores list with chart instance for toggle functionality
      updateOverallScoresList(overallScores, gameInfo, statisticsChart);
      
      // Populate chart line menu for toggle functionality
      if (typeof populateChartLineMenu === 'function') {
        setTimeout(() => {
          populateChartLineMenu();
        }, 200);
      }
      
      // Render custom toggle buttons for datasets (use setTimeout to ensure chart is fully initialized)
      setTimeout(() => {
        renderCategoryToggleButtons(statisticsChart);
      }, 100);
      
      // Add hover support for all categories view
      mousemoveHandler = function(ev) {
        if (!overlay || !statisticsChart) return;
        
        const points = statisticsChart.getElementsAtEventForMode(ev, 'index', { intersect: false }, true);
        
        if (points && points.length > 0) {
          const point = points[0];
          const dsIndex = point.datasetIndex;
          const label = statisticsChart.data.datasets[dsIndex]?.label;
          
          if (label) {
            const chartArea = statisticsChart.chartArea;
            const canvasPos = Chart.helpers.getRelativePosition(ev, statisticsChart);
            const x = canvasPos.x;
            const y = canvasPos.y;
            
            if (x >= chartArea.left && x <= chartArea.right && 
                y >= chartArea.top && y <= chartArea.bottom) {
              overlay.style.display = 'block';
              overlay.textContent = label;
              const rect = cardBody.getBoundingClientRect();
              overlay.style.left = (ev.clientX - rect.left + 12) + 'px';
              overlay.style.top = (ev.clientY - rect.top + 12) + 'px';
              return;
            }
          }
        }
        
        // Fallback: try nearest with threshold
        const nearestPoints = statisticsChart.getElementsAtEventForMode(ev, 'nearest', { intersect: false, threshold: 30 }, true);
        if (nearestPoints && nearestPoints.length > 0) {
          const dsIndex = nearestPoints[0].datasetIndex;
          const label = statisticsChart.data.datasets[dsIndex]?.label;
          if (label) {
            overlay.style.display = 'block';
            overlay.textContent = label;
            const rect = cardBody.getBoundingClientRect();
            overlay.style.left = (ev.clientX - rect.left + 12) + 'px';
            overlay.style.top = (ev.clientY - rect.top + 12) + 'px';
            return;
          }
        }
        
        overlay.style.display = 'none';
      };
      chartCanvas.addEventListener('mousemove', mousemoveHandler);
      
      mouseleaveHandler = function() {
        if (overlay) overlay.style.display = 'none';
      };
      chartCanvas.addEventListener('mouseleave', mouseleaveHandler);
    }
  }
  
  // Load statistics on page load
  loadTeamStatistics();
  
  // Handle category selector change - ensure it works properly
  categorySelect.addEventListener('change', function() {
    const selectedCategory = this.value;
    console.log('Category changed to:', selectedCategory || 'All Categories');
    
    // Clear any existing chart and buttons before loading new data
    if (statisticsChart) {
      statisticsChart.destroy();
      statisticsChart = null;
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

