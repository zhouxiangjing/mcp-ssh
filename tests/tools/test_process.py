"""
Unit tests for src/tools/process.py
"""

from unittest.mock import patch

import pytest

from tests.conftest import make_exec_result


class TestListProcesses:
    @pytest.mark.asyncio
    async def test_default_sort_cpu(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="USER PID %CPU %MEM CMD\nroot 1 99.0 0.1 stress"
        )

        from src.tools.process import list_processes
        result = await list_processes()

        assert "stress" in result
        cmd = client.exec_command.call_args[0][0]
        assert "--sort=-%cpu" in cmd

    @pytest.mark.asyncio
    async def test_sort_by_mem(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="USER PID %CPU %MEM CMD")

        from src.tools.process import list_processes
        await list_processes(sort_by="mem")

        cmd = client.exec_command.call_args[0][0]
        assert "--sort=-%mem" in cmd

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("no ssh"),
        ):
            from src.tools.process import list_processes
            result = await list_processes()
        assert "Error listing processes" in result


class TestFindProcess:
    @pytest.mark.asyncio
    async def test_found(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="root 1234 0.0 0.1 /usr/sbin/nginx"
        )

        from src.tools.process import find_process
        result = await find_process("nginx")

        assert "nginx" in result

    @pytest.mark.asyncio
    async def test_not_found(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="")

        from src.tools.process import find_process
        result = await find_process("nonexistent_proc_xyz")

        assert "No processes found" in result


class TestKillProcess:
    @pytest.mark.asyncio
    async def test_kill_term(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="Signal TERM sent to PID 1234")

        from src.tools.process import kill_process
        result = await kill_process(1234, "TERM")

        assert "TERM" in result

    @pytest.mark.asyncio
    async def test_invalid_signal(self, mock_ssh_connection_manager):
        from src.tools.process import kill_process
        result = await kill_process(1234, "BADKILL")

        assert "Error" in result
        assert "signal must be one of" in result


class TestGetOpenPorts:
    @pytest.mark.asyncio
    async def test_returns_port_list(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="State  Recv-Q Send-Q Local Address\nLISTEN 0      128    0.0.0.0:22"
        )

        from src.tools.process import get_open_ports
        result = await get_open_ports()

        assert "22" in result
