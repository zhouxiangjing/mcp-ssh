"""工具：SFTP 文件上传与下载。"""

import os
from typing import Optional

from src.common.connection import SSHConnectionManager
from src.common.server import mcp


@mcp.tool()
async def upload_file(
    local_path: str,
    remote_path: str,
    host_name: Optional[str] = None,
) -> str:
    """Upload a local file to the remote server via SFTP.

    Args:
        local_path: Absolute local file path (on the machine running this MCP server).
        remote_path: Destination absolute path on the remote server.
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Success message with transferred file size, or error details.
    """
    try:
        local_path = os.path.expanduser(local_path)
        if not os.path.isfile(local_path):
            return f"Error: local file not found: '{local_path}'"
        file_size = os.path.getsize(local_path)
        client = SSHConnectionManager.get_connection(host_name)
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_path)
            return f"Uploaded '{local_path}' → '{remote_path}' ({file_size:,} bytes)"
        finally:
            sftp.close()
    except Exception as e:
        return f"Error uploading file: {e}"


@mcp.tool()
async def download_file(
    remote_path: str,
    local_path: str,
    host_name: Optional[str] = None,
) -> str:
    """Download a file from the remote server to local via SFTP.

    Args:
        remote_path: Absolute file path on the remote server.
        local_path: Destination absolute local path (on the machine running this MCP server).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Success message with transferred file size, or error details.
    """
    try:
        local_path = os.path.expanduser(local_path)
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        client = SSHConnectionManager.get_connection(host_name)
        sftp = client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
            file_size = os.path.getsize(local_path)
            return f"Downloaded '{remote_path}' → '{local_path}' ({file_size:,} bytes)"
        finally:
            sftp.close()
    except Exception as e:
        return f"Error downloading file: {e}"


@mcp.tool()
async def get_file_info(
    path: str,
    host_name: Optional[str] = None,
) -> str:
    """Get detailed metadata of a remote file or directory.

    Args:
        path: Absolute path on the remote server.
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        File metadata: size, permissions, owner, modification time.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        sftp = client.open_sftp()
        try:
            attr = sftp.stat(path)
            import stat as stat_module
            mode = stat_module.filemode(attr.st_mode)
            from datetime import datetime
            mtime = datetime.fromtimestamp(attr.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            return (
                f"Path:        {path}\n"
                f"Type:        {'directory' if stat_module.S_ISDIR(attr.st_mode) else 'file'}\n"
                f"Size:        {attr.st_size:,} bytes\n"
                f"Permissions: {mode}\n"
                f"UID/GID:     {attr.st_uid}/{attr.st_gid}\n"
                f"Modified:    {mtime}"
            )
        finally:
            sftp.close()
    except Exception as e:
        return f"Error getting file info for '{path}': {e}"
