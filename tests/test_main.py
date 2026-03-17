"""
Unit tests for src/main.py
"""

import logging
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from src.main import SSHMCPServer, cli


class TestSSHMCPServer:
    def test_init_succeeds(self):
        server = SSHMCPServer()
        assert server is not None

    def test_init_logs_startup(self, caplog, monkeypatch):
        monkeypatch.setenv("MCP_SSH_LOG_LEVEL", "INFO")
        with caplog.at_level(logging.INFO):
            SSHMCPServer()
        assert "Starting SSH MCP Server" in caplog.text

    @patch("src.main.mcp.run")
    def test_run_calls_mcp_run(self, mock_run):
        SSHMCPServer().run()
        mock_run.assert_called_once()

    @patch("src.main.mcp.run")
    def test_run_propagates_exception(self, mock_run):
        mock_run.side_effect = RuntimeError("mcp failed")
        with pytest.raises(RuntimeError, match="mcp failed"):
            SSHMCPServer().run()


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    @patch("src.main.set_ssh_config_from_cli")
    @patch("src.main.SSHMCPServer")
    def test_cli_no_args(self, mock_server_cls, mock_set_cfg):
        mock_server_cls.return_value = Mock()
        result = self.runner.invoke(cli, [])
        assert result.exit_code == 0
        mock_set_cfg.assert_called_once()
        mock_server_cls.return_value.run.assert_called_once()

    @patch("src.main.set_ssh_config_from_cli")
    @patch("src.main.SSHMCPServer")
    def test_cli_with_host_port_username(self, mock_server_cls, mock_set_cfg):
        mock_server_cls.return_value = Mock()
        result = self.runner.invoke(
            cli, ["--host", "10.0.0.1", "--port", "2222", "--username", "admin"]
        )
        assert result.exit_code == 0
        cfg = mock_set_cfg.call_args[0][0]
        assert cfg["host"] == "10.0.0.1"
        assert cfg["port"] == 2222
        assert cfg["username"] == "admin"

    @patch("src.main.set_ssh_config_from_cli")
    @patch("src.main.SSHMCPServer")
    def test_cli_with_key_file(self, mock_server_cls, mock_set_cfg):
        mock_server_cls.return_value = Mock()
        result = self.runner.invoke(cli, ["--key-file", "~/.ssh/id_rsa"])
        assert result.exit_code == 0
        cfg = mock_set_cfg.call_args[0][0]
        assert cfg["key_file"] == "~/.ssh/id_rsa"

    @patch("src.main.set_ssh_config_from_cli")
    @patch("src.main.SSHMCPServer")
    def test_cli_ignore_known_hosts_flag(self, mock_server_cls, mock_set_cfg):
        mock_server_cls.return_value = Mock()
        result = self.runner.invoke(cli, ["--ignore-known-hosts"])
        assert result.exit_code == 0
        cfg = mock_set_cfg.call_args[0][0]
        assert cfg["ignore_known_hosts"] is True

    def test_cli_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "--host" in result.output
        assert "--port" in result.output
        assert "--key-file" in result.output

    @patch("src.main.SSHMCPServer")
    def test_cli_server_run_failure(self, mock_server_cls):
        mock_server = Mock()
        mock_server.run.side_effect = RuntimeError("broken")
        mock_server_cls.return_value = mock_server
        result = self.runner.invoke(cli, [])
        assert result.exit_code != 0
