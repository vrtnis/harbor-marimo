"""Domain-oriented summaries derived from ATIF trajectories."""

from __future__ import annotations

from datetime import datetime
from typing import Any
import json


def trajectory_rows(trajectory: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for step in trajectory.get("steps", []):
        tool_calls = step.get("tool_calls") or []
        action = ""
        if tool_calls:
            call = tool_calls[0]
            action = str(call.get("function_name", "tool"))
            arguments = call.get("arguments") or {}
            command = arguments.get("command") or arguments.get("path") or ""
            if command:
                action = f"{action}: {command}"

        observation = step.get("observation") or {}
        observation_results = observation.get("results") or []
        outcome = ""
        if observation_results:
            outcome = str(observation_results[0].get("content", ""))

        rows.append(
            {
                "step": str(step.get("step_id", "")),
                "source": str(step.get("source", "")),
                "message": str(step.get("message", "") or ""),
                "action": action,
                "outcome": outcome,
            }
        )
    return rows


def trajectory_metrics(trajectory: dict[str, Any]) -> dict[str, int | float]:
    """Derive transparent behavior signals for comparison, not new rewards."""

    steps = trajectory.get("steps") or []
    tool_calls = [
        tool_call
        for step in steps
        for tool_call in (step.get("tool_calls") or [])
    ]
    observation_count = sum(
        len(((step.get("observation") or {}).get("results") or []))
        for step in steps
    )

    validation_terms = (
        "check",
        "inspect",
        "open",
        "read",
        "recalculate",
        "test",
        "validate",
        "verify",
    )
    change_terms = ("=", "edit", "patch", "replace", "set ", "update", "write")
    validation_actions = 0
    change_actions = 0
    for tool_call in tool_calls:
        arguments = json.dumps(tool_call.get("arguments") or {}).lower()
        validation_actions += int(any(term in arguments for term in validation_terms))
        change_actions += int(any(term in arguments for term in change_terms))

    elapsed_seconds = 0.0
    timestamps = [step.get("timestamp") for step in steps if step.get("timestamp")]
    if len(timestamps) >= 2:
        try:
            started = datetime.fromisoformat(str(timestamps[0]).replace("Z", "+00:00"))
            finished = datetime.fromisoformat(str(timestamps[-1]).replace("Z", "+00:00"))
            elapsed_seconds = max(0.0, (finished - started).total_seconds())
        except ValueError:
            elapsed_seconds = 0.0

    final_metrics = trajectory.get("final_metrics") or {}
    prompt_tokens = int(final_metrics.get("total_prompt_tokens") or 0)
    completion_tokens = int(final_metrics.get("total_completion_tokens") or 0)
    cached_tokens = int(final_metrics.get("total_cached_tokens") or 0)
    cost_usd = float(final_metrics.get("total_cost_usd") or 0.0)

    return {
        "steps": len(steps),
        "tool_calls": len(tool_calls),
        "observations": observation_count,
        "validation_actions": validation_actions,
        "change_actions": change_actions,
        "elapsed_seconds": elapsed_seconds,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cached_tokens": cached_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost_usd": cost_usd,
        "cost_per_action": cost_usd / len(tool_calls) if tool_calls else 0.0,
    }
