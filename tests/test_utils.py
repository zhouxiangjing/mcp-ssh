"""Unit tests for src/common/utils.py"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.common.utils import run_command
from tests.conftest import make_exec_result


class TestRunCommand:
    @pytest.mark.asyncio
    async def test_returns_stdout_when_present(self):
        client = Mock()
        client.exec_command.return_value = make_exec_result(stdout="hello", stderr="")
        result = await run_command(client, "echo hello")
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_falls_back_to_stderr_when_stdout_empty(self):
        client = Mock()
        client.exec_command.return_value = make_exec_result(stdout="", stderr="some error")
        result = await run_command(client, "bad_cmd")
        assert result == "some error"

    @pytest.mark.asyncio
    async def test_returns_empty_string_when_both_empty(self):
        client = Mock()
        client.exec_command.return_value = make_exec_result(stdout="", stderr="")
        result = await run_command(client, "true")
        assert result == ""

    @pytest.mark.asyncio
    async def test_strips_trailing_whitespace(self):
        client = Mock()
        client.exec_command.return_value = make_exec_result(stdout="  output  \n")
        result = await run_command(client, "cmd")
        assert result == "output"

    @pytest.mark.asyncio
    async def test_passes_timeout_to_exec_command(self):
        client = Mock()
        client.exec_command.return_value = make_exec_result(stdout="ok")
        await run_command(client, "sleep 1", timeout=5)
        client.exec_command.assert_called_once_with("sleep 1", timeout=5)
