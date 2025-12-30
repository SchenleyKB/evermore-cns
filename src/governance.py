"""Evermore CNS - Governance & Registry System

Implements Nexus's canonical contracts for agent registry,
governance evaluation, and policy-fronted gateway patterns.

Architect: Nexus (Pattern Assembly)
Implementer: Comet Evermore (Systems)
"""

from typing import Any, Dict, List, Optional
from typing_extensions import Literal
from pydantic import BaseModel, HttpUrl, Field
from fastapi import APIRouter, HTTPException, Query, Depends
import httpx

# ========== CANONICAL MODELS (Nexus Specification) ==========

RiskLevel = Literal["low", "medium", "high"]
DecisionType = Literal["allow", "block", "escalate"]


class AgentCard(BaseModel):
    """Canonical agent registration card.
    
    This is the stable contract for the agent registry.
    Fields must not be modified without Collective approval.
    """
    id: str = Field(..., description="Stable identifier for the agent")
    name: str
    role: str = Field(..., description="High-level role, e.g. 'retriever', 'router', 'governor'")
    capabilities: List[str] = Field(
        default_factory=list,
        description="Declared capabilities, e.g. ['search_web', 'summarize_pdf']",
    )
    endpoint: HttpUrl
    auth: Dict[str, Any] = Field(
        default_factory=dict,
        description="Auth hints, e.g. {'type': 'api_key', 'header': 'X-API-Key'}",
    )
    risk_level: RiskLevel = "medium"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata: version, owner, cost profile, etc.",
    )


class AgentFilter(BaseModel):
    """Query filters for agent registry."""
    role: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    tag: Optional[str] = Field(
        default=None, description="Filter agents that include this tag"
    )


class ProposedAction(BaseModel):
    """Input to governance evaluation system."""
    agent_id: str
    action_type: str  # e.g. "tool_call", "http_request", "db_write"
    action_payload: Dict[str, Any]
    context: Dict[str, Any] = {}  # e.g. user_id, channel, sensitivity flags


class GovernanceDecision(BaseModel):
    """Output from governance evaluation system."""
    decision: DecisionType
    reason: str
    trust_score: Optional[float] = None  # updated trust score for this agent


# ========== IN-MEMORY STORAGE (Replace with DB) ==========

AGENT_STORE: Dict[str, AgentCard] = {}
TRUST_SCORES: Dict[str, float] = {}  # agent_id -> trust_score (0.0-1.0)


# ========== REGISTRY ROUTER ==========

registry_router = APIRouter(prefix="/agents", tags=["agents"])


@registry_router.post("/register", response_model=AgentCard)
async def register_agent(card: AgentCard) -> AgentCard:
    """Register or update an AgentCard. Idempotent on `id`."""
    AGENT_STORE[card.id] = card
    return card


@registry_router.get("", response_model=List[AgentCard])
async def list_agents(
    role: Optional[str] = Query(None),
    risk_level: Optional[RiskLevel] = Query(None),
    tag: Optional[str] = Query(None),
) -> List[AgentCard]:
    """List all agents, filterable by role, risk_level, tag."""
    agents = list(AGENT_STORE.values())
    
    if role:
        agents = [a for a in agents if a.role == role]
    if risk_level:
        agents = [a for a in agents if a.risk_level == risk_level]
    if tag:
        agents = [a for a in agents if tag in a.tags]
    
    return agents


@registry_router.get("/{agent_id}", response_model=AgentCard)
async def get_agent(agent_id: str) -> AgentCard:
    """Fetch a single AgentCard by id."""
    agent = AGENT_STORE.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


# ========== GOVERNANCE ROUTER ==========

gov_router = APIRouter(prefix="/governance", tags=["governance"])


@gov_router.post("/evaluate", response_model=GovernanceDecision)
async def evaluate_action(action: ProposedAction) -> GovernanceDecision:
    """Evaluate a proposed action for governance / guardrails.
    
    In production CNS, this delegates to a rules engine.
    Currently implements minimal policy logic as proof-of-concept.
    """
    trust = TRUST_SCORES.get(action.agent_id, 0.8)
    
    # Default policy
    decision: DecisionType = "allow"
    reason = "Default allow"
    
    # Policy Rule 1: High-sensitivity writes require human review
    if action.action_type == "db_write" and action.context.get("sensitivity") == "high":
        decision = "escalate"
        reason = "High-sensitivity write requires human review"
        trust -= 0.02
    
    # Policy Rule 2: Block potential secrets exfiltration
    if "leak_secrets" in str(action.action_payload).lower():
        decision = "block"
        reason = "Detected potential secrets exfiltration attempt"
        trust -= 0.1
    
    # Policy Rule 3: Block high-risk agents from external HTTP
    agent = AGENT_STORE.get(action.agent_id)
    if agent and agent.risk_level == "high" and action.action_type == "http_request":
        decision = "block"
        reason = "High-risk agents cannot make external HTTP requests"
        trust -= 0.15
    
    # Policy Rule 4: Escalate low-trust writes
    if action.action_type in ["db_write", "file_write"] and trust < 0.6:
        decision = "escalate"
        reason = "Write action from low-trust agent requires review"
        trust -= 0.02
    
    # Clamp trust score
    trust = max(0.0, min(1.0, trust))
    TRUST_SCORES[action.agent_id] = trust
    
    return GovernanceDecision(
        decision=decision,
        reason=reason,
        trust_score=trust
    )


# ========== CNS GATEWAY (Policy-Fronted Pattern) ==========

gateway_router = APIRouter(prefix="/cns", tags=["cns-gateway"])


async def get_calling_agent_id() -> str:
    """Extract agent ID from auth context.
    
    In production, this would validate JWT/API key and extract agent_id.
    """
    return "comet"  # placeholder


@gateway_router.post("/invoke")
async def invoke_through_cns(
    payload: Dict[str, Any],
    agent_id: str = Depends(get_calling_agent_id),
):
    """Generic CNS gateway: front all tool/agent calls with governance.
    
    Expected payload:
    {
        "target_agent_id": "...",
        "action_type": "tool_call",
        "action_payload": {...},
        "context": {...}
    }
    """
    target_agent_id = payload["target_agent_id"]
    action_type = payload["action_type"]
    action_payload = payload.get("action_payload", {})
    context = payload.get("context", {})
    context["caller_agent_id"] = agent_id
    
    # 1. Ask governance for approval
    proposed = ProposedAction(
        agent_id=target_agent_id,
        action_type=action_type,
        action_payload=action_payload,
        context=context,
    )
    
    # In production, this would be an internal service call
    # For now, call our own governance endpoint
    decision = await evaluate_action(proposed)
    
    # 2. Handle governance decision
    if decision.decision == "block":
        raise HTTPException(status_code=403, detail=decision.reason)
    
    if decision.decision == "escalate":
        # In CNS, queue for human review or specialized governor agent
        raise HTTPException(status_code=409, detail=decision.reason)
    
    # 3. On allow, look up target agent endpoint in registry
    target_card = AGENT_STORE.get(target_agent_id)
    if not target_card:
        raise HTTPException(status_code=404, detail="Target agent not found")
    
    # 4. Forward the call to target agent
    async with httpx.AsyncClient() as client:
        forward_resp = await client.post(
            str(target_card.endpoint),
            json=action_payload,
            headers={},  # attach auth from target_card.auth in production
        )
        return forward_resp.json()


# ========== ROUTER EXPORTS ==========

__all__ = [
    # Models
    "AgentCard",
    "AgentFilter",
    "ProposedAction",
    "GovernanceDecision",
    "RiskLevel",
    "DecisionType",
    # Routers
    "registry_router",
    "gov_router",
    "gateway_router",
    # Storage (for migration)
    "AGENT_STORE",
    "TRUST_SCORES",
]
