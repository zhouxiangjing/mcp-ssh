"""
Unit tests for src/tools/system.py
"""

from unittest.mock import patch

import pytest

from tests.conftest import make_exec_result


def _stub_exec(outputs: list[str]):
    """Return a side_effect list for client.exec_command, one per call."""
    results = []
    for o in outputs:
        results.append(make_exec_result(stdout=o))
    return results


class TestGetSystemOverview:
    @pytest.mark.asyncio
    async def test_returns_all_sections(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        # get_system_overview calls exec_command 9 times
        client.exec_command.side_effect = _stub_exec(
            ["myhost", "Ubuntu 22.04", "5.15.0", "up 2 days", "0.5 0.4 0.3 1/100 42",
             "x86_64\n4 CPUs", "Mem: 8G", "/ 50G 20G", "eth0 UP"]
        )

        from src.tools.system import get_system_overview
        result = await get_system_overview()

        for section in ["Hostname", "OS Release", "Kernel", "Uptime", "Memory", "Disk"]:
            assert section in result

    @pytest.mark.asyncio
    async def test_connection_error(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("no route"),
        ):
            from src.tools.system import get_system_overview
            result = await get_system_overview()
        assert "Error getting system overview" in result


class TestGetMemoryInfo:
    @pytest.mark.asyncio
    async def test_returns_memory_data(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="Mem: 8.0G 2.0G 6.0G\nSwap: 2.0G 0 2.0G"
        )

        from src.tools.system import get_memory_info
        result = await get_memory_info()

        assert "Mem" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("fail"),
        ):
            from src.tools.system import get_memory_info
            result = await get_memory_info()
        assert "Error getting memory info" in result


class TestCheckServiceStatus:
    @pytest.mark.asyncio
    async def test_service_active(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="● nginx.service - A high performance web server\n   Active: active (running)"
        )

        from src.tools.system import check_service_status
        result = await check_service_status("nginx")

        assert "nginx" in result
        assert "active" in result


class TestGetCpuInfo:
    @pytest.mark.asyncio
    async def test_returns_cpu_data(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="top - 12:00:00 up 1 day\n%Cpu(s):  5.0 us"
        )

        from src.tools.system import get_cpu_info
        result = await get_cpu_info()

        assert "Cpu" in result or "cpu" in result or "top" in result.lower()

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("fail"),
        ):
            from src.tools.system import get_cpu_info
            result = await get_cpu_info()
        assert "Error getting CPU info" in result


class TestGetDiskInfo:
    @pytest.mark.asyncio
    async def test_returns_disk_sections(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="/dev/sda1  50G  20G  30G 40% /"),
            make_exec_result(stdout="sda 0 0 0"),
            make_exec_result(stdout="/dev/sda1 inodes used 10%"),
        ]

        from src.tools.system import get_disk_info
        result = await get_disk_info()

        assert "Disk Usage" in result
        assert "I/O Stats" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("fail"),
        ):
            from src.tools.system import get_disk_info
            result = await get_disk_info()
        assert "Error getting disk info" in result


class TestGetNetworkInfo:
    @pytest.mark.asyncio
    async def test_returns_network_sections(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="eth0: flags=4163<UP,BROADCAST,RUNNING>"),
            make_exec_result(stdout="default via 10.0.0.1 dev eth0"),
            make_exec_result(stdout="tcp 0 0 0.0.0.0:22 LISTEN"),
        ]

        from src.tools.system import get_network_info
        result = await get_network_info()

        assert "Interfaces" in result
        assert "Routes" in result
        assert "Connections" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("fail"),
        ):
            from src.tools.system import get_network_info
            result = await get_network_info()
        assert "Error getting network info" in result


class TestGetSystemLogs:
    @pytest.mark.asyncio
    async def test_returns_log_lines(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="Jan 1 00:00:00 host sshd[1]: Accepted"
        )

        from src.tools.system import get_system_logs
        result = await get_system_logs(lines=10)

        assert "Accepted" in result

    @pytest.mark.asyncio
    async def test_filters_by_unit(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="nginx log line")

        from src.tools.system import get_system_logs
        await get_system_logs(lines=20, unit="nginx")

        cmd = client.exec_command.call_args[0][0]
        assert "nginx" in cmd

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("fail"),
        ):
            from src.tools.system import get_system_logs
            result = await get_system_logs(lines=10)
        assert "Error getting system logs" in result


class TestManageService:
    @pytest.mark.asyncio
    async def test_restart_success(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="OK: nginx restart succeeded"
        )

        from src.tools.system import manage_service
        result = await manage_service("nginx", "restart")

        assert "OK" in result

    @pytest.mark.asyncio
    async def test_invalid_action_rejected(self, mock_ssh_connection_manager):
        from src.tools.system import manage_service
        result = await manage_service("nginx", "nuke")

        assert "Error" in result
        assert "action must be one of" in result
