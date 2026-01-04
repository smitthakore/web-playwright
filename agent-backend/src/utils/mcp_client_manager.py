"""
MCP Client Manager

Manages connections to multiple MCP servers using the official MCP SDK.
Uses StdioServerParameters for proper stdio transport communication.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration for an MCP server.
    
    Attributes:
        name: Unique identifier for the server
        command: Executable command to spawn the server
        args: Command line arguments
        env: Environment variables (defaults to current environment)
        capabilities: MCP capabilities the server supports
    """
    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] | None = None
    capabilities: dict[str, bool] = field(default_factory=dict)
    
    def to_stdio_params(self) -> StdioServerParameters:
        """Convert to MCP SDK's StdioServerParameters."""
        return StdioServerParameters(
            command=self.command,
            args=self.args,
            env=self.env,
        )


@dataclass
class ServerConnection:
    """Active connection state for an MCP server."""
    config: ServerConfig
    session: ClientSession
    read_stream: Any
    write_stream: Any
    _exit_stack: AsyncExitStack
    _cleanup_task: asyncio.Task | None = None


class MCPClientManager:
    """Manages connections to multiple MCP servers using official MCP SDK.
    
    This class provides a high-level interface for:
    - Connecting to MCP servers via stdio transport
    - Listing available tools from connected servers
    - Calling tools on connected servers
    - Managing server lifecycle (connect/disconnect)
    
    Example:
        manager = MCPClientManager()
        await manager.connect_server(filesystem_config)
        tools = await manager.list_tools("filesystem")
        result = await manager.call_tool("filesystem", "read_file", {"path": "test.txt"})
        await manager.disconnect_all()
    """
    
    def __init__(self) -> None:
        self._connections: dict[str, ServerConnection] = {}
        self._connection_locks: dict[str, asyncio.Lock] = {}
        logger.info("MANAGER: MCPClientManager initialized")
    
    def _get_lock(self, name: str) -> asyncio.Lock:
        """Get or create a lock for a server connection."""
        if name not in self._connection_locks:
            self._connection_locks[name] = asyncio.Lock()
        return self._connection_locks[name]
    
    async def connect_server(self, config: ServerConfig) -> dict[str, Any]:
        """Connect to an MCP server.
        
        Args:
            config: Server configuration with command and arguments
            
        Returns:
            Dict with 'success' key and optional 'error' or 'message'
        """
        async with self._get_lock(config.name):
            if config.name in self._connections:
                logger.warning(f"ALREADY CONNECTED: Server {config.name} already connected")
                return {"success": True, "message": "Already connected"}
            
            logger.info(f"CONNECTING: Connecting to MCP server: {config.name}")
            logger.info(f"   Command: {config.command} {' '.join(config.args)}")
            
            # Coordination events
            stop_event = asyncio.Event()
            session_ready_event = asyncio.Event()
            session_future: asyncio.Future[ClientSession] = asyncio.Future()
            
            async def _server_loop():
                try:
                    server_params = config.to_stdio_params()
                    
                    async with stdio_client(server_params) as (read_stream, write_stream):
                        async with ClientSession(read_stream, write_stream) as session:
                            await session.initialize()
                            
                            # Signal readiness
                            if not session_future.done():
                                session_future.set_result(session)
                            session_ready_event.set()
                            
                            # Keep alive until stopped
                            await stop_event.wait()
                            
                except Exception as e:
                    logger.error(f"FAILURE: Server loop error for {config.name}: {e}")
                    if not session_future.done():
                        session_future.set_exception(e)
                    session_ready_event.set() # Unblock waiter
            
            # Start background task
            task = asyncio.create_task(_server_loop())
            
            # Wait for connection
            await session_ready_event.wait()
            
            try:
                # Check if we got a session or an exception
                session = await session_future
                
                self._connections[config.name] = ServerConnection(
                    config=config,
                    session=session,
                    read_stream=None, # Not accessible here, managed in loop
                    write_stream=None,
                    _exit_stack=None, # Not used in this pattern
                    _cleanup_task=task, # Reuse this field for the loop task
                )
                # We hackily attach the stop event to the connection object to access it later
                # ideally ServerConnection dataclass should be updated, but python is dynamic
                self._connections[config.name].stop_event = stop_event
                
                logger.info(f"CONNECTED: Connected to MCP server: {config.name}")
                return {"success": True}
                
            except Exception as e:
                return {"success": False, "error": str(e)}

    async def disconnect_server(self, name: str) -> dict[str, Any]:
        """Disconnect from an MCP server.
        
        Args:
            name: Server name to disconnect
            
        Returns:
            Dict with 'success' key and optional 'error'
        """
        async with self._get_lock(name):
            if name not in self._connections:
                return {"success": False, "error": "Server not connected"}
            
            logger.info(f"DISCONNECTING: Disconnecting from MCP server: {name}")
            
            conn = self._connections[name]
            
            try:
                # Signal the loop to stop if we attached the event
                if hasattr(conn, "stop_event"):
                    conn.stop_event.set()
                
                # Wait for the task to finish
                if conn._cleanup_task:
                    try:
                        await asyncio.wait_for(conn._cleanup_task, timeout=5.0)
                    except asyncio.TimeoutError:
                        logger.warning(f"TIMEOUT: Server {name} loop did not exit cleanly, cancelling")
                        conn._cleanup_task.cancel()
                        try:
                            await conn._cleanup_task
                        except asyncio.CancelledError:
                            pass
                
                del self._connections[name]
                logger.info(f"DISCONNECTED: Disconnected from {name}")
                return {"success": True}
                
            except Exception as e:
                logger.error(f"ERROR: Error disconnecting {name}: {e}")
                self._connections.pop(name, None)
                return {"success": False, "error": str(e)}
    
    async def list_tools(self, server_name: str) -> dict[str, Any]:
        """List available tools from a connected server.
        
        Args:
            server_name: Name of the connected server
            
        Returns:
            Dict with 'success', 'tools' list, or 'error'
        """
        if server_name not in self._connections:
            return {"success": False, "error": f"Server {server_name} not connected"}
        
        conn = self._connections[server_name]
        logger.info(f"LISTING: Listing tools from {server_name}...")
        
        try:
            response = await conn.session.list_tools()
            logger.info(f"DEBUG: list_tools response: {response}")
            tools = [
                {
                    "name": tool.name,
                    "description": getattr(tool, "description", ""),
                    "inputSchema": getattr(tool, "inputSchema", {}),
                }
                for tool in response.tools
            ]
            
            logger.info(f"Found {len(tools)} tools in {server_name}")
            return {"success": True, "tools": tools}
            
        except Exception as e:
            logger.error(f"Failed to list tools from {server_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a tool on a connected server.
        
        Args:
            server_name: Name of the connected server
            tool_name: Name of the tool to call
            args: Arguments to pass to the tool
            
        Returns:
            Dict with 'success', 'content', 'isError', or 'error'
        """
        if server_name not in self._connections:
            return {"success": False, "error": f"Server {server_name} not connected"}
        
        conn = self._connections[server_name]
        args = args or {}
        
        logger.info(f"CALLING: Calling tool {tool_name} on {server_name}")
        logger.debug(f"   Args: {str(args)[:200]}")
        
        try:
            response = await conn.session.call_tool(tool_name, arguments=args)
            
            # Extract content from response
            content = []
            for item in response.content:
                if hasattr(item, "text"):
                    content.append({"type": "text", "text": item.text})
                elif hasattr(item, "data"):
                    content.append({"type": "image", "data": item.data, "mimeType": getattr(item, "mimeType", "image/png")})
                else:
                    content.append({"type": "unknown", "raw": str(item)})
            
            is_error = getattr(response, "isError", False)
            
            if is_error:
                error_msg = str(content)
                logger.error(f"FAILED: Tool {tool_name} failed on {server_name}: {error_msg}")
            else:
                logger.info(f"COMPLETED: Tool {tool_name} completed on {server_name}")
            
            return {
                "success": not is_error,
                "content": content,
                "isError": is_error,
            }
            
        except Exception as e:
            logger.error(f"FAILED: Tool {tool_name} failed on {server_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_connected_servers(self) -> list[str]:
        """Get list of connected server names."""
        return list(self._connections.keys())
    
    def is_server_connected(self, server_name: str) -> bool:
        """Check if a server is connected."""
        return server_name in self._connections
    
    async def disconnect_all(self) -> None:
        """Disconnect all connected servers."""
        logger.info("STOPPING: Disconnecting all MCP servers...")
        
        server_names = list(self._connections.keys())
        for name in server_names:
            await self.disconnect_server(name)
        
        logger.info("STOPPED: All MCP servers disconnected")
    
    async def get_langchain_tools(self) -> list[Any]:
        """
        Get LangChain-compatible tools from all connected servers.
        Requires langchain-mcp-adapters package.
        """
        from langchain_mcp_adapters.tools import load_mcp_tools
        
        all_tools = []
        for name, conn in self._connections.items():
            try:
                # load_mcp_tools expects a session
                tools = await load_mcp_tools(conn.session)
                logger.info(f"Loaded {len(tools)} LangChain tools from {name}")
                all_tools.extend(tools)
            except Exception as e:
                logger.error(f"Failed to load LangChain tools from {name}: {e}")
                
        return all_tools

    async def __aenter__(self) -> "MCPClientManager":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - disconnects all servers."""
        await self.disconnect_all()
