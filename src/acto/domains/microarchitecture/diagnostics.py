"""Parse stored microarchitecture verifier evidence without executing the model."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import json
from typing import Any, Mapping

from harbor_marimo.models import AnalysisBundle

from ..science import DiagnosticFinding


@dataclass(frozen=True)
class MicroarchitectureMetrics:
    ipc_mape: float | None = None
    mean_workload_kendall_tau: float | None = None
    top_1_regret: float | None = None
    true_best_design: str | None = None
    predicted_best_design: str | None = None

    def to_dict(self) -> dict[str, float | str | None]:
        return {
            "ipc_mape": self.ipc_mape,
            "mean_workload_kendall_tau": self.mean_workload_kendall_tau,
            "top_1_regret": self.top_1_regret,
            "true_best_design": self.true_best_design,
            "predicted_best_design": self.predicted_best_design,
        }


def parse_microarchitecture_metrics(text: str) -> MicroarchitectureMetrics | None:
    """Read the metric object printed by the task verifier from stored text."""

    for line in reversed(text.splitlines()):
        start = line.find("{")
        end = line.rfind("}")
        if start < 0 or end <= start:
            continue
        candidate = line[start : end + 1]
        value: Any
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            try:
                value = ast.literal_eval(candidate)
            except (SyntaxError, ValueError):
                continue
        if not isinstance(value, Mapping) or "ipc_mape" not in value:
            continue
        return MicroarchitectureMetrics(
            ipc_mape=_number(value.get("ipc_mape")),
            mean_workload_kendall_tau=_number(
                value.get("mean_workload_kendall_tau")
            ),
            top_1_regret=_number(value.get("top_1_regret")),
            true_best_design=_text(value.get("true_best_design")),
            predicted_best_design=_text(value.get("predicted_best_design")),
        )
    return None


def metrics_for_trial(
    bundle: AnalysisBundle,
    *,
    trial_id: str,
) -> MicroarchitectureMetrics | None:
    for row in bundle.tables()["verifier_files"]:
        if row["trial_id"] != trial_id or not row.get("preview"):
            continue
        metrics = parse_microarchitecture_metrics(str(row["preview"]))
        if metrics:
            return metrics
    return None


def microarchitecture_findings(
    bundle: AnalysisBundle,
    *,
    trial_id: str,
) -> tuple[DiagnosticFinding, ...]:
    """Translate the three conjunctive verifier gates into expert-facing findings."""

    for row in bundle.tables()["verifier_files"]:
        if row["trial_id"] != trial_id or not row.get("preview"):
            continue
        metrics = parse_microarchitecture_metrics(str(row["preview"]))
        if not metrics:
            continue
        source = str(row.get("relative_path") or row.get("path") or "verifier output")
        findings: list[DiagnosticFinding] = []
        findings.extend(
            _threshold_finding(
                metrics.ipc_mape,
                threshold=0.15,
                lower_is_better=True,
                label="IPC prediction error",
                source=source,
            )
        )
        findings.extend(
            _threshold_finding(
                metrics.mean_workload_kendall_tau,
                threshold=0.60,
                lower_is_better=False,
                label="Workload ranking",
                source=source,
            )
        )
        findings.extend(
            _threshold_finding(
                metrics.top_1_regret,
                threshold=0.05,
                lower_is_better=True,
                label="Top-1 design-selection regret",
                source=source,
            )
        )
        if metrics.predicted_best_design or metrics.true_best_design:
            findings.append(
                DiagnosticFinding(
                    "neutral",
                    "Selected design: "
                    f"{metrics.predicted_best_design or 'not reported'}; "
                    f"oracle-best: {metrics.true_best_design or 'not reported'}",
                    source,
                )
            )
        return tuple(findings)
    return ()


def _threshold_finding(
    value: float | None,
    *,
    threshold: float,
    lower_is_better: bool,
    label: str,
    source: str,
) -> tuple[DiagnosticFinding, ...]:
    if value is None:
        return ()
    passed = value <= threshold if lower_is_better else value >= threshold
    operator = "≤" if lower_is_better else "≥"
    state = "meets" if passed else "misses"
    return (
        DiagnosticFinding(
            "positive" if passed else "attention",
            f"{label} {state} its threshold ({value:.4f} {operator} {threshold:.2f})",
            source,
        ),
    )


def _number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def _text(value: Any) -> str | None:
    return str(value) if value is not None else None
