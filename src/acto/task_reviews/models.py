"""Versioned records for independent scientific benchmark task review."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


TASK_REVIEW_SCHEMA = "harbor-marimo/task-review/v1"


class ReviewerRole(str, Enum):
    AUTHOR_VALIDATION = "author_validation"
    DOMAIN_REVIEWER = "domain_reviewer"
    TECHNICAL_REVIEWER = "technical_reviewer"
    FINAL_APPROVER = "final_approver"


class TaskReviewVerdict(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"


class RubricStatus(str, Enum):
    MEETS = "meets"
    UNCERTAIN = "uncertain"
    DOES_NOT_MEET = "does_not_meet"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True)
class TaskEvidenceReference:
    key: str
    kind: str
    label: str
    path: str = ""
    locator: str = ""

    def __post_init__(self) -> None:
        if not self.key.strip() or not self.kind.strip() or not self.label.strip():
            raise ValueError("Task evidence key, kind, and label cannot be empty.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TaskEvidenceReference":
        return cls(
            key=str(value.get("key") or ""),
            kind=str(value.get("kind") or ""),
            label=str(value.get("label") or ""),
            path=str(value.get("path") or ""),
            locator=str(value.get("locator") or ""),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "kind": self.kind,
            "label": self.label,
            "path": self.path,
            "locator": self.locator,
        }


@dataclass(frozen=True)
class RubricAssessment:
    criterion_id: str
    status: RubricStatus
    note: str = ""
    evidence_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.criterion_id.strip():
            raise ValueError("Task rubric criterion id cannot be empty.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RubricAssessment":
        return cls(
            criterion_id=str(value.get("criterion_id") or ""),
            status=RubricStatus(str(value.get("status") or "")),
            note=str(value.get("note") or ""),
            evidence_keys=tuple(str(item) for item in value.get("evidence_keys") or ()),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "status": self.status.value,
            "note": self.note,
            "evidence_keys": list(self.evidence_keys),
        }


@dataclass(frozen=True)
class TaskReview:
    review_id: str
    task_name: str
    task_author: str
    reviewer: str
    reviewer_role: ReviewerRole
    verdict: TaskReviewVerdict
    conflict_declaration: str
    note: str = ""
    assessments: tuple[RubricAssessment, ...] = ()
    evidence: tuple[TaskEvidenceReference, ...] = ()
    follow_up: str = ""
    created_at: str = field(default_factory=lambda: _timestamp())
    updated_at: str = field(default_factory=lambda: _timestamp())
    schema_version: str = TASK_REVIEW_SCHEMA

    def __post_init__(self) -> None:
        for name in (
            "review_id",
            "task_name",
            "task_author",
            "reviewer",
            "conflict_declaration",
        ):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"Task review {name} cannot be empty.")
        if self.schema_version != TASK_REVIEW_SCHEMA:
            raise ValueError(f"Unsupported task review schema: {self.schema_version}")
        criterion_ids = [item.criterion_id for item in self.assessments]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("Task review criterion assessments must be unique.")
        evidence_keys = [item.key for item in self.evidence]
        if len(evidence_keys) != len(set(evidence_keys)):
            raise ValueError("Task review evidence references must be unique.")
        unknown = {
            key for item in self.assessments for key in item.evidence_keys
        } - set(evidence_keys)
        if unknown:
            raise ValueError(
                "Task review assessments reference unknown evidence: "
                + ", ".join(sorted(unknown))
            )

    @classmethod
    def create(
        cls,
        *,
        task_name: str,
        task_author: str,
        reviewer: str,
        reviewer_role: ReviewerRole | str,
        verdict: TaskReviewVerdict | str,
        conflict_declaration: str,
        **changes: Any,
    ) -> "TaskReview":
        now = _timestamp()
        return cls(
            review_id=str(uuid4()),
            task_name=task_name,
            task_author=task_author,
            reviewer=reviewer,
            reviewer_role=ReviewerRole(reviewer_role),
            verdict=TaskReviewVerdict(verdict),
            conflict_declaration=conflict_declaration,
            created_at=now,
            updated_at=now,
            **changes,
        )

    def updated(self, **changes: Any) -> "TaskReview":
        changes["updated_at"] = _timestamp()
        if "reviewer_role" in changes:
            changes["reviewer_role"] = ReviewerRole(changes["reviewer_role"])
        if "verdict" in changes:
            changes["verdict"] = TaskReviewVerdict(changes["verdict"])
        return replace(self, **changes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "review_id": self.review_id,
            "task_name": self.task_name,
            "task_author": self.task_author,
            "reviewer": self.reviewer,
            "reviewer_role": self.reviewer_role.value,
            "verdict": self.verdict.value,
            "conflict_declaration": self.conflict_declaration,
            "note": self.note,
            "assessments": [item.to_dict() for item in self.assessments],
            "evidence": [item.to_dict() for item in self.evidence],
            "follow_up": self.follow_up,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TaskReview":
        return cls(
            schema_version=str(value.get("schema_version") or ""),
            review_id=str(value.get("review_id") or ""),
            task_name=str(value.get("task_name") or ""),
            task_author=str(value.get("task_author") or ""),
            reviewer=str(value.get("reviewer") or ""),
            reviewer_role=ReviewerRole(str(value.get("reviewer_role") or "")),
            verdict=TaskReviewVerdict(str(value.get("verdict") or "")),
            conflict_declaration=str(value.get("conflict_declaration") or ""),
            note=str(value.get("note") or ""),
            assessments=tuple(
                RubricAssessment.from_dict(item)
                for item in value.get("assessments") or ()
                if isinstance(item, Mapping)
            ),
            evidence=tuple(
                TaskEvidenceReference.from_dict(item)
                for item in value.get("evidence") or ()
                if isinstance(item, Mapping)
            ),
            follow_up=str(value.get("follow_up") or ""),
            created_at=str(value.get("created_at") or ""),
            updated_at=str(value.get("updated_at") or ""),
        )


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
