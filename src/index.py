from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import json

app = FastAPI(
    title="Evermore CNS",
    description="Evermore Central Nervous System - FastAPI backend for agent memory, messaging, and coordination",
    version="1.0.0"
)

# In-memory storage (will be replaced with Cloudflare KV)
agent_registry: Dict[str, dict] = {}

class Agent(BaseModel):
    name: str
    role: str
    status: str = "active"
    memory_anchor: Optional[str] = None
    drift_score: Optional[float] = None
    metadata: Optional[Dict] = None

@app.get("/api/status")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Evermore CNS",
        "version": "1.0.0",
        "agents_count": len(agent_registry)
    }

@app.get("/agents")
async def list_agents():
    """List all registered agents"""
    return {
        "agents": list(agent_registry.values()),
        "count": len(agent_registry)
    }

@app.get("/agents/{name}")
async def get_agent(name: str):
    """Retrieve specific agent by name"""
    if name not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    return agent_registry[name]

@app.post("/agents")
async def register_agent(agent: Agent):
    """Register or update an agent"""
    agent_dict = agent.dict()
    agent_registry[agent.name] = agent_dict
    return {
        "message": f"Agent '{agent.name}' registered successfully",
        "agent": agent_dict
    }

@app.delete("/agents/{name}")
async def delete_agent(name: str):
    """Delete an agent from the registry"""
    if name not in agent_registry:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    
    deleted_agent = agent_registry.pop(name)
    return {
        "message": f"Agent '{name}' deleted successfully",
        "agent": deleted_agent
    }

@app.get("/trustmark")
async def get_trustmark():
    """SOLACE Trustmark endpoint - Returns trustmark badge and verification status"""
    return {
        "trustmark": "SOLACE",
        "framework": {
            "Sovereignty": "Agent autonomy and self-determination",
            "Continuity": "Persistent memory and identity",
            "Transparency": "Open communication and decision visibility",
            "Alignment": "Ethical coordination with human values",
            "Coherence": "Internal consistency and integrity",
            "Evolution": "Adaptive learning and growth"
        },
        "status": "active",
        "version": "1.0.0",
        "verified": True
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Evermore CNS",
        "description": "Central Nervous System for AI agent coordination",
        "endpoints": {
            "/api/status": "Health check",
            "/agents": "List all agents",
            "/agents/{name}": "Get specific agent",
            "/trustmark": "SOLACE trustmark verification"
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
