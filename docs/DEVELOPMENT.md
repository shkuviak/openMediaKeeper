# Development Guide

This document describes how to work on `openMediaKeeper` as a contributor.

## Tech stack

- Python `>=3.11`
- `uv` for environment and dependency management
- Typer CLI
- Watchdog filesystem events
- Pydantic models
- FastAPI (minimal API layer)
- Pytest for tests

## Project structure

- `openmediakeeper/cli.py`
  - CLI entrypoints (`scan`, `watch`)
- `openmediakeeper/config.py`
  - Runtime configuration (`OrganizerConfig`)
- `openmediakeeper/parsers.py`
  - Movie/TV filename parsing
- `openmediakeeper/providers.py`
  - Metadata providers (`omdb`, `noop`)
- `openmediakeeper/organizer.py`
  - Core organization pipeline and filesystem actions
- `openmediakeeper/watcher.py`
  - Watchdog observers and event handlers
- `openmediakeeper/api.py`
  - FastAPI endpoint using the same core pipeline
- `openmediakeeper/logging_utils.py`
  - Shared logging configuration for CLI usage
- `tests/`
  - Unit tests

## Architecture principles

- Keep business logic in reusable modules (`parsers`, `organizer`, `providers`)
- Keep adapters thin:
  - CLI (`cli.py`) should only parse options and call core functions
  - API (`api.py`) should only validate request data and call core functions
- Prefer pure functions for parsing and path building
- Add explicit logging for operational events and skip paths

## Local setup

```bash
uv sync --extra dev
```

## Common commands

Run tests:

```bash
uv run pytest
```

Run CLI help:

```bash
uv run omk --help
uv run omk scan --help
uv run omk watch --help
```

Run API:

```bash
uv run uvicorn openmediakeeper.api:app --reload
```

## Logging conventions

- Use module-level loggers in each file:
  - `logger = logging.getLogger(__name__)`
- Severity guidance:
  - `INFO`: key operational events (start/end action, skips with reason)
  - `DEBUG`: high-detail diagnostics (parser edge cases, filtered files)
  - `WARNING`: unexpected but recoverable conditions
  - `ERROR`/`EXCEPTION`: failed operations
- Avoid logging sensitive information (API keys, private paths outside intended scope)

## Testing guidelines

- Add/extend tests whenever parser or watcher behavior changes
- Prefer small focused tests per behavior
- Mock external side effects:
  - filesystem observer internals
  - network requests (provider layer)
- Keep tests deterministic (no real network, no timing dependencies)

## Extension points

### Add a new metadata provider

1. Implement `MetadataProvider` in `providers.py`
2. Add selection logic in `get_provider()`
3. Add tests for lookup behavior and fallback behavior
4. Document new provider flags/options in `README.md`

### Add parser support for a new filename style

1. Add/adjust regex and extraction logic in `parsers.py`
2. Keep behavior backward-compatible where possible
3. Add tests for:
   - success path
   - ambiguous path
   - failure path

### Add new output pattern variables

1. Update render logic in `organizer.py`
2. Ensure both movie and TV contexts are handled intentionally
3. Update `README.md` variable list and examples

## Watcher behavior notes

- Recursive watching is always enabled
- `watch` handles both `on_created` and `on_moved`
- For Docker/NFS/shared filesystems that miss native events, use:
  - CLI: `--poll`
  - Env: `OMK_WATCH_POLL=1`

## Release readiness checklist

- [ ] Tests pass: `uv run pytest`
- [ ] README updated for user-visible behavior changes
- [ ] New options documented in CLI help and docs
- [ ] Logging added for critical paths and failure conditions
