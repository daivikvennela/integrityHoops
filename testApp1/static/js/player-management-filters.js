/**
 * Real-Time Player Filtering System
 * Instant search, sorting, and advanced filters without page reload
 */

class PlayerFilterSystem {
    constructor() {
        this.players = [];
        this.filteredPlayers = [];
        this.filters = {
            search: '',
            sortBy: 'name',
            sortOrder: 'asc',
            scorecardMin: 0,
            scorecardMax: 1000,
            dateRange: null,
            quickFilters: new Set()
        };
        this.searchDebounceTimer = null;
        this.debounceDelay = 300;
        this.initialized = false;
    }

    /**
     * Initialize the filter system
     */
    init() {
        if (this.initialized) return;
        
        this.setupEventListeners();
        this.initialized = true;
        console.log('Player Filter System initialized');
    }

    /**
     * Setup all event listeners for filter controls
     */
    setupEventListeners() {
        // Search input with debounce
        const searchInput = document.getElementById('player-search-modern');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.debouncedSearch(e.target.value);
            });
        }

        // Sort dropdown
        const sortSelect = document.getElementById('sort-filter-modern');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.filters.sortBy = e.target.value;
                this.applyFilters();
            });
        }

        // Sort order toggle
        const sortOrderBtn = document.getElementById('sort-order-toggle');
        if (sortOrderBtn) {
            sortOrderBtn.addEventListener('click', () => {
                this.toggleSortOrder();
            });
        }

        // Scorecard range sliders
        const scorecardMinSlider = document.getElementById('scorecard-min-slider');
        const scorecardMaxSlider = document.getElementById('scorecard-max-slider');
        
        if (scorecardMinSlider) {
            scorecardMinSlider.addEventListener('input', (e) => {
                this.filters.scorecardMin = parseInt(e.target.value);
                this.updateRangeDisplay('scorecard-min-value', this.filters.scorecardMin);
                this.applyFilters();
            });
        }
        
        if (scorecardMaxSlider) {
            scorecardMaxSlider.addEventListener('input', (e) => {
                this.filters.scorecardMax = parseInt(e.target.value);
                this.updateRangeDisplay('scorecard-max-value', this.filters.scorecardMax);
                this.applyFilters();
            });
        }

        // Quick filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                this.toggleQuickFilter(e.target.dataset.filter);
            });
        });

        // Clear filters button
        const clearBtn = document.getElementById('clear-filters-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }
    }

    /**
     * Debounced search to avoid excessive filtering
     */
    debouncedSearch(searchTerm) {
        clearTimeout(this.searchDebounceTimer);
        
        // Show loading indicator
        this.showSearchLoading();
        
        this.searchDebounceTimer = setTimeout(() => {
            this.filters.search = searchTerm.toLowerCase().trim();
            this.applyFilters();
            this.hideSearchLoading();
        }, this.debounceDelay);
    }

    /**
     * Load players data
     */
    loadPlayers(players) {
        this.players = players;
        this.filteredPlayers = [...players];
        this.applyFilters();
    }

    /**
     * Apply all active filters
     */
    applyFilters() {
        let filtered = [...this.players];

        // Search filter
        if (this.filters.search) {
            filtered = filtered.filter(player => 
                player.name.toLowerCase().includes(this.filters.search)
            );
        }

        // Scorecard count filter
        filtered = filtered.filter(player => {
            const count = player.scorecard_count || 0;
            return count >= this.filters.scorecardMin && count <= this.filters.scorecardMax;
        });

        // Quick filters
        if (this.filters.quickFilters.has('active_7d')) {
            const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
            filtered = filtered.filter(player => {
                const lastActivity = this.getLastActivity(player);
                return lastActivity && lastActivity > sevenDaysAgo;
            });
        }

        if (this.filters.quickFilters.has('high_performers')) {
            const avgScorecards = this.calculateAverageScorecards();
            filtered = filtered.filter(player => 
                (player.scorecard_count || 0) > avgScorecards
            );
        }

        if (this.filters.quickFilters.has('no_scorecards')) {
            filtered = filtered.filter(player => 
                (player.scorecard_count || 0) === 0
            );
        }

        if (this.filters.quickFilters.has('new_players')) {
            const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
            filtered = filtered.filter(player => 
                player.date_created * 1000 > thirtyDaysAgo
            );
        }

        // Sorting
        filtered = this.sortPlayers(filtered);

        this.filteredPlayers = filtered;
        this.updateDisplay();
        this.updateFilterStats();
    }

    /**
     * Sort players based on current sort settings
     */
    sortPlayers(players) {
        const sortMultiplier = this.filters.sortOrder === 'asc' ? 1 : -1;

        return players.sort((a, b) => {
            let comparison = 0;

            switch (this.filters.sortBy) {
                case 'name':
                    comparison = a.name.localeCompare(b.name);
                    break;
                case 'date':
                    comparison = (a.date_created || 0) - (b.date_created || 0);
                    break;
                case 'scorecards':
                    comparison = (a.scorecard_count || 0) - (b.scorecard_count || 0);
                    break;
                case 'last_activity':
                    const aActivity = this.getLastActivity(a) || 0;
                    const bActivity = this.getLastActivity(b) || 0;
                    comparison = aActivity - bActivity;
                    break;
                default:
                    comparison = 0;
            }

            return comparison * sortMultiplier;
        });
    }

    /**
     * Toggle sort order
     */
    toggleSortOrder() {
        this.filters.sortOrder = this.filters.sortOrder === 'asc' ? 'desc' : 'asc';
        
        const btn = document.getElementById('sort-order-toggle');
        if (btn) {
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = this.filters.sortOrder === 'asc' 
                    ? 'fas fa-sort-amount-up' 
                    : 'fas fa-sort-amount-down';
            }
        }
        
        this.applyFilters();
    }

    /**
     * Toggle quick filter chip
     */
    toggleQuickFilter(filterKey) {
        const chip = document.querySelector(`.filter-chip[data-filter="${filterKey}"]`);
        
        if (this.filters.quickFilters.has(filterKey)) {
            this.filters.quickFilters.delete(filterKey);
            if (chip) chip.classList.remove('active');
        } else {
            this.filters.quickFilters.add(filterKey);
            if (chip) chip.classList.add('active');
        }
        
        this.applyFilters();
    }

    /**
     * Clear all filters
     */
    clearAllFilters() {
        this.filters = {
            search: '',
            sortBy: 'name',
            sortOrder: 'asc',
            scorecardMin: 0,
            scorecardMax: 1000,
            dateRange: null,
            quickFilters: new Set()
        };

        // Reset UI
        const searchInput = document.getElementById('player-search-modern');
        if (searchInput) searchInput.value = '';

        const sortSelect = document.getElementById('sort-filter-modern');
        if (sortSelect) sortSelect.value = 'name';

        const scorecardMinSlider = document.getElementById('scorecard-min-slider');
        if (scorecardMinSlider) {
            scorecardMinSlider.value = 0;
            this.updateRangeDisplay('scorecard-min-value', 0);
        }

        const scorecardMaxSlider = document.getElementById('scorecard-max-slider');
        if (scorecardMaxSlider) {
            scorecardMaxSlider.value = 1000;
            this.updateRangeDisplay('scorecard-max-value', 1000);
        }

        document.querySelectorAll('.filter-chip.active').forEach(chip => {
            chip.classList.remove('active');
        });

        this.applyFilters();
    }

    /**
     * Update the filtered players display
     */
    updateDisplay() {
        if (typeof window.displayPlayers === 'function') {
            window.displayPlayers(this.filteredPlayers);
        } else {
            console.warn('displayPlayers function not found');
        }
    }

    /**
     * Update filter statistics display
     */
    updateFilterStats() {
        const statsEl = document.getElementById('filter-stats');
        if (statsEl) {
            const total = this.players.length;
            const filtered = this.filteredPlayers.length;
            
            if (filtered < total) {
                statsEl.textContent = `Showing ${filtered} of ${total} players`;
                statsEl.style.display = 'block';
            } else {
                statsEl.style.display = 'none';
            }
        }
    }

    /**
     * Update range slider display value
     */
    updateRangeDisplay(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = value;
        }
    }

    /**
     * Show search loading indicator
     */
    showSearchLoading() {
        const searchInput = document.getElementById('player-search-modern');
        if (searchInput) {
            searchInput.classList.add('loading');
        }
    }

    /**
     * Hide search loading indicator
     */
    hideSearchLoading() {
        const searchInput = document.getElementById('player-search-modern');
        if (searchInput) {
            searchInput.classList.remove('loading');
        }
    }

    /**
     * Get last activity timestamp for a player
     */
    getLastActivity(player) {
        if (!player.last_scorecard) return null;
        
        try {
            // Parse last_scorecard string to timestamp
            const date = new Date(player.last_scorecard);
            return date.getTime();
        } catch (e) {
            return null;
        }
    }

    /**
     * Calculate average scorecards across all players
     */
    calculateAverageScorecards() {
        if (this.players.length === 0) return 0;
        
        const total = this.players.reduce((sum, player) => 
            sum + (player.scorecard_count || 0), 0
        );
        
        return total / this.players.length;
    }

    /**
     * Export current filtered results
     */
    exportFiltered(format = 'json') {
        const data = {
            filters: {
                search: this.filters.search,
                sortBy: this.filters.sortBy,
                sortOrder: this.filters.sortOrder,
                scorecardRange: [this.filters.scorecardMin, this.filters.scorecardMax],
                quickFilters: Array.from(this.filters.quickFilters)
            },
            totalPlayers: this.players.length,
            filteredCount: this.filteredPlayers.length,
            players: this.filteredPlayers
        };

        if (format === 'json') {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `filtered_players_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } else if (format === 'csv') {
            let csv = 'Name,Scorecards,Created Date,Last Activity\n';
            this.filteredPlayers.forEach(player => {
                csv += `"${player.name}",${player.scorecard_count || 0},"${player.date_created_readable || ''}","${player.last_scorecard || 'N/A'}"\n`;
            });
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `filtered_players_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }

    /**
     * Get current filter state (for persistence)
     */
    getFilterState() {
        return {
            search: this.filters.search,
            sortBy: this.filters.sortBy,
            sortOrder: this.filters.sortOrder,
            scorecardMin: this.filters.scorecardMin,
            scorecardMax: this.filters.scorecardMax,
            quickFilters: Array.from(this.filters.quickFilters)
        };
    }

    /**
     * Restore filter state (from persistence)
     */
    restoreFilterState(state) {
        if (!state) return;
        
        this.filters = {
            ...this.filters,
            ...state,
            quickFilters: new Set(state.quickFilters || [])
        };
        
        // Update UI to reflect restored state
        const searchInput = document.getElementById('player-search-modern');
        if (searchInput && state.search) {
            searchInput.value = state.search;
        }
        
        const sortSelect = document.getElementById('sort-filter-modern');
        if (sortSelect && state.sortBy) {
            sortSelect.value = state.sortBy;
        }
        
        this.applyFilters();
    }
}

// Initialize filter system when DOM is ready
let filterSystem = null;

function initializeFilterSystem() {
    filterSystem = new PlayerFilterSystem();
    filterSystem.init();
    return filterSystem;
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.PlayerFilterSystem = PlayerFilterSystem;
    window.initializeFilterSystem = initializeFilterSystem;
    window.filterSystem = null; // Will be initialized in dashboard
}

