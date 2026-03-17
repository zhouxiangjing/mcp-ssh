# Contributing

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/zhouxiangjing/mcp-ssh.git
cd mcp-ssh
uv pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
# Check
ruff check src/ tests/

# Format
ruff format src/ tests/
```

## Adding a New Tool

1. Create or edit a file under `src/tools/`.
2. Decorate your async function with `@mcp.tool()`.
3. Write a clear docstring — it becomes the tool description shown to the AI.
4. Add corresponding tests under `tests/tools/`.
5. Document the tool in the README tool table.

## Pull Request Guidelines

- Keep PRs focused on a single concern.
- Add or update tests for all changes.
- Run `ruff check` and `pytest` before submitting.
- Write a clear PR description explaining *why*, not just *what*.

## Reporting Issues

Please open a GitHub issue with:
- Your OS and Python version
- Steps to reproduce
- Expected vs actual behavior
- Relevant log output (`MCP_SSH_LOG_LEVEL=DEBUG`)
