"""Atomic sidecar persistence for authored-task reviews."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from urllib.parse import quote

from .conflicts import enforce_task_review
from .models import TaskReview


class TaskReviewStore:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory).expanduser().resolve()

    def save(self, review: TaskReview) -> Path:
        enforce_task_review(review)
        destination = (
            self.directory
            / _component(review.task_name)
            / f"{_component(review.review_id)}.json"
        )
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

    def list(self, *, task_name: str | None = None) -> tuple[TaskReview, ...]:
        task_pattern = _component(task_name) if task_name else "*"
        reviews = [
            review
            for path in self.directory.glob(f"{task_pattern}/*.json")
            if (review := self._read(path)) is not None
        ]
        return tuple(sorted(reviews, key=lambda item: (item.updated_at, item.review_id)))

    @staticmethod
    def _read(path: Path) -> TaskReview | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                return None
            return TaskReview.from_dict(value)
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            return None


def _component(value: str) -> str:
    encoded = quote(str(value), safe="-_.")
    if encoded in {"", ".", ".."}:
        raise ValueError("Task review identifiers cannot be empty path components.")
    return encoded
