# SSH MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that lets AI assistants manage and analyze remote Linux/Unix systems over SSH using natural language.

## Features

- **Execute commands & scripts** — run shell commands or multi-line scripts remotely
- **System information** — CPU, memory, disk, network, uptime in one call
- **Service management** — start, stop, restart, enable/disable systemd services
- **Process management** — list, search, and signal processes
- **File operations** — read, write, append, search, and grep remote files
- **SFTP transfers** — upload and download files
- **Diagnostics** — disk health, high-load analysis, network connectivity, security audit, log analysis
- **Multi-host support** — manage multiple servers by name via `SSH_HOSTS_JSON`
- **Auto-reconnect** — connections are lazily established and automatically re-established on drop

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

### Run directly with uvx (no install needed)

```bash
uvx ssh-mcp-server --host 192.168.1.100 --username admin --key-file ~/.ssh/id_rsa
```

### Install from PyPI

```bash
pip install ssh-mcp-server
ssh-mcp-server --host 192.168.1.100 --username admin --key-file ~/.ssh/id_rsa
```

### Install from source

```bash
git clone https://github.com/zhouxiangjing/mcp-ssh.git
cd mcp-ssh
uv pip install -e ".[dev]"
```

## Configuration

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SSH_HOST` | `127.0.0.1` | Remote host IP or hostname |
| `SSH_PORT` | `22` | SSH port |
| `SSH_USERNAME` | `root` | SSH username |
| `SSH_PASSWORD` | — | Password (omit when using key auth) |
| `SSH_KEY_FILE` | — | Path to private key, e.g. `~/.ssh/id_rsa` |
| `SSH_KEY_PASSPHRASE` | — | Passphrase for encrypted private key |
| `SSH_TIMEOUT` | `30` | Connection timeout in seconds |
| `SSH_IGNORE_KNOWN_HOSTS` | `false` | Skip host key verification (not recommended in production) |
| `SSH_KNOWN_HOSTS_FILE` | `~/.ssh/known_hosts` | Custom known_hosts file path |
| `SSH_HOSTS_JSON` | — | JSON array for multi-host config (see below) |
| `MCP_SSH_LOG_LEVEL` | `WARNING` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Copy `.env.example` to `.env` and fill in your values — the server loads it automatically on startup.

### CLI arguments

All environment variables can be overridden via CLI flags:

```bash
ssh-mcp-server \
  --host 192.168.1.100 \
  --port 22 \
  --username admin \
  --key-file ~/.ssh/id_rsa \
  --timeout 60
```

Run `ssh-mcp-server --help` for the full list.

### Multi-host configuration

Manage multiple servers by name using `SSH_HOSTS_JSON`:

```bash
export SSH_HOSTS_JSON='[
  {"name": "web",  "host": "10.0.0.1", "port": 22, "username": "admin", "key_file": "~/.ssh/web_key"},
  {"name": "db",   "host": "10.0.0.2", "port": 22, "username": "root",  "password": "secret"},
  {"name": "edge", "host": "10.0.0.3", "port": 2222,"username": "ops",  "key_file": "~/.ssh/edge_key"}
]'
```

Pass `host_name="web"` to any tool call to target a specific server. Omit `host_name` to use the default host.

## MCP Client Setup

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ssh": {
      "command": "uvx",
      "args": ["ssh-mcp-server"],
      "env": {
        "SSH_HOST": "192.168.1.100",
        "SSH_USERNAME": "admin",
        "SSH_KEY_FILE": "~/.ssh/id_rsa"
      }
    }
  }
}
```

### Cursor / other MCP clients

```json
{
  "mcpServers": {
    "ssh": {
      "command": "uvx",
      "args": ["ssh-mcp-server"],
      "env": {
        "SSH_HOST": "your-server-ip",
        "SSH_USERNAME": "your-username",
        "SSH_KEY_FILE": "~/.ssh/id_rsa"
      }
    }
  }
}
```

## Available Tools

### Connection Management

| Tool | Description |
|------|-------------|
| `test_connection` | Verify SSH connectivity and return server identity |
| `list_configured_hosts` | List all named hosts from `SSH_HOSTS_JSON` |
| `close_connection` | Close connection to a specific host |
| `close_all_connections` | Close all active SSH connections |

### Command Execution

| Tool | Description |
|------|-------------|
| `execute_command` | Run a shell command and return stdout/stderr |
| `execute_script` | Run a multi-line script via bash/sh/python3/etc. |

### System Information

| Tool | Description |
|------|-------------|
| `get_system_overview` | Hostname, OS, kernel, uptime, CPU, memory, disk, network in one call |
| `get_cpu_info` | CPU load, per-core usage, top CPU processes |
| `get_memory_info` | Memory and swap usage details |
| `get_disk_info` | Disk usage per filesystem, inode usage, I/O stats |
| `get_network_info` | Network interfaces, routing table, active connections |
| `get_system_logs` | Recent journald/syslog entries, filterable by service |
| `check_service_status` | Check status of a systemd service |
| `manage_service` | Start, stop, restart, reload, enable, or disable a service |

### Process Management

| Tool | Description |
|------|-------------|
| `list_processes` | List processes sorted by CPU, memory, or PID |
| `find_process` | Search processes by name or keyword |
| `kill_process` | Send TERM/KILL/HUP/USR1/USR2 to a PID |
| `get_open_ports` | List all listening ports and their processes |

### File Operations

| Tool | Description |
|------|-------------|
| `read_file` | Read a remote file (with optional line limit) |
| `write_file` | Write/overwrite a remote file (creates parent dirs) |
| `append_file` | Append content to a remote file |
| `list_directory` | List files and dirs at a remote path |
| `delete_file` | Delete a file or directory (with optional recursive flag) |
| `search_files` | Find files by name pattern under a directory |
| `grep_file` | Search file content with regex and context lines |

### SFTP Transfers

| Tool | Description |
|------|-------------|
| `upload_file` | Upload a local file to the remote server |
| `download_file` | Download a remote file to local |
| `get_file_info` | Get file metadata: size, permissions, owner, mtime |

### Diagnostics

| Tool | Description |
|------|-------------|
| `check_disk_health` | Kernel disk errors, failed systemd units, high inode usage |
| `check_high_load` | Identify CPU/memory hogs and OOM events |
| `check_network_connectivity` | Ping test and DNS resolution from the remote server |
| `check_security` | Failed logins, SUID binaries, listening ports, recent logins |
| `tail_log` | Tail the last N lines of a log file |
| `analyze_log_errors` | Count and summarize ERROR/WARN/CRITICAL lines in a log |

## Development

### Setup

```bash
git clone https://github.com/zhouxiangjing/mcp-ssh.git
cd mcp-ssh
uv pip install -e ".[dev]"
```

### Run tests

```bash
pytest tests/ -v
```

### Run with coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Lint

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Security

- Prefer key-based authentication over passwords.
- Never set `SSH_IGNORE_KNOWN_HOSTS=true` in production.
- All credentials are read from environment variables or `.env` — never hardcoded.
- The `.env` file is excluded from version control via `.gitignore`.
- `delete_file` refuses to delete `/`, `~`, or `.` as a safety guard.
- `kill_process` and `manage_service` only accept a fixed allowlist of signals/actions.

## License

MIT — see [LICENSE](LICENSE) for details.
