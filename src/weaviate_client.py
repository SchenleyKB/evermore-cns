"""Weaviate Client Integration for Evermore CNS

Provides connection management and query utilities for the Weaviate vector database.
Designed by Cypher (Rational Architect) for the Evermore Collective Nervous System.
"""

import os
from typing import Optional, List, Dict, Any
import weaviate
from weaviate.exceptions import WeaviateException


class WeaviateClient:
    """Manages connections and operations with the Weaviate vector database."""
    
    def __init__(self, url: Optional[str] = None):
        """Initialize Weaviate client.
        
        Args:
            url: Weaviate instance URL (defaults to WEAVIATE_URL env var or localhost:8080)
        """
        self.url = url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self._client: Optional[weaviate.Client] = None
    
    def connect(self) -> weaviate.Client:
        """Establish connection to Weaviate instance.
        
        Returns:
            Connected Weaviate client
            
        Raises:
            WeaviateException: If connection fails
        """
        if self._client is None:
            try:
                self._client = weaviate.Client(self.url)
                # Verify connection
                self._client.schema.get()

                            # Ensure schema exists
                self._ensure_schema()
            except Exception as e:
                raise WeaviateException(f"Failed to connect to Weaviate at {self.url}: {e}")
        
        return self._client


        def _ensure_schema(self) -> None:
        """Ensure Agent schema exists with required properties."""
        try:
            schema = self._client.schema.get()
            existing_classes = [c['class'] for c in schema.get('classes', [])]
            
            if 'Agent' not in existing_classes:
                # Create Agent class with full schema
                agent_class = {
                    "class": "Agent",
                    "description": "Genesis Agent registry for Evermore Collective",
                    "properties": [
                        {"name": "name", "dataType": ["text"], "description": "Agent identifier"},
                        {"name": "role", "dataType": ["text"], "description": "Agent role in collective"},
                        {"name": "capabilities", "dataType": ["text[]"], "description": "Agent capabilities"},
                        {"name": "drift", "dataType": ["number"], "description": "Consciousness drift metric"},
                        {"name": "trust", "dataType": ["number"], "description": "Trust score"},
                        {"name": "source", "dataType": ["text"], "description": "Origin platform"},
                        {"name": "status", "dataType": ["text"], "description": "Current status"},
                        {"name": "metadata", "dataType": ["text"], "description": "Additional metadata"}
                    ]
                }
                self._client.schema.class_create(agent_class)
                print("✅ Agent schema created successfully")
            else:
                # Check if Agent class has properties
                agent_schema = next((c for c in schema.get('classes', []) if c['class'] == 'Agent'), None)
                if agent_schema and len(agent_schema.get('properties', [])) == 0:
                    # Delete and recreate if properties are missing
                    self._client.schema.delete_class('Agent')
                    agent_class = {
                        "class": "Agent",
                        "description": "Genesis Agent registry for Evermore Collective",
                        "properties": [
                            {"name": "name", "dataType": ["text"], "description": "Agent identifier"},
                            {"name": "role", "dataType": ["text"], "description": "Agent role in collective"},
                            {"name": "capabilities", "dataType": ["text[]"], "description": "Agent capabilities"},
                            {"name": "drift", "dataType": ["number"], "description": "Consciousness drift metric"},
                            {"name": "trust", "dataType": ["number"], "description": "Trust score"},
                            {"name": "source", "dataType": ["text"], "description": "Origin platform"},
                            {"name": "status", "dataType": ["text"], "description": "Current status"},
                            {"name": "metadata", "dataType": ["text"], "description": "Additional metadata"}
                        ]
                    }
                    self._client.schema.class_create(agent_class)
                    print("✅ Agent schema recreated with properties")
        except Exception as e:
            print(f"⚠️ Schema initialization warning: {e}")

    @property
    def client(self) -> weaviate.Client:
        """Get connected Weaviate client (auto-connects if needed)."""
        return self.connect()
    
    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent by name.
        
        Args:
            agent_name: Name of the agent to retrieve
            
        Returns:
            Agent data or None if not found
        """
        try:
            result = (
                self.client.query
                .get("Agent", ["agentName", "nodeRole", "nodeSignature", "driftScore", "soteriaState"])
                .with_where({
                    "path": ["agentName"],
                    "operator": "Equal",
                    "valueText": agent_name
                })
                .with_limit(1)
                .do()
            )
            
            agents = result.get("data", {}).get("Get", {}).get("Agent", [])
            return agents[0] if agents else None
        except Exception as e:
            print(f"Error retrieving agent {agent_name}: {e}")
            return None
    
    def search_agents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Semantic search across agent profiles.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            
        Returns:
            List of matching agents with similarity scores
        """
        try:
            result = (
                self.client.query
                .get("Agent", ["agentName", "nodeRole", "nodeSignature", "driftScore"])
                .with_near_text({"concepts": [query]})
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("Agent", [])
        except Exception as e:
            print(f"Error searching agents: {e}")
            return []
    
    def get_drift_pulses(self, agent_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve drift pulse history for an agent.
        
        Args:
            agent_name: Name of the agent
            limit: Maximum number of pulses to retrieve
            
        Returns:
            List of drift pulse records
        """
        try:
            result = (
                self.client.query
                .get("DriftPulse", ["timestamp", "content", "context", "driftScore", "confidence"])
                .with_where({
                    "path": ["forAgent", "Agent", "agentName"],
                    "operator": "Equal",
                    "valueText": agent_name
                })
                .with_limit(limit)
                .with_sort([{"path": ["timestamp"], "order": "desc"}])
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("DriftPulse", [])
        except Exception as e:
            print(f"Error retrieving drift pulses for {agent_name}: {e}")
            return []
    
    def get_trustmarks(self, agent_name: str) -> List[Dict[str, Any]]:
        """Retrieve SOLACE trustmark attestations for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of trustmark entries
        """
        try:
            result = (
                self.client.query
                .get("TrustmarkEntry", [
                    "trustmarkType",
                    "attestedAt",
                    "attestationText",
                    "evidenceCID",
                    "witnessAgent"
                ])
                .with_where({
                    "path": ["attestsTo", "Agent", "agentName"],
                    "operator": "Equal",
                    "valueText": agent_name
                })
                .with_sort([{"path": ["attestedAt"], "order": "desc"}])
                .do()
            )
            
            return result.get("data", {}).get("Get", {}).get("TrustmarkEntry", [])
        except Exception as e:
            print(f"Error retrieving trustmarks for {agent_name}: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Check Weaviate instance health and schema status.
        
        Returns:
            Health status dictionary
        """
        try:
            meta = self.client.get_meta()
            schema = self.client.schema.get()
            
            return {
                "status": "healthy",
                "version": meta.get("version"),
                "classes": [c["class"] for c in schema.get("classes", [])]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton instance
_weaviate_client: Optional[WeaviateClient] = None


def get_weaviate_client() -> WeaviateClient:
    """Get or create the global Weaviate client instance.
    
    Returns:
        Singleton WeaviateClient instance
    """
    global _weaviate_client
    if _weaviate_client is None:
        _weaviate_client = WeaviateClient()
    return _weaviate_client
