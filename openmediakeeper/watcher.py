from __future__ import annotations

import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from .config import OrganizerConfig
from .organizer import organize_files
from .parsers import is_video_file

logger = logging.getLogger(__name__)


def _make_observer(config: OrganizerConfig) -> Observer:
    if config.watch_poll:
        logger.info(
            "Using polling observer (watch_poll=True); use for Docker bind mounts, NFS, "
            "or other setups where native file events are missing."
        )
        return PollingObserver(timeout=1.0)
    return Observer()


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, config: OrganizerConfig) -> None:
        super().__init__()
        self.config = config

    def _organize_path(self, path: Path, reason: str) -> None:
        try:
            path = path.resolve()
        except OSError:
            logger.warning("Could not resolve path: %s", path)
            return
        logger.info("%s: %s", reason, path)
        if not path.is_file():
            logger.debug("Skip (not a regular file or missing): %s", path)
            return
        try:
            results = organize_files(self.config, [path])
        except Exception:
            logger.exception("Failed to organize file: %s", path)
            return
        if not results:
            if is_video_file(path):
                logger.info(
                    "No organize action for video file (name may not match movie/TV patterns "
                    "or media-type filter): %s",
                    path,
                )
            else:
                logger.debug("Ignored (not a known video extension): %s", path)

    def on_created(self, event) -> None:  # type: ignore[override]
        if event.is_directory:
            return
        self._organize_path(Path(event.src_path), "New file detected")

    def on_moved(self, event) -> None:  # type: ignore[override]
        # Torrent clients often write to a temp name then rename on completion;
        # the final media path appears as the move destination.
        if event.is_directory:
            return
        dest = getattr(event, "dest_path", None)
        if not dest:
            return
        self._organize_path(Path(dest), "File renamed/moved (destination)")


def watch_path(config: OrganizerConfig) -> None:
    handler = NewFileHandler(config)
    observer = _make_observer(config)
    logger.info(
        "Watching %s recursively (poll=%s)",
        config.source_root.resolve(),
        config.watch_poll,
    )
    observer.schedule(handler, str(config.source_root.resolve()), recursive=True)
    observer.start()
    try:
        while True:
            observer.join(timeout=1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

