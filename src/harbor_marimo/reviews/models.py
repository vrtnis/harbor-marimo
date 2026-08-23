"""Versioned review records with explicit Harbor provenance."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping
from uuid import uuid4


SCHEMA_VERSION = "harbor-marimo/review/v1"


class ReviewVerdict(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    NEEDS_FOLLOW_UP = "needs_follow_up"


@dataclass(frozen=True)
class EvidenceReference:
    key: str
    kind: str
    job_id: str
    trial_id: str
    label: str | None = None
    step_name: str | None = None
    path: str | None = None
    locator: str | None = None

    def __post_init__(self) -> None:
        for name in ("key", "kind", "job_id", "trial_id"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"Evidence {name} cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "kind": self.kind,
            "job_id": self.job_id,
            "trial_id": self.trial_id,
            "label": self.label,
            "step_name": self.step_name,
            "path": self.path,
            "locator": self.locator,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EvidenceReference":
        return cls(
            key=str(value.get("key") or ""),
            kind=str(value.get("kind") or ""),
            job_id=str(value.get("job_id") or ""),
            trial_id=str(value.get("trial_id") or ""),
            label=_optional_string(value.get("label")),
            step_name=_optional_string(value.get("step_name")),
            path=_optional_string(value.get("path")),
            locator=_optional_string(value.get("locator")),
        )


@dataclass(frozen=True)
class ExpertReview:
    review_id: str
    job_id: str
    trial_id: str
    domain: str
    verdict: ReviewVerdict
    note: str = ""
    reviewer: str | None = None
    confidence: float | None = None
    evidence: tuple[EvidenceReference, ...] = ()
    created_at: str = field(default_factory=lambda: _timestamp())
    updated_at: str = field(default_factory=lambda: _timestamp())
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("review_id", "job_id", "trial_id", "domain"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"Review {name} cannot be empty.")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("Review confidence must be between 0 and 1.")
        for reference in self.evidence:
            if reference.job_id != self.job_id or reference.trial_id != self.trial_id:
                raise ValueError("Review evidence must reference the same job and trial.")

    @classmethod
    def create(
        cls,
        *,
        job_id: str,
        trial_id: str,
        domain: str,
        verdict: ReviewVerdict | str,
        note: str = "",
        reviewer: str | None = None,
        confidence: float | None = None,
        evidence: tuple[EvidenceReference, ...] = (),
    ) -> "ExpertReview":
        now = _timestamp()
        return cls(
            review_id=str(uuid4()),
            job_id=job_id,
            trial_id=trial_id,
            domain=domain,
            verdict=ReviewVerdict(verdict),
            note=note,
            reviewer=reviewer,
            confidence=confidence,
            evidence=evidence,
            created_at=now,
            updated_at=now,
        )

    def updated(self, **changes: Any) -> "ExpertReview":
        changes["updated_at"] = _timestamp()
        if "verdict" in changes:
            changes["verdict"] = ReviewVerdict(changes["verdict"])
        return replace(self, **changes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "review_id": self.review_id,
            "job_id": self.job_id,
            "trial_id": self.trial_id,
            "domain": self.domain,
            "verdict": self.verdict.value,
            "note": self.note,
            "reviewer": self.reviewer,
            "confidence": self.confidence,
            "evidence": [reference.to_dict() for reference in self.evidence],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ExpertReview":
        schema = str(value.get("schema_version") or "")
        if schema != SCHEMA_VERSION:
            raise ValueError(f"Unsupported review schema: {schema or 'missing'}")
        raw_evidence = value.get("evidence") or []
        if not isinstance(raw_evidence, list):
            raise ValueError("Review evidence must be a list.")
        return cls(
            schema_version=schema,
            review_id=str(value.get("review_id") or ""),
            job_id=str(value.get("job_id") or ""),
            trial_id=str(value.get("trial_id") or ""),
            domain=str(value.get("domain") or ""),
            verdict=ReviewVerdict(str(value.get("verdict") or "")),
            note=str(value.get("note") or ""),
            reviewer=_optional_string(value.get("reviewer")),
            confidence=_optional_float(value.get("confidence")),
            evidence=tuple(
                EvidenceReference.from_dict(item)
                for item in raw_evidence
                if isinstance(item, Mapping)
            ),
            created_at=str(value.get("created_at") or ""),
            updated_at=str(value.get("updated_at") or ""),
        )


def _optional_string(value: Any) -> str | None:
    return str(value) if value is not None else None


def _optional_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
