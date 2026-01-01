/**
 * Filesystem MCP Handler
 * Provides file operations: read, write, list, mkdir
 */

import fs from 'fs/promises';
import path from 'path';
import { CONFIG } from './config.js';

export class FilesystemMCP {
  constructor() {
    this.workspaceRoot = CONFIG.WORKSPACE_ROOT;
    console.log(`📁 FilesystemMCP initialized | Workspace: ${this.workspaceRoot}`);
  }

/**
   * Validate that path is within workspace (security check)
   */
  _validatePath(relativePath = '') {
  if (path.isAbsolute(relativePath)) {
    throw new Error(
      `Absolute paths are not allowed. Use paths relative to workspace root: ${relativePath}`
    );
  }

  const resolvedPath = path.resolve(this.workspaceRoot, relativePath);
  const resolvedWorkspace = path.resolve(this.workspaceRoot);

  if (
    resolvedPath !== resolvedWorkspace &&
    !resolvedPath.startsWith(resolvedWorkspace + path.sep)
  ) {
    throw new Error(`Access denied: Path outside workspace: ${relativePath}`);
  }

  return resolvedPath;
}

  /**
   * Read file content
   */
  async readFile(filePath) {
    console.log(`📖 Reading file: ${filePath}`);
    
    try {
      const validPath = this._validatePath(filePath);
      const content = await fs.readFile(validPath, 'utf-8');
      
      console.log(`✅ Read ${content.length} characters from ${path.basename(filePath)}`);
      
      return {
        success: true,
        content,
        path: filePath,
      };
    } catch (error) {
      console.error(`❌ Read failed: ${error.message}`);
      
      return {
        success: false,
        error: error.message,
        path: filePath,
      };
    }
  }

  /**
   * Write file content
   */
  async writeFile(filePath, content) {
    console.log(`✍️  Writing file: ${filePath}`);
    
    try {
      const validPath = this._validatePath(filePath);
      
      // Ensure directory exists
      await fs.mkdir(path.dirname(validPath), { recursive: true });
      
      // Write file
      await fs.writeFile(validPath, content, 'utf-8');
      
      console.log(`✅ Wrote ${content.length} characters to ${path.basename(filePath)}`);
      
      return {
        success: true,
        path: filePath,
        size: content.length,
      };
    } catch (error) {
      console.error(`❌ Write failed: ${error.message}`);
      
      return {
        success: false,
        error: error.message,
        path: filePath,
      };
    }
  }

  /**
   * List directory contents
   */
  /**
   * List directory contents
   */
  async listFiles(dirPath = '') {
    // FIX: Do not join with workspaceRoot here. 
    // Pass the relative path directly to _validatePath.
    console.log(`📂 Listing directory: ${dirPath || 'root'}`);
    
    try {
      // _validatePath will handle the resolution against workspaceRoot
      const validPath = this._validatePath(dirPath); 
      
      const entries = await fs.readdir(validPath, { withFileTypes: true });
      
      const files = await Promise.all(
        entries.map(async (entry) => {
          const entryPath = path.join(validPath, entry.name);
          const stats = await fs.stat(entryPath);
          
          return {
            name: entry.name,
            path: path.relative(this.workspaceRoot, entryPath),
            type: entry.isDirectory() ? 'directory' : 'file',
            size: stats.size,
            modified: stats.mtime,
          };
        })
      );
      
      console.log(`✅ Found ${files.length} items in ${dirPath || 'root'}`);
      
      return {
        success: true,
        files,
        path: dirPath,
      };
    } catch (error) {
      console.error(`❌ List failed: ${error.message}`);
      
      return {
        success: false,
        error: error.message,
        path: dirPath,
      };
    }
  }
  /**
   * Create directory
   */
  async createDirectory(dirPath) {
    console.log(`📁 Creating directory: ${dirPath}`);
    
    try {
      const validPath = this._validatePath(dirPath);
      await fs.mkdir(validPath, { recursive: true });
      
      console.log(`✅ Directory created: ${path.basename(dirPath)}`);
      
      return {
        success: true,
        path: dirPath,
      };
    } catch (error) {
      console.error(`❌ mkdir failed: ${error.message}`);
      
      return {
        success: false,
        error: error.message,
        path: dirPath,
      };
    }
  }

  /**
   * Delete file or directory
   */
  async deleteFile(filePath) {
    console.log(`🗑️  Deleting: ${filePath}`);
    
    try {
      const validPath = this._validatePath(filePath);
      const stats = await fs.stat(validPath);
      
      if (stats.isDirectory()) {
        await fs.rm(validPath, { recursive: true });
      } else {
        await fs.unlink(validPath);
      }
      
      console.log(`✅ Deleted: ${path.basename(filePath)}`);
      
      return {
        success: true,
        path: filePath,
      };
    } catch (error) {
      console.error(`❌ Delete failed: ${error.message}`);
      
      return {
        success: false,
        error: error.message,
        path: filePath,
      };
    }
  }
}