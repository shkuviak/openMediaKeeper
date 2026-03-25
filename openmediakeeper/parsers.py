from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from .models import Episode, MediaFile, MediaType, Movie

logger = logging.getLogger(__name__)


MOVIE_YEAR_PATTERN = re.compile(
    r"^(?P<title>.+?)[ ._]\(?(?P<year>(?:19|20)\d{2})\)?(?!p)\b",
    re.IGNORECASE,
)

RESOLUTION_PATTERN = re.compile(r"\b(?P<res>\d{3,4})p\b", re.IGNORECASE)

EPISODE_PATTERN = re.compile(
    r"^(?P<series>.+?)[ ._\-]+"
    r"[Ss](?P<season>\d{1,2})[ ._\-]*[Ee](?P<episode>\d{1,2})",
    re.IGNORECASE,
)

VIDEO_EXTENSIONS = {
    ".mkv",
    ".mp4",
    ".m4v",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".ts",
    ".m2ts",
}


def is_video_file(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTENSIONS


def parse_movie_from_filename(path: Path) -> Optional[Movie]:
    name = path.stem
    match = MOVIE_YEAR_PATTERN.match(name)
    if match:
        title = re.sub(r"[._\-]+", " ", match.group("title")).strip()
        year = int(match.group("year"))
        return Movie(title=title, year=year)

    # If there's no valid year, still try to extract the title.
    # Common case: "... 1080p ..." or "... 2160p ..." where the 4-digit number
    # belongs to resolution and should not be interpreted as a year.
    res_match = RESOLUTION_PATTERN.search(name)
    title_part = name if not res_match else name[: res_match.start()]
    title_part = re.sub(r"[ ._\-]+$", "", title_part)

    if not title_part:
        logger.debug("Could not extract movie title from filename: %s", path.name)
        return None

    title = re.sub(r"[._\-]+", " ", title_part)
    title = re.sub(r"\s+", " ", title).strip()
    return Movie(title=title, year=None)


def parse_episode_from_filename(path: Path) -> Optional[Episode]:
    name = path.stem
    match = EPISODE_PATTERN.match(name)
    if not match:
        return None
    series = re.sub(r"[._]+", " ", match.group("series")).strip()
    season = int(match.group("season"))
    episode = int(match.group("episode"))
    return Episode(series_title=series, season=season, episode=episode)


def parse_media_file(path: Path, media_type: MediaType) -> Optional[MediaFile]:
    if not is_video_file(path):
        return None

    if media_type == MediaType.MOVIE:
        movie = parse_movie_from_filename(path)
        if not movie:
            return None
        return MediaFile(source_path=path, media_type=MediaType.MOVIE, movie=movie)

    if media_type == MediaType.TV:
        episode = parse_episode_from_filename(path)
        if not episode:
            return None
        return MediaFile(source_path=path, media_type=MediaType.TV, episode=episode)

    # AUTO: try TV first, then movie
    episode = parse_episode_from_filename(path)
    if episode:
        return MediaFile(source_path=path, media_type=MediaType.TV, episode=episode)

    movie = parse_movie_from_filename(path)
    if movie:
        return MediaFile(source_path=path, media_type=MediaType.MOVIE, movie=movie)

    return None

