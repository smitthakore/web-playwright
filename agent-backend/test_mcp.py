"""
Test Python MCP Client connection (Direct Integration)
"""

import asyncio
from src.utils.mcp_client_manager import MCPClientManager
from src.tools.filesystem_mcp import FilesystemMCP
from src.tools.playwright_mcp import PlaywrightMCP


async def test_mcp_operations():
    print("="*80)
    print("Testing internal Python MCP Client Manager")
    print("="*80)
    
    # Initialize Manager
    manager = MCPClientManager()
    
    try:
        # Initialize Tools
        print("\n0️⃣  Initializing Tools...")
        fs = FilesystemMCP(manager)
        pw = PlaywrightMCP(manager)
        
        # Test 1: Write a file
        print("\n1️⃣  TEST: Write file")
        success = await fs.write_file(
            "workspace/hello.py",
            'print("Hello from Python MCP Client!")'
        )
        print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        # Test 2: Read the file back
        print("\n2️⃣  TEST: Read file")
        content = await fs.read_file("workspace/hello.py")
        if content:
            print(f"   Result: ✅ SUCCESS")
            print(f"   Content: {content[:50]}...")
        else:
            print(f"   Result: ❌ FAILED")
        
        # Test 3: List files
        print("\n3️⃣  TEST: List files")
        files = await fs.list_files("")
        print(f"   Result: ✅ Found items")
        for file in files[:3]: 
            print(f"   - {file.get('name', 'unknown')}")
            
        # Test 4: Playwright Navigation (Headless)
        print("\n4️⃣  TEST: Playwright Navigate (Headless)")
        # Note: This might fail if playwright-mcp server isn't installed/setup correctly in environment
        # But we assume the npx command works.
        try:
            success = await pw.navigate("https://example.com")
            print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
            if success:
                print("\n5️⃣  TEST: Playwright Screenshot")
                # This returns the screenshot data/result
                result = await pw.screenshot()
                if result and result.get("success"):
                     print(f"   Result: ✅ SUCCESS (screenshot taken)")
                else:
                     print(f"   Result: ❌ FAILED")

        except Exception as e:
            print(f"   Result: ❌ FAILED (Playwright error: {e})")

    finally:
        # Cleanup
        print("\n" + "="*80)
        print("Cleaning up connections...")
        await manager.disconnect_all()
        print("✅ Done")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(test_mcp_operations())
