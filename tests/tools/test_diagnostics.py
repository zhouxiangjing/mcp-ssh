"""
Unit tests for src/tools/diagnostics.py
"""

from unittest.mock import patch

import pytest

from tests.conftest import make_exec_result


class TestCheckDiskHealth:
    @pytest.mark.asyncio
    async def test_no_errors(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout=""),   # dmesg
            make_exec_result(stdout=""),   # systemctl --failed
            make_exec_result(stdout="Filesystem /dev/sda1 50% used"),  # df -i
        ]

        from src.tools.diagnostics import check_disk_health
        result = await check_disk_health()

        assert "Kernel Disk Messages" in result
        assert "(none)" in result  # no dmesg errors

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("fail"),
        ):
            from src.tools.diagnostics import check_disk_health
            result = await check_disk_health()
        assert "Error checking disk health" in result


class TestCheckHighLoad:
    @pytest.mark.asyncio
    async def test_returns_load_sections(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="load average: 5.0, 4.5, 4.0"),
            make_exec_result(stdout="USER PID %CPU CMD\nroot 1 99 stress"),
            make_exec_result(stdout="USER PID %MEM CMD\nroot 2 80 java"),
            make_exec_result(stdout=""),
        ]

        from src.tools.diagnostics import check_high_load
        result = await check_high_load()

        assert "Load" in result
        assert "Top CPU Processes" in result
        assert "Top Memory Processes" in result


class TestCheckNetworkConnectivity:
    @pytest.mark.asyncio
    async def test_ping_success(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="4 packets transmitted, 4 received"),
            make_exec_result(stdout="nameserver 8.8.8.8"),
            make_exec_result(stdout="8.8.8.8"),
        ]

        from src.tools.diagnostics import check_network_connectivity
        result = await check_network_connectivity(target="8.8.8.8")

        assert "Ping 8.8.8.8" in result
        assert "4 received" in result


class TestTailLog:
    @pytest.mark.asyncio
    async def test_returns_log_lines(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="line1\nline2\nline3"
        )

        from src.tools.diagnostics import tail_log
        result = await tail_log("/var/log/syslog", lines=3)

        assert "line1" in result
        assert "line3" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("no conn"),
        ):
            from src.tools.diagnostics import tail_log
            result = await tail_log("/var/log/syslog")
        assert "Error tailing log" in result


class TestCheckSecurity:
    @pytest.mark.asyncio
    async def test_returns_all_sections(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="Failed password for root from 1.2.3.4"),
            make_exec_result(stdout="LISTEN 0 128 0.0.0.0:22"),
            make_exec_result(stdout="/usr/bin/sudo"),
            make_exec_result(stdout=""),
            make_exec_result(stdout="root pts/0 Mon Jan  1 00:00"),
        ]

        from src.tools.diagnostics import check_security
        result = await check_security()

        assert "Failed Login" in result
        assert "Listening Ports" in result
        assert "SUID" in result
        assert "Recent Logins" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("refused"),
        ):
            from src.tools.diagnostics import check_security
            result = await check_security()
        assert "Error running security audit" in result


class TestAnalyzeLogErrors:
    @pytest.mark.asyncio
    async def test_counts_errors(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="5"),   # error count
            make_exec_result(stdout="2"),   # warn count
            make_exec_result(stdout="ERROR something bad happened"),
        ]

        from src.tools.diagnostics import analyze_log_errors
        result = await analyze_log_errors("/var/log/app.log")

        assert "5" in result
        assert "ERROR" in result

    @pytest.mark.asyncio
    async def test_no_errors_shows_none(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.side_effect = [
            make_exec_result(stdout="0"),
            make_exec_result(stdout="0"),
            make_exec_result(stdout=""),
        ]

        from src.tools.diagnostics import analyze_log_errors
        result = await analyze_log_errors("/var/log/app.log")

        assert "(none found)" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("no conn"),
        ):
            from src.tools.diagnostics import analyze_log_errors
            result = await analyze_log_errors("/var/log/app.log")
        assert "Error analyzing log" in result
