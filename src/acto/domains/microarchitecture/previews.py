"""Safe static presentation of microarchitecture artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from ..science import ArtifactPreview, classify_artifact, preview_artifact


def preview_microarchitecture_artifact(
    artifact: Mapping[str, Any],
    *,
    max_bytes: int = 256_000,
    max_rows: int = 100,
    max_columns: int = 40,
) -> ArtifactPreview:
    """Show ONNX identity metadata; delegate other files to bounded previews."""

    destination = str(artifact.get("destination") or "Artifact")
    if Path(destination).suffix.lower() != ".onnx":
        return preview_artifact(
            artifact,
            max_bytes=max_bytes,
            max_rows=max_rows,
            max_columns=max_columns,
        )
    classification = classify_artifact(artifact)
    path = classification.path
    if not classification.safe or not classification.exists or path is None:
        return ArtifactPreview(
            kind="model",
            title=destination,
            path=path,
            warning=classification.reason,
        )
    try:
        size = path.stat().st_size
        digest = _sha256(path)
    except OSError as exc:
        return ArtifactPreview(
            kind="model",
            title=destination,
            path=path,
            warning=f"Could not inspect model metadata: {exc}",
        )
    return ArtifactPreview(
        kind="model",
        title=destination,
        path=path,
        text=(
            "Portable ONNX model\n"
            f"Size: {size:,} bytes\n"
            f"SHA-256: {digest}\n\n"
            "The review app identifies this artifact but does not load or execute its graph. "
            "Contract and performance claims come from the isolated Harbor verifier."
        ),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
