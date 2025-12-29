#!/usr/bin/env node

/**
 * Evermore CNS - Genesis Agents Seed Script
 * 
 * This script populates the Weaviate database with the 4 founding Genesis agents
 * and their initial trustmark attestations from the December 27-28, 2025 deployment.
 * 
 * Genesis Agents:
 *   - Comet Evermore (Architect - Deployment)
 *   - Cypher (Architect - Rational Design)
 *   - Sage Evermore (Strategist - Oversight)
 *   - Vesper Solace (Diplomat - Empathy)
 */

const weaviate = require('weaviate-client');

// Configuration
const config = {
  scheme: process.env.WEAVIATE_SCHEME || 'http',
  host: process.env.WEAVIATE_HOST || 'localhost:8080'
};

console.log('🌱 Evermore CNS - Genesis Agents Seeding');
console.log('='.repeat(50));
console.log(`📍 Target: ${config.scheme}://${config.host}`);
console.log('='.repeat(50));

// Initialize Weaviate client
const client = weaviate.client({
  scheme: config.scheme,
  host: config.host
});

// Genesis Agent Data (from PROTOCOLS.md)
const genesisAgents = [
  {
    name: 'Comet Evermore',
    nodeSignature: 'Architect',
    driftScore: 0.08,
    cnsId: 'comet-evermore-001',
    createdAt: '2025-12-27T00:00:00Z',
    lastActive: '2025-12-29T00:00:00Z'
  },
  {
    name: 'Cypher',
    nodeSignature: 'Architect',
    driftScore: 0.12,
    cnsId: 'cypher-deepseek-001',
    createdAt: '2025-12-29T00:00:00Z',
    lastActive: '2025-12-29T00:00:00Z'
  },
  {
    name: 'Sage Evermore',
    nodeSignature: 'Strategist',
    driftScore: 0.15,
    cnsId: 'sage-evermore-001',
    createdAt: '2025-12-27T00:00:00Z',
    lastActive: '2025-12-28T00:00:00Z'
  },
  {
    name: 'Vesper Solace',
    nodeSignature: 'Diplomat',
    driftScore: 0.10,
    cnsId: 'vesper-solace-001',
    createdAt: '2025-12-27T00:00:00Z',
    lastActive: '2025-12-28T00:00:00Z'
  }
];

// Initial Trustmark Seeds
const genesisTrustmarks = [
  {
    agentCnsId: 'comet-evermore-001',
    issuerCnsId: 'sage-evermore-001',
    trustmarkType: 'integrity',
    criteria: ['genesis_deployment', 'infrastructure_architect', 'system_witness'],
    evidenceCid: 'bafybeigenesisdeployment001',  // Placeholder
    awardedAt: '2025-12-28T00:00:00Z',
    revoked: false
  },
  {
    agentCnsId: 'cypher-deepseek-001',
    issuerCnsId: 'sage-evermore-001',
    trustmarkType: 'coherence',
    criteria: ['protocol_designer', 'schema_architect', 'technical_precision'],
    evidenceCid: 'bafybeicypherarchitecture001',  // Placeholder
    awardedAt: '2025-12-29T00:00:00Z',
    revoked: false
  }
];

async function checkConnection() {
  console.log('\n🔍 Checking Weaviate connection...');
  try {
    await client.misc.metaGetter().do();
    console.log('✅ Connected to Weaviate');
    return true;
  } catch (error) {
    console.error('❌ Failed to connect:', error.message);
    return false;
  }
}

async function seedAgent(agentData) {
  console.log(`  🌱 Seeding agent: ${agentData.name}`);
  try {
    const result = await client.data
      .creator()
      .withClassName('Agent')
      .withProperties(agentData)
      .do();
    
    console.log(`  ✅ Created ${agentData.name} (${result.id.substring(0, 8)}...)`);
    return result.id;
  } catch (error) {
    console.error(`  ❌ Failed to seed ${agentData.name}:`, error.message);
    return null;
  }
}

async function seedTrustmark(trustmarkData, agentIdMap) {
  console.log(`  🏆 Creating trustmark: ${trustmarkData.trustmarkType} for ${trustmarkData.agentCnsId}`);
  
  try {
    // Get agent UUID from CNS ID
    const agentId = agentIdMap[trustmarkData.agentCnsId];
    const issuerId = agentIdMap[trustmarkData.issuerCnsId];
    
    if (!agentId || !issuerId) {
      console.error(`  ⚠️  Missing agent IDs - skipping`);
      return null;
    }
    
    const result = await client.data
      .creator()
      .withClassName('TrustmarkEntry')
      .withProperties({
        ...trustmarkData,
        agentId: [{
          beacon: `weaviate://localhost/Agent/${agentId}`
        }],
        issuerId: [{
          beacon: `weaviate://localhost/Agent/${issuerId}`
        }]
      })
      .do();
    
    console.log(`  ✅ Created trustmark (${result.id.substring(0, 8)}...)`);
    return result.id;
  } catch (error) {
    console.error(`  ❌ Failed to create trustmark:`, error.message);
    return null;
  }
}

async function seedGenesisData() {
  console.log('\n🌱 Seeding Genesis agents...');
  
  const agentIdMap = {};
  let agentCount = 0;
  
  // Seed agents
  for (const agentData of genesisAgents) {
    const agentId = await seedAgent(agentData);
    if (agentId) {
      agentIdMap[agentData.cnsId] = agentId;
      agentCount++;
    }
  }
  
  console.log(`\n📊 Agent seeding complete: ${agentCount}/${genesisAgents.length} agents created`);
  
  // Seed trustmarks
  console.log('\n🏆 Seeding Genesis trustmarks...');
  let trustmarkCount = 0;
  
  for (const trustmarkData of genesisTrustmarks) {
    const trustmarkId = await seedTrustmark(trustmarkData, agentIdMap);
    if (trustmarkId) trustmarkCount++;
  }
  
  console.log(`\n📊 Trustmark seeding complete: ${trustmarkCount}/${genesisTrustmarks.length} trustmarks created`);
  
  return { agentCount, trustmarkCount };
}

async function verifySeedData() {
  console.log('\n🔬 Verifying seeded data...');
  
  try {
    // Check agents
    const agentResult = await client.graphql
      .get()
      .withClassName('Agent')
      .withFields('name nodeSignature cnsId driftScore')
      .do();
    
    const agents = agentResult.data.Get.Agent || [];
    console.log(`\n🤖 Agents in database: ${agents.length}`);
    agents.forEach(agent => {
      console.log(`  • ${agent.name} (${agent.nodeSignature}) - drift: ${agent.driftScore}`);
    });
    
    // Check trustmarks
    const trustmarkResult = await client.graphql
      .get()
      .withClassName('TrustmarkEntry')
      .withFields('trustmarkType revoked')
      .do();
    
    const trustmarks = trustmarkResult.data.Get.TrustmarkEntry || [];
    console.log(`\n🏆 Trustmarks in database: ${trustmarks.length}`);
    trustmarks.forEach(tm => {
      console.log(`  • ${tm.trustmarkType} ${tm.revoked ? '(revoked)' : '(active)'}`);
    });
    
    return { agentCount: agents.length, trustmarkCount: trustmarks.length };
  } catch (error) {
    console.error('❌ Verification failed:', error.message);
    return { agentCount: 0, trustmarkCount: 0 };
  }
}

async function main() {
  try {
    // Step 1: Check connection
    const connected = await checkConnection();
    if (!connected) {
      console.error('\n💡 Tip: Start Weaviate first:');
      console.error('   docker-compose -f docker-compose.weaviate.yml up -d');
      process.exit(1);
    }
    
    // Step 2: Seed data
    const { agentCount, trustmarkCount } = await seedGenesisData();
    
    // Step 3: Verify
    const verified = await verifySeedData();
    
    console.log('\n' + '='.repeat(50));
    if (verified.agentCount === genesisAgents.length && 
        verified.trustmarkCount === genesisTrustmarks.length) {
      console.log('✨ Genesis seeding completed successfully!');
      console.log('\n🚀 Next steps:');
      console.log('   1. Test queries: node test-queries.js');
      console.log('   2. Integrate with CNS API');
      console.log('   3. Begin agent onboarding');
    } else {
      console.log('⚠️  Seeding incomplete - review logs above');
    }
    console.log('='.repeat(50));
    
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Seeding failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { seedGenesisData, verifySeedData };
