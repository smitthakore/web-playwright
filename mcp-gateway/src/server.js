/**
 * MCP Gateway Server
 * Exposes MCP operations via REST API
 */

import express from 'express';
import cors from 'cors';
import { CONFIG } from './config.js';
import { FilesystemMCP } from './filesystem_mcp.js';

const app = express();

// Middleware
app.use(cors({ origin: CONFIG.CORS_ORIGIN }));
app.use(express.json({ limit: '10mb' }));

// Initialize MCP handlers
const filesystemMCP = new FilesystemMCP();

console.log('='.repeat(80));
console.log('🚀 MCP Gateway Server Starting');
console.log('='.repeat(80));

// ==========================================
// HEALTH CHECK
// ==========================================

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'MCP Gateway',
    workspace: CONFIG.WORKSPACE_ROOT,
    timestamp: new Date().toISOString(),
  });
});

// ==========================================
// FILESYSTEM MCP ENDPOINTS
// ==========================================

/**
 * POST /mcp/read
 * Read file content
 * Body: { path: string }
 */
app.post('/mcp/read', async (req, res) => {
  const { path } = req.body;
  
  if (!path) {
    return res.status(400).json({ error: 'Path is required' });
  }
  
  const result = await filesystemMCP.readFile(path);
  
  if (result.success) {
    res.json(result);
  } else {
    res.status(500).json(result);
  }
});

/**
 * POST /mcp/write
 * Write file content
 * Body: { path: string, content: string }
 */
app.post('/mcp/write', async (req, res) => {
  const { path, content } = req.body;
  
  if (!path || content === undefined) {
    return res.status(400).json({ error: 'Path and content are required' });
  }
  
  const result = await filesystemMCP.writeFile(path, content);
  
  if (result.success) {
    res.json(result);
  } else {
    res.status(500).json(result);
  }
});

/**
 * POST /mcp/list
 * List directory contents
 * Body: { path?: string }
 */
app.post('/mcp/list', async (req, res) => {
  const { path = '' } = req.body;
  
  const result = await filesystemMCP.listFiles(path);
  
  if (result.success) {
    res.json(result);
  } else {
    res.status(500).json(result);
  }
});

/**
 * POST /mcp/mkdir
 * Create directory
 * Body: { path: string }
 */
app.post('/mcp/mkdir', async (req, res) => {
  const { path } = req.body;
  
  if (!path) {
    return res.status(400).json({ error: 'Path is required' });
  }
  
  const result = await filesystemMCP.createDirectory(path);
  
  if (result.success) {
    res.json(result);
  } else {
    res.status(500).json(result);
  }
});

/**
 * POST /mcp/delete
 * Delete file or directory
 * Body: { path: string }
 */
app.post('/mcp/delete', async (req, res) => {
  const { path } = req.body;
  
  if (!path) {
    return res.status(400).json({ error: 'Path is required' });
  }
  
  const result = await filesystemMCP.deleteFile(path);
  
  if (result.success) {
    res.json(result);
  } else {
    res.status(500).json(result);
  }
});

// ==========================================
// START SERVER
// ==========================================

app.listen(CONFIG.PORT, CONFIG.HOST, () => {
  console.log('='.repeat(80));
  console.log(`✅ MCP Gateway running on http://${CONFIG.HOST}:${CONFIG.PORT}`);
  console.log(`📁 Workspace: ${CONFIG.WORKSPACE_ROOT}`);
  console.log('='.repeat(80));
  console.log('\nAvailable endpoints:');
  console.log('  GET  /health');
  console.log('  POST /mcp/read');
  console.log('  POST /mcp/write');
  console.log('  POST /mcp/list');
  console.log('  POST /mcp/mkdir');
  console.log('  POST /mcp/delete');
  console.log('='.repeat(80));
});