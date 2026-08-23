"""Transparent cross-trial scientific workflow summaries."""

from __future__ import annotations

from dataclasses import dataclass
import re

from ...models import AnalysisBundle, JsonObject


@dataclass(frozen=True)
class DiagnosticFinding:
    severity: str
    label: str
    source: str


def compare_trials(bundle: AnalysisBundle) -> tuple[JsonObject, ...]:
    tables = bundle.tables()
    rows: list[JsonObject] = []
    for trial in tables["trials"]:
        trial_id = trial["trial_id"]
        rows.append(
            {
                "trial_id": trial_id,
                "trial_name": trial["trial_name"],
                "agent": trial["agent"],
                "model": trial["model"],
                "reward": trial["primary_reward"],
                "environment": trial.get("environment_provider"),
                "trajectory_steps": sum(
                    row["trial_id"] == trial_id for row in tables["trajectory_steps"]
                ),
                "tool_calls": sum(
                    row["trial_id"] == trial_id for row in tables["tool_calls"]
                ),
                "artifacts": sum(
                    row["trial_id"] == trial_id for row in tables["artifacts"]
                ),
                "verifier_files": sum(
                    row["trial_id"] == trial_id for row in tables["verifier_files"]
                ),
            }
        )
    return tuple(rows)


def diagnostic_findings(
    bundle: AnalysisBundle,
    *,
    trial_id: str,
) -> tuple[DiagnosticFinding, ...]:
    findings: list[DiagnosticFinding] = []
    for row in bundle.tables()["verifier_files"]:
        if row["trial_id"] != trial_id or not row.get("preview"):
            continue
        preview = str(row["preview"])
        source = str(row.get("relative_path") or row.get("path") or "verifier output")
        normalized = preview.lower()
        if re.search(r'"?converged"?\s*[:=]\s*false', normalized):
            findings.append(
                DiagnosticFinding("attention", "Reported convergence failure", source)
            )
        elif re.search(r'"?converged"?\s*[:=]\s*true', normalized):
            findings.append(DiagnosticFinding("positive", "Reported convergence", source))
        if any(term in normalized for term in ("traceback", "exception", "failed")):
            findings.append(
                DiagnosticFinding("attention", "Failure language in verifier output", source)
            )
    return tuple(findings)
