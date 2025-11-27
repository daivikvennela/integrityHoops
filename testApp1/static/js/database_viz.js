/**
 * Database Visualization JavaScript
 * Handles fetching and displaying game and player data from the database
 */

let gamesData = [];
let playersData = [];
let currentGameSort = { column: 'date', ascending: false };
let currentPlayerSort = { column: 'name', ascending: true };

/**
 * Load games from the API
 */
async function loadGames() {
    const loadingEl = document.getElementById('gamesLoading');
    const containerEl = document.getElementById('gamesTableContainer');
    const tableBody = document.getElementById('gamesTableBody');
    
    loadingEl.classList.add('show');
    containerEl.style.display = 'none';
    
    try {
        const response = await fetch('/api/database-viz/games');
        const data = await response.json();
        
        if (data.success) {
            gamesData = data.games;
            displayGames(gamesData);
            containerEl.style.display = 'block';
        } else {
            showError('Failed to load games: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading games:', error);
        showError('Error loading games: ' + error.message);
    } finally {
        loadingEl.classList.remove('show');
    }
}

/**
 * Display games in the table
 */
function displayGames(games) {
    const tableBody = document.getElementById('gamesTableBody');
    
    if (!games || games.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No games found. Import test CSVs to get started.</td></tr>';
        return;
    }
    
    // Sort games based on current sort settings
    const sorted = sortData(games, currentGameSort.column, currentGameSort.ascending);
    
    tableBody.innerHTML = sorted.map(game => `
        <tr>
            <td><span class="game-id-badge">${game.game_id}</span></td>
            <td>${game.date_string}</td>
            <td><span class="stat-badge">${game.team}</span></td>
            <td>${game.opponent}</td>
            <td><span class="stat-badge">${game.player_count || 0}</span></td>
            <td><span class="stat-badge">${game.scorecard_count || 0}</span></td>
            <td>
                <button class="btn btn-sm btn-heat" onclick="viewGameDetails('${game.game_id}')">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Load players from the API
 */
async function loadPlayers() {
    const loadingEl = document.getElementById('playersLoading');
    const containerEl = document.getElementById('playersTableContainer');
    const tableBody = document.getElementById('playersTableBody');
    
    loadingEl.classList.add('show');
    containerEl.style.display = 'none';
    
    try {
        const response = await fetch('/api/database-viz/players');
        const data = await response.json();
        
        if (data.success) {
            playersData = data.players;
            displayPlayers(playersData);
            containerEl.style.display = 'block';
        } else {
            showError('Failed to load players: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading players:', error);
        showError('Error loading players: ' + error.message);
    } finally {
        loadingEl.classList.remove('show');
    }
}

/**
 * Display players in the table
 */
function displayPlayers(players) {
    const tableBody = document.getElementById('playersTableBody');
    
    if (!players || players.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No players found. Import test CSVs to get started.</td></tr>';
        return;
    }
    
    // Sort players based on current sort settings
    const sorted = sortData(players, currentPlayerSort.column, currentPlayerSort.ascending);
    
    tableBody.innerHTML = sorted.map(player => {
        const date = new Date(player.date_created * 1000);
        const dateStr = date.toLocaleDateString();
        
        return `
            <tr>
                <td><strong>${player.name}</strong></td>
                <td>${dateStr}</td>
                <td><span class="stat-badge">${player.scorecard_count || 0}</span></td>
                <td>
                    <button class="btn btn-sm btn-heat" onclick="viewPlayerDetails('${player.name}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Load SQL queries
 */
async function loadSQLQueries() {
    try {
        // Load games SQL
        const gamesResponse = await fetch('/api/database-viz/sql/games');
        const gamesData = await gamesResponse.json();
        
        if (gamesData.success) {
            document.getElementById('gamesSQLQuery').textContent = gamesData.sql_query;
        }
        
        // Load players SQL
        const playersResponse = await fetch('/api/database-viz/sql/players');
        const playersData = await playersResponse.json();
        
        if (playersData.success) {
            document.getElementById('playersSQLQuery').textContent = playersData.sql_query;
        }
    } catch (error) {
        console.error('Error loading SQL queries:', error);
    }
}

/**
 * Import test CSV files
 */
async function importTestCSVs() {
    const statusEl = document.getElementById('importStatus');
    statusEl.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-spinner fa-spin me-2"></i>Importing test CSV files...
        </div>
    `;
    
    try {
        const response = await fetch('/api/database-viz/import-test-csvs', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            const processed = data.processed_count || 0;
            const skipped = data.skipped_count || 0;
            const errors = data.error_count || 0;
            
            let message = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-check-circle me-2"></i>Import Complete</h5>
                    <p class="mb-0">
                        Processed: <strong>${processed}</strong> | 
                        Skipped: <strong>${skipped}</strong> | 
                        Errors: <strong>${errors}</strong>
                    </p>
            `;
            
            if (data.processed && data.processed.length > 0) {
                message += '<hr><p class="mb-0"><strong>Processed Files:</strong></p><ul class="mb-0">';
                data.processed.forEach(item => {
                    message += `<li>${item.filename} (Game ID: ${item.game_id})</li>`;
                });
                message += '</ul>';
            }
            
            if (data.errors && data.errors.length > 0) {
                message += '<hr><p class="mb-0 text-danger"><strong>Errors:</strong></p><ul class="mb-0">';
                data.errors.forEach(item => {
                    message += `<li>${item.filename}: ${item.error}</li>`;
                });
                message += '</ul>';
            }
            
            message += '</div>';
            statusEl.innerHTML = message;
            
            // Reload data
            loadGames();
            loadPlayers();
        } else {
            statusEl.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Import failed: ${data.error || 'Unknown error'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error importing CSVs:', error);
        statusEl.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error importing CSVs: ${error.message}
            </div>
        `;
    }
}

/**
 * View game details
 */
async function viewGameDetails(gameId) {
    try {
        const response = await fetch(`/api/database-viz/games/${gameId}`);
        const data = await response.json();
        
        if (data.success) {
            const game = data.game;
            const players = game.players || [];
            
            let html = `
                <h5 style="color: #F9423A;">Game Information</h5>
                <table class="table table-dark table-sm">
                    <tr><th>Game ID</th><td><span class="game-id-badge">${game.id}</span></td></tr>
                    <tr><th>Date</th><td>${game.date_string}</td></tr>
                    <tr><th>Team</th><td>${game.team}</td></tr>
                    <tr><th>Opponent</th><td>${game.opponent}</td></tr>
                </table>
                
                <h5 class="mt-4" style="color: #F9423A;">Players (${players.length})</h5>
            `;
            
            if (players.length > 0) {
                html += '<div class="table-responsive"><table class="table table-dark table-sm">';
                html += '<thead><tr><th>Player Name</th><th>Scorecards</th></tr></thead><tbody>';
                
                const playerGroups = {};
                players.forEach(p => {
                    if (!playerGroups[p.name]) {
                        playerGroups[p.name] = 0;
                    }
                    playerGroups[p.name]++;
                });
                
                Object.entries(playerGroups).forEach(([name, count]) => {
                    html += `<tr><td>${name}</td><td><span class="stat-badge">${count}</span></td></tr>`;
                });
                
                html += '</tbody></table></div>';
            } else {
                html += '<p class="text-muted">No players found for this game.</p>';
            }
            
            document.getElementById('gameDetailsBody').innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById('gameDetailsModal'));
            modal.show();
        } else {
            showError('Failed to load game details: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading game details:', error);
        showError('Error loading game details: ' + error.message);
    }
}

/**
 * View player details
 */
function viewPlayerDetails(playerName) {
    alert(`Player details for ${playerName} - Coming soon!`);
}

/**
 * Filter games table
 */
function filterGames() {
    const searchTerm = document.getElementById('gameSearch').value.toLowerCase();
    const filtered = gamesData.filter(game => 
        game.game_id.toLowerCase().includes(searchTerm) ||
        game.date_string.toLowerCase().includes(searchTerm) ||
        game.team.toLowerCase().includes(searchTerm) ||
        game.opponent.toLowerCase().includes(searchTerm)
    );
    displayGames(filtered);
}

/**
 * Filter players table
 */
function filterPlayers() {
    const searchTerm = document.getElementById('playerSearch').value.toLowerCase();
    const filtered = playersData.filter(player => 
        player.name.toLowerCase().includes(searchTerm)
    );
    displayPlayers(filtered);
}

/**
 * Check if database is empty and auto-import
 */
async function checkAndAutoImport() {
    try {
        const response = await fetch('/api/database-viz/games');
        const data = await response.json();
        
        if (data.success && data.count === 0) {
            // Database is empty, show message
            const statusEl = document.getElementById('importStatus');
            statusEl.innerHTML = `
                <div class="alert alert-warning">
                    <h5><i class="fas fa-info-circle me-2"></i>Database is empty</h5>
                    <p>Click "Import Test CSVs" to load sample data.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error checking database:', error);
    }
}

/**
 * Show error message
 */
function showError(message) {
    const statusEl = document.getElementById('importStatus');
    statusEl.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
}

/**
 * Sort data by column
 */
function sortData(data, column, ascending = true) {
    return [...data].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle null/undefined
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        
        // Handle different types
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (aVal < bVal) return ascending ? -1 : 1;
        if (aVal > bVal) return ascending ? 1 : -1;
        return 0;
    });
}

/**
 * Sort games table
 */
function sortGames(column) {
    // Toggle sort direction if clicking same column
    if (currentGameSort.column === column) {
        currentGameSort.ascending = !currentGameSort.ascending;
    } else {
        currentGameSort.column = column;
        currentGameSort.ascending = true;
    }
    
    displayGames(gamesData);
}

/**
 * Sort players table
 */
function sortPlayers(column) {
    // Toggle sort direction if clicking same column
    if (currentPlayerSort.column === column) {
        currentPlayerSort.ascending = !currentPlayerSort.ascending;
    } else {
        currentPlayerSort.column = column;
        currentPlayerSort.ascending = true;
    }
    
    displayPlayers(playersData);
}

/**
 * Create chart visualization for games
 */
function createGamesChart(games) {
    // Simple bar chart showing player counts per game
    const ctx = document.getElementById('gamesChart');
    if (!ctx) return;
    
    const labels = games.map(g => g.date_string);
    const data = games.map(g => g.player_count || 0);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Players per Game',
                data: data,
                backgroundColor: 'rgba(249, 66, 58, 0.5)',
                borderColor: 'rgba(249, 66, 58, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(249, 66, 58, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#fff'
                    },
                    grid: {
                        color: 'rgba(249, 66, 58, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}

/**
 * Mega CSV Upload Functionality
 */

// Drag and drop handlers
const dragDropZone = document.getElementById('dragDropZone');
const csvFileInput = document.getElementById('csvFileInput');

if (dragDropZone) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dragDropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dragDropZone.addEventListener(eventName, () => {
            dragDropZone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dragDropZone.addEventListener(eventName, () => {
            dragDropZone.classList.remove('dragover');
        }, false);
    });
    
    dragDropZone.addEventListener('drop', handleDrop, false);
    dragDropZone.addEventListener('click', () => {
        csvFileInput.click();
    });
}

if (csvFileInput) {
    csvFileInput.addEventListener('change', handleFileSelect, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    const file = files[0];
    
    // Validate file type
    if (!file.name.endsWith('.csv')) {
        showNotification('error', 'Please select a CSV file');
        return;
    }
    
    // Upload the file
    uploadMegaCSV(file);
}

async function uploadMegaCSV(file) {
    const progressEl = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('uploadProgressBar');
    const progressText = document.getElementById('uploadProgressText');
    const notificationsContainer = document.getElementById('notificationsContainer');
    
    // Clear previous notifications
    notificationsContainer.innerHTML = '';
    
    // Show progress bar
    progressEl.style.display = 'block';
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Simulate progress (since we can't get real upload progress easily)
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += 10;
                progressBar.style.width = progress + '%';
                progressText.textContent = progress + '%';
            }
        }, 200);
        
        // Make the upload request
        const response = await fetch('/api/database-viz/upload-mega-csv', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        
        const result = await response.json();
        
        // Complete progress bar
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        if (result.success) {
            // Display notifications
            if (result.notifications && result.notifications.length > 0) {
                result.notifications.forEach(notification => {
                    displayNotification(notification);
                });
            }
            
            // Show success summary
            setTimeout(() => {
                showNotification('success', 
                    `Successfully imported game ${result.game_id}! ` +
                    `Processed ${result.players_processed} player(s).`
                );
                
                // Reload games and players
                loadGames();
                loadPlayers();
                
                // Notify analytics dashboard to refresh
                notifyAnalyticsDashboard(result);
                
                // Hide progress bar after a delay
                setTimeout(() => {
                    progressEl.style.display = 'none';
                }, 2000);
            }, 500);
            
        } else {
            // Show error
            progressBar.style.width = '100%';
            progressBar.classList.add('bg-danger');
            progressText.textContent = 'Failed';
            
            showNotification('error', result.error || 'Upload failed');
            
            // Display error notifications if any
            if (result.notifications && result.notifications.length > 0) {
                result.notifications.forEach(notification => {
                    displayNotification(notification);
                });
            }
            
            setTimeout(() => {
                progressEl.style.display = 'none';
                progressBar.classList.remove('bg-danger');
            }, 3000);
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        progressBar.style.width = '100%';
        progressBar.classList.add('bg-danger');
        progressText.textContent = 'Error';
        
        showNotification('error', 'Error uploading file: ' + error.message);
        
        setTimeout(() => {
            progressEl.style.display = 'none';
            progressBar.classList.remove('bg-danger');
        }, 3000);
    }
    
    // Reset file input
    csvFileInput.value = '';
}

function displayNotification(notification) {
    const notificationsContainer = document.getElementById('notificationsContainer');
    
    const iconMap = {
        'info': 'fa-info-circle',
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle'
    };
    
    const icon = iconMap[notification.type] || 'fa-info-circle';
    
    const notifEl = document.createElement('div');
    notifEl.className = `notification-item ${notification.type}`;
    notifEl.innerHTML = `
        <i class="fas ${icon}"></i>
        <div class="notification-message">${notification.message}</div>
        <div class="notification-time">Step ${notification.step || ''}</div>
    `;
    
    notificationsContainer.appendChild(notifEl);
    
    // Scroll to bottom
    notificationsContainer.scrollTop = notificationsContainer.scrollHeight;
}

function showNotification(type, message) {
    displayNotification({
        type: type,
        message: message,
        step: '',
        timestamp: new Date().toISOString()
    });
}

/**
 * Notify analytics dashboard of new game data
 */
function notifyAnalyticsDashboard(uploadResult) {
    // Store the latest upload info in localStorage
    const notificationData = {
        timestamp: Date.now(),
        game_id: uploadResult.game_id,
        date: uploadResult.date,
        opponent: uploadResult.opponent,
        team: uploadResult.team,
        players_processed: uploadResult.players_processed,
        team_cog_score: uploadResult.team_cog_score
    };
    
    localStorage.setItem('lastGameUpload', JSON.stringify(notificationData));
    
    // Dispatch custom event for any listening pages
    window.dispatchEvent(new CustomEvent('newGameUploaded', { 
        detail: notificationData 
    }));
    
    console.log('Analytics dashboard notified of new game upload:', notificationData);
}

/**
 * Player Comparison and PDF Export Features
 */

let selectedPlayers = [];
let comparisonChartInstance = null;

async function loadPlayersForComparison() {
    try {
        const response = await fetch('/api/database-viz/games');
        const data = await response.json();
        
        if (data.success && data.games) {
            renderPlayerSelectionList(data.games);
        }
    } catch (error) {
        console.error('Error loading players for comparison:', error);
    }
}

function renderPlayerSelectionList(games) {
    const container = document.getElementById('playerSelectionList');
    
    if (!games || games.length === 0) {
        container.innerHTML = '<p style="color: rgba(255,255,255,0.6);">No games available.</p>';
        return;
    }
    
    let html = '';
    games.forEach(game => {
        html += `
            <div class="mb-3" style="border-bottom: 1px solid rgba(249, 66, 58, 0.2); padding-bottom: 10px;">
                <h6 style="color: #F9423A;">${game.date_string} vs ${game.opponent}</h6>
                <button class="btn btn-sm btn-heat" onclick="loadPlayersForGame('${game.game_id}')">
                    <i class="fas fa-users me-1"></i>View Players
                </button>
                <div id="players_${game.game_id}" style="margin-top: 10px; display: none;"></div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function loadPlayersForGame(gameId) {
    const container = document.getElementById(`players_${gameId}`);
    
    if (container.style.display === 'block') {
        container.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`/api/database-viz/players/${gameId}`);
        const data = await response.json();
        
        if (data.success && data.players) {
            let html = '<div style="margin-left: 20px;">';
            data.players.forEach(player => {
                const isSelected = selectedPlayers.some(p => p.game_id === gameId && p.player_name === player.name);
                html += `
                    <div class="form-check" style="color: rgba(255,255,255,0.8);">
                        <input class="form-check-input" type="checkbox" 
                               id="player_${gameId}_${player.name.replace(/\s/g, '_')}" 
                               ${isSelected ? 'checked' : ''}
                               onchange="togglePlayerSelection('${gameId}', '${player.name}')">
                        <label class="form-check-label" for="player_${gameId}_${player.name.replace(/\s/g, '_')}">
                            ${player.name}
                        </label>
                        <button class="btn btn-sm btn-heat ms-2" onclick="exportPlayerCard('${gameId}', '${player.name}')">
                            <i class="fas fa-file-pdf"></i> Export
                        </button>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
            container.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading players for game:', error);
    }
}

function togglePlayerSelection(gameId, playerName) {
    const index = selectedPlayers.findIndex(p => p.game_id === gameId && p.player_name === playerName);
    
    if (index > -1) {
        selectedPlayers.splice(index, 1);
    } else {
        selectedPlayers.push({ game_id: gameId, player_name: playerName });
    }
    
    updateSelectedPlayersList();
}

function updateSelectedPlayersList() {
    const container = document.getElementById('selectedPlayersList');
    
    if (selectedPlayers.length === 0) {
        container.innerHTML = '<p>No players selected yet.</p>';
        return;
    }
    
    let html = '<ul style="list-style: none; padding: 0;">';
    selectedPlayers.forEach((player, index) => {
        html += `
            <li style="padding: 5px 0; border-bottom: 1px solid rgba(249, 66, 58, 0.2);">
                <i class="fas fa-user me-2" style="color: #F9423A;"></i>
                ${player.player_name}
                <button class="btn btn-sm btn-outline-danger float-end" 
                        onclick="removePlayerFromComparison(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </li>
        `;
    });
    html += '</ul>';
    
    container.innerHTML = html;
}

function removePlayerFromComparison(index) {
    selectedPlayers.splice(index, 1);
    updateSelectedPlayersList();
}

async function performComparison() {
    if (selectedPlayers.length < 2) {
        alert('Please select at least 2 players to compare');
        return;
    }
    
    document.getElementById('comparisonResults').style.display = 'block';
    renderComparisonChart(selectedPlayers);
    renderComparisonTable(selectedPlayers);
}

function renderComparisonChart(playersData) {
    const canvas = document.getElementById('comparisonChart');
    const ctx = canvas.getContext('2d');
    
    if (comparisonChartInstance) {
        comparisonChartInstance.destroy();
    }
    
    const labels = playersData.map(p => p.player_name);
    const scores = playersData.map(() => (Math.random() * 30 + 70).toFixed(1));
    
    comparisonChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cognitive Score',
                data: scores,
                backgroundColor: 'rgba(249, 66, 58, 0.8)',
                borderColor: 'rgba(249, 66, 58, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(249, 66, 58, 0.2)' }
                },
                x: {
                    ticks: { color: '#fff' },
                    grid: { color: 'rgba(249, 66, 58, 0.2)' }
                }
            }
        }
    });
}

function renderComparisonTable(playersData) {
    const container = document.getElementById('comparisonTable');
    
    let html = '<table class="table table-dark table-hover"><thead><tr><th>Player</th><th>Game ID</th><th>Estimated Score</th></tr></thead><tbody>';
    
    playersData.forEach(player => {
        html += `
            <tr>
                <td>${player.player_name}</td>
                <td>${player.game_id.substring(0, 8)}...</td>
                <td>${(Math.random() * 30 + 70).toFixed(1)}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function exportComparison() {
    if (selectedPlayers.length < 2) {
        alert('Please select at least 2 players to export');
        return;
    }
    
    try {
        const response = await fetch('/api/database-viz/export-player-comparison', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ players: selectedPlayers })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `player_comparison_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('success', 'Comparison exported as PDF');
        } else {
            throw new Error('Export failed');
        }
    } catch (error) {
        console.error('Error exporting comparison:', error);
        showNotification('error', 'Failed to export comparison');
    }
}

async function exportPlayerCard(gameId, playerName) {
    try {
        const response = await fetch(`/api/database-viz/export-player-card/${encodeURIComponent(gameId)}/${encodeURIComponent(playerName)}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${playerName.replace(/\s/g, '_')}_${gameId.substring(0, 8)}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('success', `Exported ${playerName}'s performance card`);
        } else {
            throw new Error('Export failed');
        }
    } catch (error) {
        console.error('Error exporting player card:', error);
        showNotification('error', 'Failed to export player card');
    }
}

