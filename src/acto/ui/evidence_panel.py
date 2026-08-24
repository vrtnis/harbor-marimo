"""Human-facing scientific evidence presentation."""

from __future__ import annotations

from ..domains.protocol import DomainEvidence


def evidence_options(evidence: tuple[DomainEvidence, ...]) -> dict[str, str]:
    return {item.label: item.key for item in evidence}


def evidence_markdown(item: DomainEvidence) -> str:
    description = item.description or item.summary or "Collected Harbor evidence."
    guidance = (
        f"\n\n**What to examine:** {item.review_guidance}"
        if item.review_guidance
        else ""
    )
    provenance = item.technical_label or str(item.path or "Unavailable")
    return f"### {item.label}\n\n{description}{guidance}\n\n<details><summary>Evidence provenance</summary>\n\n`{provenance}`\n\n</details>"
