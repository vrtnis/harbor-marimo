import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo

    from harbor_marimo.task_reviews import (
        ReviewerRole,
        RubricAssessment,
        RubricStatus,
        TaskReview,
        TaskReviewStore,
        TaskReviewVerdict,
        load_task_bundle,
        read_task_evidence,
        reviewer_assignment_issues,
        rubric_for_role,
    )

    return (
        Path,
        ReviewerRole,
        RubricAssessment,
        RubricStatus,
        TaskReview,
        TaskReviewStore,
        TaskReviewVerdict,
        load_task_bundle,
        mo,
        read_task_evidence,
        reviewer_assignment_issues,
        rubric_for_role,
    )


@app.cell
def _(Path, TaskReviewStore, load_task_bundle, mo):
    cli = mo.cli_args()
    default_task = (
        Path.cwd()
        / "examples"
        / "science-task-review"
        / "bayesian-posterior-convergence"
    )
    task_path_input = mo.ui.text(
        value=str(Path(cli.get("task") or default_task).expanduser().resolve()),
        label="Harbor task directory",
        debounce=600,
        full_width=True,
    )
    bundle_error = None
    try:
        task_bundle = load_task_bundle(task_path_input.value)
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        bundle_error = str(exc)
        task_bundle = load_task_bundle(default_task)
    review_directory = Path(
        cli.get("review-dir") or Path.cwd() / "outputs" / "task-reviews"
    ).expanduser().resolve()
    task_review_store = TaskReviewStore(review_directory)
    return (
        bundle_error,
        cli,
        review_directory,
        task_bundle,
        task_path_input,
        task_review_store,
    )


@app.cell
def _(ReviewerRole, mo):
    reviewer_input = mo.ui.text(label="Reviewer name", full_width=True)
    role_input = mo.ui.dropdown(
        options={
            "Author validation (not approval)": ReviewerRole.AUTHOR_VALIDATION.value,
            "Independent domain review": ReviewerRole.DOMAIN_REVIEWER.value,
            "Independent technical review": ReviewerRole.TECHNICAL_REVIEWER.value,
            "Final benchmark approval": ReviewerRole.FINAL_APPROVER.value,
        },
        value="Independent domain review",
        label="Review role",
        full_width=True,
    )
    conflict_input = mo.ui.text_area(
        value="No conflict",
        label="Conflict declaration",
        rows=2,
        full_width=True,
    )
    return conflict_input, reviewer_input, role_input


@app.cell
def _(role_input, rubric_for_role):
    active_rubric = rubric_for_role(role_input.value)
    return (active_rubric,)


@app.cell
def _(ReviewerRole, mo, role_input):
    if role_input.value == ReviewerRole.AUTHOR_VALIDATION.value:
        review_mode_view = mo.callout(
            mo.md(
                "**Author-validation mode:** use this to challenge the instruction, oracle, "
                "fixtures, and verifier before handoff. This record cannot approve the task."
            ),
            kind="warn",
        )
    elif role_input.value == ReviewerRole.FINAL_APPROVER.value:
        review_mode_view = mo.callout(
            mo.md(
                "**Final-approval mode:** confirm that independent domain and technical "
                "findings are resolved before accepting the task into the benchmark."
            ),
            kind="info",
        )
    else:
        review_mode_view = mo.callout(
            mo.md(
                "**Independent-review mode:** assess the task rather than the author, cite "
                "task evidence, and disclose any relationship that could affect judgment."
            ),
            kind="info",
        )
    return (review_mode_view,)


@app.cell
def _(RubricStatus, active_rubric, mo):
    assessment_editor = mo.ui.data_editor(
        [
            {
                "criterion_id": item.id,
                "criterion": item.label,
                "review_question": item.question,
                "status": RubricStatus.UNCERTAIN.value,
                "reviewer_note": "",
                "evidence_keys": ", ".join(item.evidence_keys),
            }
            for item in active_rubric
        ],
        label="Independent task-review rubric",
    )
    return (assessment_editor,)


@app.cell
def _(TaskReviewVerdict, mo):
    verdict_input = mo.ui.radio(
        options={
            "Approve": TaskReviewVerdict.APPROVE.value,
            "Request changes": TaskReviewVerdict.REQUEST_CHANGES.value,
            "Reject": TaskReviewVerdict.REJECT.value,
        },
        value="Request changes",
        label="Task-review decision",
        inline=True,
    )
    review_note_input = mo.ui.text_area(
        label="Decision rationale",
        rows=5,
        full_width=True,
    )
    follow_up_input = mo.ui.text_area(
        label="Required changes or follow-up",
        rows=3,
        full_width=True,
    )
    save_review_button = mo.ui.run_button(label="Save task review")
    return follow_up_input, review_note_input, save_review_button, verdict_input


@app.cell
def _(
    RubricAssessment,
    RubricStatus,
    assessment_editor,
    conflict_input,
    reviewer_assignment_issues,
    reviewer_input,
    role_input,
    task_bundle,
    verdict_input,
):
    submission_error = None
    task_review = None
    try:
        assessments = tuple(
            RubricAssessment(
                criterion_id=str(row.get("criterion_id") or ""),
                status=RubricStatus(str(row.get("status") or "")),
                note=str(row.get("reviewer_note") or ""),
                evidence_keys=tuple(
                    value.strip()
                    for value in str(row.get("evidence_keys") or "").split(",")
                    if value.strip()
                ),
            )
            for row in list(assessment_editor.value)
        )
        evidence_keys = {item.key for item in task_bundle.evidence()}
        unknown_evidence = sorted(
            {
                key
                for assessment in assessments
                for key in assessment.evidence_keys
            }
            - evidence_keys
        )
        assignment_issues = reviewer_assignment_issues(
            task_author=task_bundle.task_author,
            reviewer=reviewer_input.value,
            reviewer_role=role_input.value,
            conflict_declaration=conflict_input.value,
            verdict=verdict_input.value,
        )
        if unknown_evidence:
            assignment_issues = (
                *assignment_issues,
                "Rubric rows reference unavailable task evidence: "
                + ", ".join(unknown_evidence),
            )
        if assignment_issues:
            submission_error = " ".join(assignment_issues)
    except (AttributeError, TypeError, ValueError) as exc:
        assessments = ()
        assignment_issues = (str(exc),)
        submission_error = str(exc)
    return assessments, assignment_issues, submission_error, task_review


@app.cell
def _(
    TaskReview,
    assessments,
    conflict_input,
    follow_up_input,
    review_note_input,
    reviewer_input,
    role_input,
    save_review_button,
    submission_error,
    task_bundle,
    task_review_store,
    verdict_input,
):
    saved_review_path = None
    save_error = None
    if save_review_button.value and not submission_error:
        try:
            record = TaskReview.create(
                task_name=task_bundle.task_name,
                task_author=task_bundle.task_author,
                reviewer=reviewer_input.value,
                reviewer_role=role_input.value,
                verdict=verdict_input.value,
                conflict_declaration=conflict_input.value,
                note=review_note_input.value,
                assessments=assessments,
                evidence=task_bundle.evidence(),
                follow_up=follow_up_input.value,
            )
            saved_review_path = task_review_store.save(record)
        except (OSError, TypeError, ValueError) as exc:
            save_error = str(exc)
    return save_error, saved_review_path


@app.cell
def _(mo, saved_review_path, task_bundle, task_review_store):
    prior_reviews = task_review_store.list(task_name=task_bundle.task_name)
    review_history_view = (
        mo.ui.table(
            [
                {
                    "Reviewer": item.reviewer,
                    "Role": item.reviewer_role.value.replace("_", " ").title(),
                    "Decision": item.verdict.value.replace("_", " ").title(),
                    "Updated": item.updated_at,
                }
                for item in prior_reviews
            ],
            selection=None,
        )
        if prior_reviews
        else mo.md("No task-review sidecars have been recorded yet.")
    )
    return prior_reviews, review_history_view


@app.cell
def _(mo, task_bundle):
    metadata = task_bundle.config.get("metadata") or {}
    task_overview = mo.vstack(
        [
            mo.md(
                f"## {task_bundle.task_name}\n\n"
                f"**Task author:** {task_bundle.task_author}  \n"
                f"**Domain:** {metadata.get('domain') or 'Not specified'}  \n"
                f"**Field:** {metadata.get('field') or 'Not specified'}"
            ),
            mo.accordion({"Task instruction": mo.md(task_bundle.instruction)}),
            mo.ui.table(
                [
                    {
                        "File": item.path,
                        "Bytes": item.size,
                        "SHA-256": item.sha256[:16],
                    }
                    for item in task_bundle.files
                ],
                selection=None,
            ),
        ],
        gap=1,
    )
    return (task_overview,)


@app.cell
def _(mo, task_bundle):
    evidence_options = {
        f"{item.label} — {item.path}": item.key for item in task_bundle.evidence()
    }
    evidence_picker = mo.ui.dropdown(
        options=evidence_options,
        value=next(iter(evidence_options)),
        label="Inspect task evidence",
        full_width=True,
    )
    return evidence_options, evidence_picker


@app.cell
def _(evidence_picker, mo, read_task_evidence, task_bundle):
    evidence_preview_error = None
    try:
        evidence_preview = read_task_evidence(task_bundle, evidence_picker.value)
    except (KeyError, FileNotFoundError, OSError, UnicodeError, ValueError) as exc:
        evidence_preview = ""
        evidence_preview_error = str(exc)
    evidence_preview_view = mo.vstack(
        [
            evidence_picker,
            (
                mo.callout(mo.md(evidence_preview_error), kind="warn")
                if evidence_preview_error
                else mo.accordion(
                    {
                        "Read-only file content": mo.plain_text(evidence_preview)
                    }
                )
            ),
            mo.md(
                "Use the evidence keys shown in the rubric table to cite the instruction, "
                "verifier, oracle, or environment supporting each finding. Files are read "
                "as inert text and are never executed by this review app."
            ),
        ],
        gap=1,
    )
    return (evidence_preview_view,)


@app.cell
def _(
    assessment_editor,
    bundle_error,
    conflict_input,
    evidence_preview_view,
    follow_up_input,
    mo,
    review_directory,
    review_note_input,
    review_history_view,
    review_mode_view,
    reviewer_input,
    role_input,
    save_error,
    save_review_button,
    saved_review_path,
    submission_error,
    task_overview,
    task_path_input,
    verdict_input,
):
    warnings = [item for item in (bundle_error, submission_error, save_error) if item]
    warning_view = (
        mo.callout(mo.md("\n\n".join(warnings)), kind="warn")
        if warnings
        else mo.md("")
    )
    saved_view = (
        mo.callout(
            mo.md(f"Task review saved as `{saved_review_path}`."),
            kind="success",
        )
        if saved_review_path
        else mo.md("")
    )
    mo.vstack(
        [
            mo.md(
                "# Independent scientific task review\n\n"
                "Review the benchmark task itself before agents are graded on it. "
                "Author validation can improve a task, but only an unconflicted reviewer "
                "can approve it for benchmark use."
            ),
            task_path_input,
            warning_view,
            task_overview,
            evidence_preview_view,
            mo.md("## Reviewer assignment"),
            reviewer_input,
            role_input,
            conflict_input,
            review_mode_view,
            mo.md("### Prior reviews"),
            review_history_view,
            mo.md("## Rubric assessment"),
            assessment_editor,
            mo.md("## Decision"),
            verdict_input,
            review_note_input,
            follow_up_input,
            save_review_button,
            saved_view,
            mo.accordion(
                {"Review storage": mo.md(f"Sidecars are stored under `{review_directory}`.")}
            ),
        ],
        gap=2,
    )
    return


if __name__ == "__main__":
    app.run()
