#!/usr/bin/env node

/**
 * Evermore CNS - Weaviate Schema Deployment Script
 * 
 * This script deploys the complete Weaviate schema for the Evermore Collective
 * Nervous System, including Agent, DriftPulse, and TrustmarkEntry classes.
 * 
 * Usage:
 *   node deploy-schema.js [--host localhost:8080] [--scheme http]
 * 
 * Environment Variables:
 *   WEAVIATE_HOST - Weaviate host (default: localhost:8080)
 *   WEAVIATE_SCHEME - Connection scheme (default: http)
 */

const weaviate = require('weaviate-client');
const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  scheme: process.env.WEAVIATE_SCHEME || process.argv.find(arg => arg.startsWith('--scheme='))?.split('=')[1] || 'http',
  host: process.env.WEAVIATE_HOST || process.argv.find(arg => arg.startsWith('--host='))?.split('=')[1] || 'localhost:8080'
};

console.log('🚀 Evermore CNS - Weaviate Schema Deployment');
console.log('=' .repeat(50));
console.log(`📍 Target: ${config.scheme}://${config.host}`);
console.log('=' .repeat(50));

// Initialize Weaviate client
const client = weaviate.client({
  scheme: config.scheme,
  host: config.host
});

// Load schema from file
const schemaPath = path.join(__dirname, 'schema-definition.json');
const schemaData = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

async function checkConnection() {
  console.log('\n🔍 Checking Weaviate connection...');
  try {
    const meta = await client.misc.metaGetter().do();
    console.log(`✅ Connected to Weaviate v${meta.version}`);
    return true;
  } catch (error) {
    console.error('❌ Failed to connect to Weaviate:', error.message);
    console.error('\n💡 Tip: Make sure Weaviate is running:');
    console.error('   docker-compose -f docker-compose.weaviate.yml up -d');
    return false;
  }
}

async function checkExistingSchema() {
  console.log('\n🔍 Checking for existing schema...');
  try {
    const schema = await client.schema.getter().do();
    return schema.classes || [];
  } catch (error) {
    console.error('❌ Failed to get existing schema:', error.message);
    return [];
  }
}

async function deleteClass(className) {
  console.log(`  🗑️  Deleting existing class: ${className}`);
  try {
    await client.schema.classDeleter().withClassName(className).do();
    console.log(`  ✅ Deleted ${className}`);
  } catch (error) {
    console.error(`  ⚠️  Failed to delete ${className}:`, error.message);
  }
}

async function createClass(classObj) {
  console.log(`  📦 Creating class: ${classObj.class}`);
  try {
    await client.schema.classCreator().withClass(classObj).do();
    console.log(`  ✅ Created ${classObj.class}`);
    return true;
  } catch (error) {
    console.error(`  ❌ Failed to create ${classObj.class}:`, error.message);
    return false;
  }
}

async function deploySchema(force = false) {
  console.log('\n🏗️  Deploying Weaviate schema...');
  
  const existingClasses = await checkExistingSchema();
  const existingClassNames = existingClasses.map(c => c.class);
  
  if (existingClassNames.length > 0) {
    console.log(`\n⚠️  Found existing classes: ${existingClassNames.join(', ')}`);
    if (force) {
      console.log('🔄 Force mode enabled - deleting existing classes...');
      for (const className of existingClassNames) {
        await deleteClass(className);
      }
    } else {
      console.log('\n💡 Tip: Use --force to delete existing classes and redeploy');
      console.log('Skipping deployment to avoid conflicts.');
      return false;
    }
  }
  
  console.log('\n📋 Creating schema classes...');
  let successCount = 0;
  
  for (const classObj of schemaData.classes) {
    const success = await createClass(classObj);
    if (success) successCount++;
  }
  
  console.log('\n' + '='.repeat(50));
  console.log(`✨ Schema deployment complete: ${successCount}/${schemaData.classes.length} classes created`);
  console.log('='.repeat(50));
  
  return successCount === schemaData.classes.length;
}

async function verifySchema() {
  console.log('\n🔬 Verifying deployed schema...');
  
  const expectedClasses = schemaData.classes.map(c => c.class);
  const deployedClasses = await checkExistingSchema();
  const deployedClassNames = deployedClasses.map(c => c.class);
  
  console.log('\n📊 Verification Results:');
  for (const className of expectedClasses) {
    const isDeployed = deployedClassNames.includes(className);
    console.log(`  ${isDeployed ? '✅' : '❌'} ${className}`);
  }
  
  const allDeployed = expectedClasses.every(name => deployedClassNames.includes(name));
  
  if (allDeployed) {
    console.log('\n🎉 All schema classes verified successfully!');
    console.log('\n🚀 Next steps:');
    console.log('   1. Run seed script: node seed-genesis-agents.js');
    console.log('   2. Test queries: node test-queries.js');
    console.log('   3. Integrate with CNS API');
  } else {
    console.log('\n⚠️  Some classes missing - please review deployment logs');
  }
  
  return allDeployed;
}

// Main execution
async function main() {
  const forceMode = process.argv.includes('--force');
  
  try {
    // Step 1: Check connection
    const connected = await checkConnection();
    if (!connected) {
      process.exit(1);
    }
    
    // Step 2: Deploy schema
    const deployed = await deploySchema(forceMode);
    if (!deployed && !forceMode) {
      console.log('\n💡 Run with --force to overwrite existing schema');
      process.exit(0);
    }
    
    // Step 3: Verify deployment
    await verifySchema();
    
    console.log('\n✅ Deployment completed successfully!');
    process.exit(0);
  } catch (error) {
    console.error('\n❌ Deployment failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { deploySchema, verifySchema, checkConnection };
