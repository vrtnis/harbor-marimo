"""Read exported Harbor task bundles as inert review evidence."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tomllib
from typing import Any, Mapping

from acto.tasks import TaskDraft

from .models import TaskEvidenceReference


@dataclass(frozen=True)
class TaskFile:
    path: str
    size: int
    sha256: str


@dataclass(frozen=True)
class TaskBundle:
    root: Path
    task_name: str
    task_author: str
    instruction: str
    config: Mapping[str, Any]
    files: tuple[TaskFile, ...]
    draft: TaskDraft | None = None
    review_profile_path: Path | None = None

    def evidence(self) -> tuple[TaskEvidenceReference, ...]:
        values = [
            TaskEvidenceReference(
                key="instruction",
                kind="task_instruction",
                label="Task instruction",
                path="instruction.md",
                locator=str(self.root / "instruction.md"),
            ),
            TaskEvidenceReference(
                key="task-config",
                kind="task_configuration",
                label="Harbor task configuration",
                path="task.toml",
                locator=str(self.root / "task.toml"),
            ),
        ]
        for relative, label, kind in (
            ("tests/test_verifier.py", "Generated verifier", "verifier"),
            ("solution/solve.sh", "Reference solution", "oracle"),
            ("environment/Dockerfile", "Task environment", "environment"),
            ("tests/Dockerfile", "Verifier environment", "verifier_environment"),
        ):
            if (self.root / relative).is_file():
                values.append(
                    TaskEvidenceReference(
                        key=relative.replace("/", "-"),
                        kind=kind,
                        label=label,
                        path=relative,
                        locator=str(self.root / relative),
                    )
                )
        return tuple(values)


def load_task_bundle(path: str | Path) -> TaskBundle:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Harbor task directory is unavailable: {root}")
    instruction_path = _inside(root, "instruction.md")
    config_path = _inside(root, "task.toml")
    instruction = _read_text(instruction_path, limit=500_000)
    config = tomllib.loads(_read_text(config_path, limit=500_000))
    if not isinstance(config, dict):
        raise ValueError("Harbor task.toml must contain a table.")
    draft = _load_embedded_draft(root)
    metadata = config.get("metadata") or {}
    task_author = str(metadata.get("author_name") or "Unknown task author")
    if draft:
        if draft.task_name != root.name:
            raise ValueError("Embedded task draft name does not match its Harbor directory.")
        task_author = draft.metadata.author_name
    files = tuple(
        _task_file(root, item)
        for item in sorted(root.rglob("*"))
        if item.is_file()
    )
    review_profile = root.parent / f"{root.name}.review-profile.json"
    return TaskBundle(
        root=root,
        task_name=root.name,
        task_author=task_author,
        instruction=instruction,
        config=config,
        files=files,
        draft=draft,
        review_profile_path=review_profile if review_profile.is_file() else None,
    )


def read_task_evidence(bundle: TaskBundle, reference_key: str, *, limit: int = 200_000) -> str:
    reference = next(
        (item for item in bundle.evidence() if item.key == reference_key),
        None,
    )
    if not reference or not reference.path:
        raise KeyError(f"Unknown task evidence reference: {reference_key}")
    return _read_text(_inside(bundle.root, reference.path), limit=limit)


def _load_embedded_draft(root: Path) -> TaskDraft | None:
    path = _inside(root, ".harbor-marimo/task-draft.json")
    if not path.is_file():
        return None
    value = json.loads(_read_text(path, limit=2_000_000))
    if not isinstance(value, dict):
        raise ValueError("Embedded task draft must contain a JSON object.")
    return TaskDraft.from_dict(value)


def _inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Task evidence path escapes the task directory.")
    return path


def _read_text(path: Path, *, limit: int) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Required task evidence is unavailable: {path}")
    if path.stat().st_size > limit:
        raise ValueError(f"Task evidence exceeds the {limit}-byte review limit: {path.name}")
    return path.read_text(encoding="utf-8")


def _task_file(root: Path, path: Path) -> TaskFile:
    content = path.read_bytes()
    return TaskFile(
        path=str(path.relative_to(root)).replace("\\", "/"),
        size=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
    )
