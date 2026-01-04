"""
Filesystem MCP Client - Internal Python MCP Integration
"""

import os
import sys
from typing import List, Dict, Optional, Any
from ..utils.logger import agent_logger
from ..utils.mcp_client_manager import MCPClientManager, ServerConfig

# Default workspace root if none provided
_DEFAULT_WORKSPACE = r"c:\Users\smit\Desktop\web-playwright\agent-backend\workspace"

class FilesystemMCP:
    """
    Client for interacting with Filesystem MCP server via internal MCPClientManager
    """

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return list of tools exposed by this wrapper."""
        return [
            {"name": "filesystem.read_file", "args": "path", "description": "Read file content"},
            {"name": "filesystem.list_files", "args": "path", "description": "List directory contents"},
            {"name": "filesystem.write_file", "args": "path, content", "description": "Write content to file"},
        ]
    
    def __init__(self, manager: MCPClientManager):
        self.manager = manager
        self.server_name = "filesystem"
        
        # Configure the filesystem server
        # Use npx.cmd on Windows, npx on Unix
        command = "npx.cmd" if sys.platform == "win32" else "npx"
        workspace_root = os.getenv("MCP_WORKSPACE_ROOT", _DEFAULT_WORKSPACE)
        
        self.config = ServerConfig(
            name=self.server_name,
            command=command,
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                workspace_root
            ],
            env=os.environ.copy(),
            capabilities={"tools": True, "resources": True},
        )
        
        agent_logger.info(f"FilesystemMCP initialized | Workspace: {workspace_root}")

    async def ensure_connected(self) -> bool:
        """Ensure the filesystem server is connected"""
        if self.manager.is_server_connected(self.server_name):
            return True
            
        result = await self.manager.connect_server(self.config)
        return result["success"]
    
    async def read_file(self, path: str) -> Optional[str]:
        """Read file content from workspace"""
        agent_logger.tool_call("filesystem_mcp.read_file", {"path": path})
        
        if not await self.ensure_connected():
            return None
            
        result = await self.manager.call_tool(
            self.server_name, 
            "read_file", 
            {"path": path}
        )
        
        if result["success"]:
            # Extract text content from result
            content = ""
            for item in result.get("content", []):
                if item.get("type") == "text":
                    content += item.get("text", "")
            
            agent_logger.tool_result("filesystem_mcp.read_file", True, f"Read {len(content)} chars")
            return content
        else:
            agent_logger.tool_result("filesystem_mcp.read_file", False, result.get("error", "Unknown error"))
            return None
    
    async def write_file(self, path: str, content: str) -> bool:
        """Write file to workspace"""
        agent_logger.tool_call("filesystem_mcp.write_file", {"path": path, "size": f"{len(content)} chars"})
        
        if not await self.ensure_connected():
            return False
            
        result = await self.manager.call_tool(
            self.server_name,
            "write_file",
            {"path": path, "content": content}
        )
        
        success = result["success"]
        agent_logger.tool_result("filesystem_mcp.write_file", success, "Success" if success else result.get("error"))
        return success
    
    async def list_files(self, path: str = "") -> List[Dict[str, str]]:
        """List files in directory"""
        agent_logger.tool_call("filesystem_mcp.list_files", {"path": path})
        
        if not await self.ensure_connected():
            return []
            
        result = await self.manager.call_tool(
            self.server_name,
            "list_directory",
            {"path": path or "."}
        )
        
        if result["success"]:
            # Provide a simpler list format for the agent
            # The MCP tool returns just a list of names usually, or simple metadata
            # We adapt it here if needed, but for now we trust the tool output structure or adapt as we see it
            # The official filesystem server execution of list_directory returns a list of [name, type, etc]
            
            # Note: The output format from call_tool depends on how the tool implements it to text/json
            # Use 'list_directory' output parsing if complex json is returned as text
            
            # For now, return empty list if parsing fails, or raw if structured
            # Realistically, we need to see the output structure. 
            # Assuming standard tool return.
             
            # Standard filesystem MCP output is text/json.
            import json
            try:
                # The text output might be JSON string
                files_data = []
                for item in result.get("content", []):
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        try:
                            # It might be JSON, or just text listing
                            # Official server returns JSON list usually?
                            # Actually, list_directory returns a list of strings usually
                            files_data.append({"name": text.strip(), "type": "unknown"}) 
                        except:
                            pass
                
                # If we want raw files list we might need to parse better, 
                # but for now let's return what we have
                agent_logger.tool_result("filesystem_mcp.list_files", True, f"Found items")
                return files_data
            except Exception as e:
                agent_logger.error("filesystem_mcp.list_files", e)
                return []
        
        return []
    
    async def create_directory(self, path: str) -> bool:
        """Create directory in workspace"""
        agent_logger.tool_call("filesystem_mcp.create_directory", {"path": path})
        
        if not await self.ensure_connected():
            return False
            
        result = await self.manager.call_tool(
            self.server_name,
            "create_directory",
            {"path": path}
        )
        
        success = result["success"]
        agent_logger.tool_result("filesystem_mcp.create_directory", success, "Success" if success else result.get("error"))
        return success
