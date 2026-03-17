# SSH MCP Server Extension

This extension provides a natural language interface for managing and analyzing remote Linux systems via SSH through the Model Context Protocol (MCP).

## What this extension provides

The SSH MCP Server enables AI agents to connect to remote Linux/Unix servers and perform system administration tasks using natural language commands. You can:

- **Execute commands**: Run shell commands and scripts on remote servers
- **Analyze system state**: CPU, memory, disk, network usage and statistics
- **Manage processes**: List, search, and signal processes
- **File operations**: Read, write, search, upload, and download files via SFTP
- **Service management**: Start, stop, restart, and monitor systemd services
- **Diagnose issues**: Identify high load, disk errors, network problems, and security concerns
- **Analyze logs**: Tail, search, and summarize log file errors
- **Multi-host support**: Manage multiple servers with named host configurations

## Available Tools

### Command Execution
- `execute_command` — Run a shell command and return output
- `execute_script` — Run a multi-line script (bash/sh/python3/etc.)

### System Information
- `get_system_overview` — One-call comprehensive system report
- `get_cpu_info` — CPU load and top processes
- `get_memory_info` — Memory and swap usage
- `get_disk_info` — Disk usage, inodes, and I/O stats
- `get_network_info` — Interfaces, routes, and active connections
- `get_system_logs` — Recent journald/syslog entries
- `check_service_status` — Check a systemd service status
- `manage_service` — Start/stop/restart/reload/enable/disable a service

### Process Management
- `list_processes` — List processes sorted by CPU or memory
- `find_process` — Find processes by name or keyword
- `kill_process` — Send TERM/KILL/HUP/etc. to a PID
- `get_open_ports` — List all listening ports and their processes

### File Operations
- `read_file` — Read remote file content
- `write_file` — Write/overwrite a remote file
- `append_file` — Append to a remote file
- `list_directory` — List directory contents
- `delete_file` — Delete a file or directory
- `search_files` — Find files by name pattern
- `grep_file` — Search file content with regex

### SFTP Transfer
- `upload_file` — Upload a local file to the remote server
- `download_file` — Download a remote file to local
- `get_file_info` — Get file metadata (size, permissions, owner)

### Diagnostics
- `check_disk_health` — Kernel disk errors, failed units, high inode usage
- `check_high_load` — Identify CPU/memory hogs and OOM events
- `check_network_connectivity` — Ping test and DNS check from remote
- `check_security` — Failed logins, SUID binaries, listening ports
- `tail_log` — Get the last N lines of a log file
- `analyze_log_errors` — Summarize errors and warnings in a log file

### Connection Management
- `test_connection` — Verify SSH connectivity
- `list_configured_hosts` — Show all named SSH hosts
- `close_connection` — Close a specific SSH connection
- `close_all_connections` — Close all active SSH connections

## Configuration

### Primary: Environment Variables

```bash
# Basic connection
export SSH_HOST=192.168.1.100
export SSH_PORT=22
export SSH_USERNAME=root

# Authentication (key takes priority over password)
export SSH_KEY_FILE=~/.ssh/id_rsa
export SSH_PASSWORD=your_password

# Options
export SSH_TIMEOUT=30
export SSH_IGNORE_KNOWN_HOSTS=false
```

### Multi-host (JSON)

```bash
export SSH_HOSTS_JSON='[
  {"name":"web","host":"10.0.0.1","port":22,"username":"admin","key_file":"~/.ssh/web_key"},
  {"name":"db","host":"10.0.0.2","port":22,"username":"root","password":"secret"}
]'
```

Then pass `host_name="web"` to any tool to target a specific host.

### CLI Arguments

```bash
ssh-mcp-server --host 192.168.1.100 --username root --key-file ~/.ssh/id_rsa
```

### .env File

Copy `.env.example` to `.env` and fill in your values. The server loads `.env` automatically on startup.

## Installation

```bash
# Install from source (development)
cd ssh-mcp
uv pip install -e .

# Or run directly
uvx --from . ssh-mcp-server --host 192.168.1.100 --username root --key-file ~/.ssh/id_rsa
```

## Usage Examples

You can interact with remote systems using natural language:

- "查看服务器的系统概览"
- "找出占用 CPU 最高的进程"
- "重启 nginx 服务"
- "查看 /var/log/nginx/error.log 最后 100 行"
- "检查磁盘健康状态"
- "上传 config.yml 到 /etc/myapp/config.yml"
- "在所有服务器上执行 apt update"
- "分析 /var/log/app.log 中的错误"

## Security Notes

- Prefer key-based authentication over passwords.
- Avoid `SSH_IGNORE_KNOWN_HOSTS=true` in production environments.
- All commands run with the permissions of the configured SSH user; use a least-privilege account when possible.
- Connection credentials are read from environment variables or `.env` file; never hardcode them.
