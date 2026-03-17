"""
Unit tests for src/common/connection.py
"""

import os
from unittest.mock import MagicMock, Mock, patch

import paramiko
import pytest

from src.common.connection import SSHConnectionManager


class TestSSHConnectionManager:
    def setup_method(self):
        SSHConnectionManager._instances.clear()

    def teardown_method(self):
        SSHConnectionManager._instances.clear()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _base_cfg(self, **overrides):
        cfg = {
            "host": "192.168.1.1",
            "port": 22,
            "username": "root",
            "password": None,
            "key_file": None,
            "key_passphrase": None,
            "timeout": 30,
            "ignore_known_hosts": True,
            "known_hosts_file": None,
        }
        cfg.update(overrides)
        return cfg

    # ── basic connection ──────────────────────────────────────────────────────

    @patch("src.common.connection.paramiko.SSHClient")
    def test_get_connection_default_host(self, mock_client_cls):
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        with patch.dict("src.common.connection.SSH_CFG", self._base_cfg(), clear=True):
            client = SSHConnectionManager.get_connection()

        assert client is mock_client
        mock_client.connect.assert_called_once()
        call_kw = mock_client.connect.call_args[1]
        assert call_kw["hostname"] == "192.168.1.1"
        assert call_kw["port"] == 22
        assert call_kw["username"] == "root"

    @patch("src.common.connection.paramiko.SSHClient")
    def test_get_connection_reuses_active_connection(self, mock_client_cls):
        mock_client = Mock()
        transport = Mock()
        transport.is_active.return_value = True
        mock_client.get_transport.return_value = transport
        SSHConnectionManager._instances["__default__"] = mock_client

        with patch.dict("src.common.connection.SSH_CFG", self._base_cfg(), clear=True):
            result = SSHConnectionManager.get_connection()

        assert result is mock_client
        mock_client_cls.assert_not_called()

    @patch("src.common.connection.paramiko.SSHClient")
    def test_get_connection_reconnects_on_dead_transport(self, mock_client_cls):
        old_client = Mock()
        transport = Mock()
        transport.is_active.return_value = False
        old_client.get_transport.return_value = transport
        SSHConnectionManager._instances["__default__"] = old_client

        new_client = Mock()
        mock_client_cls.return_value = new_client

        with patch.dict("src.common.connection.SSH_CFG", self._base_cfg(), clear=True):
            result = SSHConnectionManager.get_connection()

        assert result is new_client
        new_client.connect.assert_called_once()

    # ── named host ────────────────────────────────────────────────────────────

    @patch("src.common.connection.paramiko.SSHClient")
    def test_get_connection_named_host(self, mock_client_cls):
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        named = {"host": "10.0.0.2", "port": 2222, "username": "admin", "ignore_known_hosts": True}
        with patch.dict("src.common.connection.SSH_CFG", self._base_cfg(), clear=True), \
             patch.dict("src.common.connection.SSH_HOSTS", {"myserver": named}, clear=True):
            result = SSHConnectionManager.get_connection("myserver")

        assert result is mock_client
        kw = mock_client.connect.call_args[1]
        assert kw["hostname"] == "10.0.0.2"
        assert kw["port"] == 2222
        assert kw["username"] == "admin"

    @patch("src.common.connection.paramiko.SSHClient")
    def test_named_host_ignore_known_hosts_uses_per_host_cfg(self, mock_client_cls):
        """ignore_known_hosts from per-host cfg should override SSH_CFG."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        # default SSH_CFG has ignore_known_hosts=False; named host overrides to True
        default_cfg = self._base_cfg(ignore_known_hosts=False)
        named = {"host": "10.0.0.3", "port": 22, "username": "root", "ignore_known_hosts": True}

        with patch.dict("src.common.connection.SSH_CFG", default_cfg, clear=True), \
             patch.dict("src.common.connection.SSH_HOSTS", {"srv": named}, clear=True):
            SSHConnectionManager.get_connection("srv")

        # AutoAddPolicy() creates a new object each time; check the type instead
        call_args = mock_client.set_missing_host_key_policy.call_args
        assert call_args is not None
        assert isinstance(call_args[0][0], paramiko.AutoAddPolicy)

    # ── key auth ──────────────────────────────────────────────────────────────

    @patch("src.common.connection.paramiko.SSHClient")
    @patch("os.path.expanduser", side_effect=lambda p: p)
    def test_key_file_used_when_provided(self, _expand, mock_client_cls):
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        cfg = self._base_cfg(key_file="~/.ssh/id_rsa")
        with patch.dict("src.common.connection.SSH_CFG", cfg, clear=True):
            SSHConnectionManager.get_connection()

        kw = mock_client.connect.call_args[1]
        assert kw["key_filename"] == "~/.ssh/id_rsa"
        assert "password" not in kw

    @patch("src.common.connection.paramiko.SSHClient")
    def test_password_used_when_no_key_file(self, mock_client_cls):
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        cfg = self._base_cfg(password="secret")
        with patch.dict("src.common.connection.SSH_CFG", cfg, clear=True):
            SSHConnectionManager.get_connection()

        kw = mock_client.connect.call_args[1]
        assert kw["password"] == "secret"

    # ── close ─────────────────────────────────────────────────────────────────

    def test_close_connection_removes_instance(self):
        mock_client = Mock()
        SSHConnectionManager._instances["__default__"] = mock_client

        SSHConnectionManager.close_connection()

        mock_client.close.assert_called_once()
        assert "__default__" not in SSHConnectionManager._instances

    def test_close_all_clears_all_instances(self):
        c1, c2 = Mock(), Mock()
        SSHConnectionManager._instances["__default__"] = c1
        SSHConnectionManager._instances["srv2"] = c2

        SSHConnectionManager.close_all()

        c1.close.assert_called_once()
        c2.close.assert_called_once()
        assert SSHConnectionManager._instances == {}

    def test_close_nonexistent_connection_is_noop(self):
        # Should not raise even if there is no active connection
        SSHConnectionManager.close_connection("nonexistent")

    # ── error propagation ─────────────────────────────────────────────────────

    @patch("src.common.connection.paramiko.SSHClient")
    def test_auth_failure_raises(self, mock_client_cls):
        mock_client = Mock()
        mock_client.connect.side_effect = paramiko.AuthenticationException("Bad creds")
        mock_client_cls.return_value = mock_client

        with patch.dict("src.common.connection.SSH_CFG", self._base_cfg(), clear=True):
            with pytest.raises(paramiko.AuthenticationException):
                SSHConnectionManager.get_connection()
