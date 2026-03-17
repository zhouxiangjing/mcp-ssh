"""
Unit tests for src/tools/exec.py
"""

from unittest.mock import patch

import pytest

from tests.conftest import make_exec_result


class TestExecuteCommand:
    @pytest.mark.asyncio
    async def test_success_stdout(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="hello world")

        from src.tools.exec import execute_command
        result = await execute_command("echo hello world")

        assert "hello world" in result

    @pytest.mark.asyncio
    async def test_nonzero_exit_includes_stderr(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="", stderr="not found", exit_code=127
        )

        from src.tools.exec import execute_command
        result = await execute_command("bad_cmd")

        assert "127" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_connection_error(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("SSH down"),
        ):
            from src.tools.exec import execute_command
            result = await execute_command("ls")
        assert "Error executing command" in result

    @pytest.mark.asyncio
    async def test_empty_output(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="", stderr="", exit_code=0)

        from src.tools.exec import execute_command
        result = await execute_command("true")

        assert "exit code 0" in result


class TestExecuteScript:
    @pytest.mark.asyncio
    async def test_script_success(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        stdin, stdout_mock, stderr_mock = make_exec_result(stdout="script output")
        client.exec_command.return_value = (stdin, stdout_mock, stderr_mock)

        from src.tools.exec import execute_script
        result = await execute_script("echo script output", shell="bash")

        assert "script output" in result

    @pytest.mark.asyncio
    async def test_script_failure(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        stdin, stdout_mock, stderr_mock = make_exec_result(
            stdout="", stderr="syntax error", exit_code=1
        )
        client.exec_command.return_value = (stdin, stdout_mock, stderr_mock)

        from src.tools.exec import execute_script
        result = await execute_script("bad script")

        assert "Exit code: 1" in result
        assert "syntax error" in result
