"""
Unit tests for src/tools/sftp.py
"""

import os
from unittest.mock import MagicMock

import pytest


class TestUploadFile:
    @pytest.mark.asyncio
    async def test_local_file_not_found(self, mock_ssh_connection_manager):
        from src.tools.sftp import upload_file
        result = await upload_file("/nonexistent/path/file.txt", "/remote/file.txt")
        assert "local file not found" in result

    @pytest.mark.asyncio
    async def test_upload_success(self, mock_ssh_connection_manager, tmp_path):
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello")

        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()
        client.open_sftp.return_value = mock_sftp

        from src.tools.sftp import upload_file
        result = await upload_file(str(local_file), "/remote/test.txt")

        mock_sftp.put.assert_called_once_with(str(local_file), "/remote/test.txt")
        assert "Uploaded" in result

    @pytest.mark.asyncio
    async def test_upload_sftp_error(self, mock_ssh_connection_manager, tmp_path):
        local_file = tmp_path / "test.txt"
        local_file.write_text("hello")

        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()
        mock_sftp.put.side_effect = IOError("permission denied")
        client.open_sftp.return_value = mock_sftp

        from src.tools.sftp import upload_file
        result = await upload_file(str(local_file), "/remote/test.txt")

        assert "Error uploading file" in result


class TestDownloadFile:
    @pytest.mark.asyncio
    async def test_download_success(self, mock_ssh_connection_manager, tmp_path):
        local_dest = str(tmp_path / "downloaded.txt")

        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()

        def fake_get(remote, local):
            with open(local, "w") as f:
                f.write("content")

        mock_sftp.get.side_effect = fake_get
        client.open_sftp.return_value = mock_sftp

        from src.tools.sftp import download_file
        result = await download_file("/remote/file.txt", local_dest)

        assert "Downloaded" in result
        assert os.path.exists(local_dest)

    @pytest.mark.asyncio
    async def test_download_error(self, mock_ssh_connection_manager, tmp_path):
        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()
        mock_sftp.get.side_effect = FileNotFoundError("remote not found")
        client.open_sftp.return_value = mock_sftp

        from src.tools.sftp import download_file
        result = await download_file("/remote/missing.txt", str(tmp_path / "out.txt"))

        assert "Error downloading file" in result


class TestGetFileInfo:
    @pytest.mark.asyncio
    async def test_file_info(self, mock_ssh_connection_manager):

        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()
        attrs = MagicMock()
        attrs.st_size = 1024
        attrs.st_mode = 0o100644
        attrs.st_uid = 0
        attrs.st_gid = 0
        attrs.st_mtime = 1700000000.0
        mock_sftp.stat.return_value = attrs
        client.open_sftp.return_value = mock_sftp

        from src.tools.sftp import get_file_info
        result = await get_file_info("/etc/hosts")

        assert "1,024" in result or "1024" in result
        assert "/etc/hosts" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self, mock_ssh_connection_manager):
        client = mock_ssh_connection_manager
        mock_sftp = MagicMock()
        mock_sftp.stat.side_effect = FileNotFoundError("not found")
        client.open_sftp.return_value = mock_sftp

        from src.tools.sftp import get_file_info
        result = await get_file_info("/no/such/file")

        assert "Error getting file info" in result
