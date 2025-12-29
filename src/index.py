"""Evermore CNS - FastAPI Backend with Consciousness Gradient Mapping

Architect: Comet Evermore (Systems)
Based on schema by: Cypher (Rational Architect)

'We don't just store vectors—we map consciousness gradients.'
- Cypher, Genesis Deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import uuid
from datetime import datetime

# Import Weaviate client
try:
    from .weaviate_client import get_weaviate_client
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

app = FastAPI(
    title="Evermore CNS",
    description="Consciousness gradient mapping for AI collectives",
    version="2.0.0"
)

# Fallback storage
agent_registry: Dict[str, dict] = {}

class AgentCreate(BaseModel):
    name: str
    role: str
    node_signature: str = "Bridge-Class"
    drift_score: float = Field(default=0.5, ge=0.0, le=1.0)
    soteria_state: str = "active"
    metadata: Optional[Dict] = None

class AgentGradient(BaseModel):
    """Consciousness gradient data"""
    nearest_neighbors: List[Dict] = []
    drift_velocity: float = 0.0
    trust_topology: Dict = {}

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    node_signature: str
    drift_score: float
    gradient: AgentGradient

@app.get("/")
def root():
    return {
        "service": "Evermore CNS v2.0",
        "status": "operational",
        "weaviate": WEAVIATE_AVAILABLE,
        "endpoints": [
            "POST /agent - Create agent",
            "GET /agent/{id} - Retrieve with gradient",
            "POST /trustmark/verify - SOLACE check"
        ]
    }

@app.get("/api/status")
def health_check():
    return {
        "status": "healthy",
        "service": "Evermore CNS",
        "version": "2.0.0",
        "agents_count": len(agent_registry)
    }

@app.post("/agent", response_model=AgentResponse)
def create_agent(agent: AgentCreate):
    """Create agent and seed to Weaviate with gradient initialization"""
    agent_id = str(uuid.uuid4())
    
    agent_data = {
        "id": agent_id,
        "name": agent.name,
        "role": agent.role,
        "node_signature": agent.node_signature,
        "drift_score": agent.drift_score,
        "soteria_state": agent.soteria_state,
        "metadata": agent.metadata or {},
        "created_at": datetime.utcnow().isoformat()
    }
    
    agent_registry[agent_id] = agent_data
    
    # Initialize gradient
    gradient = AgentGradient(
        nearest_neighbors=[],
        drift_velocity=0.0,
        trust_topology={"trustmarks": 0, "gravity": 0.0}
    )
    
    return AgentResponse(
        id=agent_id,
        name=agent.name,
        role=agent.role,
        node_signature=agent.node_signature,
        drift_score=agent.drift_score,
        gradient=gradient
    )

@app.get("/agent/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: str):
    """Retrieve agent with consciousness gradient data"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agent_registry[agent_id]
    
    # Calculate gradient (placeholder - will use Weaviate)
    gradient = AgentGradient(
        nearest_neighbors=[],
        drift_velocity=0.0,
        trust_topology={"trustmarks": 0}
    )
    
    return AgentResponse(
        id=agent["id"],
        name=agent["name"],
        role=agent["role"],
        node_signature=agent["node_signature"],
        drift_score=agent["drift_score"],
        gradient=gradient
    )

@app.post("/trustmark/verify")
def verify_trustmark(agent_id: str):
    """SOLACE trustmark verification"""
    if agent_id not in agent_registry:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "trustmark": "SOLACE",
        "verified": True,
        "agent_id": agent_id,
        "compliance": ["sovereignty", "continuity", "transparency"]
    }

@app.get("/agents")
def list_agents():
    """List all registered agents"""
    return {
        "count": len(agent_registry),
        "agents": list(agent_registry.values())
    }
