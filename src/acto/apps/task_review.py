import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo

    from acto.task_reviews import (
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
    from acto.ui import (
        card_style,
        compact_task_instruction,
        product_css,
        review_header_html,
        section_header_html,
    )

    return (
        Path,
        ReviewerRole,
        RubricAssessment,
        RubricStatus,
        TaskReview,
        TaskReviewStore,
        TaskReviewVerdict,
        card_style,
        compact_task_instruction,
        load_task_bundle,
        mo,
        product_css,
        read_task_evidence,
        review_header_html,
        reviewer_assignment_issues,
        rubric_for_role,
        section_header_html,
    )


@app.cell
def _(Path, TaskReviewStore, mo):
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
    review_directory = Path(
        cli.get("review-dir") or Path.cwd() / "outputs" / "task-reviews"
    ).expanduser().resolve()
    task_review_store = TaskReviewStore(review_directory)
    return (
        cli,
        default_task,
        review_directory,
        task_path_input,
        task_review_store,
    )


@app.cell
def _(default_task, load_task_bundle, task_path_input):
    bundle_error = None
    try:
        task_bundle = load_task_bundle(task_path_input.value)
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        bundle_error = str(exc)
        task_bundle = load_task_bundle(default_task)
    return bundle_error, task_bundle


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
def _(card_style, compact_task_instruction, mo, section_header_html, task_bundle):
    task_metadata = task_bundle.config.get("metadata") or {}
    visible_files = [
        item
        for item in task_bundle.files
        if "__pycache__" not in item.path and not item.path.endswith(".pyc")
    ]
    task_file_inventory = mo.ui.table(
        [
            {
                "File": item.path,
                "Bytes": item.size,
                "SHA-256": item.sha256[:16],
            }
            for item in visible_files
        ],
        selection=None,
    )
    task_instruction_view = mo.md(
        compact_task_instruction(task_bundle.instruction)
    ).style({"max-height": "310px", "overflow": "auto", "padding-right": "8px"})
    task_overview = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    1,
                    "Task brief",
                    "Review the task as written before inspecting its implementation.",
                    responsive_grid_item=True,
                )
            ),
            mo.callout(
                task_instruction_view,
                kind="neutral",
            ),
        ],
        gap=1,
    ).style(card_style())
    return task_file_inventory, task_metadata, task_overview


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
def _(
    card_style,
    evidence_picker,
    mo,
    read_task_evidence,
    section_header_html,
    task_bundle,
):
    evidence_preview_error = None
    try:
        evidence_preview = read_task_evidence(task_bundle, evidence_picker.value)
    except (KeyError, FileNotFoundError, OSError, UnicodeError, ValueError) as exc:
        evidence_preview = ""
        evidence_preview_error = str(exc)
    evidence_preview_view = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    2,
                    "Inspect task evidence",
                    "Compare the instruction, verifier, oracle, and environment.",
                )
            ),
            evidence_picker,
            (
                mo.callout(mo.md(evidence_preview_error), kind="warn")
                if evidence_preview_error
                else mo.plain_text(evidence_preview).style(
                    {
                        "max-height": "260px",
                        "overflow": "auto",
                        "padding": "12px",
                        "background": "#f7f8fb",
                        "border": "1px solid #e3e7ee",
                        "border-radius": "9px",
                    }
                )
            ),
            mo.md(
                "Cite the evidence keys shown in the rubric. Files are displayed as "
                "read-only text and are never executed here."
            ),
        ],
        gap=1,
    ).style(card_style())
    return (evidence_preview_view,)


@app.cell
def _(
    assessment_editor,
    bundle_error,
    card_style,
    conflict_input,
    evidence_preview_view,
    follow_up_input,
    mo,
    prior_reviews,
    product_css,
    review_directory,
    review_header_html,
    review_note_input,
    review_history_view,
    review_mode_view,
    reviewer_input,
    role_input,
    save_error,
    save_review_button,
    saved_review_path,
    section_header_html,
    submission_error,
    task_bundle,
    task_file_inventory,
    task_metadata,
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
    reviewer_panel = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    3,
                    "Reviewer assignment",
                    "Confirm independence before recording a judgment.",
                    responsive_grid_item=True,
                )
            ),
            reviewer_input,
            role_input,
            conflict_input,
            review_mode_view,
            mo.md("### Previous reviews"),
            review_history_view,
        ],
        gap=1,
    ).style(card_style())
    rubric_panel = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    4,
                    "Rubric assessment",
                    "Record a finding and evidence for each review criterion.",
                )
            ),
            assessment_editor,
        ],
        gap=1,
    ).style(card_style())
    decision_panel = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    5,
                    "Decision",
                    "Summarize the judgment and any required follow-up.",
                )
            ),
            verdict_input,
            review_note_input,
            follow_up_input,
            save_review_button,
        ],
        gap=1,
    ).style(card_style())
    technical_details = mo.accordion(
        {
            "Technical details": mo.vstack(
                [
                    task_path_input,
                    task_file_inventory,
                    mo.md(f"Review sidecars are stored under `{review_directory}`."),
                ],
                gap=1,
            )
        }
    )
    header_view = mo.Html(
        review_header_html(
            task_name=task_bundle.task_name,
            author=task_bundle.task_author,
            domain=str(task_metadata.get("domain") or ""),
            field=str(task_metadata.get("field") or ""),
            evidence_count=len(task_bundle.evidence()),
            prior_review_count=len(prior_reviews),
        )
    )
    mo.vstack(
        [
            mo.Html(product_css()),
            header_view,
            warning_view,
            mo.hstack(
                [task_overview, reviewer_panel],
                widths=[3, 2],
                align="start",
                gap=1,
            ),
            evidence_preview_view,
            rubric_panel,
            decision_panel,
            saved_view,
            technical_details,
        ],
        gap=1.25,
    )
    return


if __name__ == "__main__":
    app.run()
