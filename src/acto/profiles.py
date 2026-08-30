"""Optional expert-facing presentation profiles for Harbor evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ReviewCriterion:
    """A domain criterion an expert should assess."""

    id: str
    label: str
    guidance: str = ""
    evidence_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.label.strip():
            raise ValueError("Review criterion id and label cannot be empty.")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ReviewCriterion":
        evidence_keys = value.get("evidence_keys") or []
        if not isinstance(evidence_keys, list):
            raise ValueError("Review criterion evidence_keys must be a list.")
        return cls(
            id=str(value.get("id") or ""),
            label=str(value.get("label") or ""),
            guidance=str(value.get("guidance") or ""),
            evidence_keys=tuple(str(item) for item in evidence_keys),
        )


@dataclass(frozen=True)
class ArtifactPresentation:
    """Human-facing copy for one artifact name or path suffix."""

    label: str
    description: str = ""
    guidance: str = ""

    @classmethod
    def from_value(cls, value: Any) -> "ArtifactPresentation":
        if isinstance(value, str):
            return cls(label=value)
        if not isinstance(value, Mapping):
            raise ValueError("Artifact presentation must be a string or object.")
        return cls(
            label=str(value.get("label") or ""),
            description=str(value.get("description") or ""),
            guidance=str(value.get("guidance") or ""),
        )


@dataclass(frozen=True)
class ReviewProfile:
    """Domain-authored copy layered over provider-neutral Harbor evidence."""

    title: str
    question: str = ""
    summary: str = ""
    acceptance_criteria: tuple[ReviewCriterion, ...] = ()
    artifact_labels: Mapping[str, ArtifactPresentation] = field(default_factory=dict)
    glossary: Mapping[str, str] = field(default_factory=dict)
    domain_adapter: str = "science"

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Review profile title cannot be empty.")
        if not self.domain_adapter.strip():
            raise ValueError("Review profile domain_adapter cannot be empty.")
        criterion_ids = [criterion.id for criterion in self.acceptance_criteria]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("Review profile criterion ids must be unique.")

    def artifact_presentation(self, destination: str) -> ArtifactPresentation | None:
        """Return the most specific presentation matching a path suffix."""

        normalized = destination.replace("\\", "/").lower()
        matches = [
            (key, presentation)
            for key, presentation in self.artifact_labels.items()
            if normalized.endswith(str(key).replace("\\", "/").lower())
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: len(str(item[0])))[1]

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ReviewProfile":
        raw_criteria = value.get("acceptance_criteria") or []
        raw_artifacts = value.get("artifact_labels") or {}
        raw_glossary = value.get("glossary") or {}
        if not isinstance(raw_criteria, list):
            raise ValueError("Review profile acceptance_criteria must be a list.")
        if not isinstance(raw_artifacts, Mapping):
            raise ValueError("Review profile artifact_labels must be an object.")
        if not isinstance(raw_glossary, Mapping):
            raise ValueError("Review profile glossary must be an object.")
        return cls(
            title=str(value.get("title") or ""),
            domain_adapter=str(value.get("domain_adapter") or "science"),
            question=str(value.get("question") or ""),
            summary=str(value.get("summary") or ""),
            acceptance_criteria=tuple(
                ReviewCriterion.from_dict(item)
                for item in raw_criteria
                if isinstance(item, Mapping)
            ),
            artifact_labels={
                str(key): ArtifactPresentation.from_value(item)
                for key, item in raw_artifacts.items()
            },
            glossary={str(key): str(item) for key, item in raw_glossary.items()},
        )


def load_review_profile(path: str | Path) -> ReviewProfile:
    """Load a UTF-8 JSON review profile."""

    source = Path(path).expanduser().resolve()
    value = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError("Review profile must contain a JSON object.")
    return ReviewProfile.from_dict(value)
