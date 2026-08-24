"""Role and conflict rules for benchmark task approval."""

from __future__ import annotations

import re

from .models import ReviewerRole, TaskReview, TaskReviewVerdict


INDEPENDENT_ROLES = frozenset(
    {
        ReviewerRole.DOMAIN_REVIEWER,
        ReviewerRole.TECHNICAL_REVIEWER,
        ReviewerRole.FINAL_APPROVER,
    }
)
_NO_CONFLICT = frozenset({"none", "no conflict", "no conflicts", "n/a"})


def reviewer_assignment_issues(
    *,
    task_author: str,
    reviewer: str,
    reviewer_role: ReviewerRole | str,
    conflict_declaration: str,
    verdict: TaskReviewVerdict | str | None = None,
) -> tuple[str, ...]:
    role = ReviewerRole(reviewer_role)
    issues: list[str] = []
    if role in INDEPENDENT_ROLES and _identity(task_author) == _identity(reviewer):
        issues.append(
            "The task author cannot serve as an independent domain, technical, or final reviewer."
        )
    declaration = conflict_declaration.strip()
    if not declaration:
        issues.append("Declare reviewer conflicts before recording a task review.")
    has_conflict = bool(declaration) and declaration.casefold() not in _NO_CONFLICT
    if (
        role in INDEPENDENT_ROLES
        and has_conflict
        and verdict is not None
        and TaskReviewVerdict(verdict) is TaskReviewVerdict.APPROVE
    ):
        issues.append(
            "A reviewer with a declared conflict cannot approve the task as benchmark-ready."
        )
    if role is ReviewerRole.AUTHOR_VALIDATION and verdict is not None:
        if TaskReviewVerdict(verdict) is TaskReviewVerdict.APPROVE:
            issues.append(
                "Author validation may test and request changes, but it is not independent approval."
            )
    return tuple(issues)


def validate_task_review(review: TaskReview) -> tuple[str, ...]:
    return reviewer_assignment_issues(
        task_author=review.task_author,
        reviewer=review.reviewer,
        reviewer_role=review.reviewer_role,
        conflict_declaration=review.conflict_declaration,
        verdict=review.verdict,
    )


def enforce_task_review(review: TaskReview) -> None:
    issues = validate_task_review(review)
    if issues:
        raise ValueError(" ".join(issues))


def _identity(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()
