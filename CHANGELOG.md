# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
