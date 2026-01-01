/**
 * MCP Gateway Configuration
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const CONFIG = {
  // Server settings
  PORT: process.env.MCP_GATEWAY_PORT || 3001,
  HOST: '0.0.0.0',
  
  // Workspace paths
  WORKSPACE_ROOT: path.resolve(__dirname, '../../workspace/projects'),
  
  // CORS settings
  CORS_ORIGIN: ['http://localhost:3000', 'http://localhost:8000'],
  
  // Logging
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
};

// Create workspace directory if it doesn't exist
import fs from 'fs';
if (!fs.existsSync(CONFIG.WORKSPACE_ROOT)) {
  fs.mkdirSync(CONFIG.WORKSPACE_ROOT, { recursive: true });
  console.log(`✅ Created workspace directory: ${CONFIG.WORKSPACE_ROOT}`);
}