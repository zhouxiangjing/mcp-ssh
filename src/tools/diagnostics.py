"""工具：系统诊断与问题排查。"""

from typing import Optional

from src.common.connection import SSHConnectionManager
from src.common.server import mcp
from src.common.utils import run_command as _run


@mcp.tool()
async def check_disk_health(host_name: Optional[str] = None) -> str:
    """Check disk health using SMART data and filesystem errors.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Disk health status and any detected errors.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        # dmesg for disk errors
        dmesg = await _run(client, "dmesg | grep -iE 'error|fail|bad sector|ata|scsi|nvme' | tail -30 2>/dev/null")
        # failed mounts or filesystem errors
        fstab = await _run(client, "systemctl --failed 2>/dev/null | head -20")
        # inode usage
        inode = await _run(client, "df -i | awk 'NR==1 || $5+0 > 80' 2>/dev/null")
        return f"=== Kernel Disk Messages ===\n{dmesg or '(none)'}\n\n=== Failed Units ===\n{fstab or '(none)'}\n\n=== High Inode Usage (>80%) ===\n{inode or '(none)'}"
    except Exception as e:
        return f"Error checking disk health: {e}"


@mcp.tool()
async def check_high_load(host_name: Optional[str] = None) -> str:
    """Diagnose high CPU/memory load and identify resource hogs.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Top resource consumers and system load details.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        load = await _run(client, "uptime && echo '' && cat /proc/loadavg")
        top_cpu = await _run(client, "ps aux --sort=-%cpu | head -11")
        top_mem = await _run(client, "ps aux --sort=-%mem | head -11")
        oom = await _run(client, "dmesg | grep -i 'oom\\|out of memory' | tail -10 2>/dev/null")
        return (
            f"=== Load ===\n{load}\n\n"
            f"=== Top CPU Processes ===\n{top_cpu}\n\n"
            f"=== Top Memory Processes ===\n{top_mem}\n\n"
            f"=== OOM Events ===\n{oom or '(none)'}"
        )
    except Exception as e:
        return f"Error diagnosing high load: {e}"


@mcp.tool()
async def check_network_connectivity(
    target: str = "8.8.8.8",
    host_name: Optional[str] = None,
) -> str:
    """Test outbound network connectivity from the remote server.

    Args:
        target: IP or hostname to ping/reach (default "8.8.8.8").
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Ping results and DNS resolution status.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        ping = await _run(client, f"ping -c 4 -W 3 {target} 2>&1")
        dns = await _run(client, "cat /etc/resolv.conf")
        nslookup = await _run(client, f"nslookup {target} 2>/dev/null || dig {target} +short 2>/dev/null")
        return f"=== Ping {target} ===\n{ping}\n\n=== DNS Config ===\n{dns}\n\n=== DNS Lookup ===\n{nslookup}"
    except Exception as e:
        return f"Error checking network connectivity: {e}"


@mcp.tool()
async def check_security(host_name: Optional[str] = None) -> str:
    """Run a basic security audit of the remote server.

    Checks for: failed login attempts, listening ports, SUID files,
    world-writable directories, and recent auth log entries.

    Args:
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Security audit report.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        failed_logins = await _run(client, "grep 'Failed password\\|Invalid user' /var/log/auth.log /var/log/secure 2>/dev/null | tail -20")
        listening = await _run(client, "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
        suid = await _run(client, "find / -perm -4000 -type f 2>/dev/null | grep -v proc | head -20")
        world_write = await _run(client, "find /tmp /var/tmp /dev/shm -perm -0002 -type f 2>/dev/null | head -20")
        last_logins = await _run(client, "last -n 20 2>/dev/null")
        return (
            f"=== Failed Login Attempts (last 20) ===\n{failed_logins or '(none)'}\n\n"
            f"=== Listening Ports ===\n{listening}\n\n"
            f"=== SUID Binaries ===\n{suid or '(none)'}\n\n"
            f"=== World-Writable Files in /tmp ===\n{world_write or '(none)'}\n\n"
            f"=== Recent Logins ===\n{last_logins}"
        )
    except Exception as e:
        return f"Error running security audit: {e}"


@mcp.tool()
async def tail_log(
    path: str,
    lines: int = 50,
    host_name: Optional[str] = None,
) -> str:
    """Tail the end of a remote log file.

    Args:
        path: Absolute path to the log file (e.g., "/var/log/nginx/error.log").
        lines: Number of lines to retrieve from the end (default 50).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Last N lines of the log file.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, f"tail -{lines} '{path}' 2>&1")
        return out
    except Exception as e:
        return f"Error tailing log '{path}': {e}"


@mcp.tool()
async def analyze_log_errors(
    path: str,
    host_name: Optional[str] = None,
) -> str:
    """Analyze a log file for error patterns and summarize findings.

    Searches for ERROR, WARN, CRITICAL, Exception, and similar keywords.

    Args:
        path: Absolute path to the log file.
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Error/warning summary with counts and recent examples.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        counts = await _run(client, f"grep -cE 'ERROR|CRITICAL|FATAL|Exception|Traceback' '{path}' 2>/dev/null || echo 0")
        warn_counts = await _run(client, f"grep -cE 'WARN|WARNING' '{path}' 2>/dev/null || echo 0")
        recent_errors = await _run(client, f"grep -E 'ERROR|CRITICAL|FATAL|Exception|Traceback' '{path}' 2>/dev/null | tail -20")
        return (
            f"Log: {path}\n"
            f"Error/Critical count: {counts.strip()}\n"
            f"Warning count:        {warn_counts.strip()}\n\n"
            f"=== Recent Errors ===\n{recent_errors or '(none found)'}"
        )
    except Exception as e:
        return f"Error analyzing log '{path}': {e}"
