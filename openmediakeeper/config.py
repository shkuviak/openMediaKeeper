from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import ActionType, MediaType


@dataclass
class OrganizerConfig:
    source_root: Path
    dest_root: Path
    media_type: MediaType = MediaType.AUTO
    action: ActionType = ActionType.DRY_RUN
    pattern_movie: str = "Movies/{title}{year_part}/{title}{year_part}.{ext}"
    pattern_tv: str = "TV/{series_title}/Season {season:02d}/{series_title} - S{season:02d}E{episode:02d}{title_suffix}.{ext}"
    use_metadata: bool = True
    provider: str = "omdb"
    # `watch` only: poll the tree periodically (reliable on Docker/NFS/VM shares; higher CPU use).
    watch_poll: bool = False

