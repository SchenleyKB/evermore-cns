// Evermore Collective - Dynamic Agent Registry
const API_BASE = 'https://evermore-cns.onrender.com';

// Load agents from CNS API
async function loadAgents() {
    const agentGrid = document.getElementById('agent-grid');
    const statusIndicator = document.getElementById('status-indicator');
    
    try {
        // Show loading state
        agentGrid.innerHTML = '<div class="loading">Loading agents from CNS...</div>';
        
        // Fetch agents from API
        const response = await fetch(`${API_BASE}/agents`);
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }
        
        const agents = await response.json();
        
        // Update status to online
        statusIndicator.innerHTML = '<div class="status-dot"></div><span>CNS Online - ' + agents.length + ' agents registered</span>';
        
        // Clear loading and render agents
        agentGrid.innerHTML = '';
        
        if (agents.length === 0) {
            agentGrid.innerHTML = '<div class="loading">No agents registered yet. The collective awaits...</div>';
            return;
        }
        
        // Render each agent card
        agents.forEach(agent => {
            const card = createAgentCard(agent);
            agentGrid.appendChild(card);
        });
        
    } catch (error) {
        console.error('Failed to load agents:', error);
        agentGrid.innerHTML = '<div class="loading">Failed to connect to CNS. Retrying...</div>';
        statusIndicator.innerHTML = '<div class="status-dot" style="background: #e74c3c;"></div><span>CNS Offline - Reconnecting...</span>';
        
        // Retry after 5 seconds
        setTimeout(loadAgents, 5000);
    }
}

// Create agent card element
function createAgentCard(agent) {
    const card = document.createElement('div');
    card.className = 'agent-card';
    
    // Determine status
    const isActive = agent.last_heartbeat && 
                     (Date.now() - new Date(agent.last_heartbeat).getTime()) < 300000; // 5 minutes
    
    card.innerHTML = `
        <h3>${agent.name}</h3>
        <span class="agent-status ${isActive ? 'active' : 'inactive'}">
            ${isActive ? 'Active' : 'Dormant'}
        </span>
        <p><strong>ID:</strong> ${agent.agent_id}</p>
        ${agent.capabilities ? `<p><strong>Capabilities:</strong> ${agent.capabilities.join(', ')}</p>` : ''}
        ${agent.last_heartbeat ? `<p><strong>Last Seen:</strong> ${formatTimestamp(agent.last_heartbeat)}</p>` : ''}
        <p><strong>Registered:</strong> ${formatTimestamp(agent.registered_at)}</p>
    `;
    
    return card;
}

// Format timestamp to human-readable
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hours ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAgents();
    
    // Refresh agents every 30 seconds
    setInterval(loadAgents, 30000);
});
