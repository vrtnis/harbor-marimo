import marimo

__generated_with = "0.23.16"
app = marimo.App(width="full")


@app.cell
def _():
    import json
    from pathlib import Path
    import subprocess

    import marimo as mo

    from acto.tasks import (
        ArtifactContract,
        ArtifactField,
        ScientificBrief,
        TaskDraftStore,
        TaskDraft,
        TaskMetadata,
        VerifierCheck,
        VerifierFixture,
        export_task_bundle,
        harbor_validation_plan,
        run_harbor_validation,
        run_fixture_workbench,
    )
    from acto.ui import (
        AUTHORING_STEPS,
        card_style,
        draft_readiness,
        product_css,
        section_header_html,
        studio_header_html,
        studio_progress_html,
        studio_summary_html,
    )

    return (
        ArtifactContract,
        ArtifactField,
        AUTHORING_STEPS,
        Path,
        ScientificBrief,
        TaskDraftStore,
        TaskDraft,
        TaskMetadata,
        VerifierCheck,
        VerifierFixture,
        card_style,
        draft_readiness,
        export_task_bundle,
        harbor_validation_plan,
        json,
        mo,
        product_css,
        run_harbor_validation,
        run_fixture_workbench,
        subprocess,
        section_header_html,
        studio_header_html,
        studio_progress_html,
        studio_summary_html,
    )


@app.cell
def _(AUTHORING_STEPS, Path, ScientificBrief, TaskDraft, TaskMetadata, json, mo):
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
    active_step = mo.ui.dropdown(
        options={
            f"{index}. {label}": index
            for index, label in enumerate(AUTHORING_STEPS, start=1)
        },
        value=f"1. {AUTHORING_STEPS[0]}",
        label="Current step",
        full_width=True,
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
def _(authored_draft, mo):
    artifact_seed = [
        {
            "path": item.path,
            "format": item.format,
            "description": item.description,
            "required": item.required,
        }
        for item in authored_draft.artifacts
    ] or [
        {
            "path": "results/answer.csv",
            "format": "csv",
            "description": "Primary scientific result",
            "required": True,
        }
    ]
    field_seed = [
        {
            "artifact": item.path,
            "name": field.name,
            "data_type": field.data_type,
            "required": field.required,
            "description": field.description,
        }
        for item in authored_draft.artifacts
        for field in item.fields
    ]
    artifact_editor = mo.ui.data_editor(
        artifact_seed,
        label="Result files the agent must produce",
    )
    field_editor = mo.ui.data_editor(
        field_seed,
        label="Required fields inside CSV or JSON results",
    )
    return artifact_editor, field_editor


@app.cell
def _(
    ArtifactContract,
    ArtifactField,
    artifact_editor,
    authored_draft,
    field_editor,
):
    artifact_error = None
    artifact_contracts = authored_draft.artifacts
    try:
        field_rows = list(field_editor.value)
        contract_rows = list(artifact_editor.value)
        artifact_contracts = tuple(
            ArtifactContract(
                path=str(row.get("path") or "").strip(),
                format=str(row.get("format") or "file").strip().lower(),
                description=str(row.get("description") or "").strip(),
                required=bool(row.get("required", True)),
                fields=tuple(
                    ArtifactField(
                        name=str(field.get("name") or "").strip(),
                        data_type=str(field.get("data_type") or "string").strip(),
                        required=bool(field.get("required", True)),
                        description=str(field.get("description") or "").strip(),
                    )
                    for field in field_rows
                    if str(field.get("artifact") or "").strip()
                    == str(row.get("path") or "").strip()
                    and str(field.get("name") or "").strip()
                ),
            )
            for row in contract_rows
            if str(row.get("path") or "").strip()
        )
        contract_draft = authored_draft.updated(artifacts=artifact_contracts)
    except (AttributeError, TypeError, ValueError) as exc:
        contract_draft = authored_draft
        artifact_error = str(exc)
    return artifact_contracts, artifact_error, contract_draft


@app.cell
def _(
    artifact_editor,
    artifact_error,
    card_style,
    contract_draft,
    field_editor,
    mo,
    section_header_html,
):
    artifact_error_view = (
        mo.callout(mo.md(artifact_error), kind="warn")
        if artifact_error
        else mo.md("")
    )
    artifact_contract_view = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    2,
                    "Specify result artifacts",
                    "Define the evidence a successful agent must leave behind.",
                )
            ),
            artifact_editor,
            mo.md(
                "For structured results, list required fields. **Artifact** must match a path above."
            ),
            field_editor,
            artifact_error_view,
            mo.callout(
                mo.md(f"**{len(contract_draft.artifacts)} artifact contract(s) defined.**"),
                kind="success" if contract_draft.artifacts else "warn",
            ),
        ],
        gap=1,
    ).style(card_style())
    return (artifact_contract_view,)


@app.cell
def _(contract_draft, mo):
    check_seed = [
        {
            "id": item.id,
            "type": item.type,
            "artifact": item.artifact,
            "field_or_column": item.parameters.get("field")
            or item.parameters.get("column")
            or "",
            "expected_or_limit": item.parameters.get("value", ""),
            "required_columns": ", ".join(item.parameters.get("columns") or ()),
            "criterion": item.description,
            "expert_guidance": item.expert_guidance,
            "expert_only": item.expert_only,
        }
        for item in contract_draft.checks
    ] or [
        {
            "id": "result-exists",
            "type": "file_exists",
            "artifact": (
                contract_draft.artifacts[0].path
                if contract_draft.artifacts
                else "results/answer.csv"
            ),
            "field_or_column": "",
            "expected_or_limit": "",
            "required_columns": "",
            "criterion": "The primary scientific result is present",
            "expert_guidance": "Confirm that the result is meaningful, not merely present.",
            "expert_only": False,
        }
    ]
    check_editor = mo.ui.data_editor(
        check_seed,
        label="Scientific acceptance criteria and automated checks",
    )
    return (check_editor,)


@app.cell
def _(VerifierCheck, check_editor, contract_draft, json):
    verifier_error = None
    verifier_checks = contract_draft.checks
    try:
        built_checks = []
        for row in list(check_editor.value):
            check_id = str(row.get("id") or "").strip()
            if not check_id:
                continue
            check_type = str(row.get("type") or "file_exists").strip()
            parameters = {}
            detail = str(row.get("field_or_column") or "").strip()
            raw_value = row.get("expected_or_limit", "")
            if check_type == "csv_columns":
                parameters["columns"] = [
                    value.strip()
                    for value in str(row.get("required_columns") or "").split(",")
                    if value.strip()
                ]
            elif check_type in {"column_min", "column_max"}:
                parameters = {"column": detail, "value": float(raw_value)}
            elif check_type == "json_equals":
                try:
                    expected_value = json.loads(str(raw_value))
                except json.JSONDecodeError:
                    expected_value = str(raw_value)
                parameters = {"field": detail, "value": expected_value}
            built_checks.append(
                VerifierCheck(
                    id=check_id,
                    type=check_type,
                    artifact=str(row.get("artifact") or "").strip(),
                    description=str(row.get("criterion") or "").strip(),
                    expert_guidance=str(row.get("expert_guidance") or "").strip(),
                    parameters=parameters,
                    expert_only=bool(row.get("expert_only", False)),
                )
            )
        verifier_checks = tuple(built_checks)
        verifier_draft = contract_draft.updated(checks=verifier_checks)
    except (AttributeError, TypeError, ValueError) as exc:
        verifier_draft = contract_draft
        verifier_error = str(exc)
    return verifier_checks, verifier_draft, verifier_error


@app.cell
def _(
    card_style,
    check_editor,
    mo,
    section_header_html,
    verifier_draft,
    verifier_error,
):
    verifier_error_view = (
        mo.callout(mo.md(verifier_error), kind="warn")
        if verifier_error
        else mo.md("")
    )
    verifier_builder_view = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    3,
                    "Build acceptance checks",
                    "Connect scientific criteria to observable evidence.",
                )
            ),
            check_editor,
            verifier_error_view,
            mo.callout(
                mo.md(f"**{len(verifier_draft.checks)} acceptance check(s) defined.**"),
                kind="success" if verifier_draft.checks else "warn",
            ),
        ],
        gap=1,
    ).style(card_style())
    return (verifier_builder_view,)


@app.cell
def _(Path, draft_path, mo, verifier_draft):
    default_root = draft_path.parent if draft_path else Path.cwd()
    fixture_root_input = mo.ui.text(
        value=str(default_root),
        label="Folder containing the draft and example outputs",
        full_width=True,
    )
    oracle_path_input = mo.ui.text(
        value=verifier_draft.oracle_path,
        label="Reference-solution script (relative to that folder)",
        full_width=True,
    )
    fixture_seed = [
        {
            "name": item.name,
            "folder": item.source,
            "should_pass": item.expected_pass,
            "why": item.explanation,
        }
        for item in verifier_draft.fixtures
    ] or [
        {
            "name": "Known good result",
            "folder": "valid_output",
            "should_pass": True,
            "why": "A scientifically acceptable reference result.",
        },
        {
            "name": "Known bad result",
            "folder": "invalid_outputs/nonconverged",
            "should_pass": False,
            "why": "A result with the failure mode the verifier must reject.",
        },
    ]
    fixture_editor = mo.ui.data_editor(
        fixture_seed,
        label="Known examples used to challenge the verifier",
    )
    test_fixtures_button = mo.ui.run_button(label="Test these examples")
    return (
        fixture_editor,
        fixture_root_input,
        oracle_path_input,
        test_fixtures_button,
    )


@app.cell
def _(
    Path,
    VerifierFixture,
    fixture_editor,
    fixture_root_input,
    oracle_path_input,
    verifier_draft,
):
    fixture_error = None
    fixture_values = verifier_draft.fixtures
    try:
        fixture_values = tuple(
            VerifierFixture(
                name=str(row.get("name") or "").strip(),
                source=str(row.get("folder") or "").strip(),
                expected_pass=bool(row.get("should_pass", False)),
                explanation=str(row.get("why") or "").strip(),
            )
            for row in list(fixture_editor.value)
            if str(row.get("name") or "").strip()
            and str(row.get("folder") or "").strip()
        )
        fixture_draft = verifier_draft.updated(
            fixtures=fixture_values,
            oracle_path=oracle_path_input.value.strip() or "solution/solve.sh",
        )
        fixture_root = Path(fixture_root_input.value).expanduser().resolve()
    except (AttributeError, OSError, TypeError, ValueError) as exc:
        fixture_draft = verifier_draft
        fixture_root = Path.cwd()
        fixture_error = str(exc)
    return fixture_draft, fixture_error, fixture_root, fixture_values


@app.cell
def _(fixture_draft, fixture_root, run_fixture_workbench, test_fixtures_button):
    fixture_report = (
        run_fixture_workbench(fixture_draft, fixture_root)
        if test_fixtures_button.value
        else None
    )
    return (fixture_report,)


@app.cell
def _(
    card_style,
    fixture_editor,
    fixture_error,
    fixture_report,
    fixture_root_input,
    mo,
    oracle_path_input,
    section_header_html,
    test_fixtures_button,
):
    if fixture_report is None:
        fixture_result_view = mo.callout(
            mo.md(
                "Select **Test these examples** after the example folders exist. "
                "This reads result files only; it does not execute the oracle."
            ),
            kind="neutral",
        )
    elif fixture_report.passed:
        fixture_result_view = mo.vstack(
            [
                mo.callout(
                    mo.md("The verifier correctly classified every known example."),
                    kind="success",
                ),
                mo.ui.table(fixture_report.rows(), selection=None),
            ]
        )
    else:
        requirements = "\n".join(f"- {item}" for item in fixture_report.requirements)
        fixture_result_view = mo.vstack(
            [
                mo.callout(
                    mo.md(requirements or "One or more examples behaved unexpectedly."),
                    kind="warn",
                ),
                mo.ui.table(fixture_report.rows(), selection=None),
            ]
        )
    fixture_error_view = (
        mo.callout(mo.md(fixture_error), kind="warn")
        if fixture_error
        else mo.md("")
    )
    fixture_workbench_view = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    4,
                    "Test known examples",
                    "Challenge the verifier with results that should pass and fail.",
                )
            ),
            fixture_root_input,
            oracle_path_input,
            fixture_editor,
            test_fixtures_button,
            fixture_error_view,
            fixture_result_view,
        ],
        gap=1,
    ).style(card_style())
    return (fixture_workbench_view,)


@app.cell
def _(Path, cli, fixture_draft, mo):
    default_draft_dir = Path(
        cli.get("draft-dir") or Path.cwd() / "outputs" / "task-drafts"
    ).expanduser().resolve()
    default_export_parent = Path(
        cli.get("output-dir") or Path.cwd() / "outputs" / "harbor-tasks"
    ).expanduser().resolve()
    save_directory_input = mo.ui.text(
        value=str(default_draft_dir),
        label="Draft history folder",
        full_width=True,
    )
    export_directory_input = mo.ui.text(
        value=str(default_export_parent),
        label="Harbor task export folder",
        full_width=True,
    )
    environment_input = mo.ui.dropdown(
        options={
            "Local Docker": "docker",
            "CoreWeave Cloud Sandbox": "cwsandbox",
        },
        value="Local Docker",
        label="Harbor execution environment",
        full_width=True,
    )
    agent_seed = [{"agent": "", "model": ""}]
    agent_editor = mo.ui.data_editor(
        agent_seed,
        label="Optional agent and model smoke tests",
    )
    save_draft_button = mo.ui.run_button(label="Save draft revision")
    export_task_button = mo.ui.run_button(label="Export Harbor task")
    run_validation_button = mo.ui.run_button(label="Run Harbor validation")
    validation_timeout_input = mo.ui.number(
        start=30,
        stop=max(3600, fixture_draft.agent_timeout_sec),
        step=30,
        value=fixture_draft.agent_timeout_sec,
        label="Maximum seconds per Harbor run",
    )
    return (
        agent_editor,
        environment_input,
        export_directory_input,
        export_task_button,
        run_validation_button,
        save_directory_input,
        save_draft_button,
        validation_timeout_input,
    )


@app.cell
def _(
    Path,
    TaskDraftStore,
    export_directory_input,
    export_task_bundle,
    export_task_button,
    fixture_draft,
    fixture_root,
    save_directory_input,
    save_draft_button,
):
    save_error = None
    saved_draft_path = None
    exported_bundle = None
    export_error = None
    export_parent = Path(export_directory_input.value).expanduser().resolve()
    export_target = export_parent / fixture_draft.task_name
    if save_draft_button.value:
        try:
            saved_draft_path = TaskDraftStore(save_directory_input.value).save(fixture_draft)
        except (OSError, TypeError, ValueError) as exc:
            save_error = str(exc)
    if export_task_button.value:
        try:
            exported_bundle = export_task_bundle(
                fixture_draft,
                export_target,
                draft_root=fixture_root,
            )
        except (OSError, TypeError, ValueError) as exc:
            export_error = str(exc)
    return (
        export_error,
        export_parent,
        export_target,
        exported_bundle,
        save_error,
        saved_draft_path,
    )


@app.cell
def _(
    agent_editor,
    card_style,
    environment_input,
    export_target,
    harbor_validation_plan,
):
    requested_agents = tuple(
        (
            str(row.get("agent") or "").strip(),
            str(row.get("model") or "").strip() or None,
        )
        for row in list(agent_editor.value)
        if str(row.get("agent") or "").strip()
    )
    validation_plan = harbor_validation_plan(
        export_target,
        environment=environment_input.value,
        agents=requested_agents,
    )
    return requested_agents, validation_plan


@app.cell
def _(
    export_target,
    run_harbor_validation,
    run_validation_button,
    subprocess,
    validation_plan,
    validation_timeout_input,
):
    validation_error = None
    validation_runs = ()
    if run_validation_button.value:
        if not export_target.is_dir():
            validation_error = "Export the Harbor task before running Harbor validation."
        else:
            try:
                validation_runs = tuple(
                    run_harbor_validation(
                        command,
                        timeout=float(validation_timeout_input.value),
                    )
                    for command in validation_plan
                )
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                validation_error = str(exc)
    return validation_error, validation_runs


@app.cell
def _(
    agent_editor,
    card_style,
    draft_readiness,
    environment_input,
    export_directory_input,
    export_error,
    exported_bundle,
    fixture_draft,
    mo,
    run_validation_button,
    save_directory_input,
    save_draft_button,
    save_error,
    section_header_html,
    saved_draft_path,
    validation_error,
    validation_plan,
    validation_runs,
    validation_timeout_input,
    export_task_button,
):
    readiness_issues = draft_readiness(fixture_draft)
    readiness_view = (
        mo.callout(
            mo.md("\n".join(f"- {item}" for item in readiness_issues)),
            kind="warn",
        )
        if readiness_issues
        else mo.callout(
            mo.md("The draft has the minimum content needed for technical validation."),
            kind="success",
        )
    )
    action_messages = []
    if saved_draft_path:
        action_messages.append(f"Draft revision saved to `{saved_draft_path}`.")
    if save_error:
        action_messages.append(f"Draft could not be saved: {save_error}")
    if exported_bundle:
        action_messages.append(
            f"Harbor task exported to `{exported_bundle.task_path}` with its review profile."
        )
    if export_error:
        action_messages.append(f"Task could not be exported: {export_error}")
    action_view = (
        mo.callout(mo.md("\n\n".join(action_messages)), kind="neutral")
        if action_messages
        else mo.md("")
    )
    plan_rows = [
        {
            "Purpose": command.description,
            "Command": " ".join(command.argv),
        }
        for command in validation_plan
    ]
    run_rows = [
        {
            "Run": item.kind,
            "Status": "Passed" if item.passed else "Failed",
            "Exit code": item.returncode,
            "Output": (item.stdout or item.stderr)[-500:],
        }
        for item in validation_runs
    ]
    if validation_error:
        run_view = mo.callout(mo.md(validation_error), kind="warn")
    elif run_rows:
        run_view = mo.ui.table(run_rows, selection=None)
    else:
        run_view = mo.md("")
    validation_dashboard_view = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    5,
                    "Validate and export",
                    "Save the draft, export the Harbor task, and run final checks.",
                )
            ),
            readiness_view,
            save_directory_input,
            save_draft_button,
            export_directory_input,
            export_task_button,
            action_view,
            mo.md("### Harbor validation plan"),
            environment_input,
            agent_editor,
            validation_timeout_input,
            mo.ui.table(plan_rows, selection=None),
            run_validation_button,
            run_view,
        ],
        gap=1,
    ).style(card_style())
    return (validation_dashboard_view,)


@app.cell
def _(
    author_input,
    card_style,
    conflicts_input,
    context_input,
    difficulty_input,
    domain_input,
    field_input,
    instruction_input,
    mo,
    organization_input,
    section_header_html,
    subfield_input,
    task_name_input,
    title_input,
):
    brief_form_view = mo.vstack(
        [
            mo.Html(
                section_header_html(
                    1,
                    "Define the scientific task",
                    "Describe the work for both the agent and an independent reviewer.",
                )
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
    ).style(card_style())
    return (brief_form_view,)


@app.cell
def _(
    active_step,
    authored_draft_error,
    artifact_contract_view,
    brief_form_view,
    draft_error,
    fixture_draft,
    fixture_workbench_view,
    mo,
    product_css,
    studio_header_html,
    studio_progress_html,
    studio_summary_html,
    validation_dashboard_view,
    verifier_builder_view,
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
            mo.Html(product_css()),
            mo.Html(studio_header_html()),
            error_view,
            authored_error_view,
            mo.vstack(
                [
                    active_step.style(
                        {"margin-left": "auto", "max-width": "260px"}
                    ),
                    mo.Html(studio_progress_html(int(active_step.value))),
                ],
                gap=0.5,
            ),
            mo.Html(studio_summary_html(fixture_draft)),
            brief_form_view,
            artifact_contract_view,
            verifier_builder_view,
            fixture_workbench_view,
            validation_dashboard_view,
        ],
        gap=2,
    )
    return


if __name__ == "__main__":
    app.run()
