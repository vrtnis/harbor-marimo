"""Shared presentation primitives for Acto's marimo applications."""

from __future__ import annotations

from html import escape

from acto.tasks import TaskDraft

from .task_authoring import AUTHORING_STEPS


def product_css() -> str:
    """Return the restrained visual system used by Acto reference apps."""

    return """
    <style>
      :root {
        --acto-ink: #172033;
        --acto-muted: #667085;
        --acto-line: #e3e7ee;
        --acto-soft: #f7f8fb;
        --acto-accent: #5654a6;
        --acto-accent-soft: #f2f1fb;
        --acto-success: #147a55;
        --acto-success-soft: #edf8f3;
        --acto-warn: #9a6700;
        --acto-warn-soft: #fff8e7;
      }
      body { background: var(--acto-soft); color: var(--acto-ink); }
      main { max-width: 1180px !important; padding: 18px 20px 40px !important; }
      .acto-product { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
      .acto-hero {
        display: flex; align-items: center; justify-content: space-between; gap: 20px;
        padding: 18px 20px; background: #fff; border: 1px solid var(--acto-line);
        border-radius: 12px; box-shadow: 0 4px 14px rgba(23,32,51,.04);
      }
      .acto-brand { display: flex; align-items: center; gap: 13px; min-width: 0; }
      .acto-mark {
        width: 36px; height: 36px; flex: 0 0 36px; display: grid; place-items: center;
        border-radius: 9px; color: #fff; background: var(--acto-accent);
        font-size: 17px; font-weight: 800; letter-spacing: -.04em;
      }
      .acto-eyebrow {
        margin: 0 0 3px; color: var(--acto-accent); font-size: 10px; font-weight: 800;
        letter-spacing: .09em; text-transform: uppercase;
      }
      .acto-hero h1 { margin: 0; font-size: 21px; line-height: 1.2; letter-spacing: -.02em; }
      .acto-hero p { margin: 5px 0 0; color: var(--acto-muted); font-size: 12px; line-height: 1.45; }
      .acto-chips { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 6px; }
      .acto-chip {
        display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;
        padding: 5px 8px; color: #475467; background: #fff;
        border: 1px solid var(--acto-line); border-radius: 999px;
        font-size: 10px; font-weight: 700;
      }
      .acto-chip.accent { color: var(--acto-accent); background: var(--acto-accent-soft); border-color: #d9d7f1; }
      .acto-chip.success { color: var(--acto-success); background: var(--acto-success-soft); border-color: #b9e3cf; }
      .acto-chip.warn { color: var(--acto-warn); background: var(--acto-warn-soft); border-color: #efd99b; }
      .acto-stepper {
        display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 7px;
        padding: 10px; background: #fff; border: 1px solid var(--acto-line); border-radius: 12px;
      }
      .acto-step {
        position: relative; min-height: 52px; padding: 8px 9px 8px 36px;
        color: var(--acto-muted); background: #fff; border: 1px solid transparent;
        border-radius: 9px; font-size: 10px; line-height: 1.3;
      }
      .acto-step b {
        position: absolute; left: 9px; top: 9px; width: 19px; height: 19px;
        display: grid; place-items: center; border-radius: 50%; background: #eef0f4;
        color: #667085; font-size: 9px;
      }
      .acto-step strong { display: block; color: #475467; font-size: 10px; font-weight: 700; }
      .acto-step.done b { color: #fff; background: #7d7bb7; }
      .acto-step.current { background: var(--acto-accent-soft); border-color: #d9d7f1; }
      .acto-step.current b { color: #fff; background: var(--acto-accent); }
      .acto-step.current strong { color: #363478; }
      .acto-summary {
        display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px;
        align-items: center; padding: 14px 16px; background: #fff;
        border: 1px solid var(--acto-line); border-radius: 12px;
      }
      .acto-summary h2 { margin: 0; font-size: 16px; letter-spacing: -.01em; }
      .acto-summary p { margin: 4px 0 0; color: var(--acto-muted); font-size: 11px; line-height: 1.4; }
      .acto-section-head { display: flex; align-items: flex-start; gap: 11px; margin-bottom: 3px; }
      .acto-section-number {
        width: 25px; height: 25px; flex: 0 0 25px; display: grid; place-items: center;
        color: var(--acto-accent); background: var(--acto-accent-soft);
        border: 1px solid #d9d7f1; border-radius: 7px; font-size: 10px; font-weight: 800;
      }
      .acto-section-head h2 { margin: 1px 0 2px; font-size: 16px; letter-spacing: -.01em; }
      .acto-section-head p { margin: 0; color: var(--acto-muted); font-size: 11px; line-height: 1.45; }
      .acto-evidence-title { margin: 0 0 4px; font-size: 15px; }
      .acto-evidence-copy { margin: 0; color: var(--acto-muted); font-size: 11px; line-height: 1.45; }
      @media (max-width: 820px) {
        main { padding-inline: 12px !important; }
        .acto-hero, .acto-summary { align-items: flex-start; grid-template-columns: 1fr; flex-direction: column; }
        .acto-chips { justify-content: flex-start; }
        .acto-stepper { grid-template-columns: 1fr; }
        .acto-step { min-height: 38px; }
        div[style*="flex-flow: row"]:has(.acto-review-grid-item) { flex-flow: column !important; }
        div[style*="flex-flow: row"]:has(.acto-review-grid-item) > div { flex: 1 1 auto !important; width: 100%; }
      }
    </style>
    """


def card_style(*, compact: bool = False) -> dict[str, str]:
    """Styles for a Marimo container without relying on internal selectors."""

    return {
        "background": "#ffffff",
        "border": "1px solid #e3e7ee",
        "border-radius": "12px",
        "box-shadow": "0 4px 14px rgba(23, 32, 51, 0.035)",
        "padding": "14px" if compact else "18px",
    }


def section_header_html(
    number: int | str,
    title: str,
    description: str = "",
    *,
    responsive_grid_item: bool = False,
) -> str:
    description_html = f"<p>{escape(description)}</p>" if description else ""
    classes = "acto-product acto-section-head"
    if responsive_grid_item:
        classes += " acto-review-grid-item"
    return (
        f'<div class="{classes}">'
        f'<span class="acto-section-number">{escape(str(number))}</span>'
        f"<div><h2>{escape(title)}</h2>{description_html}</div>"
        "</div>"
    )


def compact_task_instruction(instruction: str) -> str:
    """Keep task content visible without notebook-scale Markdown headings."""

    lines: list[str] = []
    skipped_title = False
    for line in instruction.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and not skipped_title:
            skipped_title = True
            continue
        if stripped.startswith("#"):
            label = stripped.lstrip("#").strip()
            lines.append(f"**{label}**" if label else "")
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def studio_header_html() -> str:
    return """
    <div class="acto-product acto-hero">
      <div class="acto-brand">
        <div class="acto-mark">A</div>
        <div>
          <div class="acto-eyebrow">Acto Task Studio</div>
          <h1>Terminal-Bench Science task authoring</h1>
          <p>Shape a scientific question into a reviewable benchmark task.</p>
        </div>
      </div>
      <div class="acto-chips">
        <span class="acto-chip">Scientific workflow</span>
        <span class="acto-chip accent">Harbor compatible</span>
      </div>
    </div>
    """


def studio_progress_html(active_step: int) -> str:
    current = max(1, min(len(AUTHORING_STEPS), int(active_step)))
    steps = []
    for index, label in enumerate(AUTHORING_STEPS, start=1):
        state = "current" if index == current else ("done" if index < current else "")
        status = "Current" if index == current else ("Complete" if index < current else "Upcoming")
        steps.append(
            f'<div class="acto-step {state}"><b>{index}</b>'
            f"<strong>{escape(label)}</strong>{status}</div>"
        )
    return '<div class="acto-product acto-stepper">' + "".join(steps) + "</div>"


def studio_summary_html(draft: TaskDraft) -> str:
    domain = " / ".join(
        value
        for value in (
            draft.metadata.domain,
            draft.metadata.field,
            draft.metadata.subfield,
        )
        if value
    ) or "Scientific area not set"
    ready = not any(
        (
            not draft.brief.research_context.strip(),
            not draft.artifacts,
            not draft.checks,
            bool(draft.checks and not draft.fixtures),
        )
    )
    readiness = (
        '<span class="acto-chip success">Ready for validation</span>'
        if ready
        else '<span class="acto-chip warn">Draft in progress</span>'
    )
    return (
        '<div class="acto-product acto-summary">'
        f"<div><h2>{escape(draft.brief.title)}</h2>"
        f"<p>{escape(domain)} &nbsp;·&nbsp; {escape(draft.metadata.author_name)}</p></div>"
        '<div class="acto-chips">'
        f'<span class="acto-chip">{len(draft.artifacts)} artifacts</span>'
        f'<span class="acto-chip">{len(draft.checks)} checks</span>{readiness}'
        "</div></div>"
    )


def review_header_html(
    *,
    task_name: str,
    author: str,
    domain: str,
    field: str,
    evidence_count: int,
    prior_review_count: int,
) -> str:
    scientific_area = " / ".join(value for value in (domain, field) if value) or "Scientific task"
    review_status = (
        f'<span class="acto-chip success">{prior_review_count} prior review(s)</span>'
        if prior_review_count
        else '<span class="acto-chip warn">Awaiting review</span>'
    )
    return (
        '<div class="acto-product acto-hero">'
        '<div class="acto-brand"><div class="acto-mark">A</div><div>'
        '<div class="acto-eyebrow">Acto Task Review</div>'
        f"<h1>{escape(task_name)}</h1>"
        f"<p>{escape(scientific_area)} &nbsp;·&nbsp; Task author: {escape(author)}</p>"
        '</div></div><div class="acto-chips">'
        '<span class="acto-chip accent">Independent assessment</span>'
        f'<span class="acto-chip">{evidence_count} evidence items</span>{review_status}'
        "</div></div>"
    )
