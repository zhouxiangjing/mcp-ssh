"""
Unit tests for src/common/server.py
"""

from mcp.server.fastmcp import FastMCP

from src.common.server import mcp


class TestMCPServer:
    def test_mcp_instance_exists(self):
        assert mcp is not None

    def test_mcp_is_fastmcp(self):
        assert isinstance(mcp, FastMCP)

    def test_mcp_has_tool_decorator(self):
        assert hasattr(mcp, "tool") and callable(mcp.tool)

    def test_mcp_has_run_method(self):
        assert hasattr(mcp, "run") and callable(mcp.run)

    def test_mcp_is_singleton(self):
        from src.common.server import mcp as mcp2
        assert mcp is mcp2

    def test_tool_decorator_registers_async_function(self):
        @mcp.tool()
        async def _test_tool(x: str) -> str:
            """Temporary test tool."""
            return x

        assert callable(_test_tool)
        assert _test_tool.__name__ == "_test_tool"
