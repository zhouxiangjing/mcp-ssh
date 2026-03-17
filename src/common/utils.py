"""共用工具函数。"""

import paramiko


async def run_command(client: paramiko.SSHClient, cmd: str, timeout: int = 30) -> str:
    """在远程主机执行命令并返回输出（stdout 优先，fallback stderr）。"""
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    return out if out else err
