"""Financial expert checks that remain distinct from Harbor verifier rewards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class FinancialAssessment:
    verifier_passed: bool
    expert_status: str
    needs_review: bool
    verifier_blind_spot: bool
    summary: str


def assess_financial_trial(
    reward: float | int | None,
    context: Mapping[str, Any],
) -> FinancialAssessment:
    expert_status = str(context.get("expert_status") or "Not reviewed")
    needs_review = expert_status == "Needs review"
    verifier_passed = reward == 1
    return FinancialAssessment(
        verifier_passed=verifier_passed,
        expert_status=expert_status,
        needs_review=needs_review,
        verifier_blind_spot=verifier_passed and needs_review,
        summary=str(context.get("expert_summary") or "No expert context recorded."),
    )
