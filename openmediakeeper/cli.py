from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import typer

from .config import OrganizerConfig
from .models import ActionType, MediaType
from .organizer import organize_path
from .logging_utils import configure_logging
from .watcher import watch_path

app = typer.Typer(help="Automated media library organizer (movies & TV).")

logger = logging.getLogger(__name__)


@app.command()
def scan(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    dest: Path = typer.Option(..., "--dest", "-d", exists=True, file_okay=False, dir_okay=True, help="Destination root for organized media."),
    media_type: MediaType = typer.Option(MediaType.AUTO, "--media-type", "-m", case_sensitive=False),
    action: ActionType = typer.Option(ActionType.DRY_RUN, "--action", "-a", case_sensitive=False),
    pattern_movie: Optional[str] = typer.Option(None, help="Pattern for movies, e.g. 'Movies/{title} ({year})/{title} ({year}).{ext}'"),
    pattern_tv: Optional[str] = typer.Option(None, help="Pattern for TV, e.g. 'TV/{series_title}/Season {season:02d}/{series_title} - S{season:02d}E{episode:02d}{title_suffix}.{ext}'"),
    use_metadata: bool = typer.Option(True, help="Use metadata provider (e.g. OMDb)"),
    provider: str = typer.Option("omdb", help="Metadata provider name, e.g. 'omdb' or 'noop'"),
    log_level: Optional[str] = typer.Option(None, "--log-level", help="Logging level (e.g. INFO, DEBUG). Defaults to OMK_LOG_LEVEL or INFO."),
) -> None:
    """
    Scan a folder and organize all media files found under it.
    """
    config = OrganizerConfig(
        source_root=path,
        dest_root=dest,
        media_type=media_type,
        action=action,
        use_metadata=use_metadata,
        provider=provider,
    )
    if pattern_movie:
        config.pattern_movie = pattern_movie
    if pattern_tv:
        config.pattern_tv = pattern_tv

    configure_logging(log_level)
    logger.info(
        "Scan started: path=%s dest=%s media_type=%s action=%s use_metadata=%s provider=%s",
        path,
        dest,
        media_type.value,
        action.value,
        use_metadata,
        provider,
    )
    results = organize_path(config)
    for src, dst in results:
        typer.echo(f"{action.value.upper()}: {src} -> {dst}")


@app.command()
def watch(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    dest: Path = typer.Option(..., "--dest", "-d", exists=True, file_okay=False, dir_okay=True, help="Destination root for organized media."),
    media_type: MediaType = typer.Option(MediaType.AUTO, "--media-type", "-m", case_sensitive=False),
    action: ActionType = typer.Option(ActionType.DRY_RUN, "--action", "-a", case_sensitive=False),
    pattern_movie: Optional[str] = typer.Option(None),
    pattern_tv: Optional[str] = typer.Option(None),
    use_metadata: bool = typer.Option(True),
    provider: str = typer.Option("omdb"),
    log_level: Optional[str] = typer.Option(None, "--log-level", help="Logging level (e.g. INFO, DEBUG). Defaults to OMK_LOG_LEVEL or INFO."),
) -> None:
    """
    Watch a folder for new media files and organize them as they appear.
    """
    config = OrganizerConfig(
        source_root=path,
        dest_root=dest,
        media_type=media_type,
        action=action,
        use_metadata=use_metadata,
        provider=provider,
    )
    if pattern_movie:
        config.pattern_movie = pattern_movie
    if pattern_tv:
        config.pattern_tv = pattern_tv

    configure_logging(log_level)
    logger.info(
        "Watch started: path=%s dest=%s media_type=%s action=%s use_metadata=%s provider=%s",
        path,
        dest,
        media_type.value,
        action.value,
        use_metadata,
        provider,
    )
    typer.echo(f"Watching {path} for new media files...")
    watch_path(config)


def main() -> None:
    # Commands call `configure_logging()` (so CLI options work), but keep a safe fallback.
    configure_logging()
    app()


if __name__ == "__main__":
    main()

