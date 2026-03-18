"""
Unit tests for src/tools/file.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from tests.conftest import make_exec_result


class TestReadFile:
    @pytest.mark.asyncio
    async def test_reads_with_head(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="line1\nline2")

        from src.tools.file import read_file
        result = await read_file("/etc/hosts", max_lines=10)

        assert "line1" in result
        cmd = client.exec_command.call_args[0][0]
        assert "head -10" in cmd

    @pytest.mark.asyncio
    async def test_reads_unlimited(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="all content")

        from src.tools.file import read_file
        await read_file("/etc/hosts", max_lines=0)

        cmd = client.exec_command.call_args[0][0]
        assert "cat" in cmd


class TestWriteFile:
    @pytest.mark.asyncio
    async def test_write_success(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        # mkdir -p
        client.exec_command.return_value = make_exec_result(stdout="")

        mock_sftp = MagicMock()
        mock_file = MagicMock()
        mock_sftp.__enter__ = Mock(return_value=mock_sftp)
        mock_sftp.__exit__ = Mock(return_value=False)
        mock_sftp.open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_sftp.open.return_value.__exit__ = Mock(return_value=False)
        client.open_sftp.return_value = mock_sftp

        from src.tools.file import write_file
        result = await write_file("/tmp/test.txt", "hello")

        assert "wrote" in result.lower() or "successfully" in result.lower()

    @pytest.mark.asyncio
    async def test_refuses_root_path(self, mock_ssh_connection_manager):
        from src.tools.file import delete_file
        result = await delete_file("/")
        assert "refusing" in result.lower() or "Error" in result


class TestDeleteFile:
    @pytest.mark.asyncio
    async def test_refuses_root(self, mock_ssh_connection_manager):
        from src.tools.file import delete_file
        for dangerous in ("/", "~", "."):
            result = await delete_file(dangerous)
            assert "refusing" in result.lower() or "Error" in result

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="Deleted: /tmp/test.txt")

        from src.tools.file import delete_file
        result = await delete_file("/tmp/test.txt")

        assert "Deleted" in result

    @pytest.mark.asyncio
    async def test_delete_recursive(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="Deleted: /tmp/mydir")

        from src.tools.file import delete_file
        await delete_file("/tmp/mydir", recursive=True)

        cmd = client.exec_command.call_args[0][0]
        assert "-rf" in cmd

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("no conn"),
        ):
            from src.tools.file import delete_file
            result = await delete_file("/tmp/test.txt")
        assert "Error deleting" in result


class TestAppendFile:
    @pytest.mark.asyncio
    async def test_append_success(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()
        mock_file = MagicMock()
        mock_sftp.open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_sftp.open.return_value.__exit__ = Mock(return_value=False)
        client.open_sftp.return_value = mock_sftp

        from src.tools.file import append_file
        result = await append_file("/tmp/log.txt", "new line\n")

        assert "appended" in result.lower() or "Successfully" in result

    @pytest.mark.asyncio
    async def test_error_handled(self):
        with patch(
            "src.common.connection.SSHConnectionManager.get_connection",
            side_effect=Exception("no conn"),
        ):
            from src.tools.file import append_file
            result = await append_file("/tmp/log.txt", "data")
        assert "Error appending" in result


class TestListDirectory:
    @pytest.mark.asyncio
    async def test_returns_listing(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="drwxr-xr-x 2 root root 4096 Jan 1 /etc"
        )

        from src.tools.file import list_directory
        result = await list_directory("/etc")

        assert "root" in result


class TestSearchFiles:
    @pytest.mark.asyncio
    async def test_finds_files(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="/var/log/nginx/error.log"
        )

        from src.tools.file import search_files
        result = await search_files("/var/log", "*.log")

        assert "error.log" in result

    @pytest.mark.asyncio
    async def test_no_match(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="")

        from src.tools.file import search_files
        result = await search_files("/var/log", "*.xyz")

        assert "No files matching" in result


class TestGrepFile:
    @pytest.mark.asyncio
    async def test_match_found(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(
            stdout="/etc/hosts:1:127.0.0.1 localhost"
        )

        from src.tools.file import grep_file
        result = await grep_file("/etc/hosts", "localhost")

        assert "localhost" in result

    @pytest.mark.asyncio
    async def test_no_match(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        client.exec_command.return_value = make_exec_result(stdout="")

        from src.tools.file import grep_file
        result = await grep_file("/etc/hosts", "XYZNOTHERE")

        assert "No matches" in result
