document.addEventListener('DOMContentLoaded', function() {
    // Advanced Visualization Dashboard
    class SoccerAnalyticsDashboard {
        constructor() {
            this.initCharts();
            this.setupEventListeners();
        }

        initCharts() {
            // Performance Distribution Chart
            this.renderPerformanceDistribution();
            
            // Team Comparison Chart
            this.renderTeamComparisonChart();
            
            // Player Position Analysis
            this.renderPositionPerformanceChart();
            
            // Feature Importance Visualization
            this.renderFeatureImportanceChart();
            
            // Player Similarity Network
            this.renderPlayerSimilarityNetwork();
        }

        async fetchAnalyticsData() {
            try {
                const response = await fetch('/team_performance_analysis');
                if (!response.ok) {
                    throw new Error('Failed to fetch analytics data');
                }
                return await response.json();
            } catch (error) {
                console.error('Analytics Data Fetch Error:', error);
                return null;
            }
        }

        renderPerformanceDistribution() {
            const ctx = document.getElementById('performanceDistributionChart').getContext('2d');
            
            // Sample data, replace with actual fetched data
            new Chart(ctx, {
                type: 'boxplot',
                data: {
                    labels: ['Forwards', 'Midfielders', 'Defenders', 'Goalkeepers'],
                    datasets: [{
                        label: 'Performance Distribution',
                        data: [
                            [20, 25, 30, 35, 40],  // Forwards
                            [15, 20, 25, 30, 35],  // Midfielders
                            [10, 15, 20, 25, 30],  // Defenders
                            [5, 10, 15, 20, 25]    // Goalkeepers
                        ],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Player Performance Distribution by Position'
                    }
                }
            });
        }

        renderTeamComparisonChart() {
            const ctx = document.getElementById('teamComparisonChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Goals', 'Assists', 'Pass Accuracy', 'Shot Accuracy', 'Tackles'],
                    datasets: [
                        {
                            label: 'Manchester City',
                            data: [85, 75, 88, 82, 70],
                            backgroundColor: 'rgba(54, 162, 235, 0.2)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            pointBackgroundColor: 'rgba(54, 162, 235, 1)'
                        },
                        {
                            label: 'Arsenal',
                            data: [80, 70, 85, 79, 65],
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            pointBackgroundColor: 'rgba(255, 99, 132, 1)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Team Performance Comparison'
                    }
                }
            });
        }

        renderPositionPerformanceChart() {
            const ctx = document.getElementById('positionPerformanceChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Forwards', 'Midfielders', 'Defenders', 'Goalkeepers'],
                    datasets: [{
                        label: 'Average Performance Score',
                        data: [69.29, 67.36, 59.33, 52.50],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Performance by Player Position'
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]
                    }
                }
            });
        }

        renderFeatureImportanceChart() {
            const ctx = document.getElementById('featureImportanceChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'horizontalBar',
                data: {
                    labels: [
                        'Shot Accuracy', 'Goals', 'Assists', 
                        'Pass Accuracy', 'Tackles Won'
                    ],
                    datasets: [{
                        label: 'Feature Importance',
                        data: [47.55, 28.38, 14.76, 5.86, 2.02],
                        backgroundColor: 'rgba(75, 192, 192, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Player Performance Feature Importance'
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]
                    }
                }
            });
        }

        renderPlayerSimilarityNetwork() {
            // This would typically use a library like D3.js for complex network visualization
            const ctx = document.getElementById('playerSimilarityNetwork').getContext('2d');
            
            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Player Similarity',
                        data: [
                            {x: 0.98, y: 0.5, r: 10},  // Mohamed Salah
                            {x: 0.87, y: 0.4, r: 8},   // Gabriel Martinelli
                            {x: 0.96, y: 0.6, r: 9},   // Trent Alexander-Arnold
                            {x: 0.87, y: 0.3, r: 7}    // Phil Foden
                        ],
                        backgroundColor: 'rgba(255, 99, 132, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    title: {
                        display: true,
                        text: 'Player Similarity Network'
                    },
                    scales: {
                        xAxes: [{
                            type: 'linear',
                            position: 'bottom',
                            scaleLabel: {
                                display: true,
                                labelString: 'Similarity Score'
                            }
                        }],
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: 'Performance Metric'
                            }
                        }]
                    }
                }
            });
        }

        setupEventListeners() {
            // Interactive features
            document.getElementById('recommendPlayerBtn').addEventListener('click', this.recommendPlayers);
            document.getElementById('predictPerformanceBtn').addEventListener('click', this.predictPlayerPerformance);
        }

        async recommendPlayers() {
            const playerName = document.getElementById('playerNameInput').value;
            try {
                const response = await fetch('/recommend_players', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ player_name: playerName })
                });
                const data = await response.json();
                
                // Display recommendations
                const recommendationList = document.getElementById('recommendationsList');
                recommendationList.innerHTML = data.recommendations.map(player => 
                    `<li>${player.Player_Name} (${player.Club}) - Similarity: ${player.Similarity_Score.toFixed(2)}</li>`
                ).join('');
            } catch (error) {
                console.error('Recommendation Error:', error);
            }
        }

        async predictPlayerPerformance() {
            // Placeholder for performance prediction
            alert('Performance prediction feature coming soon!');
        }
    }

    // Initialize dashboard
    new SoccerAnalyticsDashboard();
});
