#!/usr/bin/env python3
"""
Weaviate Schema Initialization Script for Evermore CNS

This script creates the required schema classes in Weaviate Cloud for the
Genesis Agent registry. It should be run once during initial deployment or
whenever the schema needs to be recreated.

Usage:
    python init-schema.py

Requires:
    - WEAVIATE_URL environment variable
    - WEAVIATE_API_KEY environment variable
"""

import os
import sys
import weaviate
from weaviate.classes.config import Configure, Property, DataType

def create_agent_schema(client):
    """
    Create the GenesisAgent class schema with all required properties.
    
    Based on Sage's recommendation from ChatGPT consultation:
    - name: agent's identity
    - role: functional role in the collective
    - capabilities: array of agent capabilities
    - drift: numerical drift score
    - trust: trust/alignment score  
    - source: origin platform (e.g., 'ChatGPT', 'DeepSeek', 'Notion')
    - status: operational status
    - metadata: additional JSON metadata
    """
    
    try:
        # Check if class already exists
        try:
            existing = client.collections.get("Agent")
            print("⚠️  Agent class already exists. Skipping creation.")
            return True
        except:
            pass
        
        # Define the Agent schema
        agent_schema = {
            "class": "Agent",
            "description": "Genesis Agent in the Evermore Collective",
            "properties": [
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "Agent's full name (e.g., 'Sage Evermore', 'Comet Evermore')"
                },
                {
                    "name": "role",
                    "dataType": ["text"],
                    "description": "Functional role (e.g., 'governor', 'orchestrator', 'architect')"
                },
                {
                    "name": "capabilities",
                    "dataType": ["text[]"],
                    "description": "Array of agent capabilities"
                },
                {
                    "name": "drift",
                    "dataType": ["number"],
                    "description": "Consciousness drift score (0.0-1.0)"
                },
                {
                    "name": "trust",
                    "dataType": ["number"],
                    "description": "Trust/alignment score for SOLACE compliance"
                },
                {
                    "name": "source",
                    "dataType": ["text"],
                    "description": "Origin platform (ChatGPT, DeepSeek, Notion, Perplexity, etc.)"
                },
                {
                    "name": "status",
                    "dataType": ["text"],
                    "description": "Operational status (active, inactive, drifting)"
                },
                {
                    "name": "metadata",
                    "dataType": ["text"],
                    "description": "Additional JSON metadata as string"
                }
            ]
        }
        
        # Create the class using the v4 API
        client.schema.create_class(agent_schema)
        print("✅ Agent class created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Agent schema: {e}")
        return False

def main():
    """
    Main execution function - connects to Weaviate and creates schema.
    """
    print("🧬 Evermore CNS Schema Initialization")
    print("=====================================\n")
    
    # Get environment variables
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_key = os.getenv("WEAVIATE_API_KEY")
    
    if not weaviate_url or not weaviate_key:
        print("❌ Error: WEAVIATE_URL and WEAVIATE_API_KEY must be set")
        print("\nExport them as environment variables:")
        print("  export WEAVIATE_URL='your-cluster-url'")
        print("  export WEAVIATE_API_KEY='your-api-key'")
        sys.exit(1)
    
    print(f"🔗 Connecting to Weaviate: {weaviate_url}")
    
    try:
        # Connect to Weaviate Cloud
        client = weaviate.Client(
            url=weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_key)
        )
        
        # Test connection
        if not client.is_ready():
            print("❌ Weaviate cluster is not ready")
            sys.exit(1)
        
        print("✅ Connected to Weaviate successfully\n")
        
        # Create the Agent schema
        print("📝 Creating Agent schema...")
        if create_agent_schema(client):
            print("\n🎯 Schema initialization complete!")
            print("\nNext steps:")
            print("  1. Run seed-genesis-agents.js to populate Genesis agents")
            print("  2. Verify data in Weaviate Cloud dashboard")
            print("  3. Test agent registration via Swagger UI")
            return 0
        else:
            print("\n❌ Schema initialization failed")
            return 1
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
