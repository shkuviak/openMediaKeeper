from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MediaType(str, Enum):
    MOVIE = "movie"
    TV = "tv"
    AUTO = "auto"


class ActionType(str, Enum):
    MOVE = "move"
    COPY = "copy"
    LINK = "link"
    DRY_RUN = "dry-run"


class Movie(BaseModel):
    title: str
    year: Optional[int] = None
    imdb_id: Optional[str] = None


class Episode(BaseModel):
    series_title: str
    season: int
    episode: int
    title: Optional[str] = None
    year: Optional[int] = None
    imdb_id: Optional[str] = None


class MediaFile(BaseModel):
    source_path: Path
    media_type: MediaType
    movie: Optional[Movie] = None
    episode: Optional[Episode] = None

