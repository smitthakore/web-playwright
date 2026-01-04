
import asyncio
from src.utils.mcp_client_manager import MCPClientManager
from src.tools.playwright_mcp import PlaywrightMCP
from src.tools.filesystem_mcp import FilesystemMCP

async def list_available_tools():
    manager = MCPClientManager()
    
    # Initialize wrappers which connects to servers
    fs = FilesystemMCP(manager)
    pw = PlaywrightMCP(manager)
    
    # Ensure connections
    print("Connecting...")
    await fs.ensure_connected()
    await pw.ensure_connected()
    
    with open("tools_list.txt", "w") as f:
        print("\n--- Filesystem Tools ---")
        f.write("\n--- Filesystem Tools ---\n")
        try:
            tools = await manager.list_tools("filesystem")
            for t in tools:
                msg = f"- {t.name}: {t.description[:50]}..."
                print(msg)
                f.write(msg + "\n")
        except Exception as e:
            print(f"Error listing filesystem tools: {e}")

        print("\n--- Playwright Tools ---")
        f.write("\n--- Playwright Tools ---\n")
        try:
            tools = await manager.list_tools("playwright")
            for t in tools:
                msg = f"- {t.name}: {t.description[:50]}..."
                print(msg)
                f.write(msg + "\n")
        except Exception as e:
            print(f"Error listing playwright tools: {e}")

    await manager.disconnect_all()

if __name__ == "__main__":
    asyncio.run(list_available_tools())
