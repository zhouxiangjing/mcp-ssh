import logging
import os
import sys


def resolve_log_level() -> int:
    """Resolve desired log level from MCP_SSH_LOG_LEVEL.

    Accepts numeric strings or standard level names (DEBUG, INFO, WARNING,
    ERROR, CRITICAL, NOTSET) including aliases WARN and FATAL. Defaults to WARNING.
    """
    name = os.getenv("MCP_SSH_LOG_LEVEL")
    if name:
        s = name.strip()
        try:
            return int(s)
        except ValueError:
            pass
        level = getattr(logging, s.upper(), None)
        if isinstance(level, int):
            return level
    return logging.WARNING


def configure_logging() -> int:
    """Configure logging based on environment.

    - Default level WARNING
    - MCP_SSH_LOG_LEVEL to override

    Returns the resolved log level. Idempotent.
    """
    level = resolve_log_level()
    root = logging.getLogger()

    root.setLevel(level)

    # Only lower overly-restrictive handler thresholds; do not raise them.
    for h in root.handlers:
        try:
            cur = getattr(h, "level", None)
            if isinstance(cur, int) and cur != logging.NOTSET and cur > level:
                h.setLevel(level)
        except Exception:
            logging.getLogger(__name__).debug(
                "Failed to adjust handler level for handler %r", h, exc_info=True
            )

    # Only add our own stderr handler if there are NO handlers at all.
    if not root.handlers:
        sh = logging.StreamHandler(sys.stderr)
        sh.setLevel(level)
        sh.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        root.addHandler(sh)

    logging.captureWarnings(True)

    return level
