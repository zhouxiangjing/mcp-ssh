# SSH MCP Server

基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 的远程 Linux/Unix 服务器管理服务，让 AI 助手通过自然语言即可完成服务器运维、诊断、文件操作等全套任务。

[English](README_EN.md) | 中文

---

## 目录

- [功能概览](#功能概览)
- [应用场景](#应用场景)
- [环境要求](#环境要求)
- [安装方式](#安装方式)
- [配置说明](#配置说明)
- [MCP 客户端接入](#mcp-客户端接入)
- [工具列表](#工具列表)
- [开发指南](#开发指南)
- [安全说明](#安全说明)
- [免责声明](#免责声明)

---

## 功能概览

| 功能模块 | 说明 |
|----------|------|
| 连接管理 | 多主机配置、连接测试、自动重连 |
| 命令执行 | 执行单条命令或多行脚本，支持任意 Shell 解释器 |
| 系统信息 | CPU、内存、磁盘、网络、系统日志一键采集 |
| 服务管理 | systemd 服务的启停、重启、状态查看 |
| 进程管理 | 进程列表、搜索、终止信号发送 |
| 文件操作 | 读写、追加、列目录、搜索、正则内容匹配 |
| 文件传输 | SFTP 上传/下载、元信息查询 |
| 系统诊断 | 磁盘健康、高负载分析、网络连通性、安全审计、日志分析 |

---

## 应用场景

### 日常运维

- **一句话查服务器状态**：「帮我看一下服务器现在的系统情况」，AI 立即返回 CPU、内存、磁盘、负载汇总。
- **服务快速管理**：「重启 nginx」、「查看 mysql 服务状态」、「把 redis 设为开机自启」。
- **批量服务器巡检**：配置多台主机，逐一采集系统信息生成巡检报告。

### 故障排查

- **高负载排查**：「服务器 CPU 跑满了，帮我看看是什么进程」，AI 自动分析 top 进程并给出建议。
- **OOM 内存溢出排查**：查看 dmesg OOM 事件、内存占用最高进程，快速定位问题。
- **磁盘爆满告警**：「磁盘快满了」，AI 检查各分区使用率、inode 占用并找出大文件。
- **网络异常诊断**：测试出站连通性、DNS 解析、路由表，定位网络层问题。
- **日志快速分析**：「分析一下 /var/log/app.log 的错误」，AI 统计 ERROR/WARN/CRITICAL 数量并给出近期错误样本。

### 安全审计

- **登录异常检测**：统计 SSH 暴力破解失败次数，查看近期登录记录。
- **端口安全扫描**：列出所有监听端口及关联进程，发现可疑开放端口。
- **SUID 文件检查**：扫描系统中 SUID 提权文件，识别潜在安全风险。
- **世界可写文件**：检查 /tmp、/var/tmp 等目录中的高危权限文件。

### 文件与配置管理

- **远程配置热改**：直接读取并修改 `/etc/nginx/nginx.conf`、`/etc/hosts` 等配置文件，无需手动 SSH 登录。
- **日志实时查尾**：「看一下 nginx 最近 100 行错误日志」，即时返回结果。
- **配置文件批量下发**：将本地修改好的配置文件通过 SFTP 上传到多台服务器。
- **跨服务器文件同步**：下载远程文件到本地后，再上传到其他服务器。

### 自动化脚本执行

- **执行复杂运维脚本**：发送多行 Bash/Python 脚本到远程服务器执行，支持任意 Shell 解释器。
- **数据库备份**：在远端执行 `mysqldump` / `pg_dump` 并将备份文件下载到本地。
- **定时任务检查**：查看 crontab 配置，确认定时任务是否正确配置并运行。
- **应用部署辅助**：远程 `git pull`、重建容器、重启服务，完成一键部署流程。

### 多环境管理

- **开发/测试/生产环境并行管理**：通过 `SSH_HOSTS_JSON` 配置多台服务器，按名称切换，一次会话管理所有环境。
- **容器宿主机管理**：查看 Docker/Kubernetes 宿主机的资源使用，辅助容器调度决策。
- **云服务器集群巡检**：批量连接 ECS/EC2 实例，汇总各节点状态。

---

## 环境要求

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/)（推荐）或 pip
- 目标服务器：Linux / Unix（支持 systemd 的发行版效果最佳）

---

## 安装方式

### 方式一：uvx 直接运行（无需安装）

```bash
uvx ssh-mcp-zlzero --host 192.168.1.100 --username admin --key-file ~/.ssh/id_rsa
```

### 方式二：pip 安装

```bash
pip install ssh-mcp-zlzero
ssh-mcp-zlzero --host 192.168.1.100 --username admin --key-file ~/.ssh/id_rsa
```

### 方式三：源码安装（开发调试）

```bash
git clone https://github.com/zhouxiangjing/mcp-ssh.git
cd mcp-ssh
uv pip install -e ".[dev]"
```

---

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SSH_HOST` | `127.0.0.1` | 远程主机 IP 或域名 |
| `SSH_PORT` | `22` | SSH 端口 |
| `SSH_USERNAME` | `root` | SSH 用户名 |
| `SSH_PASSWORD` | — | 密码（使用密钥认证时可省略）|
| `SSH_KEY_FILE` | — | 私钥路径，如 `~/.ssh/id_rsa` |
| `SSH_KEY_PASSPHRASE` | — | 加密私钥的口令 |
| `SSH_TIMEOUT` | `30` | 连接超时秒数 |
| `SSH_IGNORE_KNOWN_HOSTS` | `false` | 跳过主机密钥校验（生产环境不推荐）|
| `SSH_KNOWN_HOSTS_FILE` | `~/.ssh/known_hosts` | 自定义 known_hosts 路径 |
| `SSH_HOSTS_JSON` | — | 多主机 JSON 配置（见下方）|
| `MCP_SSH_LOG_LEVEL` | `WARNING` | 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` |

将 `.env.example` 复制为 `.env` 并填写配置，服务器启动时会自动加载。

### CLI 参数

所有环境变量均可通过 CLI 参数覆盖：

```bash
ssh-mcp-zlzero \
  --host 192.168.1.100 \
  --port 22 \
  --username admin \
  --key-file ~/.ssh/id_rsa \
  --timeout 60
```

运行 `ssh-mcp-zlzero --help` 查看完整参数列表。

### 多主机配置

通过 `SSH_HOSTS_JSON` 管理多台服务器，工具调用时传入 `host_name` 参数即可切换目标主机，省略时使用默认主机：

```bash
export SSH_HOSTS_JSON='[
  {"name": "web",   "host": "10.0.0.1", "port": 22,   "username": "admin", "key_file": "~/.ssh/web_key"},
  {"name": "db",    "host": "10.0.0.2", "port": 22,   "username": "root",  "password": "secret"},
  {"name": "edge",  "host": "10.0.0.3", "port": 2222, "username": "ops",   "key_file": "~/.ssh/edge_key"},
  {"name": "dev",   "host": "10.0.0.4", "port": 22,   "username": "dev",   "key_file": "~/.ssh/id_rsa"},
  {"name": "prod",  "host": "10.0.0.5", "port": 22,   "username": "admin", "key_file": "~/.ssh/prod_key"}
]'
```

---

## MCP 客户端接入

### Claude Desktop

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "ssh": {
      "command": "uvx",
      "args": ["ssh-mcp-zlzero"],
      "env": {
        "SSH_HOST": "192.168.1.100",
        "SSH_USERNAME": "admin",
        "SSH_KEY_FILE": "~/.ssh/id_rsa"
      }
    }
  }
}
```

### Cursor / 其他 MCP 客户端

```json
{
  "mcpServers": {
    "ssh": {
      "command": "uvx",
      "args": ["ssh-mcp-zlzero"],
      "env": {
        "SSH_HOST": "your-server-ip",
        "SSH_USERNAME": "your-username",
        "SSH_KEY_FILE": "~/.ssh/id_rsa"
      }
    }
  }
}
```

### DeepV Code

在 `~/.deepv/settings.json` 的 `mcpServers` 中添加：

```json
{
  "ssh": {
    "command": "uvx",
    "args": ["--from", "ssh-mcp-zlzero", "ssh-mcp-zlzero"],
    "env": {
      "SSH_HOST": "your-server-ip",
      "SSH_USERNAME": "your-username",
      "SSH_PASSWORD": "your-password",
      "SSH_IGNORE_KNOWN_HOSTS": "true"
    }
  }
}
```

多主机示例（生产/测试/开发环境并行）：

```json
{
  "ssh": {
    "command": "uvx",
    "args": ["--from", "ssh-mcp-zlzero", "ssh-mcp-zlzero"],
    "env": {
      "SSH_HOSTS_JSON": "[{\"name\":\"prod\",\"host\":\"10.0.0.1\",\"username\":\"admin\",\"key_file\":\"~/.ssh/prod_key\"},{\"name\":\"dev\",\"host\":\"10.0.0.2\",\"username\":\"dev\",\"key_file\":\"~/.ssh/id_rsa\"}]"
    }
  }
}
```

---

## 工具列表

### 连接管理

| 工具 | 说明 |
|------|------|
| `test_connection` | 验证 SSH 连接，返回主机名、当前用户、系统负载 |
| `list_configured_hosts` | 列出 `SSH_HOSTS_JSON` 中所有已配置的命名主机 |
| `close_connection` | 关闭指定主机的 SSH 连接（下次调用自动重连）|
| `close_all_connections` | 关闭所有活跃的 SSH 连接 |

### 命令执行

| 工具 | 说明 |
|------|------|
| `execute_command` | 执行单条 Shell 命令，返回 stdout/stderr 及退出码 |
| `execute_script` | 执行多行脚本，支持 `bash`、`sh`、`python3` 等任意解释器 |

### 系统信息

| 工具 | 说明 |
|------|------|
| `get_system_overview` | 一键采集主机名、OS、内核、负载、CPU、内存、磁盘、网络接口 |
| `get_cpu_info` | CPU 实时负载、各核使用率、top CPU 进程 |
| `get_memory_info` | 内存与 Swap 使用详情（free/used/cached/available）|
| `get_disk_info` | 各分区磁盘使用率、inode 占用、I/O 统计 |
| `get_network_info` | 网络接口详情、路由表、活跃连接列表 |
| `get_system_logs` | 读取 journald / syslog 日志，支持按服务过滤 |
| `check_service_status` | 查看 systemd 服务状态（active/inactive/failed）|
| `manage_service` | 启动/停止/重启/重载/启用/禁用 systemd 服务 |

### 进程管理

| 工具 | 参数说明 |
|------|----------|
| `list_processes` | 按 CPU / 内存 / PID 排序列出进程，默认显示 20 条 |
| `find_process` | 按名称或关键字搜索进程，返回 PID 及详情 |
| `kill_process` | 向指定 PID 发送信号：`TERM`（优雅）/ `KILL`（强制）/ `HUP`（重载）/ `USR1` / `USR2` / `INT` / `QUIT` |
| `get_open_ports` | 列出所有 TCP/UDP 监听端口及关联进程 |

### 文件操作

| 工具 | 说明 |
|------|------|
| `read_file` | 读取远程文件内容，支持 `max_lines` 限制行数（0 = 不限）|
| `write_file` | 覆盖写入远程文件，自动创建父目录 |
| `append_file` | 追加内容到远程文件末尾 |
| `list_directory` | 列出远程目录（等价于 `ls -lah`）|
| `delete_file` | 删除文件或目录，`recursive=true` 支持递归删除（禁止删除 `/`、`~`、`.`）|
| `search_files` | 按文件名模式在目录树中搜索，支持 `file` / `dir` / `any` 类型过滤 |
| `grep_file` | 在远程文件中正则搜索，支持递归、忽略大小写、上下文行数 |

### SFTP 文件传输

| 工具 | 说明 |
|------|------|
| `upload_file` | 将本地文件通过 SFTP 上传到远程服务器，返回传输字节数 |
| `download_file` | 将远程文件下载到本地，自动创建本地目录 |
| `get_file_info` | 查询远程文件元信息：大小、权限、UID/GID、修改时间 |

### 系统诊断

| 工具 | 说明 |
|------|------|
| `check_disk_health` | 检查内核磁盘错误日志、失败的 systemd 单元、inode 超 80% 的分区 |
| `check_high_load` | 分析高负载原因：top CPU/内存进程、OOM 事件记录 |
| `check_network_connectivity` | 从远程服务器出发测试 ping 和 DNS 解析，诊断出站网络问题 |
| `check_security` | 安全审计：SSH 失败登录、监听端口、SUID 文件、高危权限文件、近期登录记录 |
| `tail_log` | 读取日志文件末尾 N 行（默认 50 行）|
| `analyze_log_errors` | 统计日志中 ERROR / WARN / CRITICAL / Exception 数量，并返回近期错误样本 |

---

## 开发指南

### 环境准备

```bash
git clone https://github.com/zhouxiangjing/mcp-ssh.git
cd mcp-ssh
uv pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/ -v
```

### 测试覆盖率

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### 代码检查与格式化

```bash
ruff check src/ tests/
ruff format src/ tests/
```

### 项目结构

```
mcp-ssh/
├── src/
│   ├── common/
│   │   ├── config.py          # 环境变量与多主机配置解析
│   │   ├── connection.py      # SSH 连接池与自动重连
│   │   ├── server.py          # MCP Server 实例
│   │   └── utils.py           # 公共工具函数
│   └── tools/
│       ├── connection_mgmt.py # 连接管理工具
│       ├── diagnostics.py     # 系统诊断工具
│       ├── exec.py            # 命令/脚本执行工具
│       ├── file.py            # 文件操作工具
│       ├── process.py         # 进程管理工具
│       ├── sftp.py            # SFTP 传输工具
│       └── system.py          # 系统信息采集工具
└── tests/                     # 单元测试
```

---

## 安全说明

- **优先使用密钥认证**，避免在配置中明文存储密码。
- **生产环境禁止开启** `SSH_IGNORE_KNOWN_HOSTS=true`，防止中间人攻击。
- 所有凭据通过环境变量或 `.env` 文件读取，不会硬编码在代码中。
- `.env` 文件已通过 `.gitignore` 排除在版本控制之外。
- `delete_file` 拒绝删除 `/`、`~`、`.` 等危险路径。
- `kill_process` 仅允许发送固定白名单信号：`TERM` / `KILL` / `HUP` / `USR1` / `USR2` / `INT` / `QUIT`。
- `manage_service` 仅允许执行白名单操作：`start` / `stop` / `restart` / `reload` / `enable` / `disable`。

---

## 免责声明

> **请在使用本项目前仔细阅读以下声明。使用本项目即表示您已阅读、理解并同意以下所有条款。**

### 风险告知

本项目（SSH MCP Server）通过 AI 模型驱动的自然语言指令对远程服务器执行真实操作，包括但不限于：

- 执行任意 Shell 命令与脚本
- 读写、删除远程文件及目录
- 启停、重启系统服务
- 终止运行中的进程
- 通过 SFTP 上传/下载文件

上述操作均为**不可逆或难以回滚的真实变更**，一旦执行无法撤销。

### 责任限制

**本项目作者及贡献者对以下情形概不负责，亦不承担任何直接、间接、附带、特殊或衍生损失：**

- AI 模型误解用户意图导致执行了错误命令
- 误删文件、误停服务、误杀进程造成的数据丢失或业务中断
- 错误配置导致服务器权限泄露或安全漏洞
- 在生产环境中未经充分验证直接使用造成的任何后果
- 凭据（密码、私钥）通过不安全渠道泄露引发的安全事故
- 因网络中断、SSH 会话异常导致命令执行状态不确定引发的问题
- 第三方 AI 服务（Claude、GPT 等）产生幻觉或错误推理导致的误操作

### 推荐安全实践

为将操作风险降至最低，强烈建议遵循以下方案：

#### 1. 最小权限原则

为 MCP 专用的 SSH 账号授予最低必要权限，禁止直接使用 `root`：

```bash
# 创建专用运维账号
useradd -m -s /bin/bash mcp-ops

# 仅允许执行特定命令（通过 sudoers 精细控制）
echo 'mcp-ops ALL=(ALL) NOPASSWD: /bin/systemctl status *, /bin/journalctl *' >> /etc/sudoers.d/mcp-ops
chmod 440 /etc/sudoers.d/mcp-ops
```

#### 2. 生产环境操作前必须备份

```bash
# 操作配置文件前先备份
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak.$(date +%Y%m%d%H%M%S)

# 重要数据目录快照
tar czf /backup/data-$(date +%Y%m%d).tar.gz /var/data/
```

#### 3. 环境隔离策略

| 环境 | 建议 |
|------|------|
| 开发环境 | 可直接使用，风险可控 |
| 测试环境 | 可使用，建议开启操作日志 |
| 预发布环境 | 只读操作自动执行，写操作需人工二次确认 |
| **生产环境** | **强烈建议只读模式，所有变更操作须人工审批后执行** |

#### 4. 网络访问控制

```bash
# 通过 iptables / firewalld 限制 SSH 来源 IP
firewall-cmd --permanent --add-rich-rule='rule family=ipv4 source address=10.0.0.0/24 service name=ssh accept'
firewall-cmd --permanent --add-rich-rule='rule family=ipv4 service name=ssh drop'
firewall-cmd --reload
```

#### 5. 操作审计日志

```bash
# 开启 SSH 会话完整审计（记录所有执行命令）
# 在 /etc/ssh/sshd_config 中添加：
ForceCommand /usr/bin/script -q -f /var/log/ssh-audit/$(date +%Y%m%d-%H%M%S)-$USER.log
```

或使用 `auditd` 记录所有 `execve` 系统调用：

```bash
audit -a always,exit -F arch=b64 -S execve -k mcp-ops-audit
```

#### 6. 密钥安全管理

- 为 MCP 配置专用 SSH 密钥对，与个人密钥严格隔离
- 私钥设置口令（`SSH_KEY_PASSPHRASE`），禁止使用无口令裸私钥连接生产服务器
- 定期轮换密钥，离职人员的密钥立即吊销
- 禁止将密钥或密码提交到代码仓库

#### 7. 高危操作二次确认建议

在使用 AI 执行以下操作时，**务必在 AI 给出命令后，先阅读确认再批准执行**，切勿一键允许：

- 任何包含 `rm -rf` 的删除操作
- `systemctl stop` / `disable` 关键服务
- 修改 `/etc/sudoers`、`/etc/passwd`、`/etc/ssh/sshd_config` 等系统配置
- 涉及防火墙规则变更的命令
- 数据库清空或 truncate 操作

### 适用场景声明

本项目**适合**用于：
- 个人开发/测试服务器的日常管理
- 内网受控环境下的运维自动化
- 学习 MCP 协议与 AI 运维工具集成
- 只读监控与信息采集场景

本项目**不建议**直接用于：
- 无备份机制的生产数据库服务器
- 金融、医疗等对数据完整性有严格要求的系统
- 多人共享且无操作审计的服务器环境

---

## License

MIT — 详见 [LICENSE](LICENSE)。
