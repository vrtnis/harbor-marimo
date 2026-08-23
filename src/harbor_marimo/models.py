"""Public data model for Harbor analysis sources.

The model intentionally retains the raw Harbor and ATIF payloads.  Normalized
tables are a view over that evidence, not a lossy replacement for it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]


def _mapping(value: Any) -> JsonObject:
    return value if isinstance(value, dict) else {}


@dataclass(frozen=True)
class Diagnostic:
    level: str
    code: str
    message: str
    path: Path | None = None
    job_id: str | None = None
    trial_name: str | None = None
    step_name: str | None = None

    def to_row(self) -> JsonObject:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "path": str(self.path) if self.path else None,
            "job_id": self.job_id,
            "trial_name": self.trial_name,
            "step_name": self.step_name,
        }


@dataclass(frozen=True)
class TrialStep:
    name: str
    directory: Path
    trajectory: JsonObject | None = None
    trajectory_path: Path | None = None
    artifacts: tuple[JsonObject, ...] = ()
    verifier_files: tuple[JsonObject, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()


@dataclass(frozen=True)
class Trial:
    directory: Path
    result: JsonObject = field(default_factory=dict)
    config: JsonObject = field(default_factory=dict)
    steps: tuple[TrialStep, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def id(self) -> str:
        return str(self.result.get("id") or self.config.get("id") or self.name)

    @property
    def name(self) -> str:
        return str(
            self.result.get("trial_name")
            or self.config.get("trial_name")
            or self.directory.name
        )

    @property
    def task_name(self) -> str:
        task = _mapping(self.config.get("task"))
        return str(
            self.result.get("task_name")
            or task.get("name")
            or task.get("path")
            or "unknown"
        )

    @property
    def agent_name(self) -> str:
        info = _mapping(self.result.get("agent_info"))
        agent = _mapping(self.config.get("agent"))
        return str(info.get("name") or agent.get("name") or "unknown")

    @property
    def model_name(self) -> str:
        info = _mapping(_mapping(self.result.get("agent_info")).get("model_info"))
        agent = _mapping(self.config.get("agent"))
        return str(info.get("name") or agent.get("model_name") or "unknown")

    @property
    def provider(self) -> str | None:
        info = _mapping(_mapping(self.result.get("agent_info")).get("model_info"))
        value = info.get("provider")
        return str(value) if value is not None else None

    @property
    def environment(self) -> JsonObject:
        return _mapping(self.config.get("environment"))

    @property
    def environment_provider(self) -> str | None:
        value = (
            self.environment.get("type")
            or self.environment.get("name")
            or self.config.get("environment_type")
            or self.result.get("environment_type")
        )
        return str(value) if value is not None else None

    @property
    def rewards(self) -> dict[str, float | int]:
        raw = _mapping(_mapping(self.result.get("verifier_result")).get("rewards"))
        return {
            str(name): value
            for name, value in raw.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }

    @property
    def primary_reward(self) -> float | int | None:
        """Return a non-ambiguous headline reward.

        Harbor rewards are multi-dimensional.  We only choose a headline when
        the conventional ``reward`` dimension exists or there is exactly one
        dimension; otherwise callers should use the long-form rewards table.
        """

        if "reward" in self.rewards:
            return self.rewards["reward"]
        if len(self.rewards) == 1:
            return next(iter(self.rewards.values()))
        return None

    @property
    def status(self) -> str:
        if self.result.get("exception_info"):
            return "errored"
        if self.result.get("finished_at"):
            return "completed"
        if self.result:
            return "running"
        return "pending"


@dataclass(frozen=True)
class HarborJob:
    directory: Path
    result: JsonObject = field(default_factory=dict)
    config: JsonObject = field(default_factory=dict)
    trials: tuple[Trial, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def id(self) -> str:
        return str(self.result.get("id") or self.config.get("id") or self.directory.name)

    @property
    def name(self) -> str:
        return str(self.result.get("name") or self.config.get("name") or self.directory.name)


@dataclass(frozen=True)
class AnalysisBundle:
    jobs: tuple[HarborJob, ...]
    requested_paths: tuple[Path, ...]
    diagnostics: tuple[Diagnostic, ...] = ()

    def tables(self) -> dict[str, list[JsonObject]]:
        from .normalize import normalize_jobs

        tables = normalize_jobs(self.jobs)
        tables["diagnostics"] = [item.to_row() for item in self.all_diagnostics]
        return tables

    @property
    def all_diagnostics(self) -> tuple[Diagnostic, ...]:
        items = list(self.diagnostics)
        for job in self.jobs:
            items.extend(job.diagnostics)
            for trial in job.trials:
                items.extend(trial.diagnostics)
                for step in trial.steps:
                    items.extend(step.diagnostics)
        return tuple(items)

    def to_dict(self, *, include_raw: bool = False) -> JsonObject:
        payload: JsonObject = {
            "schema_version": "harbor-marimo/v1",
            "sources": [str(path) for path in self.requested_paths],
            "tables": self.tables(),
        }
        if include_raw:
            payload["raw"] = [
                {
                    "directory": str(job.directory),
                    "result": job.result,
                    "config": job.config,
                    "trials": [
                        {
                            "directory": str(trial.directory),
                            "result": trial.result,
                            "config": trial.config,
                            "steps": [
                                {
                                    "name": step.name,
                                    "directory": str(step.directory),
                                    "trajectory": step.trajectory,
                                }
                                for step in trial.steps
                            ],
                        }
                        for trial in job.trials
                    ],
                }
                for job in self.jobs
            ]
        return payload
