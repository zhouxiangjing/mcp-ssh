"""Unit tests for src/version.py"""

from src.version import __version__


class TestVersion:
    def test_version_is_string(self):
        assert isinstance(__version__, str)

    def test_version_not_empty(self):
        assert len(__version__) > 0

    def test_version_format(self):
        # Should be semver-like: X.Y.Z or X.Y.Z-dev
        parts = __version__.split("-")[0].split(".")
        assert len(parts) >= 2
        for part in parts:
            assert part.isdigit(), f"Non-numeric version part: {part}"
