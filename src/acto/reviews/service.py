"""Application service for creating or updating a trial's expert review."""

from __future__ import annotations

from collections.abc import Iterable

from .models import CriterionAssessment, EvidenceReference, ExpertReview, ReviewVerdict
from .store import JsonReviewStore


def record_review(
    store: JsonReviewStore,
    *,
    job_id: str,
    trial_id: str,
    domain: str,
    verdict: ReviewVerdict | str,
    note: str = "",
    reviewer: str | None = None,
    confidence: float | None = None,
    evidence: Iterable[EvidenceReference] = (),
    criteria: Iterable[CriterionAssessment] = (),
    follow_up: str | None = None,
) -> tuple[ExpertReview, str]:
    """Persist a review while retaining its identity and creation timestamp."""

    references = tuple(evidence)
    assessments = tuple(criteria)
    existing = store.latest(job_id=job_id, trial_id=trial_id, domain=domain)
    if existing:
        review = existing.updated(
            verdict=verdict,
            note=note,
            reviewer=reviewer,
            confidence=confidence,
            evidence=references,
            criteria=assessments,
            follow_up=follow_up,
        )
    else:
        review = ExpertReview.create(
            job_id=job_id,
            trial_id=trial_id,
            domain=domain,
            verdict=verdict,
            note=note,
            reviewer=reviewer,
            confidence=confidence,
            evidence=references,
            criteria=assessments,
            follow_up=follow_up,
        )
    destination = store.save(review)
    return review, str(destination)
