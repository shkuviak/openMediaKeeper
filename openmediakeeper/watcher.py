from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import OrganizerConfig
from .organizer import organize_files

logger = logging.getLogger(__name__)


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, config: OrganizerConfig) -> None:
        super().__init__()
        self.config = config

    def on_created(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        path = Path(event.src_path)
        logger.info("New file detected: %s", path)
        try:
            organize_files(self.config, [path])
        except Exception:
            logger.exception("Failed to organize new file: %s", path)


def watch_path(config: OrganizerConfig) -> None:
    handler = NewFileHandler(config)
    observer = Observer()
    observer.schedule(handler, str(config.source_root), recursive=True)
    observer.start()
    try:
        while True:
            observer.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

