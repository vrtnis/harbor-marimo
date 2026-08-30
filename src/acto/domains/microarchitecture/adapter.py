"""Expert-facing view of CPU microarchitecture model evidence."""

from __future__ import annotations

from dataclasses import replace

from harbor_marimo.models import AnalysisBundle

from acto.profiles import ReviewProfile
from ..protocol import DomainView
from ..science import ScienceAdapter
from .diagnostics import microarchitecture_findings, metrics_for_trial


class MicroarchitectureAdapter(ScienceAdapter):
    """Interpret a Harbor microarchitecture-modeling result without running its model."""

    name = "microarchitecture"
    label = "CPU Microarchitecture Model Review"

    def __init__(self, profile: ReviewProfile | None = None) -> None:
        super().__init__(profile)

    def supports(self, bundle: AnalysisBundle) -> bool:
        tables = bundle.tables()
        if any(
            "microarch" in str(row.get("task_name") or "").lower()
            for row in tables["trials"]
        ):
            return True
        return any(
            str(row.get("destination") or "").lower().endswith(".onnx")
            for row in tables["artifacts"]
        )

    def build_view(
        self,
        bundle: AnalysisBundle,
        *,
        trial_id: str | None = None,
    ) -> DomainView:
        base = super().build_view(bundle, trial_id=trial_id)
        evidence = tuple(
            replace(
                item,
                summary="Portable ONNX model (not executed by the review app)",
            )
            if item.kind == "model"
            else item
            for item in base.evidence
        )
        findings = (
            microarchitecture_findings(bundle, trial_id=trial_id)
            if trial_id
            else ()
        )
        metrics = metrics_for_trial(bundle, trial_id=trial_id) if trial_id else None
        metadata = dict(base.metadata)
        metadata.update(
            {
                "metric_family": "cpu-design-space-exploration",
                "verifier_metrics": metrics.to_dict() if metrics else {},
            }
        )
        return DomainView(
            domain=self.name,
            title=self.profile.title if self.profile else self.label,
            summary=base.summary,
            question=base.question,
            criteria=base.criteria,
            evidence=evidence,
            diagnostics=base.diagnostics + tuple(item.label for item in findings),
            metadata=metadata,
        )
