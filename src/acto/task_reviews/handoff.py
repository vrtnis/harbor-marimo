"""Carry authored task criteria into Harbor agent-result review."""

from __future__ import annotations

from pathlib import Path

from .loader import TaskBundle


def result_review_profile_path(bundle: TaskBundle) -> Path:
    if not bundle.review_profile_path:
        raise FileNotFoundError(
            "The task has no adjacent result-review profile. Re-export it from Task Studio."
        )
    return bundle.review_profile_path


def result_review_command(
    bundle: TaskBundle,
    harbor_job: str | Path,
    *,
    review_dir: str | Path = "outputs/result-reviews",
    executable: str = "harbor-marimo",
) -> tuple[str, ...]:
    """Return the science-review handoff without starting a server."""

    return (
        executable,
        "review",
        str(Path(harbor_job).expanduser().resolve()),
        "--domain",
        "science",
        "--profile",
        str(result_review_profile_path(bundle)),
        "--review-dir",
        str(Path(review_dir).expanduser().resolve()),
    )
