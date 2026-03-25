from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Iterable, List

from .config import OrganizerConfig
from .models import ActionType, MediaFile, MediaType
from .parsers import parse_media_file
from .providers import get_provider

logger = logging.getLogger(__name__)


def _render_movie_pattern(pattern: str, media: MediaFile) -> str:
    assert media.movie is not None
    movie = media.movie
    year_part = f" ({movie.year})" if movie.year is not None else ""
    year = movie.year if movie.year is not None else ""
    original_name = media.source_path.stem
    original_basename = media.source_path.name
    return pattern.format(
        title=movie.title,
        year=year,
        year_part=year_part,
        ext=media.source_path.suffix.lstrip("."),
        original_name=original_name,
        original_basename=original_basename,
    )


def _render_tv_pattern(pattern: str, media: MediaFile) -> str:
    assert media.episode is not None
    ep = media.episode
    title_suffix = f" - {ep.title}" if ep.title else ""
    original_name = media.source_path.stem
    original_basename = media.source_path.name
    return pattern.format(
        series_title=ep.series_title,
        season=ep.season,
        episode=ep.episode,
        title_suffix=title_suffix,
        ext=media.source_path.suffix.lstrip("."),
        original_name=original_name,
        original_basename=original_basename,
    )


def build_target_path(config: OrganizerConfig, media: MediaFile) -> Path:
    if media.media_type == MediaType.MOVIE:
        rel = _render_movie_pattern(config.pattern_movie, media)
    else:
        rel = _render_tv_pattern(config.pattern_tv, media)
    return config.dest_root / rel


def apply_action(action: ActionType, src: Path, dest: Path) -> None:
    if action == ActionType.DRY_RUN:
        return

    # Safety: never overwrite when using move or hardlink.
    # (copy is intentionally left as-is for now)
    if action in (ActionType.MOVE, ActionType.LINK) and dest.exists():
        logger.info(
            "Skipping %s -> %s (%s): destination already exists",
            src,
            dest,
            action.value,
        )
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating destination directory: {dest.parent}")
    if action == ActionType.MOVE:
        logger.info(f"Moving {src} to {dest}")
        shutil.move(str(src), str(dest))
    elif action == ActionType.COPY:
        logger.info(f"Copying {src} to {dest}")
        shutil.copy2(str(src), str(dest))
    elif action == ActionType.LINK:
        logger.info(f"Linking {src} to {dest}")
        os.link(src, dest)


def organize_files(config: OrganizerConfig, paths: Iterable[Path]) -> List[tuple[Path, Path]]:
    provider = get_provider(config.provider) if config.use_metadata else None
    results: List[tuple[Path, Path]] = []

    for path in paths:
        media = parse_media_file(path, config.media_type)
        if not media:
            continue

        if provider:
            if media.media_type == MediaType.MOVIE and media.movie:
                media.movie = provider.lookup_movie(media.movie)
            elif media.media_type == MediaType.TV and media.episode:
                media.episode = provider.lookup_episode(media.episode)

        target = build_target_path(config, media)
        apply_action(config.action, media.source_path, target)
        results.append((media.source_path, target))

    return results


def organize_path(config: OrganizerConfig) -> List[tuple[Path, Path]]:
    all_paths: List[Path] = []
    for root, _, files in os.walk(config.source_root):
        for name in files:
            all_paths.append(Path(root) .joinpath(name))
    return organize_files(config, all_paths)

