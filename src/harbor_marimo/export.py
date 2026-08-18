"""Stable JSON export helpers."""

from __future__ import annotations

import json
from pathlib import Path

from .models import AnalysisBundle


def export_json(
    bundle: AnalysisBundle,
    destination: str | Path,
    *,
    include_raw: bool = False,
) -> Path:
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(bundle.to_dict(include_raw=include_raw), indent=2, ensure_ascii=False, default=str)
        + "\n",
        encoding="utf-8",
    )
    return path
