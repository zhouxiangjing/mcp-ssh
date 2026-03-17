"""工具：进程管理与分析。"""

from typing import Optional

from src.common.connection import SSHConnectionManager
from src.common.server import mcp
from src.common.utils import run_command as _run


@mcp.tool()
async def list_processes(
    sort_by: str = "cpu",
    limit: int = 20,
    host_name: Optional[str] = None,
) -> str:
    """List running processes sorted by resource usage.

    Args:
        sort_by: Sort field: "cpu" (default), "mem", or "pid".
        limit: Number of processes to show (default 20).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Process list with PID, user, CPU%, MEM%, and command.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        sort_flags = {
            "cpu": "--sort=-%cpu",
            "mem": "--sort=-%mem",
            "pid": "--sort=pid",
        }
        flag = sort_flags.get(sort_by, "--sort=-%cpu")
        cmd = f"ps aux {flag} | head -{limit + 1}"
        return await _run(client, cmd)
    except Exception as e:
        return f"Error listing processes: {e}"


@mcp.tool()
async def find_process(
    name: str,
    host_name: Optional[str] = None,
) -> str:
    """Search for processes by name or keyword.

    Args:
        name: Process name or keyword to search (e.g., "nginx", "python").
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Matching processes with their PIDs and details.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, f"ps aux | grep -i '{name}' | grep -v grep")
        if not out:
            return f"No processes found matching '{name}'"
        return out
    except Exception as e:
        return f"Error finding process '{name}': {e}"


@mcp.tool()
async def kill_process(
    pid: int,
    signal: str = "TERM",
    host_name: Optional[str] = None,
) -> str:
    """Send a signal to a process by PID.

    Args:
        pid: Process ID to signal.
        signal: Signal name: "TERM" (graceful, default), "KILL" (force), "HUP" (reload).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Result of the kill command.
    """
    allowed = {"TERM", "KILL", "HUP", "USR1", "USR2", "INT", "QUIT"}
    if signal not in allowed:
        return f"Error: signal must be one of {sorted(allowed)}"
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, f"kill -s {signal} {pid} 2>&1 && echo 'Signal {signal} sent to PID {pid}'")
        return out
    except Exception as e:
        return f"Error killing process {pid}: {e}"


@mcp.tool()
async def get_open_ports(host_name: Optional[str] = None) -> str:
    """List all open listening ports and their associated processes.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Listening ports with protocol, port number, and process name.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
        return out
    except Exception as e:
        return f"Error getting open ports: {e}"
