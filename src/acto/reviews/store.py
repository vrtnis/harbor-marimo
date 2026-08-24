"""Atomic sidecar persistence that never modifies canonical Harbor results."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
import json
import os
import tempfile

from .models import ExpertReview


class JsonReviewStore:
    """Store versioned review records below a caller-selected sidecar directory."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory).expanduser().resolve()

    def save(self, review: ExpertReview) -> Path:
        destination = self._path(review)
        destination.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
            text=True,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(review.to_dict(), stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary.exists():
                temporary.unlink()
        return destination

    def get(self, review_id: str) -> ExpertReview | None:
        encoded = f"{_component(review_id)}.json"
        for path in self.directory.glob(f"*/*/{encoded}"):
            review = self._read(path)
            if review and review.review_id == review_id:
                return review
        return None

    def list(
        self,
        *,
        job_id: str | None = None,
        trial_id: str | None = None,
        domain: str | None = None,
    ) -> tuple[ExpertReview, ...]:
        job_pattern = _component(job_id) if job_id else "*"
        trial_pattern = _component(trial_id) if trial_id else "*"
        reviews = [
            review
            for path in self.directory.glob(f"{job_pattern}/{trial_pattern}/*.json")
            if (review := self._read(path)) is not None
            and (domain is None or review.domain == domain)
        ]
        return tuple(sorted(reviews, key=lambda item: (item.updated_at, item.review_id)))

    def latest(
        self,
        *,
        job_id: str,
        trial_id: str,
        domain: str | None = None,
    ) -> ExpertReview | None:
        reviews = self.list(job_id=job_id, trial_id=trial_id, domain=domain)
        return reviews[-1] if reviews else None

    def _path(self, review: ExpertReview) -> Path:
        return (
            self.directory
            / _component(review.job_id)
            / _component(review.trial_id)
            / f"{_component(review.review_id)}.json"
        )

    @staticmethod
    def _read(path: Path) -> ExpertReview | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                return None
            return ExpertReview.from_dict(value)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return None


def _component(value: str) -> str:
    encoded = quote(str(value), safe="-_.")
    if encoded in {"", ".", ".."}:
        raise ValueError("Review identifiers cannot resolve to empty path components.")
    return encoded
