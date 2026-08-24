"""Safely export task drafts as Harbor-compatible task directories."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import tempfile

from .generator import generate_verifier_script
from .models import TaskDraft
from .render import render_instruction, render_task_toml
from .templates import REQUIRED_TASK_FILES, task_template_root


@dataclass(frozen=True)
class TaskBundleExport:
    task_path: Path
    review_profile_path: Path
    files: tuple[str, ...]


def export_task_bundle(
    draft: TaskDraft,
    destination: str | Path,
    *,
    draft_root: str | Path | None = None,
) -> TaskBundleExport:
    target = Path(destination).expanduser().resolve()
    if target.exists():
        raise FileExistsError(f"Task export destination already exists: {target}")
    if target.name != draft.task_name:
        raise ValueError("Task export directory name must match the draft task_name.")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=f".{draft.task_name}-", dir=target.parent))
    staging = temporary_root / draft.task_name
    try:
        shutil.copytree(task_template_root(), staging)
        (staging / "instruction.md").write_text(
            render_instruction(draft), encoding="utf-8"
        )
        (staging / "task.toml").write_text(render_task_toml(draft), encoding="utf-8")
        (staging / "tests" / "test_verifier.py").write_text(
            generate_verifier_script(draft), encoding="utf-8"
        )
        development = staging / ".harbor-marimo"
        development.mkdir()
        (development / "task-draft.json").write_text(
            json.dumps(draft.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if draft_root:
            source_root = Path(draft_root).expanduser().resolve()
            oracle = (source_root / draft.oracle_path).resolve()
            if oracle.is_relative_to(source_root) and oracle.is_file():
                shutil.copy2(oracle, staging / "solution" / "solve.sh")
        missing = [relative for relative in REQUIRED_TASK_FILES if not (staging / relative).is_file()]
        if missing or not (staging / "tests" / "test_verifier.py").is_file():
            raise ValueError(f"Generated task bundle is incomplete: {', '.join(missing)}")
        staging.replace(target)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if temporary_root.exists():
            temporary_root.rmdir()
    profile_path = target.parent / f"{draft.task_name}.review-profile.json"
    profile_path.write_text(
        json.dumps(review_profile_payload(draft), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    files = tuple(
        sorted(str(path.relative_to(target)).replace("\\", "/") for path in target.rglob("*") if path.is_file())
    )
    return TaskBundleExport(target, profile_path, files)


def review_profile_payload(draft: TaskDraft) -> dict[str, object]:
    artifacts = {
        item.path: {
            "label": _human_label(item.path),
            "description": item.description,
            "guidance": "Use this artifact when assessing the linked acceptance criteria.",
        }
        for item in draft.artifacts
    }
    criteria = [
        {
            "id": check.id,
            "label": check.description or check.id.replace("-", " ").title(),
            "guidance": check.expert_guidance,
            "evidence_keys": [check.artifact],
        }
        for check in draft.checks
    ]
    return {
        "title": draft.brief.title,
        "question": draft.brief.instruction,
        "summary": draft.brief.research_context,
        "acceptance_criteria": criteria,
        "artifact_labels": artifacts,
        "benchmark": {
            "task_name": draft.task_name,
            "domain": draft.metadata.domain,
            "field": draft.metadata.field,
            "subfield": draft.metadata.subfield,
        },
    }


def _human_label(path: str) -> str:
    stem = Path(path).name.rsplit(".", 1)[0]
    return stem.replace("_", " ").replace("-", " ").title()
