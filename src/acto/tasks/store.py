"""Durable JSON task drafts with append-only revision snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import TaskDraft


class TaskDraftStore:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory).expanduser().resolve()

    def save(self, draft: TaskDraft) -> Path:
        root = self.directory / _component(draft.draft_id)
        history = root / "history"
        history.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(draft.to_dict(), indent=2, sort_keys=True) + "\n"
        revision = history / f"{_component(draft.updated_at)}.json"
        if not revision.exists():
            revision.write_text(payload, encoding="utf-8")
        destination = root / "draft.json"
        temporary = root / ".draft.json.tmp"
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(destination)
        return destination

    def get(self, draft_id: str) -> TaskDraft | None:
        return self._read(self.directory / _component(draft_id) / "draft.json")

    def list(self) -> tuple[TaskDraft, ...]:
        if not self.directory.exists():
            return ()
        drafts = [
            draft
            for path in self.directory.glob("*/draft.json")
            if (draft := self._read(path)) is not None
        ]
        return tuple(sorted(drafts, key=lambda item: item.updated_at, reverse=True))

    def revisions(self, draft_id: str) -> tuple[TaskDraft, ...]:
        history = self.directory / _component(draft_id) / "history"
        if not history.exists():
            return ()
        values = [
            draft
            for path in history.glob("*.json")
            if (draft := self._read(path)) is not None
        ]
        return tuple(sorted(values, key=lambda item: item.updated_at))

    @staticmethod
    def _read(path: Path) -> TaskDraft | None:
        try:
            value: Any = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                return None
            return TaskDraft.from_dict(value)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None


def _component(value: str) -> str:
    normalized = "".join(character if character.isalnum() or character in "-." else "_" for character in value)
    return normalized[:160] or "unknown"
