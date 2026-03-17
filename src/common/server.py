import importlib
import pkgutil

from mcp.server.fastmcp import FastMCP


def load_tools() -> None:
    import src.tools as tools_pkg

    for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
        importlib.import_module(f"src.tools.{module_name}")


mcp = FastMCP(
    "SSH MCP Server",
    dependencies=["paramiko", "python-dotenv"],
)

load_tools()
