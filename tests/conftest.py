"""
Pytest configuration and fixtures for SSH MCP Server tests.
"""

from unittest.mock import MagicMock, Mock, patch

import paramiko
import pytest


@pytest.fixture
def mock_ssh_client():
    """Create a mock paramiko SSHClient."""
    client = Mock(spec=paramiko.SSHClient)
    transport = Mock()
    transport.is_active.return_value = True
    client.get_transport.return_value = transport
    return client


@pytest.fixture
def mock_ssh_connection_manager(mock_ssh_client):
    """Mock SSHConnectionManager.get_connection to return a mock SSH client."""
    with patch(
        "src.common.connection.SSHConnectionManager.get_connection"
    ) as mock_get_conn:
        mock_get_conn.return_value = mock_ssh_client
        yield mock_ssh_client


def make_exec_result(stdout: str = "", stderr: str = "", exit_code: int = 0):
    """Helper: build the (stdin, stdout, stderr) triple returned by exec_command."""
    stdin = Mock()
    stdout_mock = Mock()
    stdout_mock.read.return_value = stdout.encode("utf-8")
    stdout_mock.channel.recv_exit_status.return_value = exit_code
    stderr_mock = Mock()
    stderr_mock.read.return_value = stderr.encode("utf-8")
    return stdin, stdout_mock, stderr_mock


@pytest.fixture
def ssh_config():
    """Sample SSH configuration for testing."""
    return {
        "host": "192.168.1.100",
        "port": 22,
        "username": "root",
        "password": None,
        "key_file": None,
        "key_passphrase": None,
        "timeout": 30,
        "ignore_known_hosts": False,
        "known_hosts_file": None,
    }


@pytest.fixture
def ssh_error_scenarios():
    """Common SSH error scenarios for testing."""
    import paramiko
    return {
        "auth_error": paramiko.AuthenticationException("Authentication failed"),
        "no_host": paramiko.NoValidConnectionsError({("127.0.0.1", 22): Exception("Connection refused")}),
        "timeout": paramiko.ssh_exception.SSHException("Timed out"),
        "generic": Exception("Unexpected error"),
    }


@pytest.fixture(autouse=True)
def reset_connection_manager():
    """Reset SSHConnectionManager singleton before each test."""
    from src.common.connection import SSHConnectionManager
    SSHConnectionManager._instances.clear()
    yield
    SSHConnectionManager._instances.clear()


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
