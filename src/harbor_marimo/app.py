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

    return Path, escape, json, load, mo


@app.cell
def _(Path, json, mo):
    _raw_sources = mo.cli_args().get("jobs-json")
    try:
        _cli_sources = json.loads(_raw_sources) if _raw_sources else []
    except (TypeError, json.JSONDecodeError):
        _cli_sources = []
    _demo = Path.cwd() / "demo_data" / "harbor_job"
    if not _cli_sources and _demo.is_dir():
        _cli_sources = [str(_demo.resolve())]
    source_input = mo.ui.text_area(
        value="\n".join(str(item) for item in _cli_sources),
        placeholder="One Harbor job, trial, result.json, or ATIF path per line",
        label="Harbor sources",
        rows=3,
        debounce=600,
        full_width=True,
    )
    return (source_input,)


@app.cell
def _(mo):
    mo.Html(
        """
        <style>
          :root { --hm-ink:#17212b; --hm-muted:#66717e; --hm-line:#dce3e9;
            --hm-soft:#f5f8fa; --hm-blue:#1667d9; --hm-teal:#087f73; }
          body { background:#f4f6f8; color:var(--hm-ink); }
          main { max-width:1500px !important; padding-top:18px !important; }
          .hm-hero { padding:20px 22px; border-radius:16px; color:white;
            background:linear-gradient(120deg,#102a43,#184e77); display:flex;
            justify-content:space-between; align-items:flex-start; gap:20px; }
          .hm-hero h1 { margin:0 0 7px; font-size:25px; letter-spacing:-.02em; }
          .hm-hero p { margin:0; color:#d9e8f2; max-width:780px; line-height:1.5; }
          .hm-badge { white-space:nowrap; border:1px solid #75d5c8; color:#c8fff7;
            padding:6px 9px; border-radius:999px; font-size:11px; }
          .hm-panel { background:white; border:1px solid var(--hm-line); border-radius:14px;
            padding:16px; box-shadow:0 5px 14px rgba(20,36,52,.04); }
          .hm-panel h2 { font-size:16px; margin:0 0 6px; }
          .hm-panel p { color:var(--hm-muted); margin:0 0 12px; line-height:1.45; }
          .hm-kpis { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; }
          .hm-kpi { background:white; border:1px solid var(--hm-line); border-radius:12px;
            padding:12px 14px; }
          .hm-kpi span { color:var(--hm-muted); font-size:10px; text-transform:uppercase;
            letter-spacing:.07em; font-weight:700; }
          .hm-kpi b { display:block; margin-top:5px; font-size:22px; }
          .hm-error { border:1px solid #f0b8b8; background:#fff2f2; color:#9e2525;
            border-radius:10px; padding:10px 12px; }
          .hm-note { border-left:3px solid var(--hm-teal); background:#effbf8;
            border-radius:8px; padding:10px 12px; color:#31504b; }
          .hm-path { color:var(--hm-muted); font-family:ui-monospace,SFMono-Regular,monospace;
            font-size:11px; overflow-wrap:anywhere; }
          @media (max-width:900px) { .hm-kpis { grid-template-columns:repeat(2,1fr); }
            .hm-hero { flex-direction:column; } }
        </style>
        """
    )
    return


@app.cell
def _(load, source_input):
    source_paths = [line.strip() for line in source_input.value.splitlines() if line.strip()]
    bundle = None
    source_error = None
    tables = {
        name: []
        for name in (
            "jobs",
            "trials",
            "trial_steps",
            "rewards",
            "trajectory_steps",
            "tool_calls",
            "observations",
            "artifacts",
            "verifier_files",
            "diagnostics",
        )
    }
    if source_paths:
        try:
            bundle = load(source_paths)
            tables = bundle.tables()
        except (FileNotFoundError, OSError, ValueError) as exc:
            source_error = str(exc)
    return bundle, source_error, source_paths, tables


@app.cell
def _(escape, mo, source_error, source_input, source_paths, tables):
    _error = (
        mo.Html(f'<div class="hm-error">{escape(source_error)}</div>')
        if source_error
        else mo.Html("")
    )
    _loaded = "<br>".join(escape(path) for path in source_paths) or "No source loaded."
    mo.vstack(
        [
            source_input,
            _error,
            mo.Html(f'<div class="hm-path">{_loaded}</div>'),
            mo.md(f"Loaded **{len(tables['jobs'])} jobs** and **{len(tables['trials'])} trials**."),
        ],
        gap=1,
    )
    return


@app.cell
def _(mo, tables):
    _options = {
        f"{row['trial_name']} · {row['agent']} · {row['model']}": row["trial_id"]
        for row in tables["trials"]
    }
    if not _options:
        _options = {"No trials loaded": ""}
    trial_picker = mo.ui.dropdown(
        options=_options,
        value=next(iter(_options)),
        label="Selected trial",
        searchable=True,
        full_width=True,
    )
    table_picker = mo.ui.dropdown(
        options={name.replace("_", " ").title(): name for name in tables},
        value="Trials",
        label="Normalized table",
        full_width=True,
    )
    return table_picker, trial_picker


@app.cell
def _(tables, trial_picker):
    selected_trial_id = trial_picker.value

    def _selected(name):
        return [row for row in tables[name] if row.get("trial_id") == selected_trial_id]

    selected_trial = next(
        (row for row in tables["trials"] if row.get("trial_id") == selected_trial_id),
        None,
    )
    selected_rewards = _selected("rewards")
    selected_steps = _selected("trajectory_steps")
    selected_calls = _selected("tool_calls")
    selected_observations = _selected("observations")
    selected_artifacts = _selected("artifacts")
    selected_verifier = _selected("verifier_files")
    return (
        selected_artifacts,
        selected_calls,
        selected_observations,
        selected_rewards,
        selected_steps,
        selected_trial,
        selected_trial_id,
        selected_verifier,
    )


@app.cell
def _(escape, mo, selected_trial, tables):
    def _safe_table(_rows, _empty="No rows.", **_kwargs):
        return mo.ui.table(_rows, **_kwargs) if _rows else mo.md(_empty)

    _cost = sum(float(row.get("cost_usd") or 0) for row in tables["trials"])
    _tokens = sum(
        int(row.get("input_tokens") or 0) + int(row.get("output_tokens") or 0)
        for row in tables["trials"]
    )
    _completed = sum(row.get("status") == "completed" for row in tables["trials"])
    overview = mo.vstack(
        [
            mo.Html(
                f"""
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:12px;margin:2px 0 8px;">
                  <div style="background:#fff;border:1px solid #dce3e9;border-radius:12px;padding:13px 14px;">
                    <span style="display:block;color:#66717e;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;">Jobs</span>
                    <strong style="display:block;margin-top:7px;font-size:22px;line-height:1;">{len(tables['jobs'])}</strong>
                  </div>
                  <div style="background:#fff;border:1px solid #dce3e9;border-radius:12px;padding:13px 14px;">
                    <span style="display:block;color:#66717e;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;">Trials</span>
                    <strong style="display:block;margin-top:7px;font-size:22px;line-height:1;">{len(tables['trials'])}</strong>
                  </div>
                  <div style="background:#fff;border:1px solid #dce3e9;border-radius:12px;padding:13px 14px;">
                    <span style="display:block;color:#66717e;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;">Completed</span>
                    <strong style="display:block;margin-top:7px;font-size:22px;line-height:1;">{_completed}</strong>
                  </div>
                  <div style="background:#fff;border:1px solid #dce3e9;border-radius:12px;padding:13px 14px;">
                    <span style="display:block;color:#66717e;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;">Tokens</span>
                    <strong style="display:block;margin-top:7px;font-size:22px;line-height:1;">{_tokens:,}</strong>
                  </div>
                  <div style="background:#fff;border:1px solid #dce3e9;border-radius:12px;padding:13px 14px;">
                    <span style="display:block;color:#66717e;font-size:10px;text-transform:uppercase;letter-spacing:.07em;font-weight:700;">Cost</span>
                    <strong style="display:block;margin-top:7px;font-size:22px;line-height:1;">${_cost:,.2f}</strong>
                  </div>
                </div>
                """
            ),
            mo.Html(
                '<div class="hm-note"><b>Reward semantics are preserved.</b> '
                'A value is not labeled pass or fail unless your own analysis defines that interpretation.</div>'
            ),
            _safe_table(
                tables["jobs"],
                "No jobs loaded.",
                pagination=True,
                page_size=15,
                selection=None,
            ),
            _safe_table(
                tables["diagnostics"],
                "No loader diagnostics.",
                pagination=True,
                page_size=15,
                selection=None,
            ),
        ],
        gap=1,
    )
    comparison = mo.vstack(
        [
            mo.md("## Compare models and trials"),
            _safe_table(
                tables["trials"],
                "No trials loaded.",
                pagination=True,
                page_size=20,
                selection=None,
                hidden_columns=["directory", "exception"],
            ),
            mo.md("### Reward dimensions"),
            _safe_table(
                tables["rewards"],
                "No rewards recorded.",
                pagination=True,
                page_size=20,
                selection=None,
            ),
        ],
        gap=1,
    )
    _trial_title = escape(selected_trial["trial_name"]) if selected_trial else "No trial selected"
    trial_summary = mo.vstack(
        [
            mo.Html(f'<div class="hm-panel"><h2>{_trial_title}</h2><p>Trial metadata and named verifier rewards.</p></div>'),
        ],
        gap=1,
    )
    return comparison, overview, trial_summary


@app.cell
def _(
    escape,
    json,
    mo,
    selected_artifacts,
    selected_calls,
    selected_observations,
    selected_rewards,
    selected_steps,
    selected_trial,
    selected_verifier,
    trial_picker,
    trial_summary,
):
    def _safe_table(_rows, _empty="No rows.", **_kwargs):
        return mo.ui.table(_rows, **_kwargs) if _rows else mo.md(_empty)

    _trial_table = [selected_trial] if selected_trial else []
    trial_view = mo.vstack(
        [
            trial_picker,
            trial_summary,
            _safe_table(
                _trial_table,
                "No trial selected.",
                selection=None,
                show_download=False,
            ),
            _safe_table(
                selected_rewards,
                "No rewards recorded for this trial.",
                pagination=True,
                page_size=15,
                selection=None,
            ),
        ],
        gap=1,
    )

    _timeline_items = []
    for _index, _step in enumerate(selected_steps):
        _step_key = (
            _step.get("trajectory_id"),
            _step.get("trajectory_scope"),
            _step.get("trajectory_step_id"),
        )
        _step_calls = [
            _call
            for _call in selected_calls
            if (
                _call.get("trajectory_id"),
                _call.get("trajectory_scope"),
                _call.get("trajectory_step_id"),
            )
            == _step_key
        ]
        _step_observations = [
            _observation
            for _observation in selected_observations
            if (
                _observation.get("trajectory_id"),
                _observation.get("trajectory_scope"),
                _observation.get("trajectory_step_id"),
            )
            == _step_key
        ]
        _details = []
        for _call in _step_calls:
            _call_id = _call.get("tool_call_id")
            _arguments = _call.get("arguments")
            _arguments_text = (
                json.dumps(
                    _arguments,
                    indent=2,
                    ensure_ascii=False,
                    sort_keys=True,
                    default=str,
                )
                if _arguments is not None
                else ""
            )
            _matching_observations = [
                _item
                for _item in _step_observations
                if _item.get("source_call_id") == _call_id
            ]
            _observation_html = "".join(
                f"""
                <div style="margin-top:8px;padding:9px 10px;border-radius:8px;background:#f4f7f9;border-left:3px solid #8aa0b3;">
                  <div style="font-size:9px;font-weight:750;letter-spacing:.07em;text-transform:uppercase;color:#66717e;margin-bottom:4px;">Observation</div>
                  <div style="font-size:12px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere;">{escape(str(_item.get('content') or ''))}</div>
                </div>
                """
                for _item in _matching_observations
            )
            _details.append(
                f"""
                <div style="margin-top:11px;padding:11px 12px;border:1px solid #d9e3ea;border-radius:10px;background:#f8fafb;">
                  <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
                    <div style="font-size:10px;font-weight:750;letter-spacing:.06em;text-transform:uppercase;color:#1667d9;">Tool · {escape(str(_call.get('function_name') or 'unknown'))}</div>
                    <code style="font-size:9px;color:#73808c;">{escape(str(_call_id or ''))}</code>
                  </div>
                  <pre style="margin:8px 0 0;padding:9px 10px;border-radius:8px;background:#17212b;color:#e7eef4;font-size:11px;line-height:1.45;white-space:pre-wrap;overflow-wrap:anywhere;">{escape(_arguments_text)}</pre>
                  {_observation_html}
                </div>
                """
            )
        _unmatched_observations = [
            _item
            for _item in _step_observations
            if not any(
                _item.get("source_call_id") == _call.get("tool_call_id")
                for _call in _step_calls
            )
        ]
        for _item in _unmatched_observations:
            _details.append(
                f"""
                <div style="margin-top:11px;padding:9px 10px;border-radius:8px;background:#f4f7f9;border-left:3px solid #8aa0b3;">
                  <div style="font-size:9px;font-weight:750;letter-spacing:.07em;text-transform:uppercase;color:#66717e;margin-bottom:4px;">Observation</div>
                  <div style="font-size:12px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere;">{escape(str(_item.get('content') or ''))}</div>
                </div>
                """
            )
        _source = str(_step.get("source") or "unknown")
        _source_color = "#1667d9" if _source == "user" else "#087f73"
        _timestamp = str(_step.get("timestamp") or "")
        _timeline_items.append(
            f"""
            <div style="position:relative;display:grid;grid-template-columns:36px minmax(0,1fr);gap:12px;padding-bottom:14px;">
              <div style="position:relative;z-index:1;width:30px;height:30px;border-radius:999px;background:{_source_color};color:white;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;box-shadow:0 0 0 5px #f4f6f8;">{escape(str(_step.get('trajectory_step_id') or _index + 1))}</div>
              <div style="background:#fff;border:1px solid #dce3e9;border-radius:12px;padding:13px 14px;box-shadow:0 3px 10px rgba(20,36,52,.04);min-width:0;">
                <div style="display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;align-items:center;margin-bottom:8px;">
                  <div style="display:flex;gap:7px;align-items:center;">
                    <span style="padding:3px 7px;border-radius:999px;background:{_source_color}18;color:{_source_color};font-size:9px;font-weight:800;letter-spacing:.07em;text-transform:uppercase;">{escape(_source)}</span>
                    <span style="font-size:10px;color:#73808c;">{escape(str(_step.get('trajectory_scope') or 'root'))}</span>
                  </div>
                  <time style="font-size:10px;color:#73808c;">{escape(_timestamp)}</time>
                </div>
                <div style="font-size:13px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere;">{escape(str(_step.get('message') or ''))}</div>
                {''.join(_details)}
              </div>
            </div>
            """
        )
    _timeline = (
        mo.Html(
            f"""
            <div style="position:relative;margin:8px 0 4px;">
              <div style="position:absolute;left:14px;top:15px;bottom:29px;width:2px;background:#d5e0e7;"></div>
              {''.join(_timeline_items)}
            </div>
            """
        )
        if _timeline_items
        else mo.md("No ATIF steps found for this trial.")
    )
    trajectory_view = mo.vstack(
        [
            trial_picker,
            mo.md("## ATIF timeline"),
            mo.md(
                f"{len(selected_steps)} steps · {len(selected_calls)} tool calls · "
                f"{len(selected_observations)} observations"
            ),
            _timeline,
        ],
        gap=1,
    )
    artifact_view = mo.vstack(
        [
            trial_picker,
            mo.md("## Collected artifacts"),
            mo.Html(
                '<div class="hm-note">Artifacts are inventoried as evidence. This workspace does not execute '
                'workbooks, HTML, scripts, archives, pickles, or macros.</div>'
            ),
            _safe_table(
                selected_artifacts,
                "No collected artifacts found for this trial.",
                pagination=True,
                page_size=20,
                selection=None,
            ),
        ],
        gap=1,
    )
    verifier_view = mo.vstack(
        [
            trial_picker,
            mo.md("## Verifier files"),
            _safe_table(
                selected_verifier,
                "No verifier files found for this trial.",
                pagination=True,
                page_size=20,
                selection=None,
                wrapped_columns=["preview"],
            ),
        ],
        gap=1,
    )
    return artifact_view, trajectory_view, trial_view, verifier_view


@app.cell
def _(mo, table_picker, tables):
    data_view = mo.vstack(
        [
            table_picker,
            mo.md(f"## {table_picker.value.replace('_', ' ').title()}"),
            mo.ui.table(
                tables[table_picker.value],
                pagination=True,
                page_size=25,
                selection=None,
            ),
        ],
        gap=1,
    )
    return (data_view,)


@app.cell
def _(
    artifact_view,
    comparison,
    data_view,
    mo,
    overview,
    trajectory_view,
    trial_view,
    verifier_view,
):
    mo.ui.tabs(
        {
            "Overview": overview,
            "Compare": comparison,
            "Trial": trial_view,
            "Trajectory": trajectory_view,
            "Artifacts": artifact_view,
            "Verifier": verifier_view,
            "Data": data_view,
        },
        value="Overview",
        lazy=True,
    )
    return


if __name__ == "__main__":
    app.run()
