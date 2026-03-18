# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2026-03-18

### Fixed

- 修复 CI lint 错误：清理 src/ 和 tests/ 中所有未使用的 import
- 修复 tests/tools/test_file.py 中未使用的局部变量 `result`
- 115 个测试全部通过，CI 流水线恢复绿色

## [0.1.4] - 2026-03-18

### Improved

- `GEMINI.md` ROLE ACTIVATION 改用具体例句映射替代抽象表格，解决 Claude 模型对新会话第一条消息仍不触发工具的冷启动问题
- 新增 20+ 中文口语例句覆盖（帮我看一下远程服务器的状态、服务器情况、查看服务器等）
- 明确"server/服务器/系统/远程 + 任意状态词"模式规则，提升意图识别泛化能力
- `gemini-extension.json` 版本号同步至 0.1.3

## [0.1.3] - 2026-03-18

### Improved

- `GEMINI.md` 顶部新增 `ROLE ACTIVATION` 角色激活声明，解决新会话第一条消息无法触发 SSH MCP 工具调用的冷启动问题
- 补充大量中文模糊触发词（系统信息、服务器状态、查看服务器、服务器怎么样等），提升意图识别覆盖率
- `get_system_overview` 触发词扩展至覆盖常见中文口语表达

## [0.1.2] - 2026-03-17

### Fixed

- 从版本控制中移除 DEEPV.md，避免与 GEMINI.md 冲突导致 AI 意图识别失效

## [0.1.1] - 2026-03-17

### Fixed

- 包名从 `ssh-mcp-server` 重命名为 `ssh-mcp-zlzero`（PyPI 名称冲突）
- 修复 CI/CD workflow 中 `pytest`/`ruff` 命令找不到的问题（改用 `uv run`）
- 修复 CI 触发分支配置（补充 `master` 分支）
- `gemini-extension.json` 同步更新包名，补充 `SSH_IGNORE_KNOWN_HOSTS` 配置项
- `GEMINI.md` 全面重写为 AI 意图触发指南，提升 MCP 工具调用识别率

## [0.1.0] - 2026-03-17

### Added

- Initial release
- 35 MCP tools covering command execution, system info, service management,
  process management, file operations, SFTP transfers, and diagnostics
- Multi-host support via `SSH_HOSTS_JSON`
- Lazy SSH connection management with auto-reconnect
- Key-based and password-based authentication
- `MCP_SSH_LOG_LEVEL` environment variable for log control
- Full pytest test suite with mock fixtures
