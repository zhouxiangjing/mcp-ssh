"""工具：远程文件系统操作。"""

import stat
from typing import Optional

from src.common.connection import SSHConnectionManager
from src.common.server import mcp
from src.common.utils import run_command as _run


@mcp.tool()
async def read_file(
    path: str,
    max_lines: int = 200,
    host_name: Optional[str] = None,
) -> str:
    """Read the content of a remote file.

    Args:
        path: Absolute path to the file (e.g., "/etc/nginx/nginx.conf").
        max_lines: Maximum number of lines to return (default 200, 0 = unlimited).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        File content as text.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        if max_lines > 0:
            cmd = f"head -{max_lines} '{path}' 2>&1"
        else:
            cmd = f"cat '{path}' 2>&1"
        return await _run(client, cmd)
    except Exception as e:
        return f"Error reading file '{path}': {e}"


@mcp.tool()
async def write_file(
    path: str,
    content: str,
    host_name: Optional[str] = None,
) -> str:
    """Write content to a remote file (overwrites existing content).

    Creates parent directories if they do not exist.

    Args:
        path: Absolute path to the destination file.
        content: Text content to write.
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Success message or error details.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        sftp = client.open_sftp()
        try:
            # Ensure parent directory exists
            parent = path.rsplit("/", 1)[0]
            if parent:
                await _run(client, f"mkdir -p '{parent}'")
            with sftp.open(path, "w") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} bytes to '{path}'"
        finally:
            sftp.close()
    except Exception as e:
        return f"Error writing file '{path}': {e}"


@mcp.tool()
async def append_file(
    path: str,
    content: str,
    host_name: Optional[str] = None,
) -> str:
    """Append content to a remote file.

    Args:
        path: Absolute path to the file.
        content: Text content to append.
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Success message or error details.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        sftp = client.open_sftp()
        try:
            with sftp.open(path, "a") as f:
                f.write(content)
            return f"Successfully appended {len(content)} bytes to '{path}'"
        finally:
            sftp.close()
    except Exception as e:
        return f"Error appending to file '{path}': {e}"


@mcp.tool()
async def list_directory(
    path: str = "/",
    host_name: Optional[str] = None,
) -> str:
    """List files and directories at a remote path.

    Args:
        path: Directory path to list (default "/").
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Directory listing with permissions, size, and modification time.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        out = await _run(client, f"ls -lah '{path}' 2>&1")
        return out
    except Exception as e:
        return f"Error listing directory '{path}': {e}"


@mcp.tool()
async def delete_file(
    path: str,
    recursive: bool = False,
    host_name: Optional[str] = None,
) -> str:
    """Delete a file or directory on the remote server.

    Args:
        path: Absolute path to delete.
        recursive: If True, delete directory and all its contents (use with caution).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Success message or error details.
    """
    if not path or path in ("/", "~", "."):
        return "Error: refusing to delete root or home directory"
    try:
        client = SSHConnectionManager.get_connection(host_name)
        flag = "-rf" if recursive else "-f"
        out = await _run(client, f"rm {flag} '{path}' 2>&1 && echo 'Deleted: {path}'")
        return out
    except Exception as e:
        return f"Error deleting '{path}': {e}"


@mcp.tool()
async def search_files(
    path: str,
    pattern: str,
    file_type: str = "any",
    host_name: Optional[str] = None,
) -> str:
    """Search for files by name pattern in a remote directory tree.

    Args:
        path: Root directory to search from.
        pattern: File name pattern (e.g., "*.log", "nginx.conf").
        file_type: Filter by type: "file" (f), "dir" (d), or "any" (default).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        List of matching file paths.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        type_flag = ""
        if file_type == "file":
            type_flag = "-type f"
        elif file_type == "dir":
            type_flag = "-type d"
        cmd = f"find '{path}' {type_flag} -name '{pattern}' 2>/dev/null | head -100"
        out = await _run(client, cmd)
        if not out:
            return f"No files matching '{pattern}' found under '{path}'"
        return out
    except Exception as e:
        return f"Error searching files: {e}"


@mcp.tool()
async def grep_file(
    path: str,
    pattern: str,
    recursive: bool = False,
    ignore_case: bool = True,
    context_lines: int = 2,
    host_name: Optional[str] = None,
) -> str:
    """Search for a text pattern in remote files.

    Args:
        path: File path or directory to search.
        pattern: Text or regex pattern to search for.
        recursive: Search recursively in directories (default False).
        ignore_case: Case-insensitive search (default True).
        context_lines: Lines of context around each match (default 2).
        host_name: Named host from SSH_HOSTS config; uses default host if omitted.

    Returns:
        Matching lines with file names and line numbers.
    """
    try:
        client = SSHConnectionManager.get_connection(host_name)
        flags = "-n"
        if recursive:
            flags += "r"
        if ignore_case:
            flags += "i"
        cmd = f"grep {flags} -C {context_lines} '{pattern}' '{path}' 2>&1 | head -200"
        out = await _run(client, cmd)
        if not out:
            return f"No matches for '{pattern}' in '{path}'"
        return out
    except Exception as e:
        return f"Error grepping '{path}': {e}"
