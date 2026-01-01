"""
Filesystem MCP Client - Python wrapper for Node.js MCP server
"""

import httpx
import os
from typing import List, Dict, Optional
from ..utils.logger import agent_logger


class FilesystemMCP:
    """
    Client for interacting with Filesystem MCP server via HTTP gateway
    """
    
    def __init__(self, gateway_url: str = "http://localhost:3001"):
        self.gateway_url = gateway_url
        self.workspace_root = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "..",
            "workspace",
            "projects"
        )
        agent_logger.info(f"FilesystemMCP initialized | Gateway: {gateway_url}")
        agent_logger.info(f"Workspace root: {self.workspace_root}")
    
    async def read_file(self, path: str) -> Optional[str]:
        """
        Read file content from workspace
        
        Args:
            path: Relative path from workspace root (e.g., "project_001/pages/login.py")
            
        Returns:
            File content as string, or None if not found
        """
        
        agent_logger.tool_call("filesystem_mcp.read_file", {"path": path})
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.gateway_url}/mcp/read",
                    json={"path": path} 
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "")
                    agent_logger.tool_result(
                        "filesystem_mcp.read_file",
                        True,
                        f"Read {len(content)} characters"
                    )
                    return content
                else:
                    agent_logger.tool_result(
                        "filesystem_mcp.read_file",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    return None
                    
        except Exception as e:
            agent_logger.error("filesystem_mcp.read_file", e)
            return None
    
    async def write_file(self, path: str, content: str) -> bool:
        """
        Write file to workspace
        
        Args:
            path: Relative path from workspace root
            content: File content
            
        Returns:
            True if successful, False otherwise
        """
        
        agent_logger.tool_call("filesystem_mcp.write_file", {
            "path": path,
            "size": f"{len(content)} chars"
        })
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.gateway_url}/mcp/write",
                    json={
                        "path": path,
                        "content": content
                    }
                )
                
                success = response.status_code == 200
                agent_logger.tool_result(
                    "filesystem_mcp.write_file",
                    success,
                    f"Wrote to {path}"
                )
                return success
                
        except Exception as e:
            agent_logger.error("filesystem_mcp.write_file", e)
            return False
    
    async def list_files(self, path: str = "") -> List[Dict[str, str]]:
        """
        List files in directory
        
        Args:
            path: Relative path from workspace root
            
        Returns:
            List of file metadata dicts
        """
        
        agent_logger.tool_call("filesystem_mcp.list_files", {"path": path})
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.gateway_url}/mcp/list",
                    # FIX: Send 'path' (relative), not 'full_path'
                    json={"path": path} 
                )
                
                if response.status_code == 200:
                    data = response.json()
                    files = data.get("files", [])
                    agent_logger.tool_result(
                        "filesystem_mcp.list_files",
                        True,
                        f"Found {len(files)} items"
                    )
                    return files
                else:
                    agent_logger.tool_result(
                        "filesystem_mcp.list_files",
                        False,
                        f"HTTP {response.status_code}"
                    )
                    return []
                    
        except Exception as e:
            agent_logger.error("filesystem_mcp.list_files", e)
            return []
    
    async def create_directory(self, path: str) -> bool:
        """
        Create directory in workspace
        
        Args:
            path: Relative path from workspace root
            
        Returns:
            True if successful
        """
        
        agent_logger.tool_call("filesystem_mcp.create_directory", {"path": path})
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.gateway_url}/mcp/mkdir",
                    json={"path": path}
                )
                
                success = response.status_code == 200
                agent_logger.tool_result(
                    "filesystem_mcp.create_directory",
                    success,
                    f"Created {path}"
                )
                return success
                
        except Exception as e:
            agent_logger.error("filesystem_mcp.create_directory", e)
            return False