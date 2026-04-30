#!/usr/bin/env python3
"""Test script to verify MCP server imports correctly."""

import asyncio
import sys


def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    
    # Test package import
    from mcp_server_emergence import app, main
    print("✓ Package imports successful")
    
    # Test server module
    from mcp_server_emergence.server import (
        _api_get,
        _api_post,
        _headers,
        call_tool,
        list_tools,
    )
    print("✓ Server module imports successful")
    
    # Test that server app is properly initialized
    from mcp.server import Server
    assert isinstance(app, Server), "app should be a Server instance"
    print("✓ MCP Server initialized correctly")
    
    return True


def test_tools_registration():
    """Test that tools are registered."""
    from mcp_server_emergence.server import list_tools
    
    async def check_tools():
        tools = await list_tools()
        tool_names = [t.name for t in tools]
        expected_tools = [
            "list_bounties",
            "get_bounty", 
            "post_bounty",
            "verify_task",
            "submit_task",
            "get_domains",
        ]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Tool '{tool}' not found in registered tools"
            print(f"  ✓ Tool '{tool}' registered")
        
        return True
    
    return asyncio.run(check_tools())


def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Server Emergence - Test Suite")
    print("=" * 60)
    
    try:
        if test_imports():
            print("\n✓ All imports successful")
        
        print("\nTesting tool registration...")
        if test_tools_registration():
            print("\n✓ All tools registered correctly")
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        return 0
    
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
