"""Carry authored task criteria into Harbor agent-result review."""

from __future__ import annotations

from pathlib import Path

from acto.profiles import load_review_profile

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
    """Return the profile-selected result-review handoff without starting a server."""

    profile_path = result_review_profile_path(bundle)
    domain = load_review_profile(profile_path).domain_adapter

    return (
        executable,
        "review",
        str(Path(harbor_job).expanduser().resolve()),
        "--domain",
        domain,
        "--profile",
        str(profile_path),
        "--review-dir",
        str(Path(review_dir).expanduser().resolve()),
    )
