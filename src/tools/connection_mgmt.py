"""工具：SSH 连接管理与多主机切换。"""

from typing import Optional

from src.common.config import SSH_CFG, SSH_HOSTS
from src.common.connection import SSHConnectionManager
from src.common.server import mcp


@mcp.tool()
async def test_connection(host_name: Optional[str] = None) -> str:
    """Test SSH connectivity to the target host.

    Verifies the connection is alive and returns basic server identity.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Connection status and remote hostname.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        _, stdout, _ = client.exec_command("hostname && whoami && uptime", timeout=10)
        out = stdout.read().decode("utf-8", errors="replace").strip()
        target = host_name or f"{SSH_CFG['username']}@{SSH_CFG['host']}:{SSH_CFG['port']}"
        return f"Connection OK → {target}\n{out}"
    except Exception as e:
        return f"Connection FAILED: {e}"


@mcp.tool()
async def list_configured_hosts() -> str:
    """List all SSH hosts configured in SSH_HOSTS_JSON.

    Returns:
        Table of configured host names and their connection details.
    """
    if not SSH_HOSTS:
        default = f"  default: {SSH_CFG['username']}@{SSH_CFG['host']}:{SSH_CFG['port']}"
        return f"No named hosts configured. Default host:\n{default}"

    lines = ["Configured SSH Hosts:", ""]
    for name, cfg in SSH_HOSTS.items():
        user = cfg.get("username", SSH_CFG["username"])
        host = cfg.get("host", "?")
        port = cfg.get("port", 22)
        auth = "key" if cfg.get("key_file") else "password"
        lines.append(f"  {name:20s}  {user}@{host}:{port}  [{auth}]")
    return "\n".join(lines)


@mcp.tool()
async def close_connection(host_name: Optional[str] = None) -> str:
    """Close the SSH connection to a host.

    The connection will be re-established automatically on the next tool call.

    Args:
        host_name: Named host to disconnect; disconnects default host if omitted.

    Returns:
        Confirmation message.
    """
    try:
        SSHConnectionManager.close_connection(host_name)
        target = host_name or "default"
        return f"Connection to '{target}' closed successfully."
    except Exception as e:
        return f"Error closing connection: {e}"


@mcp.tool()
async def close_all_connections() -> str:
    """Close all active SSH connections.

    Returns:
        Confirmation message.
    """
    try:
        SSHConnectionManager.close_all()
        return "All SSH connections closed."
    except Exception as e:
        return f"Error closing connections: {e}"
