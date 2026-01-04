"""
Playwright MCP Client - Internal Python MCP Integration
"""

import os
from typing import List, Dict, Optional, Any
from ..utils.logger import agent_logger
from ..utils.mcp_client_manager import MCPClientManager, ServerConfig

class PlaywrightMCP:
    """
    Client for interacting with Playwright MCP server via internal MCPClientManager
    """
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return list of tools exposed by this wrapper."""
        return [
            {"name": "playwright.navigate", "args": "url", "description": "Navigate browser to URL"},
            {"name": "playwright.extract_locator", "args": "None", "description": "Get page content to find selectors (USE THIS before clicking)"},
            {"name": "playwright.click", "args": "element", "description": "Click element matching selector"},
            {"name": "playwright.type", "args": "element, text", "description": "Type text into element"},
            {"name": "playwright.screenshot", "args": "None", "description": "Take page screenshot"},
        ]
    
    def __init__(self, manager: MCPClientManager):
        self.manager = manager
        self.server_name = "playwright"
        
        # Configure the playwright server
        # Use npx.cmd on Windows, npx on Unix
        command = "npx.cmd" if os.name == "nt" else "npx"
        
        # Use the official @playwright/mcp server
        self.config = ServerConfig(
            name=self.server_name,
            command=command,
            args=[
                "-y",
                "@playwright/mcp",
                "--caps", "testing",
                "--timeout-action", "10000",
                "--timeout-navigation", "30000"
            ],
            env=os.environ.copy(),
            capabilities={"tools": True},
        )
        
        agent_logger.info(f"PlaywrightMCP initialized")

    async def ensure_connected(self) -> bool:
        if self.manager.is_server_connected(self.server_name):
            return True
        result = await self.manager.connect_server(self.config)
        return result["success"]

    async def navigate(self, url: str) -> bool:
        return await self._call("browser_navigate", {"url": url})

    async def click(self, element: str) -> bool:
        return await self._call("browser_click", {"element": element})

    async def type(self, element: str, text: str) -> bool:
        return await self._call("browser_type", {"element": element, "text": text})

    async def screenshot(self) -> Dict[str, Any]:
        return await self._call("browser_take_screenshot", {})

    async def get_content(self) -> str:
        # Assuming there is a tool for this or we start with snapshot
        res = await self._call("browser_snapshot", {})
        # Parse result
        return str(res) # Placeholder

    async def extract_locator(self) -> str:
        """
        Get page content to extract locators.
        """
        # We use snapshot to get the accessibility tree or HTML
        # The agent will parse this.
        return await self.get_content()

    async def _call(self, tool_name: str, args: dict) -> Any:
        agent_logger.tool_call(f"playwright.{tool_name}", args)
        
        if not await self.ensure_connected():
            return False

        result = await self.manager.call_tool(self.server_name, tool_name, args)
        
        success = result["success"]
        agent_logger.tool_result(f"playwright.{tool_name}", success, "Success" if success else result.get("error"))
        return result
