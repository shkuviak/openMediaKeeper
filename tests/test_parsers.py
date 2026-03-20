from pathlib import Path

from openmediakeeper.models import MediaType
from openmediakeeper.parsers import parse_episode_from_filename, parse_media_file, parse_movie_from_filename


def test_parse_movie_extracts_year() -> None:
    movie = parse_movie_from_filename(Path("The.Matrix.1999.mkv"))
    assert movie is not None
    assert movie.title == "The Matrix"
    assert movie.year == 1999

def test_parse_movie_year_and_resolution() -> None:
    movie = parse_movie_from_filename(Path("Beverly.Hills.Cop.Axel.F.2024.MULTi.FRENCH.2160p.WEB-DL.x265"))
    assert movie is not None
    assert movie.title == "Beverly Hills Cop Axel F"
    assert movie.year == 2024

def test_parse_movie_ignores_resolution_1080p() -> None:
    movie = parse_movie_from_filename(Path("Some.Movie.1080p.BluRay.x264.mkv"))
    assert movie is not None
    assert movie.title == "Some Movie"
    assert movie.year is None


def test_parse_movie_ignores_resolution_2160p() -> None:
    movie = parse_movie_from_filename(Path("Some.Movie.2160p.WEB-DL.mkv"))
    assert movie is not None
    assert movie.title == "Some Movie"
    assert movie.year is None


def test_parse_tv_sxxexx() -> None:
    ep = parse_episode_from_filename(Path("Breaking.Bad.S01E02.mkv"))
    assert ep is not None
    assert ep.series_title == "Breaking Bad"
    assert ep.season == 1
    assert ep.episode == 2


def test_parse_media_file_auto_prefers_tv() -> None:
    media = parse_media_file(Path("Show.Name.S01E01.1080p.mkv"), MediaType.AUTO)
    assert media is not None
    assert media.media_type.value == "tv"
    assert media.episode is not None
    assert media.episode.series_title == "Show Name"

