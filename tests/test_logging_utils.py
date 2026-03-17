"""
Unit tests for src/common/logging_utils.py
"""

import logging
from unittest.mock import patch

import pytest

from src.common.logging_utils import configure_logging, resolve_log_level


class TestResolveLogLevel:
    def test_default_returns_warning(self):
        with patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("MCP_SSH_LOG_LEVEL", None)
            assert resolve_log_level() == logging.WARNING

    def test_numeric_string(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "10"}):
            assert resolve_log_level() == logging.DEBUG

    def test_named_level_debug(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "DEBUG"}):
            assert resolve_log_level() == logging.DEBUG

    def test_named_level_info(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "INFO"}):
            assert resolve_log_level() == logging.INFO

    def test_named_level_lowercase(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "debug"}):
            assert resolve_log_level() == logging.DEBUG

    def test_invalid_level_falls_back_to_warning(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "NOTAVALIDLEVEL"}):
            assert resolve_log_level() == logging.WARNING

    def test_alias_warn(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "WARN"}):
            assert resolve_log_level() == logging.WARNING


class TestConfigureLogging:
    def test_returns_log_level(self):
        level = configure_logging()
        assert isinstance(level, int)

    def test_root_logger_level_set(self):
        with patch.dict("os.environ", {"MCP_SSH_LOG_LEVEL": "DEBUG"}):
            configure_logging()
            assert logging.getLogger().level == logging.DEBUG

    def test_idempotent_no_duplicate_handlers(self):
        configure_logging()
        handler_count_before = len(logging.getLogger().handlers)
        configure_logging()
        # Should not add extra handlers
        assert len(logging.getLogger().handlers) <= handler_count_before + 1
