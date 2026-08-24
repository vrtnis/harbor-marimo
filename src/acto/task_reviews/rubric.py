"""Terminal-Bench Science rubric for authored benchmark tasks."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ReviewerRole


@dataclass(frozen=True)
class TaskRubricCriterion:
    id: str
    label: str
    question: str
    guidance: str
    evidence_keys: tuple[str, ...]
    primary_roles: tuple[ReviewerRole, ...]


TASK_REVIEW_RUBRIC = (
    TaskRubricCriterion(
        "scientific-purpose",
        "Scientific purpose",
        "Does this task represent meaningful scientific work?",
        "The research context should explain who needs the result and why it matters.",
        ("instruction",),
        (ReviewerRole.DOMAIN_REVIEWER, ReviewerRole.FINAL_APPROVER),
    ),
    TaskRubricCriterion(
        "domain-correctness",
        "Domain correctness",
        "Are the task assumptions, terminology, and requested conclusions scientifically valid?",
        "Identify hidden assumptions, invalid thresholds, or conclusions the evidence cannot support.",
        ("instruction", "solution-solve.sh"),
        (ReviewerRole.DOMAIN_REVIEWER,),
    ),
    TaskRubricCriterion(
        "instruction-clarity",
        "Instruction clarity",
        "Could a capable agent determine what to do without guessing the acceptance boundary?",
        "The task may leave method choice open, but outputs and scientific constraints must be clear.",
        ("instruction",),
        (
            ReviewerRole.DOMAIN_REVIEWER,
            ReviewerRole.TECHNICAL_REVIEWER,
        ),
    ),
    TaskRubricCriterion(
        "artifact-adequacy",
        "Evidence adequacy",
        "Do required artifacts provide enough evidence to assess the scientific claim?",
        "A scalar answer alone is usually insufficient when diagnostics or provenance matter.",
        ("instruction", "task-config"),
        (ReviewerRole.DOMAIN_REVIEWER,),
    ),
    TaskRubricCriterion(
        "verifier-validity",
        "Verifier validity",
        "Does the verifier reward the intended scientific outcome and reject important failure modes?",
        "Check for false positives, false negatives, path assumptions, and thresholds without justification.",
        ("tests-test_verifier.py", "instruction"),
        (
            ReviewerRole.DOMAIN_REVIEWER,
            ReviewerRole.TECHNICAL_REVIEWER,
        ),
    ),
    TaskRubricCriterion(
        "oracle-validity",
        "Reference solution validity",
        "Does the oracle solve the task in a scientifically defensible and reproducible way?",
        "Passing the verifier is necessary but does not by itself establish scientific correctness.",
        ("solution-solve.sh", "instruction"),
        (
            ReviewerRole.DOMAIN_REVIEWER,
            ReviewerRole.TECHNICAL_REVIEWER,
        ),
    ),
    TaskRubricCriterion(
        "isolation-and-safety",
        "Isolation and safety",
        "Are task and verifier environments reproducible, appropriately isolated, and safe to run?",
        "Inspect dependencies, network access, resource bounds, and the separate verifier environment.",
        ("environment-Dockerfile", "tests-Dockerfile", "task-config"),
        (ReviewerRole.TECHNICAL_REVIEWER,),
    ),
    TaskRubricCriterion(
        "benchmark-calibration",
        "Benchmark calibration",
        "Is the task difficult, discriminating, and feasible for the intended benchmark population?",
        "Use oracle/nop results and representative agent runs; avoid merely subjective difficulty claims.",
        ("task-config", "instruction"),
        (
            ReviewerRole.DOMAIN_REVIEWER,
            ReviewerRole.FINAL_APPROVER,
        ),
    ),
    TaskRubricCriterion(
        "benchmark-readiness",
        "Benchmark readiness",
        "Are authorship, conflicts, provenance, licensing, and review evidence sufficient for release?",
        "Final approval requires independent domain and technical review, not author validation alone.",
        ("task-config",),
        (ReviewerRole.FINAL_APPROVER,),
    ),
)


def rubric_for_role(role: ReviewerRole | str) -> tuple[TaskRubricCriterion, ...]:
    reviewer_role = ReviewerRole(role)
    if reviewer_role is ReviewerRole.AUTHOR_VALIDATION:
        return TASK_REVIEW_RUBRIC
    return tuple(
        item for item in TASK_REVIEW_RUBRIC if reviewer_role in item.primary_roles
    )
