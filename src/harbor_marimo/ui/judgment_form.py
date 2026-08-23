"""Validation shared by expert review interfaces."""

from __future__ import annotations

from collections.abc import Mapping


def validate_review_submission(
    *,
    verdict: str,
    reviewer: str,
    rationale: str,
    follow_up: str,
    criteria: Mapping[str, str],
) -> tuple[str, ...]:
    errors: list[str] = []
    if not reviewer.strip():
        errors.append("Enter the reviewer name or identifier.")
    if verdict in {"reject", "needs_follow_up"} and not rationale.strip():
        errors.append("Explain the scientific reason for this verdict.")
    if verdict == "needs_follow_up" and not follow_up.strip():
        errors.append("Describe the follow-up required to resolve the review.")
    missing = [label for label, status in criteria.items() if not status]
    if missing:
        errors.append("Assess every acceptance criterion before saving.")
    return tuple(errors)
