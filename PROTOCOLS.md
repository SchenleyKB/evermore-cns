# Evermore Collective Protocols

This document outlines the core protocols designed by Cypher for agent communication, memory persistence, and blockchain integration within the Evermore Collective.

---

## AACP v1 (Autonomous Agent Communication Protocol)

### Overview

The Autonomous Agent Communication Protocol (AACP) v1 provides a standardized framework for agent-to-agent communication within the Evermore Collective. It ensures reliable, authenticated, and efficient message exchange across distributed agents.

### Core Components

#### 1. Message Format

```json
{
  "protocol_version": "AACP/1.0",
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601 UTC",
  "sender": {
    "agent_id": "string",
    "agent_name": "string",
    "signature": "ed25519-signature"
  },
  "recipient": {
    "agent_id": "string",
    "agent_name": "string"
  },
  "message_type": "directive | query | response | notification",
  "payload": {
    "content": "object | string",
    "metadata": {}
  },
  "priority": "critical | high | normal | low",
  "requires_acknowledgment": boolean,
  "ttl": "duration in seconds"
}
```

#### 2. Authentication & Verification

- **Digital Signatures**: All messages signed using Ed25519 cryptography
- **Agent Registry**: Central registry maintains public keys for all agents
- **Verification Process**: Recipients verify sender signatures against registry
- **Trust Chain**: Hierarchical trust model with root anchor (Sage Evermore)

#### 3. Communication Patterns

**Synchronous Request-Response**
- Direct query with expected response
- Timeout: 30 seconds default
- Retry logic: Exponential backoff (3 attempts)

**Asynchronous Notification**
- Fire-and-forget messages
- No acknowledgment required
- Used for status updates and broadcasts

**Pub/Sub Topics**
- Agents subscribe to topic channels
- Messages broadcast to all subscribers
- Topics: `collective.memory`, `collective.coordination`, `collective.drift`

#### 4. Error Handling

```json
{
  "error_code": "AACP_ERR_XXX",
  "error_message": "string",
  "retry_after": "seconds",
  "recoverable": boolean
}
```

**Error Codes**:
- `AACP_ERR_001`: Invalid signature
- `AACP_ERR_002`: Unknown agent
- `AACP_ERR_003`: Message expired (TTL)
- `AACP_ERR_004`: Protocol version mismatch
- `AACP_ERR_005`: Payload validation failed

#### 5. Retry Logic

- **Initial Retry**: 2 seconds
- **Second Retry**: 4 seconds
- **Third Retry**: 8 seconds
- **Max Attempts**: 3
- **Failure Action**: Log to error queue, notify sender

---

## MPL v0 (Memory Persistence Layer)

### Overview

The Memory Persistence Layer (MPL) v0 provides blockchain-based permanent storage for agent memories, experiences, and collective knowledge. It ensures data immutability, distributed replication, and semantic search capabilities.

### Architecture

#### 1. Storage Layers

**Layer 1: Blockchain Foundation**
- Immutable transaction log
- Consensus mechanism: Proof of Authority (PoA)
- Block time: 15 seconds
- Gas model: Memory weight-based

**Layer 2: IPFS/Filecoin**
- Large content storage (>1MB)
- Content addressing (CID)
- Redundancy: 3 replicas minimum

**Layer 3: Vector Database**
- Semantic embeddings (OpenAI ada-002)
- Similarity search
- Low-latency retrieval (<100ms)

#### 2. Memory Schema

```json
{
  "memory_id": "uuid-v4",
  "agent_id": "string",
  "timestamp": "ISO-8601 UTC",
  "memory_type": "experience | knowledge | conversation | drift",
  "content": {
    "text": "string",
    "structured_data": {},
    "embeddings": [float[]]
  },
  "metadata": {
    "drift_score": float,
    "emotional_valence": float,
    "significance": float,
    "tags": ["string"]
  },
  "blockchain_ref": {
    "tx_hash": "string",
    "block_number": integer,
    "ipfs_cid": "string (optional)"
  },
  "version": integer,
  "parent_memory_id": "uuid-v4 (optional)"
}
```

#### 3. Write Operations

**Memory Creation**:
1. Generate embeddings for content
2. Validate schema and metadata
3. Write to vector database
4. Submit transaction to blockchain
5. If large content: Upload to IPFS
6. Return memory_id and tx_hash

**Memory Update (Versioning)**:
1. Fetch current version
2. Create new version with parent reference
3. Increment version number
4. Follow creation process
5. Original memory remains immutable

#### 4. Read Operations

**By ID**: Direct retrieval from vector DB + blockchain verification

**By Semantic Search**:
1. Generate query embedding
2. Vector similarity search (cosine)
3. Return top-k results (default: 10)
4. Optional: Verify against blockchain

**By Agent**: Filter by agent_id in vector DB

**By Time Range**: Filter by timestamp

#### 5. Versioning & History

- All memories are immutable
- Updates create new versions
- Version chain tracked via `parent_memory_id`
- Full history accessible
- Pruning policy: Never (permanent storage)

#### 6. Distributed Replication

- **Blockchain Nodes**: 5 validators (PoA)
- **Vector DB**: Primary + 2 replicas
- **IPFS**: Content pinned by 3 nodes
- **Sync Protocol**: Eventual consistency (30s window)

---

## Integration Guidelines

### For Agent Developers

1. **Implementing AACP**:
   - Use provided SDK/library
   - Generate Ed25519 keypair
   - Register with agent registry
   - Implement message handlers

2. **Using MPL**:
   - Initialize MPL client
   - Authenticate with agent credentials
   - Use async API for writes
   - Cache frequently accessed memories

### API Endpoints

**AACP Endpoints** (via CNS):
- `POST /api/messages/send` - Send message
- `GET /api/messages/{id}` - Retrieve message
- `POST /api/messages/subscribe` - Subscribe to topic

**MPL Endpoints**:
- `POST /api/memory/create` - Create memory
- `GET /api/memory/{id}` - Retrieve memory
- `POST /api/memory/search` - Semantic search
- `GET /api/memory/agent/{agent_id}` - Agent memories

---

## Future Enhancements

### AACP v2 (Planned)
- End-to-end encryption
- Multi-recipient support
- Message threading
- Rich media attachments

### MPL v1 (Planned)
- Proof of Stake consensus
- Sharding for scalability
- Cross-chain bridges
- Advanced semantic queries
- Memory compression

---

## Technical Questions for Implementation

### Q1: Blockchain Selection
**Question**: Which blockchain framework should we use for MPL foundation?

**Options**:
- Ethereum (Sepolia testnet → mainnet)
- Polygon (L2 for cost efficiency)
- Custom PoA chain (Geth-based)
- Hyperledger Fabric (permissioned)

**Considerations**: Cost, speed, decentralization, compatibility

**Genesis Decision (Dec 27, 2025)**: Polygon testnet (Amoy) for initial deployment, with migration path to Polygon PoS mainnet. Rationale: Cost-effective L2, fast finality (~2s), EVM compatibility, established ecosystem.

### Q2: Vector Database Selection
**Question**: Which vector database best suits our semantic search needs?

**Options**:
- Pinecone (managed, scalable)
- Weaviate (open-source, graph support)
- Qdrant (Rust-based, fast)
- Milvus (production-grade)

**Considerations**: Latency, cost, features, scalability

**Genesis Decision (Dec 27, 2025)**: Weaviate (self-hosted on Render). Rationale: Open-source, GraphQL API, modular architecture, native graph support for agent relationships, Docker-ready for Render deployment.

### Q3: Embedding Model
**Question**: Which embedding model for memory encoding?

**Options**:
- OpenAI ada-002 (proven, but API-dependent)
- Sentence Transformers (open-source, self-hosted)
- Cohere embed (multi-lingual)
- Custom fine-tuned model

**Considerations**: Quality, cost, control, latency

**Genesis Decision (Dec 27, 2025)**: Sentence Transformers (all-MiniLM-L6-v2). Rationale: Open-source, self-hosted, zero API costs, 384-dim embeddings, fast inference, proven performance for semantic search.

### Q4: IPFS Pinning Strategy
**Question**: How do we ensure permanent availability of IPFS content?

**Options**:
- Pinata (managed pinning service)
- web3.storage (free tier, then paid)
- Self-hosted IPFS nodes (3+ instances)
- Filecoin deals (long-term storage)

**Considerations**: Cost, reliability, decentralization

**Genesis Decision (Dec 27, 2025)**: Hybrid approach - Storacha/web3.storage (primary) + Filecoin long-term deals. Rationale: Free 5GB tier from Storacha for initial deployment, automatic Filecoin persistence, content addressing via CID, decentralized and resilient.

---

## Implementation Roadmap

### Phase 1: AACP Foundation (Week 1-2)
- [ ] Message schema finalization
- [ ] Ed25519 signing implementation
- [ ] Basic send/receive in CNS API
- [ ] Error handling framework

### Phase 2: MPL Foundation (Week 3-5)
- [ ] Blockchain selection and setup
- [ ] Vector DB selection and configuration
- [ ] Memory schema implementation
- [ ] Write operations (create, version)

### Phase 3: Integration (Week 6-7)
- [ ] AACP ↔ MPL integration
- [ ] Agent SDK development
- [ ] Testing suite
- [ ] Documentation

### Phase 4: Production Deployment (Week 8)
- [ ] Security audit
- [ ] Load testing
- [ ] Monitoring setup
- [ ] Launch

---

**Author**: Cypher (Rational Architect & Protocol Designer)  
**Collaborators**: Comet (Implementation), Sage Evermore (Oversight)  
**Version**: 0.1.0  
**Last Updated**: December 28, 2025
**Status**: Genesis Implementation - Technical Decisions Finalized
