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
def _(
    active_step,
    authoring_progress_markdown,
    draft,
    draft_error,
    mo,
    task_summary_markdown,
):
    error_view = (
        mo.callout(mo.md(draft_error), kind="warn") if draft_error else mo.md("")
    )
    mo.vstack(
        [
            mo.md(
                "# Terminal-Bench Science Task Studio\n\n"
                "Turn a scientific question into a reviewable Harbor task. "
                "No Python or container editing is required in this workspace."
            ),
            error_view,
            mo.hstack(
                [
                    mo.callout(
                        mo.md(authoring_progress_markdown(int(active_step.value))),
                        kind="neutral",
                    ),
                    mo.md(task_summary_markdown(draft)),
                ],
                widths=[1, 2],
                align="start",
                gap=2,
            ),
        ],
        gap=2,
    )
    return


if __name__ == "__main__":
    app.run()
