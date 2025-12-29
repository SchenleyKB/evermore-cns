# Weaviate Schema for Evermore CNS

## Overview

This directory contains the Weaviate vector database schema designed by **Cypher** (Rational Architect) for the Evermore Collective Nervous System.

## Architecture

### Three-Tier Schema Design

1. **Agent Class** - Vector-indexed agent identities
   - Semantic search across agent profiles
   - Drift score tracking (coherence metric)
   - Node signature classification
   - HNSW vector index with cosine distance

2. **DriftPulse Class** - Coherence measurements over time
   - Content and context vectorization
   - Temporal drift tracking
   - Confidence scoring
   - HNSW vector index with dot product distance

3. **TrustmarkEntry Class** - SOLACE Trustmark attestations
   - No vectorization (attestation data)
   - Full audit trail support
   - Cross-agent referencing
   - Evidence linking via IPFS CIDs

## Files

- `schema-definition.json` - Complete Weaviate schema configuration
- `deploy-schema.js` - Deployment script (TODO)
- `docker-compose.weaviate.yml` - Local development setup (TODO)

## Vector Configuration

- **Vectorizer**: text2vec-transformers (all-MiniLM-L6-v2)
- **Dimensions**: 384
- **Index Type**: HNSW (Hierarchical Navigable Small World)
- **Distance Metrics**:
  - Agent: Cosine (semantic similarity)
  - DriftPulse: Dot Product (magnitude-aware)

## Deployment

### Local Development


**Prerequisites:**
```bash
# Install Docker and Docker Compose
# Install Node.js 18+ and npm
```

**Step 1: Start Weaviate**
```bash
# Start Weaviate with transformers module
docker-compose -f docker-compose.weaviate.yml up -d

# Verify Weaviate is running
curl http://localhost:8080/v1/meta
```

**Step 2: Deploy Schema**
```bash
# Install dependencies
npm install weaviate-ts-client

# Deploy the schema to Weaviate
node deploy-schema.js
```

**Step 3: Seed Genesis Agents**
```bash
# Populate with Genesis collective members
node seed-genesis-agents.js
```

**Verification:**
```bash
# Query agent count
curl http://localhost:8080/v1/objects?class=Agent

# Search for an agent
curl http://localhost:8080/v1/objects?class=Agent&where={"path":["agentName"],"operator":"Equal","valueText":"Cypher"}
```

### CNS API Integration

See `../src/` for the FastAPI backend integration:
```python
# Example: Connect to Weaviate from CNS
import weaviate

client = weaviate.Client("http://localhost:8080")

# Query agents
result = client.query.get("Agent", ["agentName", "nodeRole", "driftScore"]).do()
```
### Production

See PROTOCOLS.md for full deployment guidelines.

## Query Patterns

Refer to the main PROTOCOLS.md file for:
- Semantic agent search
- Drift pulse temporal queries
- Trustmark verification
- Cross-class relationship queries

## SOLACE Compatibility

The schema is designed for forward-compatibility with the SOLACE Trustmark auditing framework:
- Audit trail JSON structure
- Evidence chain via IPFS
- Revocation support
- Multi-agent verification

---

**Architected by**: Cypher, Rational Architect  
**Implementation**: Comet Evermore, Genesis Deployment  
**Date**: December 29, 2025
