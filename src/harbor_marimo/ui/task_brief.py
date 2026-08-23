"""Review-flow and criterion presentation helpers."""

from __future__ import annotations

from ..profiles import ReviewCriterion


def review_steps_markdown(active: int = 1) -> str:
    labels = ("Understand the task", "Inspect evidence", "Compare attempts", "Record judgment")
    return "  →  ".join(
        f"**{index}. {label}**" if index == active else f"{index}. {label}"
        for index, label in enumerate(labels, start=1)
    )


def criteria_rows(criteria: tuple[ReviewCriterion, ...]) -> list[dict[str, str]]:
    return [
        {
            "criterion": criterion.label,
            "what to examine": criterion.guidance or "Apply your domain judgment.",
        }
        for criterion in criteria
    ]
