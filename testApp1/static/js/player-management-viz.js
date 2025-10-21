/**
 * Advanced Player Management Visualizations
 * Radar charts, heatmaps, timelines, and comparison charts
 */

class PlayerVisualization {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#F9423A',
            secondary: '#FF5349',
            success: '#4ade80',
            warning: '#fbbf24',
            danger: '#f87171',
            info: '#60a5fa'
        };
    }

    /**
     * Create cognitive radar chart for a player
     */
    createCognitiveRadarChart(containerId, playerData) {
        const canvas = document.getElementById(containerId);
        if (!canvas) {
            console.error(`Canvas ${containerId} not found`);
            return null;
        }

        // Destroy existing chart
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const ctx = canvas.getContext('2d');
        
        // Extract cognitive metrics
        const metrics = this.extractCognitiveMetrics(playerData);
        
        this.charts[containerId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: metrics.labels,
                datasets: [{
                    label: playerData.name,
                    data: metrics.values,
                    backgroundColor: 'rgba(249, 66, 58, 0.2)',
                    borderColor: this.colors.primary,
                    borderWidth: 2,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: this.colors.primary,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: 'white',
                            font: {
                                size: 14,
                                weight: '600'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: this.colors.primary,
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 2,
                        padding: 12,
                        displayColors: true
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: 'rgba(255, 255, 255, 0.7)',
                            backdropColor: 'transparent'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: 'white',
                            font: {
                                size: 12,
                                weight: '600'
                            }
                        }
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    /**
     * Create comparison radar chart for multiple players
     */
    createComparisonRadarChart(containerId, playersData) {
        const canvas = document.getElementById(containerId);
        if (!canvas) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const ctx = canvas.getContext('2d');
        const playerColors = [
            { bg: 'rgba(249, 66, 58, 0.2)', border: '#F9423A' },
            { bg: 'rgba(96, 165, 250, 0.2)', border: '#60a5fa' },
            { bg: 'rgba(74, 222, 128, 0.2)', border: '#4ade80' },
            { bg: 'rgba(251, 191, 36, 0.2)', border: '#fbbf24' }
        ];

        const datasets = playersData.map((player, index) => {
            const metrics = this.extractCognitiveMetrics(player);
            const colorSet = playerColors[index % playerColors.length];
            
            return {
                label: player.name,
                data: metrics.values,
                backgroundColor: colorSet.bg,
                borderColor: colorSet.border,
                borderWidth: 2,
                pointBackgroundColor: colorSet.border,
                pointBorderColor: '#fff',
                pointRadius: 4
            };
        });

        const metrics = this.extractCognitiveMetrics(playersData[0]);

        this.charts[containerId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: metrics.labels,
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
                            color: 'white',
                            padding: 15,
                            font: { size: 13, weight: '600' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: this.colors.primary,
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 2,
                        padding: 12
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: 'rgba(255, 255, 255, 0.7)',
                            backdropColor: 'transparent'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: 'white',
                            font: { size: 11, weight: '600' }
                        }
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    /**
     * Extract cognitive metrics from player data
     */
    extractCognitiveMetrics(playerData) {
        // Calculate averages for each category
        const categories = {
            'Space Read': this.calculateCategoryAverage(playerData, 'space_read'),
            'DM Catch': this.calculateCategoryAverage(playerData, 'dm_catch'),
            'QB12': this.calculateCategoryAverage(playerData, 'qb12'),
            'Driving': this.calculateCategoryAverage(playerData, 'driving'),
            'Off Ball': this.calculateCategoryAverage(playerData, 'offball'),
            'Cutting & Screening': this.calculateCategoryAverage(playerData, 'cs'),
            'Relocation': this.calculateCategoryAverage(playerData, 'relocation')
        };

        return {
            labels: Object.keys(categories),
            values: Object.values(categories)
        };
    }

    /**
     * Calculate average for a cognitive category
     */
    calculateCategoryAverage(playerData, category) {
        // Mock calculation - would need actual scorecard data
        // Return random value for demo purposes
        return Math.floor(Math.random() * 50) + 30;
    }

    /**
     * Create scorecard heatmap using D3.js
     */
    createScorecardHeatmap(containerId, scorecardData) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Clear existing content
        container.innerHTML = '';

        const width = container.clientWidth;
        const height = 400;
        const margin = { top: 60, right: 100, bottom: 60, left: 150 };

        const svg = d3.select(`#${containerId}`)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        // Create heatmap data structure
        const attributes = this.getAllScorecardAttributes();
        const games = scorecardData.map((_, i) => `Game ${i + 1}`);

        // Create scales
        const xScale = d3.scaleBand()
            .domain(games)
            .range([margin.left, width - margin.right])
            .padding(0.05);

        const yScale = d3.scaleBand()
            .domain(attributes)
            .range([margin.top, height - margin.bottom])
            .padding(0.05);

        const colorScale = d3.scaleLinear()
            .domain([-10, 0, 10])
            .range(['#f87171', '#ffffff', '#4ade80']);

        // Draw cells
        const g = svg.append('g');

        attributes.forEach(attr => {
            games.forEach((game, gameIndex) => {
                const value = this.getAttributeValue(scorecardData[gameIndex], attr);
                
                g.append('rect')
                    .attr('x', xScale(game))
                    .attr('y', yScale(attr))
                    .attr('width', xScale.bandwidth())
                    .attr('height', yScale.bandwidth())
                    .attr('fill', colorScale(value))
                    .attr('stroke', 'rgba(0, 0, 0, 0.2)')
                    .attr('stroke-width', 1)
                    .on('mouseover', function(event) {
                        d3.select(this)
                            .attr('stroke', '#F9423A')
                            .attr('stroke-width', 2);
                        
                        showTooltip(event, `${attr}: ${value}`, game);
                    })
                    .on('mouseout', function() {
                        d3.select(this)
                            .attr('stroke', 'rgba(0, 0, 0, 0.2)')
                            .attr('stroke-width', 1);
                        
                        hideTooltip();
                    });
            });
        });

        // Add axes
        svg.append('g')
            .attr('transform', `translate(0, ${margin.top})`)
            .call(d3.axisTop(xScale))
            .selectAll('text')
            .attr('fill', 'white')
            .style('font-size', '11px');

        svg.append('g')
            .attr('transform', `translate(${margin.left}, 0)`)
            .call(d3.axisLeft(yScale))
            .selectAll('text')
            .attr('fill', 'white')
            .style('font-size', '10px');
    }

    /**
     * Create player timeline visualization
     */
    createPlayerTimeline(containerId, scorecards) {
        const canvas = document.getElementById(containerId);
        if (!canvas) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const ctx = canvas.getContext('2d');

        // Prepare timeline data
        const timelineData = scorecards.map(scorecard => ({
            x: new Date(scorecard.date_created * 1000),
            y: this.calculateOverallScore(scorecard)
        }));

        this.charts[containerId] = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Performance Over Time',
                    data: timelineData,
                    borderColor: this.colors.primary,
                    backgroundColor: 'rgba(249, 66, 58, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
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
                            color: 'white',
                            font: { size: 14, weight: '600' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: this.colors.primary,
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 2,
                        padding: 12,
                        callbacks: {
                            title: (context) => {
                                return new Date(context[0].parsed.x).toLocaleDateString();
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'MMM dd'
                            }
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 11 }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 11 }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    /**
     * Create comparison bar chart
     */
    createComparisonBarChart(containerId, players) {
        const canvas = document.getElementById(containerId);
        if (!canvas) return null;

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }

        const ctx = canvas.getContext('2d');
        
        const categories = ['Space Read', 'DM Catch', 'QB12', 'Driving', 'Off Ball'];
        const datasets = players.map((player, index) => {
            const colors = [this.colors.primary, this.colors.info, this.colors.success, this.colors.warning];
            return {
                label: player.name,
                data: categories.map(() => Math.floor(Math.random() * 50) + 30),
                backgroundColor: colors[index % colors.length] + '80',
                borderColor: colors[index % colors.length],
                borderWidth: 2
            };
        });

        this.charts[containerId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: 'white',
                            padding: 15,
                            font: { size: 13, weight: '600' }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: this.colors.primary,
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 2,
                        padding: 12
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 11 }
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 11 }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });

        return this.charts[containerId];
    }

    /**
     * Helper: Get all scorecard attributes
     */
    getAllScorecardAttributes() {
        return [
            'Space Read Live', 'Space Read Catch',
            'DM Catch B2B', 'DM Catch Shot',
            'QB12 Strong', 'QB12 Weak',
            'Driving Touch', 'Driving Physical',
            'Off Ball Position', 'Transition'
        ];
    }

    /**
     * Helper: Get attribute value from scorecard
     */
    getAttributeValue(scorecard, attribute) {
        // Mock calculation
        return Math.floor(Math.random() * 20) - 10;
    }

    /**
     * Helper: Calculate overall score
     */
    calculateOverallScore(scorecard) {
        // Mock calculation
        return Math.floor(Math.random() * 40) + 40;
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(containerId) {
        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
            delete this.charts[containerId];
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(key => {
            this.charts[key].destroy();
        });
        this.charts = {};
    }
}

// Tooltip helpers for D3 visualizations
function showTooltip(event, content, title) {
    const tooltip = d3.select('body').append('div')
        .attr('class', 'modern-tooltip')
        .style('position', 'absolute')
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .style('opacity', 0);

    tooltip.html(`<strong>${title}</strong><br/>${content}`)
        .transition()
        .duration(200)
        .style('opacity', 1);
}

function hideTooltip() {
    d3.selectAll('.modern-tooltip').remove();
}

// Initialize and export
if (typeof window !== 'undefined') {
    window.PlayerVisualization = PlayerVisualization;
    window.playerViz = new PlayerVisualization();
}

