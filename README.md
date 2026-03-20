# openMediaKeeper

Python backend and CLI to organize a local media library (movies and TV shows) in an automated and extensible way, inspired by tools like FileBot.

The backend is designed to:

- Watch a folder for new media files and organize them automatically
- Run one-off organization passes over an existing folder
- Move, copy, or hardlink files into a clean folder structure
- Normalize titles and years using external metadata sources (e.g. IMDb via OMDb)
- Be API-ready so a web UI can be added later

## Features (initial)

- CLI built with `typer`
- Pluggable metadata providers (OMDb to start)
- Basic filename parsing for movies and TV shows
- Configurable organization actions:
  - Move
  - Copy
  - Hardlink
  - Dry-run
- Optional folder watching using `watchdog`

## Quick start (with `uv`)

```bash
cd openMediaKeeper

# Install dependencies into an isolated environment
uv sync

# Example: organize a folder of movies into /media/movies using move
uv run omk scan /path/to/downloads \
  --media-type movie \
  --dest /media/movies \
  --action move
```

## CLI overview

- `scan PATH`
  - Scan an existing folder and organize discovered media files.
- `watch PATH`
  - Watch a folder for newly created media files and organize them as they appear.

Shared options (subject to change as the project evolves):

- `--media-type`: `movie`, `tv`, or `auto`
- `--dest`: destination root folder for organized media
- `--action`: `move`, `copy`, `link`, or `dry-run`
- `--pattern-movie`: override movie target pattern (template variables supported, see below)
- `--pattern-tv`: override TV target pattern (template variables supported, see below)
- `--use-metadata`: enable/disable metadata enrichment (provider-dependent)
- `--provider`: metadata provider name (currently `omdb` or `noop`)
- `--log-level`: `INFO`/`DEBUG`/... (defaults to `OMK_LOG_LEVEL` or `INFO`)

Available pattern variables include:

- Movies:
  - `{title}`, `{year}`, `{year_part}`, `{ext}`
  - `{original_name}` (filename without extension)
  - `{original_basename}` (full original filename with extension)
- TV:
  - `{series_title}`, `{season}`, `{episode}`, `{title_suffix}`, `{ext}`
  - `{original_name}`, `{original_basename}`

### Pattern examples

Movies example (use original filename in the leaf):

`Movies/{title}{year_part}/{original_basename}`

Movies example (default-like layout, with optional year):

`Movies/{title}{year_part}/{title}{year_part}.{ext}`

TV example (include parsed episode title when available):

`TV/{series_title}/Season {season:02d}/{series_title} - S{season:02d}E{episode:02d}{title_suffix}.{ext}`

TV example (keep original basename):

`TV/{series_title}/Season {season:02d}/{original_basename}`

## API readiness

The core logic (parsing, metadata lookup, and path computation) is implemented in reusable modules and a small FastAPI app is provided in `openmediakeeper/api.py`.

Run the API with:

```bash
uv run uvicorn openmediakeeper.api:app --reload
```

You can then call `POST /organize` with JSON describing `source_paths`, `dest_root`, and options like `media_type` / `action`.

## Logging strategy

Logging is done with Python's standard `logging` module and per-module loggers (`logger = logging.getLogger(__name__)`).

- Default level is `INFO` (or override with the CLI option `--log-level` or env var `OMK_LOG_LEVEL`).
- Use `INFO` for user-visible operational events (e.g. skipped `move`/`link` because the destination already exists).
- Use `DEBUG` for troubleshooting (e.g. parser details when a filename can't be parsed).
- Failures are logged with `logger.exception(...)` in long-running processes (e.g. the folder watcher) so you can see stack traces.


