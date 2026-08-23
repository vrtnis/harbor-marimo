"""Stable boundary between Harbor evidence and domain-specific interpretation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..models import AnalysisBundle, JsonObject


@dataclass(frozen=True)
class DomainEvidence:
    """A domain-significant piece of evidence with Harbor provenance."""

    key: str
    label: str
    kind: str
    job_id: str
    trial_id: str
    step_name: str | None = None
    path: Path | None = None
    summary: str | None = None
    metadata: JsonObject = field(default_factory=dict)


@dataclass(frozen=True)
class DomainView:
    """Provider-neutral data consumed by an expert review notebook."""

    domain: str
    title: str
    summary: str
    evidence: tuple[DomainEvidence, ...] = ()
    diagnostics: tuple[str, ...] = ()
    metadata: JsonObject = field(default_factory=dict)


@runtime_checkable
class DomainAdapter(Protocol):
    """Interpret normalized Harbor evidence without controlling execution."""

    name: str
    label: str

    def supports(self, bundle: AnalysisBundle) -> bool:
        """Return whether the adapter can interpret at least one loaded trial."""

    def build_view(
        self,
        bundle: AnalysisBundle,
        *,
        trial_id: str | None = None,
    ) -> DomainView:
        """Build domain evidence for one trial or a bundle-level comparison."""
