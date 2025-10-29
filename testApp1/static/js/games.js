// Minimal JS to wire filters and charts; can be expanded when backend is ready
(function() {
  function $(sel) { return document.querySelector(sel); }

  const applyBtn = $('#apply-filters');
  const clearBtn = $('#clear-filters');

  if (applyBtn) {
    applyBtn.addEventListener('click', function() {
      const date = ($('#filter-date') || {}).value || '';
      const team = ($('#filter-team') || {}).value || '';
      const opponent = ($('#filter-opponent') || {}).value || '';
      const params = new URLSearchParams();
      if (date) params.set('date', date);
      if (team) params.set('team', team);
      if (opponent) params.set('opponent', opponent);
      const url = params.toString() ? `/games?${params.toString()}` : '/games';
      window.location.href = url;
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', function() {
      window.location.href = '/games';
    });
  }

  // Charts on game detail
  const dataScript = document.getElementById('game-data-json');
  if (dataScript) {
    try {
      const game = JSON.parse(dataScript.textContent || '{}');

      // Example category chart (placeholder values)
      const ctx1 = document.getElementById('teamCategoryChart');
      if (ctx1 && window.Chart) {
        new Chart(ctx1, {
          type: 'bar',
          data: {
            labels: ['Space Read', 'DM Catch', 'Driving', 'QB12'],
            datasets: [{
              label: 'Positive',
              backgroundColor: 'rgba(249, 66, 58, 0.7)',
              borderColor: 'rgba(249, 66, 58, 1)',
              data: [22, 18, 16, 20]
            },
            {
              label: 'Negative',
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              borderColor: 'rgba(255, 255, 255, 0.4)',
              data: [6, 7, 5, 8]
            }]
          },
          options: {
            responsive: true,
            plugins: { legend: { labels: { color: '#fff' } } },
            scales: {
              x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
              y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
          }
        });
      }

      // Example player comparison radar chart (placeholder)
      const ctx2 = document.getElementById('playerComparisonChart');
      if (ctx2 && window.Chart) {
        new Chart(ctx2, {
          type: 'radar',
          data: {
            labels: ['Space Read', 'DM Catch', 'Driving', 'QB12', 'Cut/Screen'],
            datasets: [
              { label: 'Butler', data: [8,7,6,7,5], backgroundColor: 'rgba(249,66,58,0.2)', borderColor: 'rgba(249,66,58,1)' },
              { label: 'Adebayo', data: [6,5,7,6,6], backgroundColor: 'rgba(255,255,255,0.1)', borderColor: 'rgba(255,255,255,0.6)' }
            ]
          },
          options: {
            plugins: { legend: { labels: { color: '#fff' } } },
            scales: { r: { grid: { color: 'rgba(255,255,255,0.1)' }, pointLabels: { color: '#fff' } } }
          }
        });
      }
    } catch (e) {
      console.warn('Failed to initialize game detail charts:', e);
    }
  }
})();


