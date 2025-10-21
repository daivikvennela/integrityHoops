/**
 * SQL Database Visualization
 * Visualize database metrics, attribute usage, and data quality
 */

class SQLVisualization {
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
     * Initialize SQL visualizations
     */
    async init() {
        try {
            const data = await this.fetchDatabaseMetrics();
            if (data && data.success) {
                this.visualizeSQLMetrics(data);
            }
        } catch (error) {
            console.error('Error initializing SQL visualizations:', error);
        }
    }

    /**
     * Fetch database metrics from API
     */
    async fetchDatabaseMetrics() {
        try {
            const response = await fetch('/api/database/detailed-stats');
            return await response.json();
        } catch (error) {
            console.error('Error fetching database metrics:', error);
            return null;
        }
    }

    /**
     * Visualize all SQL metrics
     */
    visualizeSQLMetrics(data) {
        if (data.attribute_usage) {
            this.createAttributeUsageHeatmap(data.attribute_usage);
        }
        
        if (data.table_stats) {
            this.createTableDistributionChart(data.table_stats);
        }
        
        if (data.data_quality) {
            this.createDataCompletenessChart(data.data_quality);
        }
    }

    /**
     * Create attribute usage heatmap
     */
    createAttributeUsageHeatmap(attributeData) {
        const canvas = document.getElementById('attributeHeatmap');
        if (!canvas) return;

        if (this.charts.heatmap) {
            this.charts.heatmap.destroy();
        }

        const ctx = canvas.getContext('2d');

        // Transform data for matrix display
        const attributes = Object.keys(attributeData);
        const values = attributes.map(attr => attributeData[attr]);

        // Create a pseudo-heatmap using bar chart
        this.charts.heatmap = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: attributes.map(attr => this.formatAttributeName(attr)),
                datasets: [{
                    label: 'Usage Frequency',
                    data: values,
                    backgroundColor: values.map(val => this.getHeatColor(val)),
                    borderColor: 'rgba(249, 66, 58, 0.5)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: this.colors.primary,
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 2,
                        padding: 12,
                        callbacks: {
                            label: (context) => {
                                return `Used ${context.parsed.x} times`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Scorecard Attribute Usage',
                        color: 'white',
                        font: {
                            size: 16,
                            weight: '700'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 11 }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            font: { size: 10 }
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    /**
     * Create table distribution pie chart
     */
    createTableDistributionChart(tableStats) {
        const canvas = document.getElementById('tableUsageChart');
        if (!canvas) return;

        if (this.charts.tableDistribution) {
            this.charts.tableDistribution.destroy();
        }

        const ctx = canvas.getContext('2d');

        const tables = Object.keys(tableStats);
        const counts = tables.map(table => tableStats[table].row_count || 0);

        this.charts.tableDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: tables.map(t => this.formatTableName(t)),
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        'rgba(249, 66, 58, 0.8)',
                        'rgba(96, 165, 250, 0.8)',
                        'rgba(74, 222, 128, 0.8)',
                        'rgba(251, 191, 36, 0.8)',
                        'rgba(168, 85, 247, 0.8)'
                    ],
                    borderColor: 'rgba(0, 0, 0, 0.8)',
                    borderWidth: 2
                }]
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
                            font: { size: 12, weight: '600' }
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
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} rows (${percentage}%)`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Table Size Distribution',
                        color: 'white',
                        font: {
                            size: 16,
                            weight: '700'
                        }
                    }
                }
            }
        });
    }

    /**
     * Create data completeness bar chart
     */
    createDataCompletenessChart(qualityData) {
        const canvas = document.getElementById('dataCompletenessChart');
        if (!canvas) return;

        if (this.charts.completeness) {
            this.charts.completeness.destroy();
        }

        const ctx = canvas.getContext('2d');

        const metrics = Object.keys(qualityData);
        const values = metrics.map(metric => qualityData[metric]);

        this.charts.completeness = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: metrics.map(m => this.formatMetricName(m)),
                datasets: [{
                    label: 'Completeness %',
                    data: values,
                    backgroundColor: values.map(val => this.getCompletenessColor(val)),
                    borderColor: 'rgba(249, 66, 58, 0.5)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: this.colors.primary,
                        bodyColor: 'white',
                        borderColor: this.colors.primary,
                        borderWidth: 2,
                        padding: 12,
                        callbacks: {
                            label: (context) => {
                                return `${context.parsed.y.toFixed(1)}% complete`;
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Data Quality Metrics',
                        color: 'white',
                        font: {
                            size: 16,
                            weight: '700'
                        }
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
                            font: { size: 11 },
                            callback: (value) => value + '%'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }

    /**
     * Get heat color based on value
     */
    getHeatColor(value) {
        const max = 100; // Adjust based on your data
        const ratio = Math.min(value / max, 1);
        
        if (ratio < 0.33) {
            return 'rgba(96, 165, 250, 0.8)'; // Blue (low)
        } else if (ratio < 0.66) {
            return 'rgba(251, 191, 36, 0.8)'; // Yellow (medium)
        } else {
            return 'rgba(249, 66, 58, 0.8)'; // Red (high)
        }
    }

    /**
     * Get completeness color based on percentage
     */
    getCompletenessColor(percentage) {
        if (percentage >= 90) {
            return 'rgba(74, 222, 128, 0.8)'; // Green
        } else if (percentage >= 70) {
            return 'rgba(251, 191, 36, 0.8)'; // Yellow
        } else {
            return 'rgba(248, 113, 113, 0.8)'; // Red
        }
    }

    /**
     * Format attribute name for display
     */
    formatAttributeName(attr) {
        return attr.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Format table name for display
     */
    formatTableName(table) {
        return table.charAt(0).toUpperCase() + table.slice(1);
    }

    /**
     * Format metric name for display
     */
    formatMetricName(metric) {
        return metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Destroy a specific chart
     */
    destroyChart(chartId) {
        if (this.charts[chartId]) {
            this.charts[chartId].destroy();
            delete this.charts[chartId];
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

    /**
     * Refresh all visualizations
     */
    async refresh() {
        this.destroyAllCharts();
        await this.init();
    }
}

// Initialize and export
if (typeof window !== 'undefined') {
    window.SQLVisualization = SQLVisualization;
    window.sqlViz = new SQLVisualization();
}

