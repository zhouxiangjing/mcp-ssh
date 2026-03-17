"""工具：系统信息采集与分析。"""

from typing import Optional

from src.common.connection import SSHConnectionManager
from src.common.server import mcp
from src.common.utils import run_command as _run


@mcp.tool()
async def get_system_overview(host_name: Optional[str] = None) -> str:
    """Get a comprehensive system overview of the remote server.

    Collects hostname, OS release, kernel, uptime, CPU, memory, disk, and
    load average in one call. Best starting point for system analysis.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Formatted system overview report.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        sections = {}

        sections["Hostname"] = await _run(client, "hostname -f 2>/dev/null || hostname")
        sections["OS Release"] = await _run(client, "cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null || uname -a")
        sections["Kernel"] = await _run(client, "uname -r")
        sections["Uptime"] = await _run(client, "uptime")
        sections["Load Average"] = await _run(client, "cat /proc/loadavg")
        sections["CPU Info"] = await _run(client, "lscpu | grep -E 'Architecture|CPU\\(s\\)|Model name|CPU MHz'")
        sections["Memory"] = await _run(client, "free -h")
        sections["Disk Usage"] = await _run(client, "df -h --total 2>/dev/null | grep -v tmpfs | grep -v devtmpfs")
        sections["Network Interfaces"] = await _run(client, "ip -brief addr show 2>/dev/null || ifconfig -s 2>/dev/null")

        lines = []
        for title, content in sections.items():
            lines.append(f"=== {title} ===")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        return f"Error getting system overview: {e}"


@mcp.tool()
async def get_cpu_info(host_name: Optional[str] = None) -> str:
    """Get detailed CPU usage and statistics.

    Returns current CPU load, per-core usage, and top CPU-consuming processes.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        CPU usage report.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, "top -bn1 | head -20 && echo '---' && mpstat 1 1 2>/dev/null || vmstat 1 2")
        return out
    except Exception as e:
        return f"Error getting CPU info: {e}"


@mcp.tool()
async def get_memory_info(host_name: Optional[str] = None) -> str:
    """Get memory and swap usage details.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Memory usage report including free, used, cached, and swap.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, "free -h && echo '' && cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree|Cached|Buffers'")
        return out
    except Exception as e:
        return f"Error getting memory info: {e}"


@mcp.tool()
async def get_disk_info(host_name: Optional[str] = None) -> str:
    """Get disk usage and I/O statistics.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Disk usage per filesystem and I/O stats.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        df = await _run(client, "df -h")
        io = await _run(client, "iostat -x 1 1 2>/dev/null || cat /proc/diskstats | head -20")
        inode = await _run(client, "df -i | grep -v tmpfs")
        return f"=== Disk Usage ===\n{df}\n\n=== Inode Usage ===\n{inode}\n\n=== I/O Stats ===\n{io}"
    except Exception as e:
        return f"Error getting disk info: {e}"


@mcp.tool()
async def get_network_info(host_name: Optional[str] = None) -> str:
    """Get network interface status, connections, and statistics.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Network interfaces, active connections, and routing table.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        ifaces = await _run(client, "ip addr show 2>/dev/null || ifconfig -a")
        routes = await _run(client, "ip route show 2>/dev/null || route -n")
        conns = await _run(client, "ss -tunap 2>/dev/null || netstat -tunap 2>/dev/null | head -40")
        return f"=== Interfaces ===\n{ifaces}\n\n=== Routes ===\n{routes}\n\n=== Active Connections ===\n{conns}"
    except Exception as e:
        return f"Error getting network info: {e}"


@mcp.tool()
async def get_system_logs(
    lines: int = 100,
    unit: Optional[str] = None,
    host_name: Optional[str] = None,
) -> str:
    """Retrieve system logs from journald or /var/log/syslog.

    Args:
        lines: Number of recent log lines to retrieve (default 100).
        unit: Optional systemd service name to filter logs (e.g., "nginx", "sshd").
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Recent system log entries.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        if unit:
            cmd = f"journalctl -u {unit} -n {lines} --no-pager 2>/dev/null || grep '{unit}' /var/log/syslog 2>/dev/null | tail -{lines}"
        else:
            cmd = f"journalctl -n {lines} --no-pager 2>/dev/null || tail -{lines} /var/log/syslog 2>/dev/null || tail -{lines} /var/log/messages 2>/dev/null"
        return await _run(client, cmd)
    except Exception as e:
        return f"Error getting system logs: {e}"


@mcp.tool()
async def check_service_status(
    service: str,
    host_name: Optional[str] = None,
) -> str:
    """Check the status of a systemd service.

    Args:
        service: Service name (e.g., "nginx", "mysql", "docker").
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Service status including active state, PID, and recent logs.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, f"systemctl status {service} --no-pager -l 2>/dev/null || service {service} status 2>/dev/null")
        return out
    except Exception as e:
        return f"Error checking service '{service}': {e}"


@mcp.tool()
async def manage_service(
    service: str,
    action: str,
    host_name: Optional[str] = None,
) -> str:
    """Start, stop, restart, or reload a systemd service.

    Args:
        service: Service name (e.g., "nginx", "mysql", "docker").
        action: Action to perform: "start", "stop", "restart", "reload", "enable", "disable".
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Result of the service management action.
    """
    allowed = {"start", "stop", "restart", "reload", "enable", "disable"}
    if action not in allowed:
        return f"Error: action must be one of {sorted(allowed)}"
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, f"systemctl {action} {service} 2>&1 && echo 'OK: {service} {action} succeeded'")
        return out
    except Exception as e:
        return f"Error managing service '{service}': {e}"
