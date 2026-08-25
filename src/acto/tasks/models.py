"""Versioned, framework-independent scientific task drafts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timedelta, timezone
import re
from typing import Any, Mapping
from uuid import uuid4


TASK_DRAFT_SCHEMA = "harbor-marimo/task-draft/v1"
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class TaskMetadata:
    author_name: str
    author_email: str = ""
    author_organization: str = ""
    author_profile: str = ""
    research_advisor: str = ""
    domain: str = ""
    field: str = ""
    subfield: str = ""
    tags: tuple[str, ...] = ()
    expert_time_estimate_hours: float = 0.0
    relevant_experience: str = ""
    conflicts_of_interest: str = "None"

    def __post_init__(self) -> None:
        if not self.author_name.strip():
            raise ValueError("Task author name cannot be empty.")
        if self.expert_time_estimate_hours < 0:
            raise ValueError("Expert time estimate cannot be negative.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TaskMetadata":
        return cls(
            author_name=str(value.get("author_name") or ""),
            author_email=str(value.get("author_email") or ""),
            author_organization=str(value.get("author_organization") or ""),
            author_profile=str(value.get("author_profile") or ""),
            research_advisor=str(value.get("research_advisor") or ""),
            domain=str(value.get("domain") or ""),
            field=str(value.get("field") or ""),
            subfield=str(value.get("subfield") or ""),
            tags=tuple(str(item) for item in value.get("tags") or ()),
            expert_time_estimate_hours=float(
                value.get("expert_time_estimate_hours") or 0
            ),
            relevant_experience=str(value.get("relevant_experience") or ""),
            conflicts_of_interest=str(value.get("conflicts_of_interest") or "None"),
        )


@dataclass(frozen=True)
class ScientificBrief:
    title: str
    instruction: str
    research_context: str = ""
    difficulty_explanation: str = ""
    solution_explanation: str = ""
    verification_explanation: str = ""

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.instruction.strip():
            raise ValueError("Scientific brief title and instruction cannot be empty.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ScientificBrief":
        return cls(
            title=str(value.get("title") or ""),
            instruction=str(value.get("instruction") or ""),
            research_context=str(value.get("research_context") or ""),
            difficulty_explanation=str(value.get("difficulty_explanation") or ""),
            solution_explanation=str(value.get("solution_explanation") or ""),
            verification_explanation=str(value.get("verification_explanation") or ""),
        )


@dataclass(frozen=True)
class ArtifactField:
    name: str
    data_type: str = "string"
    required: bool = True
    description: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ArtifactField":
        return cls(
            name=str(value.get("name") or ""),
            data_type=str(value.get("data_type") or "string"),
            required=bool(value.get("required", True)),
            description=str(value.get("description") or ""),
        )


@dataclass(frozen=True)
class ArtifactContract:
    path: str
    format: str = "file"
    description: str = ""
    required: bool = True
    fields: tuple[ArtifactField, ...] = ()

    def __post_init__(self) -> None:
        if not self.path.strip() or self.path.startswith(("/", "\\")):
            raise ValueError("Artifact contract path must be a non-empty relative path.")
        if ".." in self.path.replace("\\", "/").split("/"):
            raise ValueError("Artifact contract path cannot escape the task workspace.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ArtifactContract":
        return cls(
            path=str(value.get("path") or ""),
            format=str(value.get("format") or "file"),
            description=str(value.get("description") or ""),
            required=bool(value.get("required", True)),
            fields=tuple(
                ArtifactField.from_dict(item)
                for item in value.get("fields") or ()
                if isinstance(item, Mapping)
            ),
        )


@dataclass(frozen=True)
class VerifierCheck:
    id: str
    type: str
    artifact: str
    description: str = ""
    expert_guidance: str = ""
    parameters: Mapping[str, Any] = field(default_factory=dict)
    expert_only: bool = False

    def __post_init__(self) -> None:
        if not _SLUG.fullmatch(self.id):
            raise ValueError("Verifier check id must be a kebab-case slug.")
        if not self.type.strip() or not self.artifact.strip():
            raise ValueError("Verifier check type and artifact cannot be empty.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "VerifierCheck":
        raw_parameters = value.get("parameters") or {}
        if not isinstance(raw_parameters, Mapping):
            raise ValueError("Verifier check parameters must be an object.")
        return cls(
            id=str(value.get("id") or ""),
            type=str(value.get("type") or ""),
            artifact=str(value.get("artifact") or ""),
            description=str(value.get("description") or ""),
            expert_guidance=str(value.get("expert_guidance") or ""),
            parameters=dict(raw_parameters),
            expert_only=bool(value.get("expert_only", False)),
        )


@dataclass(frozen=True)
class VerifierFixture:
    name: str
    source: str
    expected_pass: bool
    explanation: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "VerifierFixture":
        return cls(
            name=str(value.get("name") or ""),
            source=str(value.get("source") or ""),
            expected_pass=bool(value.get("expected_pass", False)),
            explanation=str(value.get("explanation") or ""),
        )


@dataclass(frozen=True)
class TaskDraft:
    draft_id: str
    task_name: str
    metadata: TaskMetadata
    brief: ScientificBrief
    artifacts: tuple[ArtifactContract, ...] = ()
    checks: tuple[VerifierCheck, ...] = ()
    fixtures: tuple[VerifierFixture, ...] = ()
    oracle_path: str = "solution/solve.sh"
    agent_timeout_sec: int = 1800
    verifier_timeout_sec: int = 120
    build_timeout_sec: int = 600
    cpus: int = 1
    memory_mb: int = 2048
    storage_mb: int = 10240
    gpus: int = 0
    allow_internet: bool = True
    created_at: str = field(default_factory=lambda: _timestamp())
    updated_at: str = field(default_factory=lambda: _timestamp())
    schema_version: str = TASK_DRAFT_SCHEMA

    def __post_init__(self) -> None:
        if not self.draft_id.strip():
            raise ValueError("Task draft id cannot be empty.")
        if not _SLUG.fullmatch(self.task_name):
            raise ValueError("Task name must be a kebab-case slug.")
        if self.schema_version != TASK_DRAFT_SCHEMA:
            raise ValueError(f"Unsupported task draft schema: {self.schema_version}")

    @classmethod
    def create(
        cls,
        *,
        task_name: str,
        metadata: TaskMetadata,
        brief: ScientificBrief,
        **changes: Any,
    ) -> "TaskDraft":
        return cls(
            draft_id=str(uuid4()),
            task_name=task_name,
            metadata=metadata,
            brief=brief,
            **changes,
        )

    def updated(self, **changes: Any) -> "TaskDraft":
        return replace(self, updated_at=_timestamp_after(self.updated_at), **changes)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TaskDraft":
        return cls(
            schema_version=str(value.get("schema_version") or ""),
            draft_id=str(value.get("draft_id") or ""),
            task_name=str(value.get("task_name") or ""),
            metadata=TaskMetadata.from_dict(_mapping(value.get("metadata"))),
            brief=ScientificBrief.from_dict(_mapping(value.get("brief"))),
            artifacts=tuple(
                ArtifactContract.from_dict(item)
                for item in value.get("artifacts") or ()
                if isinstance(item, Mapping)
            ),
            checks=tuple(
                VerifierCheck.from_dict(item)
                for item in value.get("checks") or ()
                if isinstance(item, Mapping)
            ),
            fixtures=tuple(
                VerifierFixture.from_dict(item)
                for item in value.get("fixtures") or ()
                if isinstance(item, Mapping)
            ),
            oracle_path=str(value.get("oracle_path") or "solution/solve.sh"),
            agent_timeout_sec=int(value.get("agent_timeout_sec") or 1800),
            verifier_timeout_sec=int(value.get("verifier_timeout_sec") or 120),
            build_timeout_sec=int(value.get("build_timeout_sec") or 600),
            cpus=int(value.get("cpus") or 1),
            memory_mb=int(value.get("memory_mb") or 2048),
            storage_mb=int(value.get("storage_mb") or 10240),
            gpus=int(value.get("gpus") or 0),
            allow_internet=bool(value.get("allow_internet", True)),
            created_at=str(value.get("created_at") or ""),
            updated_at=str(value.get("updated_at") or ""),
        )


def _mapping(value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("Task draft object is missing required nested data.")
    return value


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _timestamp_after(previous: str) -> str:
    """Return a timestamp later than the prior revision on coarse clocks."""

    current = datetime.now(timezone.utc)
    try:
        prior = datetime.fromisoformat(previous.replace("Z", "+00:00"))
    except ValueError:
        prior = current - timedelta(microseconds=1)
    if current <= prior:
        current = prior + timedelta(microseconds=1)
    return current.isoformat().replace("+00:00", "Z")
