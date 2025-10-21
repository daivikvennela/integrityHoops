/**
 * Player Comparison System
 * Multi-player comparison with drag-and-drop and export functionality
 */

class PlayerComparison {
    constructor() {
        this.selectedPlayers = [];
        this.maxPlayers = 4;
        this.isOpen = false;
        this.charts = {};
        this.draggedPlayer = null;
    }

    /**
     * Initialize the comparison system
     */
    init() {
        this.setupToggleButton();
        this.setupCloseButton();
        this.setupDragAndDrop();
        this.setupKeyboardShortcuts();
        console.log('Player Comparison System initialized');
    }

    /**
     * Setup toggle button to open/close panel
     */
    setupToggleButton() {
        const toggleBtn = document.getElementById('comparison-toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.togglePanel();
            });
        }
    }

    /**
     * Setup close button
     */
    setupCloseButton() {
        const closeBtn = document.getElementById('close-comparison-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closePanel();
            });
        }
    }

    /**
     * Toggle comparison panel
     */
    togglePanel() {
        const panel = document.getElementById('comparison-panel');
        if (panel) {
            this.isOpen = !this.isOpen;
            if (this.isOpen) {
                panel.classList.add('active');
                this.renderPanel();
            } else {
                panel.classList.remove('active');
            }
        }
    }

    /**
     * Close comparison panel
     */
    closePanel() {
        const panel = document.getElementById('comparison-panel');
        if (panel) {
            this.isOpen = false;
            panel.classList.remove('active');
        }
    }

    /**
     * Open comparison panel
     */
    openPanel() {
        const panel = document.getElementById('comparison-panel');
        if (panel) {
            this.isOpen = true;
            panel.classList.add('active');
            this.renderPanel();
        }
    }

    /**
     * Setup drag and drop functionality
     */
    setupDragAndDrop() {
        // Make player cards draggable
        document.addEventListener('click', (e) => {
            const playerCard = e.target.closest('.player-card-modern');
            if (playerCard && e.target.closest('.compare-btn')) {
                const playerName = playerCard.dataset.playerName;
                if (playerName) {
                    this.addPlayerToComparison(playerName);
                }
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+C: Open comparison panel
            if (e.ctrlKey && e.key === 'c') {
                e.preventDefault();
                this.openPanel();
            }
            // Escape: Close panel
            if (e.key === 'Escape' && this.isOpen) {
                this.closePanel();
            }
        });
    }

    /**
     * Add player to comparison
     */
    async addPlayerToComparison(playerName) {
        // Check if player already added
        if (this.selectedPlayers.some(p => p.name === playerName)) {
            this.showNotification('Player already in comparison', 'warning');
            return;
        }

        // Check max players limit
        if (this.selectedPlayers.length >= this.maxPlayers) {
            this.showNotification(`Maximum ${this.maxPlayers} players can be compared`, 'warning');
            return;
        }

        // Fetch player data
        try {
            const response = await fetch(`/api/players/${encodeURIComponent(playerName)}`);
            const data = await response.json();
            
            if (data.success) {
                this.selectedPlayers.push(data.player);
                this.updateBadge();
                this.renderPanel();
                this.openPanel();
                this.showNotification(`${playerName} added to comparison`, 'success');
            } else {
                this.showNotification('Failed to load player data', 'error');
            }
        } catch (error) {
            console.error('Error loading player:', error);
            this.showNotification('Error loading player data', 'error');
        }
    }

    /**
     * Remove player from comparison
     */
    removePlayerFromComparison(playerName) {
        this.selectedPlayers = this.selectedPlayers.filter(p => p.name !== playerName);
        this.updateBadge();
        this.renderPanel();
        this.showNotification(`${playerName} removed from comparison`, 'info');
    }

    /**
     * Clear all players
     */
    clearAllPlayers() {
        this.selectedPlayers = [];
        this.updateBadge();
        this.renderPanel();
        this.destroyAllCharts();
    }

    /**
     * Update comparison badge count
     */
    updateBadge() {
        const badge = document.getElementById('comparison-badge');
        if (badge) {
            const count = this.selectedPlayers.length;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    /**
     * Render comparison panel content
     */
    renderPanel() {
        const content = document.getElementById('comparison-panel-content');
        if (!content) return;

        if (this.selectedPlayers.length === 0) {
            content.innerHTML = this.renderEmptyState();
            return;
        }

        content.innerHTML = `
            ${this.renderPlayerSlots()}
            ${this.selectedPlayers.length >= 2 ? this.renderComparisonCharts() : ''}
            ${this.renderActionButtons()}
        `;

        // Initialize charts if 2+ players
        if (this.selectedPlayers.length >= 2) {
            setTimeout(() => {
                this.generateComparisonCharts();
            }, 100);
        }
    }

    /**
     * Render empty state
     */
    renderEmptyState() {
        return `
            <div class="comparison-empty-state">
                <i class="fas fa-chart-bar"></i>
                <h4>No Players Selected</h4>
                <p>Click the "Compare" button on player cards to add them here</p>
                <p class="mt-2"><small>You can compare up to ${this.maxPlayers} players at once</small></p>
            </div>
        `;
    }

    /**
     * Render player slots
     */
    renderPlayerSlots() {
        const slots = [];
        
        // Filled slots
        this.selectedPlayers.forEach((player, index) => {
            slots.push(`
                <div class="player-slot filled" data-index="${index}">
                    <i class="fas fa-user slot-icon"></i>
                    <div class="slot-player-name">${player.name}</div>
                    <div class="stat-badge mt-2">${player.scorecard_count || 0} scorecards</div>
                    <button class="remove-player-btn" onclick="playerComparison.removePlayerFromComparison('${player.name}')">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
            `);
        });

        // Empty slots
        const emptyCount = this.maxPlayers - this.selectedPlayers.length;
        for (let i = 0; i < emptyCount; i++) {
            slots.push(`
                <div class="player-slot empty">
                    <i class="fas fa-plus-circle slot-icon"></i>
                    <div class="slot-label">Add Player</div>
                </div>
            `);
        }

        return `
            <div class="comparison-player-slots">
                ${slots.join('')}
            </div>
        `;
    }

    /**
     * Render comparison charts section
     */
    renderComparisonCharts() {
        return `
            <div class="comparison-charts">
                <div class="comparison-chart-card">
                    <div class="chart-card-header">
                        <i class="fas fa-radar"></i> Cognitive Metrics Comparison
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="comparison-radar-chart"></canvas>
                    </div>
                </div>

                <div class="comparison-chart-card">
                    <div class="chart-card-header">
                        <i class="fas fa-chart-bar"></i> Performance Metrics
                    </div>
                    <div class="chart-canvas-wrapper">
                        <canvas id="comparison-bar-chart"></canvas>
                    </div>
                </div>

                <div class="comparison-chart-card">
                    <div class="chart-card-header">
                        <i class="fas fa-table"></i> Statistical Comparison
                    </div>
                    ${this.renderComparisonTable()}
                </div>
            </div>
        `;
    }

    /**
     * Render comparison table
     */
    renderComparisonTable() {
        const metrics = ['Total Scorecards', 'Avg Score', 'Last Activity'];
        
        let html = `
            <table class="metrics-comparison-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        ${this.selectedPlayers.map(p => `<th>${p.name}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
        `;

        metrics.forEach(metric => {
            html += `<tr><td><strong>${metric}</strong></td>`;
            
            this.selectedPlayers.forEach(player => {
                let value = '';
                if (metric === 'Total Scorecards') {
                    value = player.scorecard_count || 0;
                } else if (metric === 'Avg Score') {
                    value = Math.floor(Math.random() * 30) + 60; // Mock
                } else if (metric === 'Last Activity') {
                    value = player.last_scorecard || 'N/A';
                }
                html += `<td class="metric-value">${value}</td>`;
            });
            
            html += `</tr>`;
        });

        html += `</tbody></table>`;
        return html;
    }

    /**
     * Render action buttons
     */
    renderActionButtons() {
        return `
            <div class="comparison-actions">
                <button class="comparison-action-btn" onclick="playerComparison.exportComparison('pdf')">
                    <i class="fas fa-file-pdf"></i> Export PDF
                </button>
                <button class="comparison-action-btn" onclick="playerComparison.exportComparison('image')">
                    <i class="fas fa-image"></i> Export Image
                </button>
                <button class="comparison-action-btn" onclick="playerComparison.clearAllPlayers()">
                    <i class="fas fa-trash"></i> Clear All
                </button>
            </div>
        `;
    }

    /**
     * Generate comparison charts
     */
    generateComparisonCharts() {
        if (typeof window.playerViz === 'undefined') {
            console.warn('PlayerVisualization not available');
            return;
        }

        // Radar chart
        const radarCanvas = document.getElementById('comparison-radar-chart');
        if (radarCanvas) {
            this.charts.radar = window.playerViz.createComparisonRadarChart(
                'comparison-radar-chart',
                this.selectedPlayers
            );
        }

        // Bar chart
        const barCanvas = document.getElementById('comparison-bar-chart');
        if (barCanvas) {
            this.charts.bar = window.playerViz.createComparisonBarChart(
                'comparison-bar-chart',
                this.selectedPlayers
            );
        }
    }

    /**
     * Export comparison
     */
    exportComparison(format = 'pdf') {
        if (this.selectedPlayers.length < 2) {
            this.showNotification('Add at least 2 players to export comparison', 'warning');
            return;
        }

        if (format === 'image') {
            this.exportAsImage();
        } else if (format === 'pdf') {
            this.exportAsPDF();
        }
    }

    /**
     * Export as image
     */
    exportAsImage() {
        const panel = document.getElementById('comparison-panel-content');
        if (!panel) return;

        // Use html2canvas library if available
        if (typeof html2canvas !== 'undefined') {
            html2canvas(panel).then(canvas => {
                const link = document.createElement('a');
                link.download = `player_comparison_${Date.now()}.png`;
                link.href = canvas.toDataURL();
                link.click();
            });
        } else {
            this.showNotification('Export library not loaded', 'error');
        }
    }

    /**
     * Export as PDF
     */
    exportAsPDF() {
        // Trigger print dialog
        window.print();
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key] && typeof this.charts[key].destroy === 'function') {
                this.charts[key].destroy();
            }
        });
        this.charts = {};
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }
}

// Initialize and export
if (typeof window !== 'undefined') {
    window.PlayerComparison = PlayerComparison;
    window.playerComparison = new PlayerComparison();
}

