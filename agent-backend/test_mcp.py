"""
Test Python MCP Client connection to Node.js MCP Gateway
"""

import asyncio
from src.tools.filesystem_mcp import FilesystemMCP


async def test_mcp_operations():
    print("="*80)
    print("Testing Python → MCP Gateway Connection")
    print("="*80)
    
    # Initialize MCP client
    mcp = FilesystemMCP(gateway_url="http://localhost:3001")
    
    # Test 1: Write a file
    print("\n1️⃣  TEST: Write file")
    success = await mcp.write_file(
        "python_test/hello.py",
        'print("Hello from Python MCP Client!")'
    )
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test 2: Read the file back
    print("\n2️⃣  TEST: Read file")
    content = await mcp.read_file("python_test/hello.py")
    if content:
        print(f"   Result: ✅ SUCCESS")
        print(f"   Content: {content[:50]}...")
    else:
        print(f"   Result: ❌ FAILED")
    
    # Test 3: List files
    print("\n3️⃣  TEST: List files")
    files = await mcp.list_files("")
    print(f"   Result: ✅ Found {len(files)} items")
    for file in files[:3]:  # Show first 3
        print(f"   - {file['name']} ({file['type']})")
    
    # Test 4: Create directory
    print("\n4️⃣  TEST: Create directory")
    success = await mcp.create_directory("python_test/pages")
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test 5: Write a POM file
    print("\n5️⃣  TEST: Write POM file")
    pom_code = """class LoginPage:
    def __init__(self, page):
        self.page = page
    
    async def login(self, username, password):
        await self.page.fill("#username", username)
        await self.page.fill("#password", password)
        await self.page.click("#login-button")
"""
    success = await mcp.write_file("python_test/pages/login_page.py", pom_code)
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Test 6: List the pages directory
    print("\n6️⃣  TEST: List pages directory")
    files = await mcp.list_files("python_test/pages")
    print(f"   Result: ✅ Found {len(files)} items")
    for file in files:
        print(f"   - {file['name']} ({file['size']} bytes)")
    
    print("\n" + "="*80)
    print("✅ All Python MCP Client Tests Complete")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(test_mcp_operations())