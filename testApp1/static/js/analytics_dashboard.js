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
      const label = point.label + ' → ' + point.score;
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

  // ETL upload - calculate cog scores from CSV
  const etlForm = document.getElementById('etlForm');
  if (etlForm) {
    etlForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const fileInput = document.getElementById('etlFile');
      const file = fileInput.files[0];
      
      if (!file) {
        alert('Please select a CSV file first.');
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await fetch('/api/cog-scores/calculate-from-csv', {
          method: 'POST',
          body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
          const data = result.data;
          console.log('Cognitive Score Report:', data);
          
          // Show 2K/Madden style score reveal
          showScoreReveal(data);
          
          // Reset form
          etlForm.reset();
        } else {
          alert(`Error: ${result.error}`);
        }
      } catch (error) {
        console.error('Error uploading CSV:', error);
        alert('Failed to process CSV file. Please try again.');
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
      return `
        <tr>
          <td>${point.date}</td>
          <td>${point.label}</td>
          <td><strong style="color: #F9423A;">${point.score}%</strong></td>
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
  
  // Category colors
  const categoryColors = {
    'Cutting & Screening': '#FF6B6B',
    'DM Catch': '#4ECDC4',
    'Finishing': '#FFE66D',
    'Footwork': '#95E1D3',
    'Passing': '#F38181',
    'Positioning': '#AA96DA',
    'QB12 DM': '#FCBAD3',
    'Relocation': '#A8E6CF',
    'Space Read': '#FFD3A5',
    'Transition': '#C7CEEA'
  };
  
  async function loadTeamStatistics(category = '') {
    try {
      const url = category 
        ? `/api/team-statistics?category=${encodeURIComponent(category)}`
        : '/api/team-statistics';
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (!data.success || !data.statistics) {
        console.error('Failed to load statistics:', data.error);
        return;
      }
      
      updateStatisticsChart(data.statistics, category);
    } catch (error) {
      console.error('Error loading team statistics:', error);
    }
  }
  
  function updateStatisticsChart(statistics, category) {
    const ctx = chartCanvas.getContext('2d');
    
    // Destroy existing chart if it exists
    if (statisticsChart) {
      statisticsChart.destroy();
    }
    
    // Group data by date
    const dates = [...new Set(statistics.map(s => s.date))].sort();
    
    // Format dates for display (MM/DD/YY)
    const formattedDates = dates.map(date => {
      const d = new Date(date);
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const year = String(d.getFullYear()).slice(-2);
      return `${month}/${day}/${year}`;
    });
    
    if (category) {
      // Single category view
      const categoryData = statistics
        .filter(s => s.category === category)
        .sort((a, b) => a.date.localeCompare(b.date));
      
      const percentages = dates.map(date => {
        const point = categoryData.find(d => d.date === date);
        return point ? point.percentage : null;
      });
      
      statisticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: formattedDates,
          datasets: [{
            label: category,
            data: percentages,
            borderColor: categoryColors[category] || '#CCCCCC',
            backgroundColor: categoryColors[category] ? categoryColors[category] + '20' : 'rgba(204, 204, 204, 0.2)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: categoryColors[category] || '#CCCCCC',
            pointBorderColor: '#000',
            pointBorderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              labels: {
                color: '#fff',
                font: {
                  size: 14,
                  weight: 'bold'
                }
              }
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
                  return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
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
          }
        }
      });
    } else {
      // All categories view
      const categories = [...new Set(statistics.map(s => s.category))];
      
      const datasets = categories.map(cat => {
        const categoryData = statistics
          .filter(s => s.category === cat)
          .sort((a, b) => a.date.localeCompare(b.date));
        
        const percentages = dates.map(date => {
          const point = categoryData.find(d => d.date === date);
          return point ? point.percentage : null;
        });
        
        return {
          label: cat,
          data: percentages,
          borderColor: categoryColors[cat] || '#CCCCCC',
          backgroundColor: categoryColors[cat] ? categoryColors[cat] + '20' : 'rgba(204, 204, 204, 0.2)',
          borderWidth: 2,
          fill: false,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: categoryColors[cat] || '#CCCCCC',
          pointBorderColor: '#000',
          pointBorderWidth: 1.5
        };
      });
      
      statisticsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: formattedDates,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              position: 'bottom',
              labels: {
                color: '#fff',
                font: {
                  size: 12
                },
                padding: 15,
                usePointStyle: true
              }
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
                  return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`;
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
          }
        }
      });
    }
  }
  
  // Load statistics on page load
  loadTeamStatistics();
  
  // Handle category selector change
  categorySelect.addEventListener('change', function() {
    loadTeamStatistics(this.value);
  });
})();


