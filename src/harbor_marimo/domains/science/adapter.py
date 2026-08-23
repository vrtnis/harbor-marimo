"""Build expert-facing scientific evidence from normalized Harbor tables."""

from __future__ import annotations

from ...models import AnalysisBundle
from ..protocol import DomainEvidence, DomainView
from .artifacts import classify_artifact


class ScienceAdapter:
    name = "science"
    label = "Scientific workflow review"

    def supports(self, bundle: AnalysisBundle) -> bool:
        return bool(bundle.tables()["artifacts"])

    def build_view(
        self,
        bundle: AnalysisBundle,
        *,
        trial_id: str | None = None,
    ) -> DomainView:
        tables = bundle.tables()
        rows = [
            row
            for row in tables["artifacts"]
            if trial_id is None or row["trial_id"] == trial_id
        ]
        evidence: list[DomainEvidence] = []
        diagnostics: list[str] = []
        for index, row in enumerate(rows):
            classification = classify_artifact(row)
            destination = str(row.get("destination") or f"artifact-{index + 1}")
            if classification.reason:
                diagnostics.append(f"{destination}: {classification.reason}")
            evidence.append(
                DomainEvidence(
                    key=f"artifact:{row['trial_id']}:{row.get('step_name')}:{index}",
                    label=destination,
                    kind=classification.kind,
                    job_id=str(row["job_id"]),
                    trial_id=str(row["trial_id"]),
                    step_name=row.get("step_name"),
                    path=classification.path,
                    summary=classification.label,
                    metadata={
                        "previewable": classification.previewable,
                        "size_bytes": row.get("size_bytes"),
                        "status": row.get("status"),
                    },
                )
            )
        trial_count = len(
            {
                row["trial_id"]
                for row in tables["trials"]
                if trial_id is None or row["trial_id"] == trial_id
            }
        )
        return DomainView(
            domain=self.name,
            title=self.label,
            summary=f"{len(evidence)} artifacts across {trial_count} trial(s).",
            evidence=tuple(evidence),
            diagnostics=tuple(diagnostics),
            metadata={"trial_count": trial_count, "artifact_count": len(evidence)},
        )
