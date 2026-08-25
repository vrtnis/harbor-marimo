"""Framework-light presentation helpers for expert review applications."""

from .comparison import expert_comparison_rows, trial_options
from .evidence_panel import evidence_markdown, evidence_options
from .glossary import glossary_markdown
from .judgment_form import validate_review_submission
from .presentation import (
    card_style,
    compact_task_instruction,
    product_css,
    review_header_html,
    section_header_html,
    studio_header_html,
    studio_progress_html,
    studio_summary_html,
)
from .review_header import review_header_markdown, technical_details_markdown
from .task_brief import criteria_rows, review_steps_markdown
from .task_authoring import (
    AUTHORING_STEPS,
    artifact_rows,
    authoring_progress_markdown,
    check_rows,
    draft_readiness,
    fixture_rows,
    task_summary_markdown,
    validation_rows,
)

__all__ = [
    "criteria_rows",
    "AUTHORING_STEPS",
    "artifact_rows",
    "authoring_progress_markdown",
    "check_rows",
    "card_style",
    "compact_task_instruction",
    "draft_readiness",
    "fixture_rows",
    "task_summary_markdown",
    "validation_rows",
    "evidence_markdown",
    "evidence_options",
    "expert_comparison_rows",
    "glossary_markdown",
    "product_css",
    "review_header_html",
    "review_header_markdown",
    "review_steps_markdown",
    "section_header_html",
    "studio_header_html",
    "studio_progress_html",
    "studio_summary_html",
    "technical_details_markdown",
    "trial_options",
    "validate_review_submission",
]
