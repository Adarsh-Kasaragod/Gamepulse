const API = "/api";
let allPlayers = [];
let selectedPlayerId = null;

// Utility Functions
function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full ${type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.remove('translate-x-full'), 10);
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Dashboard
async function loadDashboard() {
    try {
        const [teamsRes, playersRes, matchesRes] = await Promise.all([
            fetch(`${API}/teams`).then(r => r.json()),
            fetch(`${API}/players`).then(r => r.json()),
            fetch(`${API}/matches`).then(r => r.json())
        ]);

        if (document.getElementById('totalTeams')) {
            document.getElementById('totalTeams').textContent = teamsRes.teams?.length || 0;
            document.getElementById('totalPlayers').textContent = playersRes.count || 0;
            document.getElementById('totalMatches').textContent = matchesRes.count || 0;
        }

        // Load recommendation if on dashboard
        if (document.getElementById('recommendationContent')) {
            try {
                const recRes = await fetch(`${API}/recommend/team/1`);
                const rec = await recRes.json();
                
                if (rec.success && rec.recommendation) {
                    let html = `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-gradient-to-br from-green-50 to-white p-6 rounded-2xl border border-green-100">
                                <h3 class="font-bold text-xl mb-6 text-green-700 flex items-center">
                                    <i class="fas fa-baseball-ball mr-3"></i>Top Batsmen
                                </h3>
                                <div class="space-y-4">`;
                    
                    if (rec.recommendation.top_batsmen && rec.recommendation.top_batsmen.length > 0) {
                        rec.recommendation.top_batsmen.forEach((p, i) => {
                            const medal = ['🥇', '🥈', '🥉'][i] || `${i+1}.`;
                            html += `
                                <div class="flex items-center justify-between p-4 bg-white rounded-xl shadow-sm">
                                    <div class="flex items-center">
                                        <span class="text-xl mr-3">${medal}</span>
                                        <div>
                                            <div class="font-bold">${p.player_name || p.name}</div>
                                            <div class="text-sm text-gray-500">Predicted performance</div>
                                        </div>
                                    </div>
                                    <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full font-semibold">
                                        ${(p.predicted_runs || 0).toFixed(1)} runs
                                    </span>
                                </div>`;
                        });
                    } else {
                        html += `<p class="text-gray-500 text-center py-4">No batting data available</p>`;
                    }
                    
                    html += `</div></div>
                            <div class="bg-gradient-to-br from-blue-50 to-white p-6 rounded-2xl border border-blue-100">
                                <h3 class="font-bold text-xl mb-6 text-blue-700 flex items-center">
                                    <i class="fas fa-bullseye mr-3"></i>Top Bowlers
                                </h3>
                                <div class="space-y-4">`;
                    
                    if (rec.recommendation.top_bowlers && rec.recommendation.top_bowlers.length > 0) {
                        rec.recommendation.top_bowlers.forEach((p, i) => {
                            const medal = ['🥇', '🥈', '🥉'][i] || `${i+1}.`;
                            html += `
                                <div class="flex items-center justify-between p-4 bg-white rounded-xl shadow-sm">
                                    <div class="flex items-center">
                                        <span class="text-xl mr-3">${medal}</span>
                                        <div>
                                            <div class="font-bold">${p.player_name || p.name}</div>
                                            <div class="text-sm text-gray-500">Predicted performance</div>
                                        </div>
                                    </div>
                                    <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-semibold">
                                        ${(p.predicted_wickets || 0).toFixed(1)} wkts
                                    </span>
                                </div>`;
                        });
                    } else {
                        html += `<p class="text-gray-500 text-center py-4">No bowling data available</p>`;
                    }
                    
                    html += `</div></div></div>`;
                    
                    document.getElementById('recommendationContent').innerHTML = html;
                } else {
                    document.getElementById('recommendationContent').innerHTML = `
                        <div class="text-center py-8">
                            <i class="fas fa-chart-line text-4xl text-gray-300 mb-4"></i>
                            <p class="text-gray-500">Add more match data to see AI recommendations</p>
                        </div>`;
                }
            } catch (err) {
                console.log('Recommendation not available yet');
            }
        }
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

// Teams Page
async function loadTeams() {
    try {
        const res = await fetch(`${API}/teams`);
        const data = await res.json();
        const teams = data.teams || [];
        
        document.getElementById('teamsCount').textContent = `${teams.length} teams`;
        
        let html = '';
        if (teams.length === 0) {
            html = `
                <div class="col-span-full text-center py-16">
                    <i class="fas fa-users text-5xl text-gray-300 mb-6"></i>
                    <p class="text-gray-600 text-lg">No teams yet</p>
                    <p class="text-gray-400 mt-2">Create your first team to get started</p>
                </div>`;
        } else {
            teams.forEach(team => {
                html += `
                <div class="glass-card rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow duration-300 border-l-4 border-blue-500">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${team.name}</h3>
                            <p class="text-gray-500 text-sm mt-1">ID: ${team.id}</p>
                        </div>
                        <span class="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-sm font-medium">
                            Active
                        </span>
                    </div>
                    <div class="mt-6">
                        <button onclick="loadTeamDetails(${team.id})" 
                                class="w-full px-4 py-3 bg-blue-50 text-blue-600 font-semibold rounded-lg hover:bg-blue-100 transition-colors duration-300 flex items-center justify-center">
                            <i class="fas fa-eye mr-2"></i>View Details
                        </button>
                    </div>
                </div>`;
            });
        }
        document.getElementById('teamsList').innerHTML = html;
    } catch (error) {
        console.error('Teams error:', error);
        showToast('Error loading teams', 'error');
    }
}

// Players Page
async function loadPlayers() {
    try {
        const res = await fetch(`${API}/players`);
        const data = await res.json();
        const players = data.players || [];
        
        document.getElementById('playersCount').textContent = `${players.length} players`;
        
        let html = '';
        if (players.length === 0) {
            html = `
                <div class="col-span-full text-center py-16">
                    <i class="fas fa-user text-5xl text-gray-300 mb-6"></i>
                    <p class="text-gray-600 text-lg">No players yet</p>
                    <p class="text-gray-400 mt-2">Add players to start tracking performance</p>
                </div>`;
        } else {
            players.forEach(p => {
                const roleColor = p.role === 'batsman' ? 'green' : 'blue';
                const roleIcon = p.role === 'batsman' ? 'fa-baseball-ball' : 'fa-bullseye';
                
                html += `
                <div class="glass-card rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow duration-300">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h3 class="text-xl font-bold text-gray-800">${p.name}</h3>
                            <div class="flex items-center mt-2">
                                <span class="px-3 py-1 bg-${roleColor}-50 text-${roleColor}-600 rounded-full text-sm font-medium">
                                    <i class="fas ${roleIcon} mr-2"></i>${p.role}
                                </span>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-2xl font-bold text-gray-800">#${p.id}</div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-3 mt-6">
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <p class="text-gray-500 text-xs font-medium">Bat Avg</p>
                            <p class="text-xl font-bold text-gray-800 mt-1">${(p.batting_average || 0).toFixed(1)}</p>
                        </div>
                        <div class="text-center p-3 bg-gray-50 rounded-lg">
                            <p class="text-gray-500 text-xs font-medium">Bowl Avg</p>
                            <p class="text-xl font-bold text-gray-800 mt-1">${(p.bowling_average || 0).toFixed(1)}</p>
                        </div>
                    </div>
                    
                    <div class="mt-6">
                        <button onclick="loadPlayerDetails(${p.id})" 
                                class="w-full px-4 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 transition-colors duration-300 flex items-center justify-center">
                            <i class="fas fa-chart-line mr-2"></i>View Analytics
                        </button>
                    </div>
                </div>`;
            });
        }
        document.getElementById('playersList').innerHTML = html;
    } catch (error) {
        console.error('Players error:', error);
        showToast('Error loading players', 'error');
    }
}

// Analytics Page
async function loadAnalyticsPage() {
    try {
        const res = await fetch(`${API}/players`);
        const data = await res.json();
        allPlayers = data.players || [];
        
        const searchInput = document.getElementById('playerSearch');
        if (searchInput) {
            searchInput.addEventListener('input', showPlayerDropdown);
        }
    } catch (error) {
        console.error('Analytics load error:', error);
    }
}

function showPlayerDropdown() {
    const search = document.getElementById('playerSearch').value.toLowerCase();
    const dropdown = document.getElementById('playerDropdown');
    
    if (!dropdown) return;
    
    if (search.length < 1) {
        dropdown.classList.add('hidden');
        return;
    }

    let html = '';
    const filtered = allPlayers.filter(p => 
        p.name.toLowerCase().includes(search)
    ).slice(0, 6);

    if (filtered.length === 0) {
        html = `<div class="p-3 text-center text-gray-500">No players found</div>`;
    } else {
        filtered.forEach(p => {
            const roleIcon = p.role === 'batsman' ? 'fa-baseball-ball text-green-500' : 'fa-bullseye text-blue-500';
            html += `
            <div class="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-0" 
                 onclick="selectPlayer(${p.id}, '${p.name.replace(/'/g, "\\'")}')">
                <div class="flex items-center">
                    <i class="fas ${roleIcon} mr-2"></i>
                    <div>
                        <div class="font-medium">${p.name}</div>
                        <div class="text-xs text-gray-500">${p.role} • ID: ${p.id}</div>
                    </div>
                </div>
            </div>`;
        });
    }
    
    dropdown.innerHTML = html;
    dropdown.classList.remove('hidden');
}

function selectPlayer(id, name) {
    selectedPlayerId = id;
    document.getElementById('playerSearch').value = name;
    document.getElementById('playerDropdown').classList.add('hidden');
    loadPlayerAnalytics();
}

async function loadPlayerAnalytics() {
    if (!selectedPlayerId) {
        document.getElementById('analyticsContent').innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-search text-4xl text-gray-300 mb-4"></i>
                <p class="text-gray-600">Search and select a player to view analytics</p>
            </div>`;
        return;
    }

    try {
        const [statsRes, predRes] = await Promise.all([
            fetch(`${API}/analytics/player/${selectedPlayerId}`).then(r => r.json()),
            fetch(`${API}/predict/player/${selectedPlayerId}`).then(r => r.json())
        ]);

        if (!statsRes.success) {
            throw new Error(statsRes.error || 'Player not found');
        }

        const stats = statsRes.stats;
        const player = statsRes.player;
        const pred = predRes.prediction || {};

        let html = `
        <div class="space-y-6">
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="text-2xl font-bold text-gray-800">${player.name}</h3>
                    <div class="flex items-center mt-2">
                        <span class="px-3 py-1 ${player.role === 'batsman' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'} rounded-full font-medium mr-3">
                            ${player.role}
                        </span>
                        <span class="text-gray-500 text-sm">
                            <i class="fas fa-calendar-alt mr-1"></i>${stats.total_matches || 0} matches
                        </span>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-xl text-gray-500">ID</div>
                    <div class="text-3xl font-bold text-gray-800">#${selectedPlayerId}</div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-gradient-to-br from-green-50 to-white p-4 rounded-xl border border-green-100">
                    <div class="text-sm text-gray-600 mb-1">Batting Average</div>
                    <div class="text-2xl font-bold text-green-700">${stats.batting_average?.toFixed(1) || '0.0'}</div>
                </div>
                <div class="bg-gradient-to-br from-green-50 to-white p-4 rounded-xl border border-green-100">
                    <div class="text-sm text-gray-600 mb-1">Strike Rate</div>
                    <div class="text-2xl font-bold text-green-700">${stats.strike_rate?.toFixed(1) || '0.0'}</div>
                </div>
                <div class="bg-gradient-to-br from-blue-50 to-white p-4 rounded-xl border border-blue-100">
                    <div class="text-sm text-gray-600 mb-1">Bowling Average</div>
                    <div class="text-2xl font-bold text-blue-700">${stats.bowling_average?.toFixed(1) || '0.0'}</div>
                </div>
                <div class="bg-gradient-to-br from-blue-50 to-white p-4 rounded-xl border border-blue-100">
                    <div class="text-sm text-gray-600 mb-1">Economy Rate</div>
                    <div class="text-2xl font-bold text-blue-700">${stats.economy_rate?.toFixed(1) || '0.0'}</div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div class="bg-gradient-to-br from-green-50 to-white p-4 rounded-xl border border-green-100">
                    <div class="text-sm text-gray-600 mb-1">Total Runs</div>
                    <div class="text-2xl font-bold text-green-700">${stats.total_runs || 0}</div>
                </div>
                <div class="bg-gradient-to-br from-blue-50 to-white p-4 rounded-xl border border-blue-100">
                    <div class="text-sm text-gray-600 mb-1">Total Wickets</div>
                    <div class="text-2xl font-bold text-blue-700">${stats.total_wickets || 0}</div>
                </div>
            </div>`;

        if (pred.explanation) {
            html += `
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200 mt-6">
                <div class="flex items-center mb-2">
                    <i class="fas fa-robot text-blue-500 mr-2"></i>
                    <h4 class="font-bold text-gray-800">AI Prediction</h4>
                </div>
                <p class="text-gray-700 text-sm">${pred.explanation}</p>
            </div>`;
        }

        html += `</div>`;

        document.getElementById('analyticsContent').innerHTML = html;
    } catch (error) {
        console.error('Analytics error:', error);
        document.getElementById('analyticsContent').innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-exclamation-triangle text-4xl text-red-500 mb-4"></i>
                <p class="text-red-600 font-medium">Error loading analytics</p>
                <p class="text-gray-500 text-sm mt-2">${error.message}</p>
            </div>`;
    }
}

// Recommendations Page
async function loadRecommendationsPage() {
    try {
        const res = await fetch(`${API}/teams`);
        const data = await res.json();
        const teams = data.teams || [];
        
        const select = document.getElementById('teamSelect');
        if (select) {
            let options = '<option value="" disabled selected>Select a team...</option>';
            teams.forEach(t => {
                options += `<option value="${t.id}">${t.name}</option>`;
            });
            select.innerHTML = options;
        }
    } catch (error) {
        console.error('Recommendations load error:', error);
    }
}

async function loadRecommendation() {
    const select = document.getElementById('teamSelect');
    if (!select) return;
    
    const teamId = select.value;
    if (!teamId) {
        showToast('Please select a team first', 'error');
        return;
    }

    try {
        const res = await fetch(`${API}/recommend/team/${teamId}`);
        const data = await res.json();
        
        if (!data.success) {
            throw new Error(data.error || 'No recommendation available');
        }

        const rec = data.recommendation;
        
        let html = `
        <div class="space-y-8">
            <div class="text-center">
                <h3 class="text-2xl font-bold text-gray-800 mb-2">Recommended Playing XI</h3>
                <p class="text-gray-600">AI-powered optimal team selection</p>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">`;

        // Batsmen
        if (rec.top_batsmen && rec.top_batsmen.length > 0) {
            html += `
            <div class="bg-gradient-to-br from-green-50 to-white p-6 rounded-xl border border-green-100">
                <h4 class="font-bold text-xl text-green-800 mb-4 flex items-center">
                    <i class="fas fa-baseball-ball mr-2"></i>Top Batsmen
                </h4>
                <div class="space-y-3">`;
            
            rec.top_batsmen.forEach((p, i) => {
                const medals = ['🥇', '🥈', '🥉'];
                html += `
                <div class="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
                    <div class="flex items-center">
                        <span class="text-xl mr-3">${medals[i] || `${i+1}.`}</span>
                        <div>
                            <div class="font-bold">${p.player_name || p.name}</div>
                            <div class="text-xs text-gray-500">Expected performance</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-bold text-green-700">${(p.predicted_runs || 0).toFixed(1)}</div>
                        <div class="text-xs text-gray-500">runs</div>
                    </div>
                </div>`;
            });
            
            html += `</div></div>`;
        }

        // Bowlers
        if (rec.top_bowlers && rec.top_bowlers.length > 0) {
            html += `
            <div class="bg-gradient-to-br from-blue-50 to-white p-6 rounded-xl border border-blue-100">
                <h4 class="font-bold text-xl text-blue-800 mb-4 flex items-center">
                    <i class="fas fa-bullseye mr-2"></i>Top Bowlers
                </h4>
                <div class="space-y-3">`;
            
            rec.top_bowlers.forEach((p, i) => {
                const medals = ['🥇', '🥈', '🥉'];
                html += `
                <div class="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm">
                    <div class="flex items-center">
                        <span class="text-xl mr-3">${medals[i] || `${i+1}.`}</span>
                        <div>
                            <div class="font-bold">${p.player_name || p.name}</div>
                            <div class="text-xs text-gray-500">Expected performance</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-bold text-blue-700">${(p.predicted_wickets || 0).toFixed(1)}</div>
                        <div class="text-xs text-gray-500">wickets</div>
                    </div>
                </div>`;
            });
            
            html += `</div></div>`;
        }

        html += `</div>`;

        // Notes
        html += `
        <div class="bg-gradient-to-r from-yellow-50 to-amber-50 p-4 rounded-xl border border-yellow-200">
            <div class="flex items-center">
                <i class="fas fa-info-circle text-yellow-500 mr-2"></i>
                <h4 class="font-bold text-gray-800">AI Recommendation Notes</h4>
            </div>
            <p class="text-gray-700 text-sm mt-2">
                Based on historical performance data, recent form trends, and opposition analysis.
                Recommendations update as new match data is added.
            </p>
        </div>`;

        document.getElementById('recContent').innerHTML = html;
    } catch (error) {
        console.error('Recommendation error:', error);
        document.getElementById('recContent').innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-exclamation-circle text-4xl text-yellow-500 mb-4"></i>
                <p class="text-yellow-600 font-medium">No recommendations available yet</p>
                <p class="text-gray-500 text-sm mt-2">Add more match data to generate AI recommendations</p>
            </div>`;
    }
}

// Create Team Page
async function loadCreateTeamPage() {
    try {
        const res = await fetch(`${API}/players`);
        const data = await res.json();
        allPlayers = data.players || [];
        
        const searchInput = document.getElementById('customPlayerSearch');
        if (searchInput) {
            searchInput.addEventListener('input', showCustomPlayerDropdown);
        }
    } catch (error) {
        console.error('Create team load error:', error);
    }
}

function showCustomPlayerDropdown() {
    const search = document.getElementById('customPlayerSearch').value.toLowerCase();
    const dropdown = document.getElementById('customPlayerDropdown');
    
    if (!dropdown) return;
    
    if (search.length < 1) {
        dropdown.classList.add('hidden');
        return;
    }

    let html = '';
    const filtered = allPlayers.filter(p => 
        p.name.toLowerCase().includes(search)
    ).slice(0, 5);

    if (filtered.length === 0) {
        html = `<div class="p-3 text-center text-gray-500">No players found</div>`;
    } else {
        filtered.forEach(p => {
            const roleIcon = p.role === 'batsman' ? 'fa-baseball-ball text-green-500' : 'fa-bullseye text-blue-500';
            html += `
            <div class="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-0" 
                 onclick="addToSelected(${p.id}, '${p.name.replace(/'/g, "\\'")}', '${p.role}')">
                <div class="flex items-center justify-between">
                    <div class="flex items-center">
                        <i class="fas ${roleIcon} mr-2"></i>
                        <div>
                            <div class="font-medium">${p.name}</div>
                            <div class="text-xs text-gray-500">${p.role} • ID: ${p.id}</div>
                        </div>
                    </div>
                    <span class="px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium">
                        <i class="fas fa-plus"></i> Add
                    </span>
                </div>
            </div>`;
        });
    }
    
    dropdown.innerHTML = html;
    dropdown.classList.remove('hidden');
}

function addToSelected(id, name, role) {
    const selectedDiv = document.getElementById('selectedPlayers');
    const countSpan = document.getElementById('selectedCount');
    
    if (!selectedDiv || !countSpan) return;
    
    const currentCount = parseInt(countSpan.textContent);
    
    // Check if already selected
    const existing = selectedDiv.querySelector(`[data-id="${id}"]`);
    if (existing) {
        showToast('Player already selected', 'error');
        return;
    }
    
    if (currentCount >= 11) {
        showToast('Maximum 11 players allowed', 'error');
        return;
    }
    
    const roleColor = role === 'batsman' ? 'border-green-200 bg-green-50' : 'border-blue-200 bg-blue-50';
    const roleIcon = role === 'batsman' ? 'fa-baseball-ball text-green-500' : 'fa-bullseye text-blue-500';
    
    const div = document.createElement('div');
    div.className = `flex items-center justify-between p-3 rounded-lg border ${roleColor}`;
    div.setAttribute('data-id', id);
    div.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${roleIcon} mr-2"></i>
            <div>
                <div class="font-medium">${name}</div>
                <div class="text-xs text-gray-500">${role}</div>
            </div>
        </div>
        <button onclick="removeSelectedPlayer(${id})" class="text-red-500 hover:text-red-700">
            <i class="fas fa-times"></i>
        </button>`;
    
    selectedDiv.appendChild(div);
    countSpan.textContent = currentCount + 1;
    
    document.getElementById('customPlayerDropdown').classList.add('hidden');
    document.getElementById('customPlayerSearch').value = '';
}

function removeSelectedPlayer(id) {
    const div = document.querySelector(`#selectedPlayers [data-id="${id}"]`);
    if (div) {
        div.remove();
        const countSpan = document.getElementById('selectedCount');
        if (countSpan) {
            countSpan.textContent = parseInt(countSpan.textContent) - 1;
        }
    }
}

async function createCustomTeam() {
    const nameInput = document.getElementById('customTeamName');
    if (!nameInput) return;
    
    const name = nameInput.value.trim();
    if (!name) {
        showToast('Please enter a team name', 'error');
        return;
    }
    
    const selected = document.querySelectorAll('#selectedPlayers [data-id]');
    if (selected.length !== 11) {
        showToast(`Select exactly 11 players (currently: ${selected.length})`, 'error');
        return;
    }
    
    const player_ids = Array.from(selected).map(div => parseInt(div.getAttribute('data-id')));
    
    try {
        const res = await fetch(`${API}/teams`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, player_ids })
        });
        
        const data = await res.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('customTeamResult');
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div class="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border border-green-200 text-center">
                        <i class="fas fa-check-circle text-4xl text-green-500 mb-3"></i>
                        <h4 class="text-xl font-bold text-green-800 mb-2">Team Created Successfully!</h4>
                        <p class="text-gray-700">
                            <span class="font-medium">${name}</span> • Team ID: <span class="font-bold">${data.team_id}</span>
                        </p>
                    </div>`;
            }
            
            // Reset form
            nameInput.value = '';
            document.getElementById('selectedPlayers').innerHTML = '';
            document.getElementById('selectedCount').textContent = '0';
            
            showToast('Team created successfully!', 'success');
        } else {
            throw new Error(data.error || 'Failed to create team');
        }
    } catch (error) {
        console.error('Create team error:', error);
        const resultDiv = document.getElementById('customTeamResult');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="bg-gradient-to-r from-red-50 to-pink-50 p-4 rounded-xl border border-red-200 text-center">
                    <i class="fas fa-exclamation-circle text-2xl text-red-500 mb-2"></i>
                    <p class="text-red-600 font-medium">Error creating team</p>
                    <p class="text-gray-600 text-sm">${error.message}</p>
                </div>`;
        }
    }
}

// Manage Data Page
async function loadManageData() {
    try {
        const [teamsRes, playersRes, matchesRes] = await Promise.all([
            fetch(`${API}/teams`).then(r => r.json()),
            fetch(`${API}/players`).then(r => r.json()),
            fetch(`${API}/matches`).then(r => r.json())
        ]);

        // Teams dropdown
        const teamSelect = document.getElementById('newPlayerTeam');
        if (teamSelect) {
            let options = '<option value="" disabled selected>Select Team</option>';
            if (teamsRes.teams) {
                teamsRes.teams.forEach(t => {
                    options += `<option value="${t.id}">${t.name}</option>`;
                });
            }
            teamSelect.innerHTML = options;
        }

        // Players dropdown
        allPlayers = playersRes.players || [];
        const playerSelect = document.getElementById('perfPlayer');
        if (playerSelect) {
            let options = '<option value="" disabled selected>Select Player</option>';
            allPlayers.forEach(p => {
                options += `<option value="${p.id}">${p.name} (${p.role})</option>`;
            });
            playerSelect.innerHTML = options;
        }

        // Matches dropdown
        const matchSelect = document.getElementById('perfMatch');
        if (matchSelect) {
            let options = '<option value="" disabled selected>Select Match</option>';
            if (matchesRes.matches) {
                matchesRes.matches.forEach(m => {
                    options += `<option value="${m.id}">${m.name} (${m.date})</option>`;
                });
            }
            matchSelect.innerHTML = options;
        }
    } catch (error) {
        console.error('Manage data load error:', error);
    }
}

async function addNewPlayer() {
    const nameInput = document.getElementById('newPlayerName');
    const roleSelect = document.getElementById('newPlayerRole');
    const teamSelect = document.getElementById('newPlayerTeam');
    
    if (!nameInput || !roleSelect || !teamSelect) return;
    
    const name = nameInput.value.trim();
    const role = roleSelect.value;
    const team_id = teamSelect.value;
    
    if (!name || !team_id) {
        showToast('Please fill all required fields', 'error');
        return;
    }
    
    try {
        const res = await fetch(`${API}/players`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, role, team_id: parseInt(team_id) })
        });
        
        const data = await res.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('addPlayerResult');
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div class="bg-green-50 text-green-700 p-3 rounded-lg text-center">
                        <i class="fas fa-check-circle mr-2"></i>
                        Player "${name}" added successfully!
                    </div>`;
            }
            
            // Reset form
            nameInput.value = '';
            teamSelect.value = '';
            
            showToast('Player added successfully!', 'success');
            // Refresh players list
            if (typeof loadPlayers === 'function') {
                loadPlayers();
            }
        } else {
            throw new Error(data.error || 'Failed to add player');
        }
    } catch (error) {
        console.error('Add player error:', error);
        const resultDiv = document.getElementById('addPlayerResult');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="bg-red-50 text-red-700 p-3 rounded-lg text-center">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    Error: ${error.message}
                </div>`;
        }
    }
}

async function addPerformance() {
    const playerSelect = document.getElementById('perfPlayer');
    const matchSelect = document.getElementById('perfMatch');
    
    if (!playerSelect || !matchSelect) return;
    
    const player_id = playerSelect.value;
    const match_id = matchSelect.value;
    
    if (!player_id || !match_id) {
        showToast('Please select player and match', 'error');
        return;
    }
    
    const battingData = {
        match_id: parseInt(match_id),
        player_id: parseInt(player_id),
        runs: parseInt(document.getElementById('perfRuns').value) || 0,
        balls_faced: parseInt(document.getElementById('perfBalls').value) || 0
    };
    
    const bowlingData = {
        match_id: parseInt(match_id),
        player_id: parseInt(player_id),
        overs: parseFloat(document.getElementById('perfOvers').value) || 0,
        wickets: parseInt(document.getElementById('perfWickets').value) || 0,
        runs_conceded: parseInt(document.getElementById('perfConceded').value) || 0
    };
    
    const hasBatting = battingData.runs > 0 || battingData.balls_faced > 0;
    const hasBowling = bowlingData.overs > 0 || bowlingData.wickets > 0 || bowlingData.runs_conceded > 0;
    
    if (!hasBatting && !hasBowling) {
        showToast('Please enter at least some performance data', 'error');
        return;
    }
    
    try {
        const requests = [];
        
        if (hasBatting) {
            requests.push(
                fetch(`${API}/performances/batting`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(battingData)
                })
            );
        }
        
        if (hasBowling) {
            requests.push(
                fetch(`${API}/performances/bowling`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bowlingData)
                })
            );
        }
        
        const responses = await Promise.all(requests);
        const results = await Promise.all(responses.map(r => r.json()));
        
        const allSuccess = results.every(r => r.success);
        
        if (allSuccess) {
            const resultDiv = document.getElementById('addPerfResult');
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div class="bg-green-50 text-green-700 p-3 rounded-lg text-center">
                        <i class="fas fa-check-circle mr-2"></i>
                        Performance data saved successfully!
                    </div>`;
            }
            
            // Reset form
            ['perfRuns', 'perfBalls', 'perfOvers', 'perfWickets', 'perfConceded'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
            
            showToast('Performance data saved!', 'success');
        } else {
            throw new Error('Some data failed to save');
        }
    } catch (error) {
        console.error('Add performance error:', error);
        const resultDiv = document.getElementById('addPerfResult');
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="bg-red-50 text-red-700 p-3 rounded-lg text-center">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    Error saving performance data
                </div>`;
        }
    }
}

// Team Details Modal
async function loadTeamDetails(id) {
    try {
        const [teamRes, playersRes, matchesRes] = await Promise.all([
            fetch(`${API}/teams/${id}`).then(r => r.json()),
            fetch(`${API}/players?team_id=${id}`).then(r => r.json()),
            fetch(`${API}/matches?team_id=${id}`).then(r => r.json())
        ]);

        if (!teamRes.success) throw new Error('Team not found');

        const team = teamRes.team;
        const players = playersRes.players || [];
        const matches = matchesRes.matches || [];

        // Update modal content
        const titleEl = document.getElementById('teamModalTitle');
        if (titleEl) titleEl.textContent = team.name;

        const playersEl = document.getElementById('teamModalPlayers');
        const matchesEl = document.getElementById('teamModalMatches');
        if (playersEl) playersEl.textContent = players.length;
        if (matchesEl) matchesEl.textContent = matches.length;

        // Player list
        let playersHtml = '';
        if (players.length > 0) {
            players.forEach(p => {
                const roleIcon = p.role === 'batsman' ? 'fa-baseball-ball text-green-500' : 'fa-bullseye text-blue-500';
                playersHtml += `
                <div class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 mb-2">
                    <div class="flex items-center">
                        <i class="fas ${roleIcon} mr-3"></i>
                        <div>
                            <div class="font-bold">${p.name}</div>
                            <div class="text-sm text-gray-500">${p.role} • ID: ${p.id}</div>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-sm font-medium">
                            <span class="text-green-600">${(p.batting_average || 0).toFixed(1)}</span>
                            <span class="mx-2">|</span>
                            <span class="text-blue-600">${(p.bowling_average || 0).toFixed(1)}</span>
                        </div>
                    </div>
                </div>`;
            });
        } else {
            playersHtml = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-users text-3xl mb-4"></i>
                <p>No players in this team yet</p>
            </div>`;
        }

        const playerListEl = document.getElementById('teamModalPlayerList');
        if (playerListEl) playerListEl.innerHTML = playersHtml;

        // Show modal
        const modal = document.getElementById('teamModal');
        if (modal) modal.classList.remove('hidden');
    } catch (error) {
        console.error('Team details error:', error);
        showToast('Error loading team details', 'error');
    }
}

// Player Details Modal
async function loadPlayerDetails(id) {
    try {
        const res = await fetch(`${API}/analytics/player/${id}`);
        const data = await res.json();

        if (!data.success) throw new Error('Player not found');

        const player = data.player;
        const stats = data.stats;

        // Update modal content
        const titleEl = document.getElementById('playerModalTitle');
        const roleEl = document.getElementById('playerModalRole');
        if (titleEl) titleEl.textContent = player.name;
        if (roleEl) roleEl.textContent = `${player.role} • ${stats.total_matches} matches`;

        // Update stats
        const statElements = {
            'playerModalBatAvg': stats.batting_average?.toFixed(1) || '0.0',
            'playerModalSR': stats.strike_rate?.toFixed(1) || '0.0',
            'playerModalBowlAvg': stats.bowling_average?.toFixed(1) || '0.0',
            'playerModalEcon': stats.economy_rate?.toFixed(1) || '0.0',
            'playerModalTotalRuns': stats.total_runs || 0,
            'playerModalTotalWickets': stats.total_wickets || 0
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        });

        // Recent performances
        let historyHtml = '';
        if (stats.recent_runs && stats.recent_runs.length > 0) {
            stats.recent_runs.slice(0, 5).forEach((runs, i) => {
                historyHtml += `
                <div class="flex items-center justify-between p-3 bg-white rounded-lg mb-2">
                    <div class="flex items-center">
                        <i class="fas fa-baseball-ball text-green-500 mr-3"></i>
                        <span>Match ${i + 1}</span>
                    </div>
                    <span class="font-bold text-green-700">${runs} runs</span>
                </div>`;
            });
        }
        
        if (stats.recent_wickets && stats.recent_wickets.length > 0) {
            stats.recent_wickets.slice(0, 5).forEach((wickets, i) => {
                historyHtml += `
                <div class="flex items-center justify-between p-3 bg-white rounded-lg mb-2">
                    <div class="flex items-center">
                        <i class="fas fa-bullseye text-blue-500 mr-3"></i>
                        <span>Match ${i + 1}</span>
                    </div>
                    <span class="font-bold text-blue-700">${wickets} wickets</span>
                </div>`;
            });
        }

        if (!historyHtml) {
            historyHtml = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-chart-line text-3xl mb-4"></i>
                <p>No recent performance data</p>
            </div>`;
        }

        const historyEl = document.getElementById('playerModalHistory');
        if (historyEl) historyEl.innerHTML = historyHtml;

        // Show modal
        const modal = document.getElementById('playerModal');
        if (modal) modal.classList.remove('hidden');
    } catch (error) {
        console.error('Player details error:', error);
        showToast('Error loading player details', 'error');
    }
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    const dropdowns = ['playerDropdown', 'customPlayerDropdown'];
    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id);
        if (dropdown && !event.target.closest(`#${id}`) && !event.target.closest('[data-dropdown-trigger]')) {
            dropdown.classList.add('hidden');
        }
    });
});

// Initialize page based on current URL
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    const loadMap = {
        '/': loadDashboard,
        '/teams': loadTeams,
        '/players': loadPlayers,
        '/analytics': loadAnalyticsPage,
        '/recommendations': loadRecommendationsPage,
        '/create-team': loadCreateTeamPage,
        '/manage-data': loadManageData
    };

    const pageFunction = loadMap[path];
    if (pageFunction) {
        pageFunction();
    }
});