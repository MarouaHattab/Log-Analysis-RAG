/**
 * Build script to inject environment variables into config.js
 * This is useful for Vercel deployments where env vars are available at build time
 */

const fs = require('fs');
const path = require('path');

const configPath = path.join(__dirname, 'config.js');

// Read the current config
let configContent = fs.readFileSync(configPath, 'utf8');

// Get environment variables (Vercel provides these)
const apiBaseUrl = process.env.API_BASE_URL || process.env.VERCEL_ENV_API_BASE_URL || 'http://4.232.170.195/';
const wsBaseUrl = process.env.WS_BASE_URL || process.env.VERCEL_ENV_WS_BASE_URL || 'ws://4.232.170.195/';

console.log('🔧 Building config.js with:');
console.log(`   API_BASE_URL: ${apiBaseUrl}`);
console.log(`   WS_BASE_URL: ${wsBaseUrl}`);

// Replace default values in config.js
// Match the const declarations and replace the default values
configContent = configContent.replace(
  /const API_BASE_URL = 'http:\/\/4\.232\.170\.195\/';/,
  `const API_BASE_URL = '${apiBaseUrl}';`
);

configContent = configContent.replace(
  /const WS_BASE_URL = 'ws:\/\/4\.232\.170\.195\/';/,
  `const WS_BASE_URL = '${wsBaseUrl}';`
);

// Write back
fs.writeFileSync(configPath, configContent);
console.log('✅ Config updated successfully!');
