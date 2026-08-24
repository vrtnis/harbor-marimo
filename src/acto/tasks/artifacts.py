"""Safe structural checks for authored scientific artifact contracts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .models import ArtifactContract


@dataclass(frozen=True)
class ArtifactIssue:
    artifact: str
    code: str
    message: str


def inspect_artifact_contract(
    root: str | Path, contract: ArtifactContract
) -> tuple[ArtifactIssue, ...]:
    base = Path(root).expanduser().resolve()
    path = (base / contract.path).resolve()
    if not path.is_relative_to(base):
        return (ArtifactIssue(contract.path, "unsafe_path", "Artifact path escapes its fixture root."),)
    if not path.exists():
        return (
            (ArtifactIssue(contract.path, "missing", "Required artifact is missing."),)
            if contract.required
            else ()
        )
    if not path.is_file() and contract.format != "directory":
        return (ArtifactIssue(contract.path, "wrong_kind", "Expected a file artifact."),)
    if contract.format == "csv":
        return _inspect_csv(path, contract)
    if contract.format == "json":
        return _inspect_json(path, contract)
    return ()


def _inspect_csv(path: Path, contract: ArtifactContract) -> tuple[ArtifactIssue, ...]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
    except (OSError, UnicodeError, csv.Error) as exc:
        return (ArtifactIssue(contract.path, "unreadable", f"CSV could not be read: {exc}"),)
    return _missing_fields(contract, set(header))


def _inspect_json(path: Path, contract: ArtifactContract) -> tuple[ArtifactIssue, ...]:
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return (ArtifactIssue(contract.path, "unreadable", f"JSON could not be read: {exc}"),)
    if not isinstance(value, dict):
        return (ArtifactIssue(contract.path, "wrong_shape", "Expected a JSON object."),)
    return _missing_fields(contract, set(value))


def _missing_fields(
    contract: ArtifactContract, available: set[str]
) -> tuple[ArtifactIssue, ...]:
    return tuple(
        ArtifactIssue(
            contract.path,
            "missing_field",
            f"Required field {field.name!r} is missing.",
        )
        for field in contract.fields
        if field.required and field.name not in available
    )
