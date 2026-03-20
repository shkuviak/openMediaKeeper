from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from .config import OrganizerConfig
from .models import ActionType, MediaType
from .organizer import organize_files

logger = logging.getLogger(__name__)


class OrganizeRequest(BaseModel):
    source_paths: List[Path]
    dest_root: Path
    media_type: MediaType = MediaType.AUTO
    action: ActionType = ActionType.DRY_RUN
    pattern_movie: str | None = None
    pattern_tv: str | None = None
    use_metadata: bool = True
    provider: str = "omdb"


class OrganizeResult(BaseModel):
    source: Path
    target: Path


app = FastAPI(title="openMediaKeeper API", version="0.1.0")


@app.post("/organize", response_model=list[OrganizeResult])
def organize(req: OrganizeRequest) -> list[OrganizeResult]:
    logger.info(
        "API organize request: paths=%d dest_root=%s action=%s media_type=%s",
        len(req.source_paths),
        req.dest_root,
        req.action.value,
        req.media_type.value,
    )
    config = OrganizerConfig(
        source_root=req.source_paths[0].parent if req.source_paths else Path("."),
        dest_root=req.dest_root,
        media_type=req.media_type,
        action=req.action,
        use_metadata=req.use_metadata,
        provider=req.provider,
    )
    if req.pattern_movie:
        config.pattern_movie = req.pattern_movie
    if req.pattern_tv:
        config.pattern_tv = req.pattern_tv

    results = organize_files(config, req.source_paths)
    return [OrganizeResult(source=s, target=t) for s, t in results]

