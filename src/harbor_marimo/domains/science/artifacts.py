"""Safe, dependency-light classification of scientific output artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


_EXTENSION_KINDS = {
    ".csv": ("table", "CSV table", True),
    ".tsv": ("table", "TSV table", True),
    ".parquet": ("table", "Parquet table", False),
    ".json": ("structured", "JSON data", True),
    ".jsonl": ("structured", "JSON lines", True),
    ".yaml": ("structured", "YAML data", True),
    ".yml": ("structured", "YAML data", True),
    ".png": ("image", "PNG image", True),
    ".jpg": ("image", "JPEG image", True),
    ".jpeg": ("image", "JPEG image", True),
    ".gif": ("image", "GIF image", True),
    ".svg": ("image", "SVG image", True),
    ".tif": ("image", "TIFF image", True),
    ".tiff": ("image", "TIFF image", True),
    ".nc": ("array", "NetCDF dataset", False),
    ".h5": ("array", "HDF5 dataset", False),
    ".hdf5": ("array", "HDF5 dataset", False),
    ".npy": ("array", "NumPy array", False),
    ".npz": ("array", "NumPy archive", False),
    ".sdf": ("molecule", "Structure data", True),
    ".mol": ("molecule", "Molecular structure", True),
    ".pdb": ("molecule", "Protein structure", True),
    ".cif": ("molecule", "Crystallographic data", True),
    ".md": ("report", "Markdown report", True),
    ".txt": ("report", "Text report", True),
    ".log": ("report", "Log output", True),
    ".pdf": ("report", "PDF report", True),
    ".html": ("report", "HTML report", False),
    ".ipynb": ("notebook", "Jupyter notebook", False),
    ".py": ("code", "Python source", True),
    ".onnx": ("model", "ONNX model", False),
    ".pt": ("model", "PyTorch model", False),
    ".pth": ("model", "PyTorch model", False),
    ".pkl": ("model", "Serialized model", False),
    ".joblib": ("model", "Serialized model", False),
}


@dataclass(frozen=True)
class ArtifactClassification:
    kind: str
    label: str
    previewable: bool
    safe: bool
    exists: bool
    path: Path | None
    reason: str | None = None


def classify_artifact(artifact: Mapping[str, Any]) -> ArtifactClassification:
    safe = artifact.get("safe") is not False
    exists = artifact.get("exists") is not False
    raw_path = artifact.get("path")
    path = Path(raw_path) if safe and isinstance(raw_path, str) else None
    destination = str(artifact.get("destination") or raw_path or "")
    suffix = Path(destination).suffix.lower()
    kind, label, supports_preview = _EXTENSION_KINDS.get(
        suffix,
        ("binary", "Unrecognized artifact", False),
    )
    reason = None
    if not safe:
        reason = "Artifact path escapes the Harbor trial boundary."
    elif not exists:
        reason = "Artifact was recorded but is not available locally."
    elif not supports_preview:
        reason = "Metadata is available; a specialized renderer is required."
    return ArtifactClassification(
        kind=kind,
        label=label,
        previewable=safe and exists and supports_preview,
        safe=safe,
        exists=exists,
        path=path,
        reason=reason,
    )
