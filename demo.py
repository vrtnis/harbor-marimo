import marimo

__generated_with = "0.18.0"
app = marimo.App(width="full")


@app.cell
def _():
    from pathlib import Path
    from html import escape
    import marimo as mo

    from acto_harbor_demo.harbor_loader import (
        load_harbor_source,
        trajectory_metrics,
        trajectory_rows,
        workbook_grid,
    )

    return (
        Path,
        escape,
        load_harbor_source,
        mo,
        trajectory_metrics,
        trajectory_rows,
        workbook_grid,
    )


@app.cell
def _(Path, mo):
    ROOT = Path(__file__).parent
    default_source = ROOT / "demo_data" / "harbor_job"
    source_input = mo.ui.text(
        value=str(default_source),
        placeholder=r"C:\path\to\jobs\job-name or ...\agent\trajectory.json",
        label="Harbor job or ATIF path",
        debounce=700,
        full_width=True,
    )
    return ROOT, default_source, source_input


@app.cell
def _(default_source, load_harbor_source, source_input):
    requested_source = source_input.value or str(default_source)
    source_error = None
    try:
        loaded_source = load_harbor_source(requested_source)
    except (FileNotFoundError, OSError, ValueError) as exc:
        source_error = str(exc)
        loaded_source = load_harbor_source(default_source)
    job = loaded_source.job
    return job, loaded_source, requested_source, source_error


@app.cell
def _(mo):
    component_css = """
        <style>
        :root {
          --acto-ink: #182230;
          --acto-muted: #667085;
          --acto-line: #e2e7ee;
          --acto-soft: #f7f9fc;
          --acto-navy: #182a3f;
          --acto-teal: #087f73;
          --acto-aqua: #e9f8f4;
          --acto-amber: #fff5dc;
          --acto-red: #b42318;
        }
        body { background: #f5f7fa; color: var(--acto-ink); }
        main { max-width: 1480px !important; padding-top: 18px !important; }
        .acto-shell { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
        .acto-topbar {
          display: flex; justify-content: space-between; align-items: center; gap: 18px;
          padding: 13px 18px; background: #fff; border: 1px solid var(--acto-line);
          border-radius: 14px; box-shadow: 0 4px 14px rgba(25,39,61,.04);
        }
        .acto-brand { display:flex; align-items:center; gap:12px; }
        .acto-mark { width:34px; height:34px; border-radius:10px; color:#fff; background:var(--acto-navy); display:flex; align-items:center; justify-content:center; font-weight:800; }
        .acto-topbar h1 { margin:0; font-size:18px; line-height:1.2; letter-spacing:-.015em; }
        .acto-topbar p { margin:3px 0 0; color:var(--acto-muted); font-size:12px; }
        .acto-meta { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:7px; }
        .acto-meta span { color:#475467; background:var(--acto-soft); border:1px solid var(--acto-line); padding:5px 8px; border-radius:999px; font-size:11px; white-space:nowrap; }
        .acto-sourcebar { padding:10px 14px; background:#fff; border:1px solid var(--acto-line); border-radius:14px; }
        .acto-source-title { display:flex; justify-content:space-between; gap:10px; align-items:center; margin-bottom:4px; }
        .acto-source-title strong { font-size:13px; }
        .acto-source-title span { color:var(--acto-muted); font-size:11px; }
        .acto-toolbar-title { margin:0 0 2px; font-size:13px; font-weight:750; }
        .acto-toolbar-copy { color:var(--acto-muted); font-size:11px; margin:0; }
        .acto-panel { background:#fff; border:1px solid var(--acto-line); border-radius:14px; padding:17px; box-shadow:0 5px 16px rgba(25,39,61,.045); }
        .acto-panel h2 { font-size:16px; margin:0 0 5px; letter-spacing:-.01em; }
        .acto-panel p { color:var(--acto-muted); line-height:1.48; margin:4px 0 12px; font-size:12px; }
        .acto-panel-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:10px; }
        .acto-kpis { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-bottom:14px; }
        .acto-kpi { background:#fff; border:1px solid var(--acto-line); border-radius:12px; padding:13px 14px; }
        .acto-kpi .label { color:var(--acto-muted); font-size:10px; text-transform:uppercase; letter-spacing:.07em; font-weight:750; }
        .acto-kpi .value { font-size:22px; font-weight:780; margin-top:4px; letter-spacing:-.025em; }
        .acto-table { width:100%; border-collapse:separate; border-spacing:0; overflow:hidden; border:1px solid var(--acto-line); border-radius:11px; }
        .acto-table th { background:#f0f4f8; color:#344054; text-align:left; padding:9px 10px; font-size:10px; text-transform:uppercase; letter-spacing:.05em; }
        .acto-table td { padding:10px; border-top:1px solid var(--acto-line); font-size:12px; vertical-align:top; }
        .acto-table tbody tr:hover td { background:#f8fbfd; }
        .acto-table td:not(:first-child) { font-variant-numeric:tabular-nums; }
        .acto-pass, .acto-fail, .acto-review { padding:4px 7px; border-radius:999px; font-size:10px; font-weight:750; white-space:nowrap; }
        .acto-pass { color:#067647; background:#ecfdf3; border:1px solid #abefc6; }
        .acto-fail { color:#b42318; background:#fef3f2; border:1px solid #fecdca; }
        .acto-review { color:#934f00; background:var(--acto-amber); border:1px solid #f3cf83; }
        .acto-check { display:flex; gap:9px; align-items:center; padding:9px 0; border-bottom:1px solid var(--acto-line); font-size:12px; }
        .acto-check:last-child { border-bottom:0; }
        .acto-focus { background:var(--acto-amber) !important; box-shadow:inset 0 0 0 2px #e9a23b; font-weight:760; }
        .acto-callout { border-left:3px solid var(--acto-teal); background:var(--acto-aqua); border-radius:9px; padding:11px 12px; margin-top:11px; font-size:12px; line-height:1.45; }
        .acto-callout.warning { border-left-color:#d97706; background:var(--acto-amber); }
        .acto-callout strong { display:block; margin-bottom:3px; }
        .acto-review-head { background:#fff; border:1px solid var(--acto-line); border-radius:12px; padding:13px 14px; }
        .acto-review-head h2 { margin:0; font-size:15px; }
        .acto-review-head p { margin:4px 0 0; color:var(--acto-muted); font-size:11px; line-height:1.45; }
        .acto-receipt { padding:10px 12px; border-radius:9px; background:#ecfdf3; border:1px solid #abefc6; color:#067647; font-size:12px; }
        .acto-runbar { display:grid; grid-template-columns:repeat(auto-fit,minmax(118px,1fr)); gap:8px; margin:10px 0 14px; }
        .acto-runstep { min-height:70px; border:1px solid var(--acto-line); border-radius:10px; padding:9px; background:#fff; }
        .acto-runstep.selected { border-color:var(--acto-teal); box-shadow:inset 0 0 0 1px var(--acto-teal); background:var(--acto-aqua); }
        .acto-runstep .num { color:var(--acto-teal); font-size:10px; text-transform:uppercase; letter-spacing:.06em; font-weight:780; }
        .acto-runstep strong { display:block; font-size:11px; margin-top:5px; line-height:1.35; }
        .acto-evidence-grid { display:grid; grid-template-columns:minmax(0,1.5fr) minmax(280px,.65fr); gap:14px; }
        .acto-evidence { border:1px solid var(--acto-line); border-radius:10px; padding:11px 12px; margin-top:9px; background:var(--acto-soft); }
        .acto-evidence .label { color:var(--acto-muted); font-size:9px; text-transform:uppercase; letter-spacing:.07em; font-weight:750; margin-bottom:4px; }
        .acto-evidence .content { font-size:12px; line-height:1.5; overflow-wrap:anywhere; }
        .acto-code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; color:#31546f; }
        .acto-footnote { color:var(--acto-muted); font-size:10px; margin-top:10px; }
        .acto-error { color:#b42318; background:#fef3f2; border:1px solid #fecdca; border-radius:8px; padding:8px 10px; font-size:11px; margin-bottom:6px; }
        .acto-loaded { color:#475467; font-size:10px; overflow-wrap:anywhere; margin-bottom:6px; }
        .acto-analysis-intro { display:flex; justify-content:space-between; align-items:flex-start; gap:18px; padding:16px 17px; background:linear-gradient(120deg,#182a3f,#24445d); border-radius:14px; color:#fff; }
        .acto-analysis-intro h2 { margin:0 0 5px; font-size:17px; letter-spacing:-.01em; }
        .acto-analysis-intro p { margin:0; color:#d8e4ec; font-size:12px; line-height:1.5; max-width:760px; }
        .acto-analysis-intro .tag { color:#d4fff5; border:1px solid rgba(153,246,228,.38); background:rgba(8,127,115,.3); padding:5px 8px; border-radius:999px; font-size:10px; font-weight:750; white-space:nowrap; }
        .acto-analysis-note { display:flex; align-items:flex-start; gap:10px; padding:11px 13px; border:1px solid #b9e5db; background:#f0fbf8; border-radius:11px; font-size:12px; line-height:1.5; }
        .acto-analysis-note strong { color:var(--acto-teal); white-space:nowrap; }
        .acto-behavior-list { display:grid; gap:9px; }
        .acto-behavior { border:1px solid var(--acto-line); background:#fff; border-radius:12px; padding:12px 13px; }
        .acto-behavior-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:9px; }
        .acto-behavior-head strong { font-size:12px; }
        .acto-behavior-head small { display:block; margin-top:3px; color:var(--acto-muted); font-size:10px; }
        .acto-behavior-badges { display:flex; gap:5px; flex-wrap:wrap; justify-content:flex-end; }
        .acto-profile { display:grid; grid-template-columns:78px minmax(90px,1fr) 30px; align-items:center; gap:8px; margin-top:6px; }
        .acto-profile label { color:var(--acto-muted); font-size:10px; }
        .acto-meter { height:7px; background:#e9eef3; border-radius:999px; overflow:hidden; }
        .acto-meter span { display:block; height:100%; border-radius:999px; background:var(--acto-teal); min-width:3px; }
        .acto-meter.change span { background:#52779b; }
        .acto-profile b { font-size:10px; text-align:right; font-variant-numeric:tabular-nums; }
        .acto-behavior-stats { display:flex; flex-wrap:wrap; gap:12px; margin-top:10px; color:#475467; font-size:10px; }
        .acto-behavior-stats b { color:var(--acto-ink); }
        .acto-empty { padding:28px; text-align:center; color:var(--acto-muted); background:#fff; border:1px dashed #cbd5df; border-radius:12px; font-size:12px; }
        @media (max-width: 900px) {
          .acto-topbar { align-items:flex-start; flex-direction:column; }
          .acto-meta { justify-content:flex-start; }
          .acto-kpis { grid-template-columns:repeat(2,1fr); }
          .acto-evidence-grid { grid-template-columns:1fr; }
          .acto-analysis-intro { flex-direction:column; }
        }
        </style>
        """
    mo.Html(component_css)
    return (component_css,)


@app.cell
def _(job, loaded_source, mo):
    trial_options = {
        f"{trial.name.replace('forecast-update__', '').replace('-', ' ').title()} · {trial.agent_name}": trial.name
        for trial in job.trials
    }
    initial_trial_name = loaded_source.selected_trial_name or next(
        iter(trial_options.values())
    )
    initial_trial = next(
        label for label, value in trial_options.items() if value == initial_trial_name
    )
    trial_picker = mo.ui.dropdown(
        options=trial_options,
        value=initial_trial,
        label="Review item",
        searchable=True,
        full_width=True,
    )
    artifact_mode = mo.ui.radio(
        options={"Values": "values", "Formulas": "formulas"},
        value="Values",
        label="Workbook mode",
        inline=True,
    )
    return artifact_mode, trial_picker


@app.cell
def _(job, mo):
    analysis_agent_options = {"All agents": "all"}
    for _agent_name in sorted({item.agent_name for item in job.trials}):
        analysis_agent_options[_agent_name] = _agent_name
    analysis_agent = mo.ui.dropdown(
        options=analysis_agent_options,
        value="All agents",
        label="Agent",
        full_width=True,
    )
    analysis_outcome = mo.ui.dropdown(
        options={
            "All outcomes": "all",
            "Verifier pass": "pass",
            "Verifier fail": "fail",
            "Expert attention": "review",
            "Verifier blind spot": "blind_spot",
        },
        value="All outcomes",
        label="Outcome lens",
        full_width=True,
    )
    analysis_sort = mo.ui.dropdown(
        options={
            "Reward, high to low": "reward_desc",
            "Cost, low to high": "cost_asc",
            "Elapsed time, low to high": "time_asc",
            "Tool actions, high to low": "actions_desc",
        },
        value="Reward, high to low",
        label="Sort runs",
        full_width=True,
    )
    return analysis_agent, analysis_outcome, analysis_sort


@app.cell
def _(
    analysis_agent,
    analysis_outcome,
    analysis_sort,
    job,
    trajectory_metrics,
):
    analysis_records = []
    for _analysis_trial in job.trials:
        _metrics = trajectory_metrics(_analysis_trial.trajectory)
        _expert_status = _analysis_trial.context.get("expert_status", "Not reviewed")
        _needs_review = _expert_status == "Needs review"
        _verifier_passed = _analysis_trial.reward == 1.0
        _failed_checks = sum(
            1
            for _check in _analysis_trial.context.get("verifier_checks", [])
            if _check.get("status") == "fail"
        )
        analysis_records.append(
            {
                "trial": _analysis_trial,
                "metrics": _metrics,
                "expert_status": _expert_status,
                "needs_review": _needs_review,
                "verifier_passed": _verifier_passed,
                "blind_spot": _verifier_passed and _needs_review,
                "failed_checks": _failed_checks,
            }
        )

    visible_analysis_records = [
        _record
        for _record in analysis_records
        if analysis_agent.value == "all"
        or _record["trial"].agent_name == analysis_agent.value
    ]
    if analysis_outcome.value == "pass":
        visible_analysis_records = [
            _record for _record in visible_analysis_records if _record["verifier_passed"]
        ]
    elif analysis_outcome.value == "fail":
        visible_analysis_records = [
            _record for _record in visible_analysis_records if not _record["verifier_passed"]
        ]
    elif analysis_outcome.value == "review":
        visible_analysis_records = [
            _record for _record in visible_analysis_records if _record["needs_review"]
        ]
    elif analysis_outcome.value == "blind_spot":
        visible_analysis_records = [
            _record for _record in visible_analysis_records if _record["blind_spot"]
        ]

    _sort_key, _sort_reverse = {
        "reward_desc": (lambda record: record["trial"].reward or 0.0, True),
        "cost_asc": (lambda record: record["metrics"]["cost_usd"], False),
        "time_asc": (lambda record: record["metrics"]["elapsed_seconds"], False),
        "actions_desc": (lambda record: record["metrics"]["tool_calls"], True),
    }[analysis_sort.value]
    visible_analysis_records = sorted(
        visible_analysis_records, key=_sort_key, reverse=_sort_reverse
    )
    return analysis_records, visible_analysis_records


@app.cell
def _(job, trial_picker):
    trial = next(item for item in job.trials if item.name == trial_picker.value)
    return (trial,)


@app.cell
def _(mo, trajectory_rows, trial):
    existing_status = trial.context.get("expert_status", "Needs review")
    default_decision = {
        "Approved": "Approve",
        "Looks good": "Approve",
        "Needs review": "Needs review",
        "Rejected": "Reject",
    }.get(
        existing_status,
        "Approve" if existing_status == "Aligned" and trial.reward == 1.0 else "Reject",
    )
    decision_input = mo.ui.dropdown(
        options={
            "Approve": "Approved",
            "Needs review": "Needs review",
            "Reject": "Rejected",
        },
        value=default_decision,
        label="Decision",
        full_width=True,
    )
    note_input = mo.ui.text_area(
        placeholder="Record the issue, evidence, or follow-up an expert should know…",
        rows=4,
        label="Review note",
        full_width=True,
    )
    trace_rows = trajectory_rows(trial.trajectory)
    trace_options = {}
    for _trace_item in trace_rows:
        _summary = _trace_item["action"] or _trace_item["message"] or _trace_item["source"]
        _summary = " ".join(_summary.split())
        if len(_summary) > 64:
            _summary = f"{_summary[:61]}…"
        trace_options[f"Step {_trace_item['step']} · {_summary}"] = _trace_item["step"]
    trajectory_step_picker = mo.ui.dropdown(
        options=trace_options,
        value=next(iter(trace_options)),
        label="Inspect event",
        full_width=True,
    )
    return decision_input, note_input, trace_rows, trajectory_step_picker


@app.cell
def _(escape):
    def badge(text, kind="pass"):
        css = {"pass": "acto-pass", "fail": "acto-fail", "review": "acto-review"}[kind]
        return f'<span class="{css}">{escape(str(text))}</span>'

    def money_or_text(value):
        if value is None:
            return "—"
        if isinstance(value, (int, float)):
            return f"{value:,.1f}"
        return escape(str(value))

    return badge, money_or_text


@app.cell
def _(badge, component_css, escape, job, loaded_source, mo, trial):
    _reward_kind = "pass" if trial.reward == 1.0 else "fail"
    workspace_header = mo.Html(
        f"""{component_css}
        <div class="acto-shell acto-topbar">
          <div class="acto-brand">
            <div class="acto-mark">A</div>
            <div>
              <h1>Evaluation review</h1>
              <p>{escape(trial.task_name)} · inspect the work, evidence, and agent trace</p>
            </div>
          </div>
          <div class="acto-meta">
            <span>{escape(loaded_source.kind)}</span>
            <span>Job {escape(job.id[:8])}</span>
            <span>{escape(trial.agent_name)} · {escape(trial.model_name)}</span>
            {badge(f"Reward {trial.reward:.1f}", _reward_kind)}
          </div>
        </div>
        """
    )
    return (workspace_header,)


@app.cell
def _(component_css, escape, loaded_source, mo, source_error, source_input):
    if source_error:
        _source_feedback = mo.Html(
            f'{component_css}<div class="acto-shell acto-error"><strong>Could not load that source.</strong> {escape(source_error)} The sample job remains open.</div>'
        )
    else:
        _source_feedback = mo.Html(
            f'{component_css}<div class="acto-shell acto-loaded">Loaded {escape(loaded_source.kind.lower())}: {escape(str(loaded_source.requested_path))}</div>'
        )
    source_heading = mo.Html(
        f"""{component_css}
        <div class="acto-shell acto-source-title">
          <strong>Harbor source</strong>
          <span>Paste a job folder or agent/trajectory.json; it loads after you pause</span>
        </div>
        """
    )
    source_block = mo.vstack([source_heading, source_input, _source_feedback], gap=0.2)
    source_accordion = mo.accordion(
        {"Change Harbor source": source_block}, multiple=False, lazy=False
    )
    return (source_accordion,)


@app.cell
def _(artifact_mode, component_css, mo, trial_picker):
    toolbar_heading = mo.Html(
        f"""{component_css}
        <div class="acto-shell">
          <p class="acto-toolbar-title">Review workspace</p>
          <p class="acto-toolbar-copy">Choose a run, inspect its workbook, then record your judgment.</p>
        </div>
        """
    )
    toolbar_controls = mo.hstack(
        [trial_picker, artifact_mode],
        widths=[0.68, 0.32],
        align="end",
        wrap=True,
        gap=1.2,
    )
    return toolbar_controls, toolbar_heading


@app.cell
def _(
    artifact_mode,
    badge,
    component_css,
    escape,
    money_or_text,
    mo,
    trial,
    workbook_grid,
):
    artifact_path = trial.artifact_path
    grid = workbook_grid(artifact_path, formulas=artifact_mode.value == "formulas")
    _header = "".join(f"<th>{escape(column)}</th>" for column in grid["columns"])
    _body_rows = []
    for _grid_row_index, _grid_row in enumerate(grid["rows"]):
        _cells = []
        for _grid_column_index, _grid_value in enumerate(_grid_row):
            _grid_focus = _grid_row_index == 5 and _grid_column_index == 3
            _grid_css = ' class="acto-focus"' if _grid_focus else ""
            _cells.append(f"<td{_grid_css}>{money_or_text(_grid_value)}</td>")
        _body_rows.append(f"<tr>{''.join(_cells)}</tr>")

    artifact_panel = mo.Html(
        f"""{component_css}
        <div class="acto-shell acto-panel">
          <div class="acto-panel-head">
            <div><h2>Work product</h2><p>{escape(trial.context.get('artifact_kind', 'Artifact'))} · {escape(artifact_path.name)}</p></div>
            {badge(artifact_mode.value.title(), 'review')}
          </div>
          <table class="acto-table">
            <thead><tr>{_header}</tr></thead>
            <tbody>{''.join(_body_rows)}</tbody>
          </table>
          <div class="acto-footnote">Review focus: {escape(trial.context.get('focus_cell', '—'))}. Highlighted evidence is selected for expert attention.</div>
        </div>
        """
    )

    _checks = []
    for _verifier_check in trial.context.get("verifier_checks", []):
        _verifier_kind = "pass" if _verifier_check["status"] == "pass" else "fail"
        _checks.append(
            f'<div class="acto-check">{badge(_verifier_check["status"].upper(), _verifier_kind)}<span>{escape(_verifier_check["label"])}</span></div>'
        )
    _reward_kind = "pass" if trial.reward == 1.0 else "fail"
    verifier_panel = mo.Html(
        f"""{component_css}
        <div class="acto-shell acto-panel">
          <div class="acto-panel-head"><div><h2>Automated checks</h2><p>Harbor verifier evidence</p></div>{badge(f'Reward {trial.reward:.1f}', _reward_kind)}</div>
          {''.join(_checks)}
        </div>
        """
    )
    return artifact_panel, verifier_panel


@app.cell
def _(badge, component_css, decision_input, escape, mo, note_input, trial):
    _prior_status = trial.context.get("expert_status", "Not reviewed")
    _prior_kind = "review" if _prior_status == "Needs review" else "pass"
    review_heading = mo.Html(
        f"""{component_css}
        <div class="acto-shell acto-review-head">
          <div class="acto-panel-head">
            <div><h2>Your expert review</h2><p>Make the final call independently of the automated reward.</p></div>
            {badge(_prior_status, _prior_kind)}
          </div>
          <div class="acto-callout{' warning' if _prior_kind == 'review' else ''}">
            <strong>Existing expert context</strong>
            {escape(trial.context.get('expert_summary', 'No prior expert note recorded.'))}
          </div>
        </div>
        """
    )
    _current_decision = escape(str(decision_input.value))
    _current_note = escape(note_input.value.strip())
    _current_detail = f" — {_current_note}" if _current_note else ""
    review_receipt = mo.Html(
        f'{component_css}<div class="acto-shell acto-receipt"><strong>Current decision: {_current_decision}</strong>{_current_detail}<br><span>Changes are reflected immediately in the run trace.</span></div>'
    )
    review_panel = mo.vstack(
        [review_heading, decision_input, note_input, review_receipt], gap=0.55
    )
    return (review_panel,)


@app.cell
def _(artifact_panel, mo, review_panel, verifier_panel):
    review_decision_row = mo.hstack(
        [verifier_panel, review_panel],
        widths=[0.38, 0.62],
        align="start",
        wrap=True,
        gap=0.85,
    )
    review_workspace = mo.vstack([artifact_panel, review_decision_row], gap=0.8)
    return (review_workspace,)


@app.cell
def _(
    badge,
    component_css,
    decision_input,
    escape,
    mo,
    note_input,
    trace_rows,
    trajectory_step_picker,
    trial,
):
    selected_trace = next(
        row for row in trace_rows if row["step"] == trajectory_step_picker.value
    )
    _run_steps = []
    for _run_row in trace_rows:
        _run_summary = _run_row["action"] or _run_row["message"] or _run_row["source"]
        _run_summary = " ".join(_run_summary.split())
        if len(_run_summary) > 46:
            _run_summary = f"{_run_summary[:43]}…"
        _selected_css = " selected" if _run_row["step"] == selected_trace["step"] else ""
        _run_steps.append(
            f'<div class="acto-runstep{_selected_css}"><div class="num">Step {escape(_run_row["step"])} · {escape(_run_row["source"])}</div><strong>{escape(_run_summary)}</strong></div>'
        )

    _message = selected_trace["message"] or "No narrative message recorded for this event."
    _action = selected_trace["action"] or "No tool action recorded."
    _outcome = selected_trace["outcome"] or "No observation recorded."
    _expert_status = trial.context.get("expert_status", "Not reviewed")
    _expert_kind = "review" if _expert_status == "Needs review" else "pass"
    _current_decision = decision_input.value
    _current_note = note_input.value.strip() or trial.context.get(
        "expert_summary", "No expert note recorded."
    )

    trajectory_detail = mo.Html(
        f"""{component_css}
        <div class="acto-shell acto-panel">
          <div class="acto-panel-head">
            <div><h2>Run map</h2><p>{escape(trial.trajectory.get('schema_version', 'ATIF'))} · {len(trace_rows)} recorded events</p></div>
            {badge(f"Step {selected_trace['step']}", 'review')}
          </div>
          <div class="acto-runbar">{''.join(_run_steps)}</div>
          <div class="acto-evidence-grid">
            <div>
              <div class="acto-evidence"><div class="label">Agent message</div><div class="content">{escape(_message)}</div></div>
              <div class="acto-evidence"><div class="label">Action</div><div class="content acto-code">{escape(_action)}</div></div>
              <div class="acto-evidence"><div class="label">Observation</div><div class="content">{escape(_outcome)}</div></div>
            </div>
            <div>
              <div class="acto-evidence"><div class="label">Expert decision</div><div class="content">{badge(_current_decision, _expert_kind)}</div></div>
              <div class="acto-evidence"><div class="label">Expert note</div><div class="content">{escape(str(_current_note) or 'No note entered.')}</div></div>
              <div class="acto-callout"><strong>Why this event matters</strong>Use the action and observation together to determine whether the work product is trustworthy—not merely whether the agent reported success.</div>
            </div>
          </div>
        </div>
        """
    )
    trajectory_workspace = mo.vstack([trajectory_step_picker, trajectory_detail], gap=0.65)
    return (trajectory_workspace,)


@app.cell
def _(badge, component_css, escape, job, mo):
    _trial_rows = []
    for _queue_item in job.trials:
        _queue_reward_kind = "pass" if _queue_item.reward == 1.0 else "fail"
        _queue_expert_kind = "review" if _queue_item.context.get("expert_status") == "Needs review" else "pass"
        _trial_rows.append(
            "<tr>"
            f"<td><strong>{escape(_queue_item.name.replace('forecast-update__', ''))}</strong><br><span style='color:#667085'>{escape(_queue_item.task_name)}</span></td>"
            f"<td>{escape(_queue_item.agent_name)}</td>"
            f"<td>{escape(_queue_item.model_name)}</td>"
            f"<td>{badge(f'{_queue_item.reward:.1f}', _queue_reward_kind)}</td>"
            f"<td>{badge(_queue_item.context.get('expert_status', '—'), _queue_expert_kind)}</td>"
            "</tr>"
        )
    queue_view = mo.Html(
        f"""{component_css}
        <div class="acto-shell">
          <div class="acto-kpis">
            <div class="acto-kpi"><div class="label">Queue</div><div class="value">{len(job.trials)}</div></div>
            <div class="acto-kpi"><div class="label">Completed</div><div class="value">{job.result['stats']['n_completed_trials']}</div></div>
            <div class="acto-kpi"><div class="label">Mean reward</div><div class="value">{job.mean_reward:.2f}</div></div>
            <div class="acto-kpi"><div class="label">Artifacts</div><div class="value">{sum(len(item.manifest) for item in job.trials)}</div></div>
          </div>
          <div class="acto-panel">
            <div class="acto-panel-head"><div><h2>Review queue</h2><p>Choose any trial above to open it in the workspace.</p></div></div>
            <table class="acto-table">
              <thead><tr><th>Trial</th><th>Agent</th><th>Model</th><th>Reward</th><th>Expert status</th></tr></thead>
              <tbody>{''.join(_trial_rows)}</tbody>
            </table>
          </div>
        </div>
        """
    )
    return (queue_view,)


@app.cell
def _(analysis_agent, analysis_outcome, analysis_sort, mo):
    analysis_controls = mo.hstack(
        [analysis_agent, analysis_outcome, analysis_sort],
        widths=[0.30, 0.34, 0.36],
        align="end",
        wrap=True,
        gap=0.8,
    )
    return (analysis_controls,)


@app.cell
def _(
    analysis_records,
    badge,
    component_css,
    escape,
    mo,
    visible_analysis_records,
):
    _shown = len(visible_analysis_records)
    _passes = sum(1 for record in visible_analysis_records if record["verifier_passed"])
    _blind_spots = sum(1 for record in visible_analysis_records if record["blind_spot"])
    _mean_cost = (
        sum(record["metrics"]["cost_usd"] for record in visible_analysis_records)
        / _shown
        if _shown
        else 0.0
    )
    _pass_rate = f"{(_passes / _shown):.0%}" if _shown else "--"
    _max_actions = max(
        (
            max(
                int(record["metrics"]["change_actions"]),
                int(record["metrics"]["validation_actions"]),
            )
            for record in visible_analysis_records
        ),
        default=1,
    )

    _behavior_rows = []
    _table_rows = []
    for _record in visible_analysis_records:
        _trial = _record["trial"]
        _metrics = _record["metrics"]
        _reward_kind = "pass" if _record["verifier_passed"] else "fail"
        _expert_kind = "review" if _record["needs_review"] else "pass"
        _change_width = int(100 * _metrics["change_actions"] / _max_actions)
        _validation_width = int(100 * _metrics["validation_actions"] / _max_actions)
        _behavior_rows.append(
            f"""
            <div class="acto-behavior">
              <div class="acto-behavior-head">
                <div><strong>{escape(_trial.agent_name)}</strong><small>{escape(_trial.model_name)} &middot; {escape(_trial.name)}</small></div>
                <div class="acto-behavior-badges">{badge(f'Reward {_trial.reward:.1f}', _reward_kind)}{badge(_record['expert_status'], _expert_kind)}</div>
              </div>
              <div class="acto-profile"><label>Change actions</label><div class="acto-meter change"><span style="width:{_change_width}%"></span></div><b>{_metrics['change_actions']}</b></div>
              <div class="acto-profile"><label>Validation</label><div class="acto-meter"><span style="width:{_validation_width}%"></span></div><b>{_metrics['validation_actions']}</b></div>
              <div class="acto-behavior-stats">
                <span><b>{_metrics['tool_calls']}</b> tool calls</span>
                <span><b>{_metrics['observations']}</b> observations</span>
                <span><b>{_metrics['elapsed_seconds'] / 60:.1f}m</b> elapsed</span>
                <span><b>${_metrics['cost_usd']:.2f}</b> cost</span>
                <span><b>{_metrics['total_tokens']:,}</b> tokens</span>
              </div>
            </div>
            """
        )
        _table_rows.append(
            "<tr>"
            f"<td><strong>{escape(_trial.name)}</strong><br><span style='color:#667085'>{escape(_trial.agent_name)}</span></td>"
            f"<td>{escape(_trial.model_name)}</td>"
            f"<td>{badge(f'{_trial.reward:.1f}', _reward_kind)}</td>"
            f"<td>{_metrics['change_actions']}</td>"
            f"<td>{_metrics['validation_actions']}</td>"
            f"<td>{_metrics['observations']}</td>"
            f"<td>{_metrics['elapsed_seconds'] / 60:.1f}m</td>"
            f"<td>${_metrics['cost_usd']:.2f}</td>"
            "</tr>"
        )

    _all_blind_spots = sum(1 for record in analysis_records if record["blind_spot"])
    _no_change_failures = sum(
        1
        for record in analysis_records
        if not record["verifier_passed"] and record["metrics"]["change_actions"] == 0
    )
    if _all_blind_spots:
        _insight = (
            f"{_all_blind_spots} verifier-passing run still needs expert attention. "
            "The reward confirms the checked output, but it does not establish that the agent used a trustworthy method."
        )
    elif _no_change_failures:
        _insight = (
            f"{_no_change_failures} failed run made no detected change action. "
            "The ATIF behavior helps explain the verifier outcome."
        )
    else:
        _insight = "Verifier outcomes and expert judgments align across the loaded runs."

    _behavior_content = (
        f'<div class="acto-behavior-list">{"".join(_behavior_rows)}</div>'
        if _behavior_rows
        else '<div class="acto-empty">No runs match the current filters.</div>'
    )
    _table_content = (
        f"""
        <table class="acto-table">
          <thead><tr><th>Run</th><th>Model</th><th>Reward</th><th>Changes</th><th>Validation</th><th>Observations</th><th>Time</th><th>Cost</th></tr></thead>
          <tbody>{''.join(_table_rows)}</tbody>
        </table>
        """
        if _table_rows
        else '<div class="acto-empty">Broaden the filters to compare runs.</div>'
    )

    analysis_view = mo.Html(
        f"""{component_css}
        <div class="acto-shell">
          <div class="acto-analysis-intro">
            <div><h2>ATIF behavior &times; Harbor outcome</h2><p>Compare how agents worked, not only whether they received a reward. Every measure below is recalculated from the loaded trajectories when you change a filter.</p></div>
            <span class="tag">Reactive Python analysis</span>
          </div>
          <div class="acto-kpis" style="margin-top:10px">
            <div class="acto-kpi"><div class="label">Runs shown</div><div class="value">{_shown}</div></div>
            <div class="acto-kpi"><div class="label">Pass rate</div><div class="value">{_pass_rate}</div></div>
            <div class="acto-kpi"><div class="label">Blind spots</div><div class="value">{_blind_spots}</div></div>
            <div class="acto-kpi"><div class="label">Mean cost</div><div class="value">${_mean_cost:.2f}</div></div>
          </div>
          <div class="acto-analysis-note"><strong>Live finding</strong><span>{escape(_insight)}</span></div>
          <div class="acto-panel" style="margin-top:10px">
            <div class="acto-panel-head"><div><h2>Behavior profiles</h2><p>Derived from tool calls, observations, timestamps, and ATIF final metrics.</p></div></div>
            {_behavior_content}
          </div>
          <div class="acto-panel" style="margin-top:10px">
            <div class="acto-panel-head"><div><h2>Comparable run data</h2><p>A research-ready table computed from ATIF plus Harbor verifier results.</p></div></div>
            {_table_content}
            <div class="acto-footnote">Change and validation counts are transparent keyword-derived signals for exploration, not additional verifier scores.</div>
          </div>
        </div>
        """
    )
    return (analysis_view,)


@app.cell
def _(analysis_controls, analysis_view, mo):
    analysis_workspace = mo.vstack([analysis_controls, analysis_view], gap=0.65)
    return (analysis_workspace,)


@app.cell
def _(mo):
    get_workspace_tab, set_workspace_tab = mo.state("Review")
    return get_workspace_tab, set_workspace_tab


@app.cell
def _(
    analysis_workspace,
    get_workspace_tab,
    mo,
    review_workspace,
    set_workspace_tab,
    source_accordion,
    toolbar_controls,
    toolbar_heading,
    trajectory_workspace,
    workspace_header,
):
    tabs = mo.ui.tabs(
        {
            "Review": review_workspace,
            "Run trace": trajectory_workspace,
            "Analysis": analysis_workspace,
        },
        value=get_workspace_tab(),
        on_change=set_workspace_tab,
    )
    mo.vstack(
        [workspace_header, source_accordion, toolbar_heading, toolbar_controls, tabs],
        gap=0.65,
    )
    return (tabs,)


if __name__ == "__main__":
    app.run()
