"""Normalize Harbor and ATIF evidence into relational, provenance-rich tables."""

from __future__ import annotations

import json
from typing import Any, Iterator

from .models import HarborJob, JsonObject, Trial, TrialStep


def _mapping(value: Any) -> JsonObject:
    return value if isinstance(value, dict) else {}


def _sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _content(value: Any) -> tuple[str, str]:
    if value is None:
        return "", ""
    if isinstance(value, str):
        return value, "text"
    if isinstance(value, list):
        text_parts: list[str] = []
        types: list[str] = []
        for item in value:
            if isinstance(item, str):
                text_parts.append(item)
                types.append("text")
            elif isinstance(item, dict):
                kind = str(item.get("type") or "object")
                types.append(kind)
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    text_parts.append(text)
                else:
                    text_parts.append(f"[{kind}]")
            else:
                text_parts.append(str(item))
                types.append(type(item).__name__)
        return "\n".join(text_parts), ",".join(dict.fromkeys(types))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True), str(value.get("type") or "object")
    return str(value), type(value).__name__


def _trajectory_tree(trajectory: JsonObject) -> Iterator[tuple[str, JsonObject]]:
    """Yield the root and known nested ATIF subagent trajectories."""

    seen: set[int] = set()

    def visit(value: Any, scope: str) -> Iterator[tuple[str, JsonObject]]:
        if not isinstance(value, dict) or id(value) in seen:
            return
        if isinstance(value.get("steps"), list):
            seen.add(id(value))
            yield scope, value
        for key in ("subagent_trajectory", "trajectory"):
            child = value.get(key)
            if isinstance(child, dict) and isinstance(child.get("steps"), list):
                yield from visit(child, f"{scope}/{key}")
        children = value.get("subagent_trajectories")
        if isinstance(children, list):
            for index, child in enumerate(children):
                yield from visit(child, f"{scope}/subagent[{index}]")
        for step_index, step in enumerate(_sequence(value.get("steps"))):
            if not isinstance(step, dict):
                continue
            for call_index, call in enumerate(_sequence(step.get("tool_calls"))):
                if isinstance(call, dict):
                    yield from visit(call, f"{scope}/step[{step_index}]/call[{call_index}]")
            observation = _mapping(step.get("observation"))
            for result_index, result in enumerate(_sequence(observation.get("results"))):
                if isinstance(result, dict):
                    yield from visit(
                        result,
                        f"{scope}/step[{step_index}]/observation[{result_index}]",
                    )

    yield from visit(trajectory, "root")


def _base(job: HarborJob, trial: Trial, step: TrialStep | None = None) -> JsonObject:
    return {
        "job_id": job.id,
        "job_name": job.name,
        "trial_id": trial.id,
        "trial_name": trial.name,
        "step_name": step.name if step else None,
    }


def _trajectory_metrics(trial: Trial) -> JsonObject:
    totals: JsonObject = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_tokens": 0,
        "cost_usd": 0.0,
    }
    found: set[str] = set()
    mapping = {
        "total_prompt_tokens": "input_tokens",
        "total_completion_tokens": "output_tokens",
        "total_cached_tokens": "cache_tokens",
        "total_cost_usd": "cost_usd",
    }
    for step in trial.steps:
        metrics = _mapping((step.trajectory or {}).get("final_metrics"))
        for source, destination in mapping.items():
            value = metrics.get(source)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                totals[destination] += value
                found.add(destination)
    return {name: value for name, value in totals.items() if name in found}


def _step_reward_rows(job: HarborJob, trial: Trial) -> list[JsonObject]:
    rows: list[JsonObject] = []
    for item in _sequence(trial.result.get("step_results")):
        if not isinstance(item, dict):
            continue
        step_name = item.get("step_name") or item.get("name")
        verifier_result = _mapping(item.get("verifier_result"))
        rewards = _mapping(verifier_result.get("rewards") or item.get("rewards"))
        for dimension, value in rewards.items():
            rows.append(
                {
                    **_base(job, trial),
                    "scope": "step",
                    "step_name": step_name,
                    "dimension": str(dimension),
                    "value": value,
                }
            )
    return rows


def normalize_jobs(jobs: tuple[HarborJob, ...]) -> dict[str, list[JsonObject]]:
    tables: dict[str, list[JsonObject]] = {
        "jobs": [],
        "trials": [],
        "trial_steps": [],
        "rewards": [],
        "trajectory_steps": [],
        "tool_calls": [],
        "observations": [],
        "artifacts": [],
        "verifier_files": [],
    }
    for job in jobs:
        stats = _mapping(job.result.get("stats"))
        environment_providers = sorted(
            {
                provider
                for trial in job.trials
                if (provider := trial.environment_provider) is not None
            }
        )
        tables["jobs"].append(
            {
                "job_id": job.id,
                "job_name": job.name,
                "directory": str(job.directory),
                "started_at": job.result.get("started_at"),
                "finished_at": job.result.get("finished_at"),
                "trial_count": len(job.trials),
                "completed_trials": stats.get("n_completed_trials"),
                "errored_trials": stats.get("n_errored_trials"),
                "input_tokens": stats.get("n_input_tokens"),
                "output_tokens": stats.get("n_output_tokens"),
                "cache_tokens": stats.get("n_cache_tokens"),
                "cost_usd": stats.get("cost_usd"),
                "environment_providers": environment_providers,
            }
        )
        for trial in job.trials:
            agent_result = _mapping(trial.result.get("agent_result"))
            trajectory_metrics = _trajectory_metrics(trial)
            environment = trial.environment
            resources = _mapping(environment.get("resources"))
            task = _mapping(trial.config.get("task"))
            tables["trials"].append(
                {
                    **_base(job, trial),
                    "task_name": trial.task_name,
                    "agent": trial.agent_name,
                    "model": trial.model_name,
                    "provider": trial.provider,
                    "environment_provider": trial.environment_provider,
                    "environment_image": environment.get("docker_image")
                    or environment.get("image"),
                    "environment_cpu": resources.get("cpu")
                    or resources.get("cpu_request")
                    or environment.get("cpu"),
                    "environment_memory": resources.get("memory")
                    or resources.get("memory_request")
                    or environment.get("memory"),
                    "environment_gpus": resources.get("gpus")
                    if "gpus" in resources
                    else environment.get("gpus"),
                    "verifier_environment_mode": trial.result.get(
                        "verifier_environment_mode"
                    ),
                    "task_source": task.get("source") or trial.result.get("source"),
                    "task_path": task.get("path"),
                    "task_checksum": trial.result.get("task_checksum"),
                    "status": trial.status,
                    "primary_reward": trial.primary_reward,
                    "reward_dimensions": len(trial.rewards),
                    "started_at": trial.result.get("started_at"),
                    "finished_at": trial.result.get("finished_at"),
                    "input_tokens": agent_result.get("n_input_tokens", trajectory_metrics.get("input_tokens")),
                    "output_tokens": agent_result.get("n_output_tokens", trajectory_metrics.get("output_tokens")),
                    "cache_tokens": agent_result.get("n_cache_tokens", trajectory_metrics.get("cache_tokens")),
                    "cost_usd": agent_result.get("cost_usd", trajectory_metrics.get("cost_usd")),
                    "exception": trial.result.get("exception_info"),
                    "directory": str(trial.directory),
                }
            )
            for dimension, value in trial.rewards.items():
                tables["rewards"].append(
                    {
                        **_base(job, trial),
                        "scope": "trial",
                        "dimension": dimension,
                        "value": value,
                    }
                )
            tables["rewards"].extend(_step_reward_rows(job, trial))
            for step in trial.steps:
                final_metrics = _mapping((step.trajectory or {}).get("final_metrics"))
                tables["trial_steps"].append(
                    {
                        **_base(job, trial, step),
                        "directory": str(step.directory),
                        "has_trajectory": step.trajectory is not None,
                        "trajectory_step_count": len(
                            _sequence((step.trajectory or {}).get("steps"))
                        ),
                        "input_tokens": final_metrics.get("total_prompt_tokens"),
                        "output_tokens": final_metrics.get("total_completion_tokens"),
                        "cache_tokens": final_metrics.get("total_cached_tokens"),
                        "cost_usd": final_metrics.get("total_cost_usd"),
                        "artifact_count": len(step.artifacts),
                        "verifier_file_count": len(step.verifier_files),
                    }
                )
                for artifact in step.artifacts:
                    tables["artifacts"].append({**_base(job, trial, step), **artifact})
                for verifier_file in step.verifier_files:
                    tables["verifier_files"].append(
                        {**_base(job, trial, step), **verifier_file}
                    )
                if not step.trajectory:
                    continue
                for scope, trajectory in _trajectory_tree(step.trajectory):
                    trajectory_id = trajectory.get("trajectory_id")
                    for index, item in enumerate(_sequence(trajectory.get("steps"))):
                        if not isinstance(item, dict):
                            continue
                        message, message_types = _content(item.get("message"))
                        step_id = item.get("step_id", index + 1)
                        row_base = {
                            **_base(job, trial, step),
                            "trajectory_id": trajectory_id,
                            "trajectory_scope": scope,
                            "trajectory_step_id": step_id,
                        }
                        tables["trajectory_steps"].append(
                            {
                                **row_base,
                                "index": index,
                                "timestamp": item.get("timestamp"),
                                "source": item.get("source"),
                                "message": message,
                                "message_content_types": message_types,
                                "tool_call_count": len(_sequence(item.get("tool_calls"))),
                                "observation_count": len(
                                    _sequence(
                                        _mapping(item.get("observation")).get("results")
                                    )
                                ),
                            }
                        )
                        for call_index, call in enumerate(
                            _sequence(item.get("tool_calls"))
                        ):
                            if not isinstance(call, dict):
                                continue
                            tables["tool_calls"].append(
                                {
                                    **row_base,
                                    "call_index": call_index,
                                    "tool_call_id": call.get("tool_call_id") or call.get("id"),
                                    "function_name": call.get("function_name") or call.get("name"),
                                    "arguments": call.get("arguments"),
                                }
                            )
                        observation = _mapping(item.get("observation"))
                        for result_index, result in enumerate(
                            _sequence(observation.get("results"))
                        ):
                            if not isinstance(result, dict):
                                continue
                            content, content_types = _content(result.get("content"))
                            tables["observations"].append(
                                {
                                    **row_base,
                                    "result_index": result_index,
                                    "source_call_id": result.get("source_call_id"),
                                    "content": content,
                                    "content_types": content_types,
                                }
                            )
    return tables
