from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from harbor_marimo.domains.financial import (
    trajectory_metrics,
    trajectory_rows,
    workbook_grid,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _reward(result: dict[str, Any]) -> float | None:
    rewards = (result.get("verifier_result") or {}).get("rewards") or {}
    if "reward" in rewards:
        return float(rewards["reward"])
    if rewards:
        return float(next(iter(rewards.values())))
    return None


@dataclass(frozen=True)
class TrialRecord:
    directory: Path
    result: dict[str, Any]
    trajectory: dict[str, Any]
    manifest: list[dict[str, Any]]
    context: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.result["id"])

    @property
    def name(self) -> str:
        return str(self.result["trial_name"])

    @property
    def task_name(self) -> str:
        return str(self.result["task_name"])

    @property
    def agent_name(self) -> str:
        return str((self.result.get("agent_info") or {}).get("name", "unknown"))

    @property
    def model_name(self) -> str:
        model = ((self.result.get("agent_info") or {}).get("model_info") or {}).get(
            "name"
        )
        return str(model or "unknown")

    @property
    def reward(self) -> float | None:
        return _reward(self.result)

    @property
    def artifact_path(self) -> Path | None:
        for entry in self.manifest:
            destination = entry.get("destination", "")
            if entry.get("status") == "ok" and destination.lower().endswith(".xlsx"):
                path = self.directory / destination
                if path.exists():
                    return path
        return None

    @property
    def status(self) -> str:
        return "Errored" if self.result.get("exception_info") else "Completed"


@dataclass(frozen=True)
class HarborJob:
    directory: Path
    result: dict[str, Any]
    trials: tuple[TrialRecord, ...]

    @property
    def id(self) -> str:
        return str(self.result["id"])

    @property
    def pass_count(self) -> int:
        return sum(1 for trial in self.trials if trial.reward == 1.0)

    @property
    def mean_reward(self) -> float:
        scores = [trial.reward for trial in self.trials if trial.reward is not None]
        return sum(scores) / len(scores) if scores else 0.0


@dataclass(frozen=True)
class LoadedHarborSource:
    """A Harbor job resolved from either a job directory or one of its ATIF files."""

    job: HarborJob
    requested_path: Path
    job_directory: Path
    kind: str
    selected_trial_name: str | None = None


def load_harbor_job(job_dir: str | Path) -> HarborJob:
    directory = Path(job_dir).resolve()
    result = _read_json(directory / "result.json")
    trials: list[TrialRecord] = []

    for trial_result in result.get("trial_results", []):
        trial_dir = directory / trial_result["trial_name"]
        stored_result = _read_json(trial_dir / "result.json")
        trajectory = _read_json(trial_dir / "agent" / "trajectory.json")
        manifest = _read_json(trial_dir / "artifacts" / "manifest.json")
        context_path = trial_dir / "domain_context.json"
        context = _read_json(context_path) if context_path.exists() else {}
        trials.append(
            TrialRecord(
                directory=trial_dir,
                result=stored_result,
                trajectory=trajectory,
                manifest=manifest,
                context=context,
            )
        )

    return HarborJob(directory=directory, result=result, trials=tuple(trials))


def load_harbor_source(source: str | Path) -> LoadedHarborSource:
    """Resolve a Harbor job directory, trial directory, or ATIF trajectory path.

    A standalone ATIF file does not contain verifier results or collected artifacts,
    so the expert workspace requires it to live inside a Harbor trial directory.
    """

    requested_path = Path(source).expanduser().resolve()
    if not requested_path.exists():
        raise FileNotFoundError(f"Harbor source does not exist: {requested_path}")

    job_directory: Path | None = None
    selected_trial_name: str | None = None
    kind = "Harbor job"

    if requested_path.is_file():
        if requested_path.suffix.lower() != ".json":
            raise ValueError("Choose a Harbor job directory or a JSON ATIF trajectory.")

        payload = _read_json(requested_path)
        if str(payload.get("schema_version", "")).startswith("ATIF-"):
            if requested_path.parent.name != "agent":
                raise ValueError(
                    "This is an ATIF file, but it is not inside "
                    "<job>/<trial>/agent/. Choose the enclosing Harbor job or its "
                    "agent/trajectory.json so rewards and artifacts can be reviewed."
                )
            trial_directory = requested_path.parent.parent
            job_directory = trial_directory.parent
            selected_trial_name = trial_directory.name
            kind = "Harbor ATIF"
        elif "trial_results" in payload:
            job_directory = requested_path.parent
        else:
            raise ValueError(
                "The JSON file is neither a Harbor job result nor an ATIF trajectory."
            )
    else:
        directory_result = requested_path / "result.json"
        if directory_result.exists():
            payload = _read_json(directory_result)
            if "trial_results" in payload:
                job_directory = requested_path
            elif "trial_name" in payload:
                job_directory = requested_path.parent
                selected_trial_name = str(payload["trial_name"])
                kind = "Harbor trial"
        elif requested_path.name == "agent" and (
            requested_path / "trajectory.json"
        ).exists():
            job_directory = requested_path.parent.parent
            selected_trial_name = requested_path.parent.name
            kind = "Harbor ATIF"

    if job_directory is None or not (job_directory / "result.json").exists():
        raise ValueError(
            "Could not find the enclosing Harbor job. Choose the job directory or "
            "<job>/<trial>/agent/trajectory.json."
        )

    job = load_harbor_job(job_directory)
    if selected_trial_name and not any(
        trial.name == selected_trial_name for trial in job.trials
    ):
        raise ValueError(
            f"The selected ATIF trial '{selected_trial_name}' is not listed in the "
            "enclosing Harbor job result."
        )

    return LoadedHarborSource(
        job=job,
        requested_path=requested_path,
        job_directory=job_directory,
        kind=kind,
        selected_trial_name=selected_trial_name,
    )

