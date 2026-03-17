"""
Unit tests for src/tools/connection_mgmt.py
"""

from unittest.mock import patch

import pytest

from tests.conftest import make_exec_result


class TestTestConnection:
    @pytest.mark.asyncio
    async def test_connection_ok(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result("myhost\nroot\n up 1 day")

        from src.tools.connection_mgmt import test_connection
        result = await test_connection()

        assert "Connection OK" in result
        assert "myhost" in result

    @pytest.mark.asyncio
    async def test_connection_failed(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("Connection refused"),
        ):
            from src.tools.connection_mgmt import test_connection
            result = await test_connection()

        assert "Connection FAILED" in result
        assert "Connection refused" in result


class TestListConfiguredHosts:
    @pytest.mark.asyncio
    async def test_no_named_hosts(self):
        with patch.dict("src.common.config.SSH_HOSTS", {}, clear=True), \
             patch.dict(
                 "src.common.config.SSH_CFG",
                 {"host": "1.2.3.4", "port": 22, "username": "root"},
                 clear=False,
             ):
            from src.tools.connection_mgmt import list_configured_hosts
            result = await list_configured_hosts()
        assert "No named hosts" in result
        assert "1.2.3.4" in result

    @pytest.mark.asyncio
    async def test_with_named_hosts(self):
        hosts = {
            "web": {"host": "10.0.0.1", "port": 22, "username": "admin"},
        }
        with patch("src.tools.connection_mgmt.SSH_HOSTS", hosts):
            from src.tools.connection_mgmt import list_configured_hosts
            result = await list_configured_hosts()
        assert "web" in result
        assert "10.0.0.1" in result


class TestCloseConnection:
    @pytest.mark.asyncio
    async def test_close_default(self):
        with patch("src.common.connection.SSHConnectionManager.close_connection") as mock_close:
            from src.tools.connection_mgmt import close_connection
            result = await close_connection()
        mock_close.assert_called_once_with(None)
        assert "closed" in result.lower()

    @pytest.mark.asyncio
    async def test_close_named(self):
        with patch("src.common.connection.SSHConnectionManager.close_connection") as mock_close:
            from src.tools.connection_mgmt import close_connection
            result = await close_connection("myserver")
        mock_close.assert_called_once_with("myserver")
        assert "myserver" in result


class TestCloseAllConnections:
    @pytest.mark.asyncio
    async def test_close_all(self):
        with patch("src.common.connection.SSHConnectionManager.close_all") as mock_all:
            from src.tools.connection_mgmt import close_all_connections
            result = await close_all_connections()
        mock_all.assert_called_once()
        assert "closed" in result.lower()
