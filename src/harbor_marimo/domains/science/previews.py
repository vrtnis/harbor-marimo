"""Bounded previews for scientific evidence; artifacts are never executed."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import csv
import json

from .artifacts import classify_artifact


@dataclass(frozen=True)
class ArtifactPreview:
    kind: str
    title: str
    path: Path | None
    rows: tuple[tuple[str, ...], ...] = ()
    text: str | None = None
    truncated: bool = False
    warning: str | None = None


def preview_artifact(
    artifact: Mapping[str, Any],
    *,
    max_bytes: int = 256_000,
    max_rows: int = 100,
    max_columns: int = 40,
) -> ArtifactPreview:
    classification = classify_artifact(artifact)
    destination = str(artifact.get("destination") or "Artifact")
    path = classification.path
    if not classification.previewable or path is None:
        return ArtifactPreview(
            kind=classification.kind,
            title=destination,
            path=path,
            warning=classification.reason,
        )
    if classification.kind == "image" or path.suffix.lower() == ".pdf":
        return ArtifactPreview(
            kind=classification.kind,
            title=destination,
            path=path,
        )
    try:
        size = path.stat().st_size
        if size > max_bytes:
            return ArtifactPreview(
                kind=classification.kind,
                title=destination,
                path=path,
                truncated=True,
                warning=f"Artifact exceeds the {max_bytes:,}-byte preview limit.",
            )
        if classification.kind == "table":
            return _table_preview(
                path,
                destination,
                max_rows=max_rows,
                max_columns=max_columns,
            )
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() == ".json":
            value = json.loads(text)
            text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)
        return ArtifactPreview(
            kind=classification.kind,
            title=destination,
            path=path,
            text=text,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, csv.Error) as exc:
        return ArtifactPreview(
            kind=classification.kind,
            title=destination,
            path=path,
            warning=f"Preview failed: {exc}",
        )


def _table_preview(
    path: Path,
    title: str,
    *,
    max_rows: int,
    max_columns: int,
) -> ArtifactPreview:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    rows: list[tuple[str, ...]] = []
    truncated = False
    with path.open("r", encoding="utf-8", errors="replace", newline="") as stream:
        reader = csv.reader(stream, delimiter=delimiter)
        for index, row in enumerate(reader):
            if index >= max_rows:
                truncated = True
                break
            rows.append(tuple(str(value) for value in row[:max_columns]))
            truncated = truncated or len(row) > max_columns
    return ArtifactPreview(
        kind="table",
        title=title,
        path=path,
        rows=tuple(rows),
        truncated=truncated,
    )
