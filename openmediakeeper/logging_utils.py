from __future__ import annotations

import logging
import os
from typing import Optional


def configure_logging(log_level: Optional[str] = None) -> None:
    """
    Configure Python logging once for CLI usage.

    Strategy:
    - Default to INFO to keep output readable.
    - Allow overriding via `log_level` argument or `OMK_LOG_LEVEL` env var.
    - Use per-module loggers (`logger = logging.getLogger(__name__)`) everywhere else.
    """
    level_name = (log_level or os.getenv("OMK_LOG_LEVEL") or "INFO").upper()
    level = logging._nameToLevel.get(level_name, logging.INFO)

    root = logging.getLogger()
    if root.handlers:
        return

    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s: %(message)s",
    )

