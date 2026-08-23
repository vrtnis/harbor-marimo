import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full")


@app.cell
def _():
    from html import escape
    import json
    from pathlib import Path

    import marimo as mo

    from harbor_marimo import load
    from harbor_marimo.domains.science import (
        ScienceAdapter,
        compare_trials,
        diagnostic_findings,
        preview_artifact,
        science_glossary,
    )
    from harbor_marimo.profiles import load_review_profile
    from harbor_marimo.reviews import (
        CriterionAssessment,
        CriterionStatus,
        EvidenceReference,
        JsonReviewStore,
        record_review,
    )
    from harbor_marimo.ui import (
        criteria_rows,
        evidence_markdown,
        evidence_options,
        expert_comparison_rows,
        glossary_markdown,
        review_header_markdown,
        review_steps_markdown,
        technical_details_markdown,
        trial_options as build_trial_options,
        validate_review_submission,
    )

    return (
        CriterionAssessment,
        CriterionStatus,
        EvidenceReference,
        JsonReviewStore,
        Path,
        ScienceAdapter,
        compare_trials,
        criteria_rows,
        diagnostic_findings,
        evidence_markdown,
        evidence_options,
        expert_comparison_rows,
        escape,
        glossary_markdown,
        json,
        load,
        load_review_profile,
        mo,
        preview_artifact,
        record_review,
        review_header_markdown,
        review_steps_markdown,
        science_glossary,
        technical_details_markdown,
        build_trial_options,
        validate_review_submission,
    )


@app.cell
def _(JsonReviewStore, Path, json, load_review_profile, mo):
    cli = mo.cli_args()
    raw_sources = cli.get("jobs-json")
    try:
        cli_sources = json.loads(raw_sources) if raw_sources else []
    except (TypeError, json.JSONDecodeError):
        cli_sources = []
    demo = (
        Path.cwd()
        / "examples"
        / "science-review"
        / "demo_data"
        / "harbor_job"
    )
    default_source = Path(cli_sources[0]) if cli_sources else demo
    demo_profile = demo.parents[1] / "review_profile.json"
    requested_profile = cli.get("profile")
    profile_path = Path(requested_profile) if requested_profile else (
        demo_profile if not cli_sources else None
    )
    profile_error = None
    profile = None
    if profile_path:
        try:
            profile = load_review_profile(profile_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            profile_error = str(exc)
    guided = str(cli.get("guided") or "").lower() in {"1", "true", "yes", "on"}
    developer = str(cli.get("developer") or "").lower() in {"1", "true", "yes", "on"}
    source_input = mo.ui.text(
        value=str(default_source),
        label="Harbor job, trial, result, or ATIF path",
        debounce=600,
        full_width=True,
    )
    review_directory = Path(
        cli.get("review-dir") or Path.cwd() / "reviews"
    ).expanduser().resolve()
    review_store = JsonReviewStore(review_directory)
    return (
        default_source,
        developer,
        guided,
        profile,
        profile_error,
        profile_path,
        review_directory,
        review_store,
        source_input,
    )


@app.cell
def _(default_source, load, source_input):
    source_error = None
    try:
        bundle = load(source_input.value or default_source)
    except (FileNotFoundError, OSError, ValueError) as exc:
        source_error = str(exc)
        bundle = load(default_source)
    tables = bundle.tables()
    return bundle, source_error, tables


@app.cell
def _(build_trial_options, mo, tables):
    trial_options = build_trial_options(tables["trials"])
    trial_picker = mo.ui.radio(
        options=trial_options,
        value=next(iter(trial_options)),
        label="Review attempt",
        inline=True,
    )
    return (trial_picker,)


@app.cell
def _(mo, profile, tables, trial_picker):
    selected_trial = next(
        row for row in tables["trials"] if row["trial_id"] == trial_picker.value
    )
    selected_artifacts = [
        row for row in tables["artifacts"] if row["trial_id"] == trial_picker.value
    ]
    artifact_options = {}
    for _index, _row in enumerate(selected_artifacts):
        _destination = str(_row.get("destination") or f"Artifact {_index + 1}")
        _presentation = (
            profile.artifact_presentation(_destination) if profile else None
        )
        _label = (
            _presentation.label
            if _presentation and _presentation.label
            else _destination
        )
        artifact_options[_label] = str(_index)
    if not artifact_options:
        artifact_options = {"No collected artifact": "-1"}
    artifact_picker = mo.ui.dropdown(
        options=artifact_options,
        value=next(iter(artifact_options)),
        label="Scientific artifact",
        full_width=True,
    )
    return artifact_picker, selected_artifacts, selected_trial


@app.cell
def _(
    ScienceAdapter,
    bundle,
    criteria_rows,
    evidence_options,
    guided,
    glossary_markdown,
    mo,
    profile,
    review_header_markdown,
    review_steps_markdown,
    science_glossary,
    selected_trial,
    technical_details_markdown,
):
    domain_view = ScienceAdapter(profile).build_view(
        bundle, trial_id=selected_trial["trial_id"]
    )
    header_view = mo.md(review_header_markdown(domain_view, guided=guided))
    steps_view = mo.callout(mo.md(review_steps_markdown(1)), kind="neutral")
    criterion_rows = criteria_rows(domain_view.criteria)
    criteria_view = (
        mo.ui.table(criterion_rows, selection=None)
        if criterion_rows
        else mo.md("No domain-specific acceptance criteria were supplied.")
    )
    technical_view = mo.accordion(
        {"Technical run details": mo.md(technical_details_markdown(selected_trial))}
    )
    glossary_view = mo.accordion(
        {
            "Terms used in this review": mo.md(
                glossary_markdown(science_glossary(profile))
            )
        }
    )
    onboarding_view = (
        mo.callout(
            mo.md(
                "This is a guided training review. Work from the scientific question "
                "to the evidence, compare attempts, then record your independent judgment."
            ),
            kind="info",
        )
        if guided
        else mo.md("")
    )
    evidence_citation_input = mo.ui.multiselect(
        options=evidence_options(domain_view.evidence),
        label="Evidence supporting this judgment",
        full_width=True,
    )
    return (
        criteria_view,
        domain_view,
        evidence_citation_input,
        glossary_view,
        header_view,
        onboarding_view,
        steps_view,
        technical_view,
    )


@app.cell
def _(
    artifact_picker,
    domain_view,
    evidence_markdown,
    mo,
    preview_artifact,
    selected_artifacts,
):
    artifact_index = int(artifact_picker.value)
    selected_artifact = (
        selected_artifacts[artifact_index] if artifact_index >= 0 else None
    )
    artifact_preview = (
        preview_artifact(selected_artifact) if selected_artifact else None
    )
    selected_evidence = (
        domain_view.evidence[artifact_index] if artifact_index >= 0 else None
    )
    evidence_context_view = (
        mo.md(evidence_markdown(selected_evidence))
        if selected_evidence
        else mo.md("No evidence was collected for this attempt.")
    )
    return artifact_preview, evidence_context_view, selected_artifact, selected_evidence


@app.cell
def _(domain_view, mo, review_store, selected_trial):
    prior_review = review_store.latest(
        job_id=selected_trial["job_id"],
        trial_id=selected_trial["trial_id"],
        domain="science",
    )
    decision_options = {
        "Approve": "approve",
        "Needs follow-up": "needs_follow_up",
        "Reject": "reject",
    }
    initial_decision = prior_review.verdict.value if prior_review else "needs_follow_up"
    decision_input = mo.ui.dropdown(
        options=decision_options,
        value=next(
            label for label, value in decision_options.items() if value == initial_decision
        ),
        label="Expert verdict",
        full_width=True,
    )
    _prior_assessments = {
        item.criterion_id: item.status.value
        for item in (prior_review.criteria if prior_review else ())
    }
    _status_options = {
        "Satisfied": "satisfied",
        "Uncertain": "uncertain",
        "Not satisfied": "not_satisfied",
    }
    criterion_inputs = {}
    for _criterion in domain_view.criteria:
        _initial_status = _prior_assessments.get(_criterion.id, "uncertain")
        _initial_label = next(
            _label
            for _label, _value in _status_options.items()
            if _value == _initial_status
        )
        criterion_inputs[_criterion.id] = mo.ui.dropdown(
            options=_status_options,
            value=_initial_label,
            label=_criterion.label,
            full_width=True,
        )
    criterion_assessment_view = (
        mo.vstack(list(criterion_inputs.values()), gap=0.5)
        if criterion_inputs
        else mo.md("No structured criteria were supplied for this review.")
    )
    note_input = mo.ui.text_area(
        value=prior_review.note if prior_review else "",
        label="Scientific rationale",
        placeholder="Reference convergence, validity, artifacts, or follow-up work.",
        rows=5,
        full_width=True,
    )
    follow_up_input = mo.ui.text_area(
        value=(prior_review.follow_up or "") if prior_review else "",
        label="Required follow-up",
        placeholder="Describe the additional evidence, correction, or rerun required.",
        rows=3,
        full_width=True,
    )
    reviewer_input = mo.ui.text(
        value=(prior_review.reviewer or "") if prior_review else "",
        label="Reviewer",
        full_width=True,
    )
    confidence_input = mo.ui.slider(
        0,
        100,
        step=5,
        value=int(
            (prior_review.confidence if prior_review and prior_review.confidence is not None else 0.8)
            * 100
        ),
        label="Confidence",
        show_value=True,
    )
    save_button = mo.ui.run_button(label="Save scientific review")
    return (
        confidence_input,
        criterion_assessment_view,
        criterion_inputs,
        decision_input,
        follow_up_input,
        note_input,
        reviewer_input,
        save_button,
    )


@app.cell
def _(
    CriterionAssessment,
    CriterionStatus,
    EvidenceReference,
    confidence_input,
    criterion_inputs,
    decision_input,
    developer,
    domain_view,
    evidence_citation_input,
    follow_up_input,
    mo,
    note_input,
    record_review,
    review_directory,
    review_store,
    reviewer_input,
    save_button,
    selected_trial,
    validate_review_submission,
):
    save_status = (
        mo.md(f"Developer sidecar destination: `{review_directory}`")
        if developer
        else mo.md("Complete the assessment, cite evidence, and save your judgment.")
    )
    if save_button.value:
        _cited_keys = set(evidence_citation_input.value)
        _criterion_values = {
            _criterion.label: criterion_inputs[_criterion.id].value
            for _criterion in domain_view.criteria
        }
        _validation_errors = validate_review_submission(
            verdict=decision_input.value,
            reviewer=reviewer_input.value,
            rationale=note_input.value,
            follow_up=follow_up_input.value,
            criteria=_criterion_values,
            evidence_count=len(_cited_keys),
        )
        if _validation_errors:
            save_status = mo.callout(
                mo.md("**Review not saved**\n\n" + "\n".join(f"- {_error}" for _error in _validation_errors)),
                kind="danger",
            )
        else:
            _evidence = tuple(
                EvidenceReference(
                    key=_item.key,
                    kind=_item.kind,
                    job_id=selected_trial["job_id"],
                    trial_id=selected_trial["trial_id"],
                    step_name=_item.step_name,
                    label=_item.label,
                    path=str(_item.path) if _item.path else None,
                    locator=_item.technical_label,
                )
                for _item in domain_view.evidence
                if _item.key in _cited_keys
            )
            _assessments = tuple(
                CriterionAssessment(
                    criterion_id=_criterion.id,
                    status=CriterionStatus(criterion_inputs[_criterion.id].value),
                )
                for _criterion in domain_view.criteria
            )
            review, destination = record_review(
                review_store,
                job_id=selected_trial["job_id"],
                trial_id=selected_trial["trial_id"],
                domain="science",
                verdict=decision_input.value,
                note=note_input.value.strip(),
                reviewer=reviewer_input.value.strip() or None,
                confidence=confidence_input.value / 100,
                evidence=_evidence,
                criteria=_assessments,
                follow_up=follow_up_input.value.strip() or None,
            )
            _developer_destination = (
                f"\n\nDeveloper destination: `{destination}`" if developer else ""
            )
            save_status = mo.callout(
                mo.md(
                    f"**Review saved**\n\n"
                    f"Verdict: `{review.verdict.value}`  \n"
                    f"Review: `{review.review_id}`  \n"
                    f"Updated: `{review.updated_at}`\n\n"
                    "The original Harbor run was not modified."
                    f"{_developer_destination}"
                ),
                kind="success",
            )
    return (save_status,)


@app.cell
def _(artifact_preview, escape, mo):
    if artifact_preview is None:
        preview_view = mo.callout("No collected artifact for this trial.", kind="warn")
    elif artifact_preview.rows:
        header = artifact_preview.rows[0]
        preview_view = mo.ui.table(
            [
                {
                    header[index] if index < len(header) else f"column_{index + 1}": value
                    for index, value in enumerate(row)
                }
                for row in artifact_preview.rows[1:]
            ],
            selection=None,
        )
    elif artifact_preview.text is not None:
        preview_view = mo.Html(
            f"<pre style='max-height:32rem;overflow:auto;white-space:pre-wrap'>{escape(artifact_preview.text)}</pre>"
        )
    elif artifact_preview.kind == "image" and artifact_preview.path:
        preview_view = mo.image(str(artifact_preview.path))
    else:
        preview_view = mo.callout(
            artifact_preview.warning or f"Artifact available at {artifact_preview.path}",
            kind="warn",
        )
    return (preview_view,)


@app.cell
def _(
    bundle,
    compare_trials,
    diagnostic_findings,
    expert_comparison_rows,
    mo,
    selected_trial,
):
    comparison_view = mo.ui.table(
        expert_comparison_rows(compare_trials(bundle)), selection=None
    )
    findings = diagnostic_findings(bundle, trial_id=selected_trial["trial_id"])
    findings_view = (
        mo.ui.table(
            [
                {
                    "severity": item.severity,
                    "finding": item.label,
                    "source": item.source,
                }
                for item in findings
            ],
            selection=None,
        )
        if findings
        else mo.md("No explicit convergence or failure signal was found in verifier text.")
    )
    return comparison_view, findings_view


@app.cell
def _(
    artifact_picker,
    comparison_view,
    confidence_input,
    criterion_assessment_view,
    criteria_view,
    developer,
    decision_input,
    evidence_citation_input,
    evidence_context_view,
    findings_view,
    follow_up_input,
    glossary_view,
    header_view,
    mo,
    note_input,
    onboarding_view,
    profile_error,
    preview_view,
    reviewer_input,
    save_button,
    save_status,
    selected_trial,
    source_error,
    source_input,
    steps_view,
    technical_view,
    trial_picker,
):
    error_view = (
        mo.callout(source_error, kind="danger") if source_error else mo.md("")
    )
    profile_error_view = (
        mo.callout(f"Review profile could not be loaded: {profile_error}", kind="warn")
        if profile_error
        else mo.md("")
    )
    source_control_view = (
        mo.vstack([mo.md("### Developer source control"), source_input])
        if developer
        else mo.md("")
    )
    mo.vstack(
        [
            header_view,
            onboarding_view,
            steps_view,
            technical_view,
            mo.md("## Acceptance criteria"),
            criteria_view,
            glossary_view,
            source_control_view,
            error_view,
            profile_error_view,
            mo.hstack([trial_picker, artifact_picker], widths="equal"),
            mo.md("## Collected scientific evidence"),
            evidence_context_view,
            preview_view,
            mo.md("## Verifier diagnostic signals"),
            findings_view,
            mo.md("## Compare trials"),
            comparison_view,
            mo.md("## Domain-expert judgment"),
            mo.md("Assess each acceptance criterion before choosing an overall verdict."),
            criterion_assessment_view,
            evidence_citation_input,
            decision_input,
            note_input,
            follow_up_input,
            reviewer_input,
            confidence_input,
            save_button,
            save_status,
        ],
        gap=0.8,
    )


if __name__ == "__main__":
    app.run()
