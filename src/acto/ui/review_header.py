"""Copy helpers for an expert-facing review header."""

from __future__ import annotations

from typing import Mapping, Any

from ..domains.protocol import DomainView


def review_header_markdown(view: DomainView, *, guided: bool) -> str:
    banner = "**Training example** · Your decisions are saved separately from Harbor.\n\n" if guided else ""
    question = f"\n\n### Review question\n{view.question}" if view.question else ""
    return f"# {view.title}\n\n{banner}{view.summary}{question}"


def technical_details_markdown(trial: Mapping[str, Any]) -> str:
    return "\n".join(
        (
            f"- **Harbor job:** `{trial.get('job_id', 'unknown')}`",
            f"- **Trial:** `{trial.get('trial_name', 'unknown')}`",
            f"- **Agent:** `{trial.get('agent', 'unknown')}`",
            f"- **Model:** `{trial.get('model', 'unknown')}`",
            f"- **Environment:** `{trial.get('environment_provider') or 'unknown'}`",
            f"- **Automated reward:** `{trial.get('primary_reward')}`",
        )
    )
