// Global variables
let currentTeam = 'all';
let playersData = [];
let featureImportance = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Add click event listeners to club filter buttons (which contain team logos)
    const clubFilters = document.querySelectorAll('.club-filter');
    console.log(`Found ${clubFilters.length} club filters`);
    
    clubFilters.forEach(filter => {
        // Skip the "All Teams" filter
        if (filter.getAttribute('data-club') === 'all') return;
        
        filter.addEventListener('click', function(event) {
            const teamName = this.querySelector('span').textContent.trim();
            console.log(`Clicked team filter: ${teamName}`);
            
            // Prevent default behavior
            event.preventDefault();
            event.stopPropagation();
            
            // Show team details
            showTeamDetails(teamName);
        });
    });

    // Ensure modal close functionality
    const closeModalBtn = document.querySelector('.close-modal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            const modal = document.getElementById('teamModal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }

    // Close modal when clicking outside
    const modal = document.getElementById('teamModal');
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    loadFeatureImportance();
    loadPlayers();
    setupTeamLogos();
    loadTeamsAndPlayers();
});

// Load feature importance data
async function loadFeatureImportance() {
    try {
        const response = await fetch('/api/feature-importance');
        featureImportance = await response.json();
    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

// Setup team logo click handlers
function setupTeamLogos() {
    document.querySelectorAll('.team-logo').forEach(logo => {
        logo.addEventListener('click', function() {
            const teamName = this.alt.replace(' Logo', '');
            showTeamDetails(teamName);
        });
    });
}

// Load players data
async function loadPlayers() {
    try {
        const url = currentTeam === 'all' 
            ? '/api/players'
            : `/api/players?club=${encodeURIComponent(currentTeam)}`;
            
        const response = await fetch(url);
        playersData = await response.json();
        updatePlayersTable(playersData);
    } catch (error) {
        console.error('Error loading players:', error);
    }
}

// Function to show team details modal
async function showTeamDetails(teamName) {
    console.log(`Attempting to show details for team: ${teamName}`);
    
    // Normalize team name
    const normalizedTeamName = normalizeTeamName(teamName);
    
    const modal = document.getElementById('teamModal');
    const teamLogo = document.getElementById('teamLogo');
    const teamNameEl = document.getElementById('teamName');
    
    // Validate modal elements exist
    if (!modal || !teamLogo || !teamNameEl) {
        console.error('Modal elements not found. Check your HTML structure.');
        alert('Modal setup error. Please check console.');
        return;
    }

    try {
        // Fetch team details with error handling
        const response = await fetch(`/get_team_details/${encodeURIComponent(normalizedTeamName)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        // Check response status
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        // Parse JSON safely
        const data = await response.json();
        
        // Validate received data
        if (!data || !data.team_name) {
            throw new Error('Received invalid team data');
        }
        
        console.log('Team details received:', data);
        
        // Update team header
        try {
            teamLogo.src = `/static/images/${data.team_name.toLowerCase().replace(/\s+/g, '-')}.png`;
            teamNameEl.textContent = data.team_name;
        } catch (logoError) {
            console.warn('Error setting team logo:', logoError);
            teamLogo.src = '/static/images/premier-league.png'; // Fallback logo
        }
        
        // Update team metadata with fallback values
        document.getElementById('teamRating').textContent = 
            (data.team_rating || 'N/A').toFixed(1);
        document.getElementById('teamForm').textContent = 
            data.team_form || 'N/A';
        document.getElementById('formation').textContent = 
            data.formation || 'N/A';
        
        // Update team stats
        const statsGrid = document.querySelector('.team-stats-grid');
        if (statsGrid) {
            const stats = data.team_stats || {};
            statsGrid.innerHTML = `
                <div class="stat-box">
                    <div class="value">${stats.total_goals || 0}</div>
                    <div class="label">Goals</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.total_assists || 0}</div>
                    <div class="label">Assists</div>
                </div>
                <div class="stat-box">
                    <div class="value">${(stats.avg_pass_accuracy || 0).toFixed(1)}%</div>
                    <div class="label">Pass Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="value">${(stats.avg_shot_accuracy || 0).toFixed(1)}%</div>
                    <div class="label">Shot Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.total_tackles || 0}</div>
                    <div class="label">Tackles Won</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.total_passes || 0}</div>
                    <div class="label">Total Passes</div>
                </div>
            `;
        }
        
        // Update squad list
        const squadList = document.querySelector('.squad-list');
        if (squadList) {
            const players = data.players || [];
            squadList.innerHTML = players.map((player, index) => `
                <div class="player-row" data-role="${player.position || 'Unknown'}">
                    <div class="player-info">
                        <span class="player-number">${index + 1}</span>
                        <div>
                            <div class="player-name">${player.name || 'Unknown Player'}</div>
                            <div class="player-meta">
                                <span class="player-rating">${(player.predicted_rating || 0).toFixed(1)}</span>
                                <span class="player-form">${player.form || 'N/A'}</span>
                                <span class="player-status ${(player.injury_status || '').toLowerCase()}">${player.injury_status || 'Unknown'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="player-stats">
                        <div title="Goals">
                            <i class="fas fa-futbol"></i> ${player.goals || 0}
                        </div>
                        <div title="Assists">
                            <i class="fas fa-hands-helping"></i> ${player.assists || 0}
                        </div>
                        <div title="Pass Accuracy">
                            <i class="fas fa-bullseye"></i> ${(player.pass_accuracy || 0).toFixed(1)}%
                        </div>
                        <div title="Shot Accuracy">
                            <i class="fas fa-crosshairs"></i> ${(player.shot_accuracy || 0).toFixed(1)}%
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // Show modal
        modal.style.display = 'flex';
        
        console.log('Team details modal displayed successfully');
        
    } catch (error) {
        console.error('Error loading team details:', error);
        alert(`Failed to load team details: ${error.message}`);
    }
}

// Top 4 teams
const TOP_TEAMS = [
    'Manchester City', 
    'Arsenal', 
    'Manchester United', 
    'Liverpool'
];

function normalizeTeamName(teamName) {
    const teamMapping = {
        // Top 4 teams variations
        'Man City': 'Manchester City',
        'City': 'Manchester City',
        
        'Man United': 'Manchester United',
        'United': 'Manchester United',
        
        'Liverpool FC': 'Liverpool',
        
        'Arsenal FC': 'Arsenal'
    };
    
    // First try exact match
    if (teamMapping[teamName]) {
        return teamMapping[teamName];
    }
    
    // Try case-insensitive match
    const lowerName = teamName.toLowerCase();
    for (const [key, value] of Object.entries(teamMapping)) {
        if (key.toLowerCase() === lowerName) {
            return value;
        }
    }
    
    // If no match found, return original name
    return teamName;
}

// Modify club filter to only show top 4 teams
function createClubFilter() {
    const filterContainer = document.getElementById('club-filter');
    filterContainer.innerHTML = ''; // Clear existing filters
    
    TOP_TEAMS.forEach(team => {
        const teamLogo = document.createElement('img');
        teamLogo.src = `/static/images/${team.toLowerCase().replace(/\s+/g, '-')}.png`;
        teamLogo.alt = team;
        teamLogo.classList.add('club-logo');
        teamLogo.addEventListener('click', () => showTeamDetails(team));
        filterContainer.appendChild(teamLogo);
    });
}

// Modify team details to validate against top teams
async function showTeamDetails(teamName) {
    // Validate team is in top 4
    const normalizedTeamName = normalizeTeamName(teamName);
    if (!TOP_TEAMS.includes(normalizedTeamName)) {
        console.error('Team not in top 4:', teamName);
        alert('This team is not available in the current system.');
        return;
    }

    // Rest of the existing showTeamDetails function remains the same
    console.log(`Attempting to show details for team: ${normalizedTeamName}`);
    
    const modal = document.getElementById('teamModal');
    const teamLogo = document.getElementById('teamLogo');
    const teamNameEl = document.getElementById('teamName');
    
    // Validate modal elements exist
    if (!modal || !teamLogo || !teamNameEl) {
        console.error('Modal elements not found. Check your HTML structure.');
        alert('Modal setup error. Please check console.');
        return;
    }

    try {
        // Fetch team details with error handling
        const response = await fetch(`/get_team_details/${encodeURIComponent(normalizedTeamName)}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        // Check response status
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        
        // Parse JSON safely
        const data = await response.json();
        
        // Validate received data
        if (!data || !data.team_name) {
            throw new Error('Received invalid team data');
        }
        
        console.log('Team details received:', data);
        
        // Update team header
        try {
            teamLogo.src = `/static/images/${data.team_name.toLowerCase().replace(/\s+/g, '-')}.png`;
            teamNameEl.textContent = data.team_name;
        } catch (logoError) {
            console.warn('Error setting team logo:', logoError);
            teamLogo.src = '/static/images/premier-league.png'; // Fallback logo
        }
        
        // Update team metadata with fallback values
        document.getElementById('teamRating').textContent = 
            (data.team_rating || 'N/A').toFixed(1);
        document.getElementById('teamForm').textContent = 
            data.team_form || 'N/A';
        document.getElementById('formation').textContent = 
            data.formation || 'N/A';
        
        // Update team stats
        const statsGrid = document.querySelector('.team-stats-grid');
        if (statsGrid) {
            const stats = data.team_stats || {};
            statsGrid.innerHTML = `
                <div class="stat-box">
                    <div class="value">${stats.total_goals || 0}</div>
                    <div class="label">Goals</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.total_assists || 0}</div>
                    <div class="label">Assists</div>
                </div>
                <div class="stat-box">
                    <div class="value">${(stats.avg_pass_accuracy || 0).toFixed(1)}%</div>
                    <div class="label">Pass Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="value">${(stats.avg_shot_accuracy || 0).toFixed(1)}%</div>
                    <div class="label">Shot Accuracy</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.total_tackles || 0}</div>
                    <div class="label">Tackles Won</div>
                </div>
                <div class="stat-box">
                    <div class="value">${stats.total_passes || 0}</div>
                    <div class="label">Total Passes</div>
                </div>
            `;
        }
        
        // Update squad list
        const squadList = document.querySelector('.squad-list');
        if (squadList) {
            const players = data.players || [];
            squadList.innerHTML = players.map((player, index) => `
                <div class="player-row" data-role="${player.position || 'Unknown'}">
                    <div class="player-info">
                        <span class="player-number">${index + 1}</span>
                        <div>
                            <div class="player-name">${player.name || 'Unknown Player'}</div>
                            <div class="player-meta">
                                <span class="player-rating">${(player.predicted_rating || 0).toFixed(1)}</span>
                                <span class="player-form">${player.form || 'N/A'}</span>
                                <span class="player-status ${(player.injury_status || '').toLowerCase()}">${player.injury_status || 'Unknown'}</span>
                            </div>
                        </div>
                    </div>
                    <div class="player-stats">
                        <div title="Goals">
                            <i class="fas fa-futbol"></i> ${player.goals || 0}
                        </div>
                        <div title="Assists">
                            <i class="fas fa-hands-helping"></i> ${player.assists || 0}
                        </div>
                        <div title="Pass Accuracy">
                            <i class="fas fa-bullseye"></i> ${(player.pass_accuracy || 0).toFixed(1)}%
                        </div>
                        <div title="Shot Accuracy">
                            <i class="fas fa-crosshairs"></i> ${(player.shot_accuracy || 0).toFixed(1)}%
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // Show modal
        modal.style.display = 'flex';
        
        console.log('Team details modal displayed successfully');
        
    } catch (error) {
        console.error('Error loading team details:', error);
        alert(`Failed to load team details: ${error.message}`);
    }
}

// Call createClubFilter when the page loads
document.addEventListener('DOMContentLoaded', createClubFilter);

// Close modal when clicking the close button
document.querySelector('.close-modal').addEventListener('click', () => {
    const modal = document.getElementById('teamModal');
    gsap.to('.team-modal', {
        y: -50,
        opacity: 0,
        duration: 0.3,
        ease: 'power2.in',
        onComplete: () => {
            modal.style.display = 'none';
        }
    });
});

// Close modal when clicking outside
document.getElementById('teamModal').addEventListener('click', (e) => {
    if (e.target.id === 'teamModal') {
        document.querySelector('.close-modal').click();
    }
});

// Load and display team statistics
async function loadTeamStats(team) {
    if (team === 'all') {
        hideTeamStats();
        return;
    }

    try {
        const response = await fetch(`/api/team-stats/${encodeURIComponent(team)}`);
        const stats = await response.json();
        displayTeamStats(stats);
    } catch (error) {
        console.error('Error loading team stats:', error);
    }
}

// Display team statistics
function displayTeamStats(stats) {
    const statsContainer = document.getElementById('team-stats');
    statsContainer.innerHTML = `
        <div class="team-stats-container">
            <h2>${currentTeam.replace('-', ' ').toUpperCase()} Team Analysis</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Team Ratings</h3>
                    <p>Average Rating: ${stats.average_rating}</p>
                    <p>Predicted Rating: ${stats.predicted_team_rating}</p>
                    <p>Players: ${stats.player_count}</p>
                </div>
                
                <div class="stat-card">
                    <h3>Performance Stats</h3>
                    <p>Total Goals: ${stats.total_goals}</p>
                    <p>Total Assists: ${stats.total_assists}</p>
                    <p>Avg Pass Accuracy: ${stats.avg_pass_accuracy}%</p>
                    <p>Avg Shot Accuracy: ${stats.avg_shot_accuracy}%</p>
                </div>
                
                <div class="stat-card">
                    <h3>Top Performers</h3>
                    <p>Top Scorer: ${stats.top_scorer.name} (${stats.top_scorer.goals} goals)</p>
                    <p>Top Assister: ${stats.top_assister.name} (${stats.top_assister.assists} assists)</p>
                    <p>Highest Rated: ${stats.highest_rated.name} (${stats.highest_rated.rating})</p>
                </div>
            </div>
            
            <div class="analysis-section">
                <div class="strengths">
                    <h3>Team Strengths</h3>
                    <ul>
                        ${stats.strengths.map(s => `
                            <li>${s.feature}: ${s.value} (+${s.diff}% above average)</li>
                        `).join('')}
                    </ul>
                </div>
                
                <div class="weaknesses">
                    <h3>Areas for Improvement</h3>
                    <ul>
                        ${stats.weaknesses.map(w => `
                            <li>${w.feature}: ${w.value} (${w.diff}% below average)</li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="feature-importance">
                <h3>Key Performance Indicators</h3>
                <div class="feature-bars">
                    ${Object.entries(stats.feature_importance)
                        .sort(([,a], [,b]) => b - a)
                        .map(([feature, importance]) => `
                            <div class="feature-bar">
                                <span class="feature-name">${feature.replace('_', ' ')}</span>
                                <div class="bar" style="width: ${importance * 100}%"></div>
                                <span class="importance-value">${(importance * 100).toFixed(1)}%</span>
                            </div>
                        `).join('')}
                </div>
            </div>
        </div>
    `;
    statsContainer.style.display = 'block';
}

// Hide team statistics
function hideTeamStats() {
    const statsContainer = document.getElementById('team-stats');
    statsContainer.style.display = 'none';
}

// Update players table
function updatePlayersTable(players) {
    const tableBody = document.querySelector('#players-table tbody');
    tableBody.innerHTML = players.map(player => `
        <tr>
            <td>${player.Player_Name}</td>
            <td>${player.Club}</td>
            <td>${player.Position}</td>
            <td>${player.Rating.toFixed(1)}</td>
            <td>${player.Goals}</td>
            <td>${player.Assists}</td>
            <td>${player.Pass_Accuracy}%</td>
            <td>${player.Shot_Accuracy}%</td>
            <td>${player.Tackles_Won}</td>
        </tr>
    `).join('');
}

// Modal close handlers
document.querySelector('.close-button').addEventListener('click', () => {
    const modal = document.getElementById('playerModal');
    modal.style.opacity = '0';
    setTimeout(() => {
        modal.style.display = 'none';
        modal.style.opacity = '1';
    }, 300);
});

window.addEventListener('click', (event) => {
    const modal = document.getElementById('playerModal');
    if (event.target === modal) {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.display = 'none';
            modal.style.opacity = '1';
        }, 300);
    }
});

// Function to animate numbers
function animateValue(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const value = Math.floor(start + (range * progress));
        element.textContent = value;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Function to create a glowing effect
function addGlowEffect(element) {
    gsap.to(element, {
        boxShadow: '0 0 20px rgba(1, 180, 228, 0.5)',
        duration: 1,
        yoyo: true,
        repeat: -1
    });
}

// Function to load and display teams and players with animations
async function loadTeamsAndPlayers() {
    try {
        const response = await fetch('/get_teams_and_players');
        const teamsData = await response.json();
        
        const teamsContainer = document.getElementById('teams-container');
        teamsContainer.innerHTML = ''; // Clear existing content
        
        Object.entries(teamsData).forEach(([teamName, players], teamIndex) => {
            const teamSection = document.createElement('div');
            teamSection.className = `team-section ${teamName.replace(/\s+/g, '-')}`;
            teamSection.style.opacity = '0';
            teamSection.style.transform = 'translateY(50px)';
            
            const teamHeader = document.createElement('div');
            teamHeader.className = 'team-header';
            teamHeader.innerHTML = `
                <h2 class="team-name">
                    <i class="fas fa-shield-alt"></i> ${teamName}
                </h2>
            `;
            
            const playersGrid = document.createElement('div');
            playersGrid.className = 'team-players';
            
            players.forEach((player, playerIndex) => {
                const playerCard = document.createElement('div');
                playerCard.className = 'player-card';
                playerCard.style.opacity = '0';
                playerCard.style.transform = 'scale(0.9)';
                
                const ratingClass = player.rating >= 85 ? 'elite' : 
                                  player.rating >= 80 ? 'gold' : 
                                  player.rating >= 75 ? 'silver' : 'bronze';
                
                playerCard.innerHTML = `
                    <div class="player-name">
                        <i class="fas fa-user-alt"></i> ${player.name}
                    </div>
                    <div class="player-stats">
                        <div class="stat-item">
                            <span><i class="fas fa-futbol"></i> Goals</span>
                            <span class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span><i class="fas fa-hands-helping"></i> Assists</span>
                            <span class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span><i class="fas fa-bullseye"></i> Pass Acc</span>
                            <span class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span><i class="fas fa-crosshairs"></i> Shot Acc</span>
                            <span class="stat-value">0</span>
                        </div>
                    </div>
                `;
                
                playersGrid.appendChild(playerCard);
                
                // Animate player card appearance
                setTimeout(() => {
                    gsap.to(playerCard, {
                        opacity: 1,
                        scale: 1,
                        duration: 0.5,
                        ease: 'back.out(1.7)',
                        onComplete: () => {
                            // Animate statistics
                            const statValues = playerCard.querySelectorAll('.stat-value');
                            statValues[0].textContent = player.goals;
                            statValues[1].textContent = player.assists;
                            statValues[2].textContent = player.pass_accuracy;
                            statValues[3].textContent = player.shot_accuracy;
                            
                            statValues.forEach((stat, index) => {
                                const value = parseFloat(stat.textContent);
                                animateValue(stat, 0, value, 1000);
                            });
                        }
                    });
                }, playerIndex * 100);
                
                // Add hover effect
                playerCard.addEventListener('mouseenter', () => {
                    addGlowEffect(playerCard);
                });
                
                playerCard.addEventListener('mouseleave', () => {
                    gsap.to(playerCard, {
                        boxShadow: '0 8px 20px rgba(0, 0, 0, 0.2)',
                        duration: 0.3
                    });
                });
            });
            
            teamSection.appendChild(teamHeader);
            teamSection.appendChild(playersGrid);
            teamsContainer.appendChild(teamSection);
            
            // Animate team section appearance
            setTimeout(() => {
                gsap.to(teamSection, {
                    opacity: 1,
                    y: 0,
                    duration: 0.8,
                    ease: 'power2.out'
                });
            }, teamIndex * 200);
        });
    } catch (error) {
        console.error('Error loading teams and players:', error);
    }
}

// Function to create player performance chart
function createPlayerPerformanceChart(players) {
    const ctx = document.getElementById('playerPerformance').getContext('2d');
    
    if (window.playerChart) {
        window.playerChart.destroy();
    }
    
    const labels = players.map(p => p.name);
    const ratings = players.map(p => p.predicted_rating);
    
    window.playerChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Player Ratings',
                data: ratings,
                backgroundColor: 'rgba(1, 180, 228, 0.8)',
                borderColor: 'rgba(1, 180, 228, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Function to determine player role based on stats
function getPlayerRole(player) {
    if (player.goals > player.assists && player.goals > player.tackles) {
        return 'attackers';
    } else if (player.assists > player.tackles) {
        return 'midfielders';
    } else {
        return 'defenders';
    }
}

// Function to initialize squad filters
function initSquadFilters() {
    const filters = document.querySelectorAll('.squad-filters button');
    const players = document.querySelectorAll('.player-row');
    
    filters.forEach(filter => {
        filter.addEventListener('click', () => {
            // Update active filter
            filters.forEach(f => f.classList.remove('active'));
            filter.classList.add('active');
            
            const role = filter.dataset.filter;
            
            // Filter players
            players.forEach(player => {
                if (role === 'all' || player.dataset.role === role) {
                    gsap.to(player, {
                        opacity: 1,
                        x: 0,
                        duration: 0.3,
                        display: 'flex'
                    });
                } else {
                    gsap.to(player, {
                        opacity: 0,
                        x: -20,
                        duration: 0.3,
                        display: 'none'
                    });
                }
            });
        });
    });
}

// Add click event listeners to team logos
document.querySelectorAll('.club-filter').forEach(button => {
    button.addEventListener('click', () => {
        const teamName = button.querySelector('span').textContent.trim();
        if (teamName !== 'All Teams') {
            showTeamDetails(teamName);
        }
    });
});

// Add close button handler for modal
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('teamModal').style.display = 'none';
});

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('teamModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Add squad filter functionality
function initSquadFilters() {
    document.querySelectorAll('.squad-filter').forEach(filter => {
        filter.addEventListener('click', () => {
            // Remove active class from all filters
            document.querySelectorAll('.squad-filter').forEach(f => f.classList.remove('active'));
            // Add active class to clicked filter
            filter.classList.add('active');
            
            const role = filter.dataset.role;
            // Show/hide players based on role
            document.querySelectorAll('.player-row').forEach(player => {
                if (role === 'all' || player.dataset.role === role) {
                    player.style.display = 'flex';
                } else {
                    player.style.display = 'none';
                }
            });
        });
    });
}

// Function to create radar chart for team stats
function createTeamStatsRadar(stats) {
    const ctx = document.getElementById('teamStatsRadar').getContext('2d');
    
    if (window.teamRadarChart) {
        window.teamRadarChart.destroy();
    }
    
    window.teamRadarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Goals', 'Assists', 'Pass Accuracy', 'Shot Accuracy', 'Tackles', 'Passes'],
            datasets: [{
                label: 'Team Stats',
                data: [
                    stats.total_goals,
                    stats.total_assists,
                    stats.avg_pass_accuracy,
                    stats.avg_shot_accuracy,
                    stats.total_tackles,
                    stats.total_passes / 100 // Scale down passes for better visualization
                ],
                backgroundColor: 'rgba(1, 180, 228, 0.2)',
                borderColor: 'rgba(1, 180, 228, 1)',
                pointBackgroundColor: 'rgba(255, 215, 0, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(1, 180, 228, 1)'
            }]
        },
        options: {
            scales: {
                r: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        backdropColor: 'transparent'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Function to create performance chart for top players
function createPlayerPerformanceChart(players) {
    const ctx = document.getElementById('playerPerformanceChart').getContext('2d');
    
    if (window.playerPerformanceChart) {
        window.playerPerformanceChart.destroy();
    }
    
    window.playerPerformanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: players.map(p => p.name),
            datasets: [{
                label: 'Rating',
                data: players.map(p => p.predicted_rating),
                backgroundColor: 'rgba(255, 215, 0, 0.5)',
                borderColor: 'rgba(255, 215, 0, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Fallback error handling
window.addEventListener('error', function(event) {
    console.error('Unhandled error:', event.error);
    alert('An unexpected error occurred. Please check the console.');
});
