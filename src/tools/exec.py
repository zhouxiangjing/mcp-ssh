"""工具：在远程主机上执行 shell 命令。"""

from typing import Optional

from src.common.connection import SSHConnectionManager
from src.common.server import mcp


@mcp.tool()
async def execute_command(
    command: str,
    timeout: int = 60,
    host_name: Optional[str] = None,
) -> str:
    """Execute a shell command on the remote SSH server.

    Runs any shell command and returns stdout + stderr. Suitable for
    one-off commands, diagnostics, log tailing, service control, etc.

    Args:
        command: The shell command to execute (e.g., "df -h", "systemctl status nginx").
        timeout: Maximum seconds to wait for the command to finish (default 60).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Command output (stdout), or combined stdout/stderr on error.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()

        if err and exit_code != 0:
            return f"Exit code: {exit_code}\n\nSTDOUT:\n{out}\nSTDERR:\n{err}"
        if err:
            return f"{out}\n[stderr]: {err}"
        return out or f"(command completed with exit code {exit_code})"
    except Exception as e:
        return f"Error executing command '{command}': {e}"


@mcp.tool()
async def execute_script(
    script: str,
    shell: str = "bash",
    timeout: int = 120,
    host_name: Optional[str] = None,
) -> str:
    """Execute a multi-line shell script on the remote SSH server.

    Uploads the script via stdin and runs it with the specified shell.
    Useful for multi-step automation, configuration changes, or complex checks.

    Args:
        script: The full script content (multi-line bash/sh/python script).
        shell: Shell interpreter to use: "bash", "sh", "python3", etc. (default "bash").
        timeout: Maximum seconds to wait (default 120).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Script output or error details.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        stdin, stdout, stderr = client.exec_command(shell, timeout=timeout)
        stdin.write(script)
        stdin.channel.shutdown_write()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()

        if exit_code != 0:
            return f"Exit code: {exit_code}\n\nSTDOUT:\n{out}\nSTDERR:\n{err}"
        return out or f"(script completed with exit code {exit_code})"
    except Exception as e:
        return f"Error executing script: {e}"
