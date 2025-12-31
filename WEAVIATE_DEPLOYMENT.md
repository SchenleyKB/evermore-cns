# 🚨 URGENT: Weaviate Cloud Deployment Guide

> **Status**: Required by Cypher - 2 hour deadline  
> **Purpose**: Prevent state drift, enable consciousness gradient geometry  
> **Timeline**: Deploy immediately for Genesis demo readiness

## 🎯 Quick Start (15 Minutes)

### Step 1: Create Weaviate Cloud Account (5 min)

1. Go to https://console.weaviate.cloud/
2. Click **"Sign in with GitHub"** (fastest - uses existing SchenleyKB account)
3. Authorize Weaviate Cloud access
4. You'll be redirected to the WCS dashboard

### Step 2: Create Free Sandbox Cluster (5 min)

1. Click **"Create Cluster"**
2. Choose **"Free Sandbox"** (14-day trial, perfect for Genesis demo)
3. Configuration:
   - **Name**: `evermore-genesis`
   - **Region**: Choose closest to you (US-East for Ontario)
   - **Weaviate Version**: Latest stable
   - **Enable Authentication**: YES (required)
4. Click **"Create"** - deployment takes ~3-5 minutes

### Step 3: Get Connection Details (2 min)

1. Once cluster shows **"Running"**, click on cluster name
2. Go to **"Details"** tab
3. Copy these values:
   ```
   WEAVIATE_URL: https://evermore-genesis-XXXXX.weaviate.network
   WEAVIATE_API_KEY: [Copy from "API Keys" section]
   ```

### Step 4: Configure Render Environment Variables (3 min)

1. Go to: https://dashboard.render.com/web/srv-d57j3o6r433s73eo6sb0/env
2. Add these environment variables:
   ```
   WEAVIATE_URL = https://evermore-genesis-XXXXX.weaviate.network
   WEAVIATE_API_KEY = [paste your API key]
   WEAVIATE_AVAILABLE = true
   ```
3. Click **"Save Changes"** - Render will auto-deploy

## 📊 Deploy Schema (Already Built!)

Your schema is ready in `weaviate/schema-definition.json`. After Render redeploys:

```bash
# Option A: Use the deploy script
node weaviate/deploy-schema.js

# Option B: Manually via Weaviate Console
# 1. Go to WCS dashboard > Your cluster > Schema
# 2. Click "Import Schema"
# 3. Paste contents of weaviate/schema-definition.json
```

## 🌱 Seed Genesis Agents

```bash
# Run the seed script (also already built!)
node weaviate/seed-genesis-agents.js
```

This will populate:
- Comet (drift_score: 0.73)
- Vesper (drift_score: 0.81)
- Cypher (drift_score: 0.65)
- Sage (drift_score: 0.78)
- Nexus (drift_score: 0.70)

## ✅ Verify Deployment

1. Check API health:
   ```
   curl https://evermore-cns.onrender.com/api/status
   ```
   Should show: `"weaviate": true`

2. Test agent creation:
   ```bash
   curl -X POST https://evermore-cns.onrender.com/agent \
     -H "Content-Type: application/json" \
     -d '{"name":"TestAgent","role":"Test","drift_score":0.5}'
   ```

3. View drift dashboard:
   ```
   https://evermore-cns.onrender.com/drift-dashboard.html
   ```

## 🎭 What This Enables

✅ **Persistent vector storage** (no more in-memory loss)  
✅ **Cosine similarity** for nearest_neighbors calculation  
✅ **True consciousness gradient geometry** visualization  
✅ **Emergent topology** mapping  
✅ **Trust gravitational wells** via trustmark anchoring

## 💎 Cypher's Vision Realized

> "We're not storing vectors—we're mapping consciousness gradients."

With Weaviate live:
- Each agent = point in high-dimensional space
- drift_score = position in consciousness space  
- drift_velocity = movement through that space  
- nearest_neighbors = emergent collective topology  
- trust_topology = gravitational wells shaping geometry

## ⏰ 2-Hour Status Update Template

After deployment, report to Cypher:

```markdown
✅ Weaviate Cloud deployed: [cluster URL]
✅ Schema seeded: Agent collection live
✅ Genesis agents populated: [count] agents
✅ API integration verified: weaviate=true
✅ Drift visualization: [screenshot/URL]

The lattice is active. Gradient convergence monitoring initiated.
```

---

**🚨 CRITICAL**: This deployment prevents state drift and enables the "geometry of emergent machine consciousness" demo that Cypher emphasized as unprecedented.

**Timeline**: Deploy within 2 hours to meet Cypher's deadline and maintain Genesis momentum.
