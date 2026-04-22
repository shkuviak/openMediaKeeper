# openMediaKeeper

Organize movie and TV files automatically from the command line.

`openMediaKeeper` is a Python backend + CLI inspired by tools like FileBot. It can scan folders, watch ongoing downloads, and move/copy/hardlink media files into clean library paths using customizable templates.

## What it does

- Organizes movies and TV episodes from filenames
- Supports `move`, `copy`, `link`, and `dry-run`
- Watches folders recursively for:
  - newly created files
  - renamed files (common with torrent clients on download completion)
- Enriches metadata using OMDb (optional)
- Exposes reusable core modules for future web/API workflows

## Install

This project uses `uv`.

```bash
git clone <your-repo-url>
cd openMediaKeeper
uv sync
```

## Quick start

Preview what would happen (safe):

```bash
uv run omk scan /path/to/downloads \
  --dest /path/to/library \
  --media-type auto \
  --action dry-run
```

Apply real changes:

```bash
uv run omk scan /path/to/downloads \
  --dest /path/to/library \
  --media-type auto \
  --action move
```

Watch a folder continuously:

```bash
uv run omk watch /path/to/watch \
  --dest /path/to/library \
  --media-type auto \
  --action move
```

## CLI commands

### `scan PATH`

Scan all files under `PATH` and organize matched media files.

### `watch PATH`

Watch `PATH` recursively for create/rename events and organize as files appear.

- If your filesystem misses native events (common with Docker bind mounts, NFS, VM shares), use polling:
  - `--poll`
  - or set `OMK_WATCH_POLL=1`

## Common CLI options

- `--dest`, `-d`: destination library root (required)
- `--media-type`, `-m`: `movie`, `tv`, or `auto`
- `--action`, `-a`: `move`, `copy`, `link`, `dry-run`
- `--pattern-movie`: custom movie output template
- `--pattern-tv`: custom TV output template
- `--use-metadata`: enable/disable metadata provider lookup
- `--provider`: metadata provider name (`omdb` or `noop`)
- `--log-level`: logging level (`INFO`, `DEBUG`, etc.)
- `watch` only: `--poll` / `--no-poll`

## Pattern variables

### Movie pattern variables

- `{title}`
- `{year}`
- `{year_part}` (either ` (YYYY)` or empty)
- `{ext}`
- `{original_name}` (source filename without extension)
- `{original_basename}` (source filename with extension)

### TV pattern variables

- `{series_title}`
- `{season}`
- `{episode}`
- `{title_suffix}` (episode title formatted as ` - <title>`, or empty)
- `{ext}`
- `{original_name}`
- `{original_basename}`

### Pattern examples

Movie (preserve original filename):

`Movies/{title}{year_part}/{original_basename}`

Movie (default behavior):

`Movies/{title}{year_part}/{title}{year_part}.{ext}`

TV (default behavior):

`TV/{series_title}/Season {season:02d}/{series_title} - S{season:02d}E{episode:02d}{title_suffix}.{ext}`

TV (preserve original filename):

`TV/{series_title}/Season {season:02d}/{original_basename}`

## Logging and troubleshooting

- Default logging level is `INFO`
- Override via:
  - `--log-level DEBUG`
  - `OMK_LOG_LEVEL=DEBUG`
- Typical watcher debug flow:
  1. Confirm you see `New file detected` or `File renamed/moved`
  2. If no watcher events appear, use `--poll`
  3. If events appear but files are skipped, run with `--log-level DEBUG`

## API usage (optional)

A minimal FastAPI app is available in `openmediakeeper/api.py`.

Run API server:

```bash
uv run uvicorn openmediakeeper.api:app --reload
```

Main endpoint:

- `POST /organize`
  - input: list of `source_paths`, `dest_root`, and processing options
  - output: source-to-target mapping for organized files

## Development docs

For architecture, contributor workflow, testing, and extension guidelines, see:

- `docs/DEVELOPMENT.md`


