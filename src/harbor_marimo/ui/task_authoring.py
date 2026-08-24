"""Framework-light presentation helpers for the task-authoring application."""

from __future__ import annotations

from typing import Iterable, Mapping

from harbor_marimo.tasks import TaskDraft


AUTHORING_STEPS = (
    "Define the scientific task",
    "Specify result artifacts",
    "Build acceptance checks",
    "Test known examples",
    "Validate and export",
)


def authoring_progress_markdown(active_step: int) -> str:
    """Render a compact, non-technical progress list."""

    rows = []
    for index, label in enumerate(AUTHORING_STEPS, start=1):
        marker = "**Current**" if index == active_step else ("Done" if index < active_step else "Next")
        rows.append(f"{index}. {label} — {marker}")
    return "\n".join(rows)


def task_summary_markdown(draft: TaskDraft) -> str:
    domain = " / ".join(
        value
        for value in (
            draft.metadata.domain,
            draft.metadata.field,
            draft.metadata.subfield,
        )
        if value
    ) or "Not yet specified"
    return (
        f"## {draft.brief.title}\n\n"
        f"**Task ID:** `{draft.task_name}`  \n"
        f"**Scientific area:** {domain}  \n"
        f"**Author:** {draft.metadata.author_name}\n\n"
        f"{draft.brief.research_context or 'Add the research context for reviewers and task solvers.'}"
    )


def artifact_rows(draft: TaskDraft) -> list[dict[str, object]]:
    return [
        {
            "Result artifact": item.path,
            "Format": item.format.upper(),
            "Required": "Yes" if item.required else "No",
            "Purpose": item.description,
            "Expected fields": ", ".join(field.name for field in item.fields) or "—",
        }
        for item in draft.artifacts
    ]


def check_rows(draft: TaskDraft) -> list[dict[str, object]]:
    return [
        {
            "Criterion": item.description or item.id,
            "Evidence": item.artifact,
            "Automated check": item.type.replace("_", " ").title(),
            "Expert guidance": item.expert_guidance,
            "Human judgment": "Required" if item.expert_only else "Supported by verifier",
        }
        for item in draft.checks
    ]


def fixture_rows(draft: TaskDraft) -> list[dict[str, object]]:
    return [
        {
            "Example": item.name,
            "Expected outcome": "Pass" if item.expected_pass else "Fail",
            "Folder": item.source,
            "Why": item.explanation,
        }
        for item in draft.fixtures
    ]


def validation_rows(results: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "Validation": str(item.get("label") or item.get("name") or "Check"),
            "Status": "Passed" if item.get("passed") else "Needs attention",
            "Details": str(item.get("details") or item.get("message") or ""),
        }
        for item in results
    ]


def draft_readiness(draft: TaskDraft) -> tuple[str, ...]:
    """Return author-facing blockers without executing task content."""

    issues: list[str] = []
    if not draft.brief.research_context.strip():
        issues.append("Explain why the task matters scientifically.")
    if not draft.artifacts:
        issues.append("Define at least one result artifact.")
    if not draft.checks:
        issues.append("Define at least one acceptance check.")
    if draft.checks and not draft.fixtures:
        issues.append("Add passing and failing examples for the verifier.")
    artifact_paths = {item.path for item in draft.artifacts}
    missing = sorted({item.artifact for item in draft.checks} - artifact_paths)
    if missing:
        issues.append("Checks reference undefined artifacts: " + ", ".join(missing))
    return tuple(issues)
