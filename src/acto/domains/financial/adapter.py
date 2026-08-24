"""Financial view model backed exclusively by the public Harbor loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from harbor_marimo.loader import load
from harbor_marimo.models import HarborJob, JsonObject, Trial


def _read_context(trial: Trial) -> JsonObject:
    path = trial.directory / "domain_context.json"
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


@dataclass(frozen=True)
class FinancialTrial:
    source: Trial
    context: JsonObject

    @property
    def directory(self) -> Path:
        return self.source.directory

    @property
    def id(self) -> str:
        return self.source.id

    @property
    def name(self) -> str:
        return self.source.name

    @property
    def task_name(self) -> str:
        return self.source.task_name

    @property
    def agent_name(self) -> str:
        return self.source.agent_name

    @property
    def model_name(self) -> str:
        return self.source.model_name

    @property
    def reward(self) -> float | int | None:
        return self.source.primary_reward

    @property
    def artifact_path(self) -> Path | None:
        for step in self.source.steps:
            for artifact in step.artifacts:
                value = artifact.get("path")
                if (
                    artifact.get("safe")
                    and artifact.get("exists")
                    and isinstance(value, str)
                    and value.lower().endswith(".xlsx")
                ):
                    return Path(value)
        return None

    @property
    def trajectory(self) -> dict[str, Any]:
        for step in self.source.steps:
            if step.trajectory:
                return step.trajectory
        return {}

    @property
    def status(self) -> str:
        return self.source.status.title()


@dataclass(frozen=True)
class FinancialJob:
    source: HarborJob
    trials: tuple[FinancialTrial, ...]

    @property
    def directory(self) -> Path:
        return self.source.directory

    @property
    def id(self) -> str:
        return self.source.id

    @property
    def pass_count(self) -> int:
        return sum(trial.reward == 1 for trial in self.trials)

    @property
    def mean_reward(self) -> float:
        values = [
            float(trial.reward)
            for trial in self.trials
            if isinstance(trial.reward, (int, float))
        ]
        return sum(values) / len(values) if values else 0.0


@dataclass(frozen=True)
class LoadedFinancialSource:
    job: FinancialJob
    requested_path: Path
    job_directory: Path
    kind: str
    selected_trial_name: str | None = None


def _selection(requested: Path, job: HarborJob) -> tuple[str, str | None]:
    for trial in job.trials:
        try:
            requested.relative_to(trial.directory)
        except ValueError:
            continue
        is_atif = requested.name == "trajectory.json" or requested.name == "agent"
        return ("Harbor ATIF" if is_atif else "Harbor trial", trial.name)
    return "Harbor job", None


def load_financial_source(source: str | Path) -> LoadedFinancialSource:
    """Load a financial review source through :func:`harbor_marimo.load`."""

    requested = Path(source).expanduser().resolve()
    bundle = load(requested)
    if len(bundle.jobs) != 1:
        raise ValueError("Financial review currently accepts one Harbor job at a time.")
    harbor_job = bundle.jobs[0]
    kind, selected = _selection(requested, harbor_job)
    job = FinancialJob(
        source=harbor_job,
        trials=tuple(
            FinancialTrial(source=trial, context=_read_context(trial))
            for trial in harbor_job.trials
        ),
    )
    return LoadedFinancialSource(
        job=job,
        requested_path=requested,
        job_directory=harbor_job.directory,
        kind=kind,
        selected_trial_name=selected,
    )


def load_financial_job(source: str | Path) -> FinancialJob:
    return load_financial_source(source).job
