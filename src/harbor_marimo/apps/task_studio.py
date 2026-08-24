import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    from pathlib import Path

    import marimo as mo

    from harbor_marimo.tasks import ScientificBrief, TaskDraft, TaskMetadata
    from harbor_marimo.ui import authoring_progress_markdown, task_summary_markdown

    return (
        Path,
        ScientificBrief,
        TaskDraft,
        TaskMetadata,
        authoring_progress_markdown,
        json,
        mo,
        task_summary_markdown,
    )


@app.cell
def _(Path, ScientificBrief, TaskDraft, TaskMetadata, json, mo):
    cli = mo.cli_args()
    requested_draft = cli.get("draft")
    draft_path = Path(requested_draft).expanduser().resolve() if requested_draft else None
    draft_error = None
    try:
        if not draft_path:
            raise FileNotFoundError
        draft = TaskDraft.from_dict(json.loads(draft_path.read_text(encoding="utf-8")))
    except (FileNotFoundError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        if draft_path:
            draft_error = f"Could not open the requested task draft: {exc}"
        draft = TaskDraft.create(
            task_name="new-scientific-task",
            metadata=TaskMetadata(author_name="Task author"),
            brief=ScientificBrief(
                title="New scientific benchmark task",
                instruction="Describe the scientific work the agent must complete.",
            ),
        )
    active_step = mo.ui.number(
        start=1,
        stop=5,
        step=1,
        value=1,
        label="Authoring step",
    )
    return active_step, cli, draft, draft_error, draft_path


@app.cell
def _(draft, mo):
    task_name_input = mo.ui.text(
        value=draft.task_name,
        label="Task ID (lowercase words separated by hyphens)",
        full_width=True,
    )
    title_input = mo.ui.text(
        value=draft.brief.title,
        label="Task title",
        full_width=True,
    )
    instruction_input = mo.ui.text_area(
        value=draft.brief.instruction,
        label="What must the agent accomplish?",
        rows=5,
        full_width=True,
    )
    context_input = mo.ui.text_area(
        value=draft.brief.research_context,
        label="Why does this task matter scientifically?",
        rows=4,
        full_width=True,
    )
    difficulty_input = mo.ui.text_area(
        value=draft.brief.difficulty_explanation,
        label="What makes this task challenging?",
        rows=3,
        full_width=True,
    )
    author_input = mo.ui.text(
        value=draft.metadata.author_name,
        label="Task author",
        full_width=True,
    )
    organization_input = mo.ui.text(
        value=draft.metadata.author_organization,
        label="Organization (optional)",
        full_width=True,
    )
    domain_input = mo.ui.text(
        value=draft.metadata.domain,
        label="Scientific domain",
        full_width=True,
    )
    field_input = mo.ui.text(
        value=draft.metadata.field,
        label="Field",
        full_width=True,
    )
    subfield_input = mo.ui.text(
        value=draft.metadata.subfield,
        label="Subfield (optional)",
        full_width=True,
    )
    conflicts_input = mo.ui.text_area(
        value=draft.metadata.conflicts_of_interest,
        label="Conflicts of interest",
        rows=2,
        full_width=True,
    )
    return (
        author_input,
        conflicts_input,
        context_input,
        difficulty_input,
        domain_input,
        field_input,
        instruction_input,
        organization_input,
        subfield_input,
        task_name_input,
        title_input,
    )


@app.cell
def _(
    ScientificBrief,
    TaskMetadata,
    author_input,
    conflicts_input,
    context_input,
    difficulty_input,
    domain_input,
    draft,
    field_input,
    instruction_input,
    organization_input,
    subfield_input,
    task_name_input,
    title_input,
):
    authored_draft_error = None
    try:
        authored_draft = draft.updated(
            task_name=task_name_input.value.strip(),
            metadata=TaskMetadata(
                author_name=author_input.value,
                author_email=draft.metadata.author_email,
                author_organization=organization_input.value,
                author_profile=draft.metadata.author_profile,
                research_advisor=draft.metadata.research_advisor,
                domain=domain_input.value,
                field=field_input.value,
                subfield=subfield_input.value,
                tags=draft.metadata.tags,
                expert_time_estimate_hours=draft.metadata.expert_time_estimate_hours,
                relevant_experience=draft.metadata.relevant_experience,
                conflicts_of_interest=conflicts_input.value,
            ),
            brief=ScientificBrief(
                title=title_input.value,
                instruction=instruction_input.value,
                research_context=context_input.value,
                difficulty_explanation=difficulty_input.value,
                solution_explanation=draft.brief.solution_explanation,
                verification_explanation=draft.brief.verification_explanation,
            ),
        )
    except ValueError as exc:
        authored_draft = draft
        authored_draft_error = str(exc)
    return authored_draft, authored_draft_error


@app.cell
def _(
    author_input,
    conflicts_input,
    context_input,
    difficulty_input,
    domain_input,
    field_input,
    instruction_input,
    mo,
    organization_input,
    subfield_input,
    task_name_input,
    title_input,
):
    brief_form_view = mo.vstack(
        [
            mo.md("## 1. Define the scientific task"),
            mo.md(
                "Write for both an agent attempting the work and an independent scientist "
                "reviewing whether the task is meaningful."
            ),
            task_name_input,
            title_input,
            instruction_input,
            context_input,
            difficulty_input,
            mo.md("### Authorship and scientific area"),
            mo.hstack([author_input, organization_input], widths="equal", gap=2),
            mo.hstack([domain_input, field_input, subfield_input], widths="equal", gap=2),
            conflicts_input,
        ],
        gap=1,
    )
    return (brief_form_view,)


@app.cell
def _(
    active_step,
    authoring_progress_markdown,
    authored_draft,
    authored_draft_error,
    brief_form_view,
    draft_error,
    mo,
    task_summary_markdown,
):
    error_view = (
        mo.callout(mo.md(draft_error), kind="warn") if draft_error else mo.md("")
    )
    authored_error_view = (
        mo.callout(mo.md(authored_draft_error), kind="warn")
        if authored_draft_error
        else mo.md("")
    )
    mo.vstack(
        [
            mo.md(
                "# Terminal-Bench Science Task Studio\n\n"
                "Turn a scientific question into a reviewable Harbor task. "
                "No Python or container editing is required in this workspace."
            ),
            error_view,
            authored_error_view,
            mo.hstack(
                [
                    mo.callout(
                        mo.md(authoring_progress_markdown(int(active_step.value))),
                        kind="neutral",
                    ),
                    mo.md(task_summary_markdown(authored_draft)),
                ],
                widths=[1, 2],
                align="start",
                gap=2,
            ),
            brief_form_view,
        ],
        gap=2,
    )
    return


if __name__ == "__main__":
    app.run()
