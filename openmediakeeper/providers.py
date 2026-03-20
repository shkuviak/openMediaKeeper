from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

import requests

from .models import Episode, Movie

logger = logging.getLogger(__name__)


class MetadataProvider(ABC):
    @abstractmethod
    def lookup_movie(self, movie: Movie) -> Movie:
        ...

    @abstractmethod
    def lookup_episode(self, episode: Episode) -> Episode:
        ...


class NoopProvider(MetadataProvider):
    def lookup_movie(self, movie: Movie) -> Movie:
        return movie

    def lookup_episode(self, episode: Episode) -> Episode:
        return episode


class OmdbProvider(MetadataProvider):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("OMDB_API_KEY")

    def _request(self, params: dict) -> Optional[dict]:
        if not self.api_key:
            logger.warning("OMDb provider enabled but OMDB_API_KEY is not set; skipping metadata lookup.")
            return None
        params = {**params, "apikey": self.api_key}
        try:
            resp = requests.get("https://www.omdbapi.com/", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("Response") != "True":
                return None
            return data
        except Exception:
            logger.debug("OMDb request failed for params=%s", params, exc_info=True)
            return None

    def lookup_movie(self, movie: Movie) -> Movie:
        params = {"t": movie.title}
        if movie.year:
            params["y"] = movie.year
        data = self._request(params)
        if not data:
            return movie
        return Movie(
            title=data.get("Title") or movie.title,
            year=int(data["Year"].split("–")[0]) if data.get("Year") else movie.year,
            imdb_id=data.get("imdbID") or movie.imdb_id,
        )

    def lookup_episode(self, episode: Episode) -> Episode:
        # OMDb has an episode API, but for now keep it simple and just enrich series title/year if possible.
        params = {"t": episode.series_title}
        data = self._request(params)
        if not data:
            return episode
        return Episode(
            series_title=data.get("Title") or episode.series_title,
            season=episode.season,
            episode=episode.episode,
            title=episode.title,
            year=int(data["Year"].split("–")[0]) if data.get("Year") else episode.year,
            imdb_id=data.get("imdbID") or episode.imdb_id,
        )


def get_provider(name: str) -> MetadataProvider:
    if name.lower() == "omdb":
        return OmdbProvider()
    return NoopProvider()

