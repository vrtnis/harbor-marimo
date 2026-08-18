"""Tolerant, read-only loader for Harbor job directories."""

from __future__ import annotations

from collections.abc import Iterable
import json
from pathlib import Path
from typing import Any

from .models import AnalysisBundle, Diagnostic, HarborJob, JsonObject, Trial, TrialStep


_TEXT_SUFFIXES = {".csv", ".json", ".log", ".md", ".txt", ".yaml", ".yml"}
_PREVIEW_LIMIT = 64 * 1024


def _read_json(
    path: Path,
    diagnostics: list[Diagnostic],
    *,
    required: bool = False,
    **context: Any,
) -> JsonObject | list[Any] | None:
    if not path.is_file():
        if required:
            diagnostics.append(
                Diagnostic("warning", "missing_json", "Expected JSON file is missing.", path, **context)
            )
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        diagnostics.append(
            Diagnostic("warning", "invalid_json", f"Could not read JSON: {exc}", path, **context)
        )
        return None
    if not isinstance(payload, (dict, list)):
        diagnostics.append(
            Diagnostic("warning", "unexpected_json", "Expected a JSON object or array.", path, **context)
        )
        return None
    return payload


def _object(value: Any) -> JsonObject:
    return value if isinstance(value, dict) else {}


def _manifest_entries(value: Any) -> list[JsonObject]:
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, dict)]
    if isinstance(value, dict):
        entries = value.get("artifacts") or value.get("entries") or []
        return [entry for entry in entries if isinstance(entry, dict)]
    return []


def _contained_path(root: Path, destination: str) -> Path | None:
    if not destination or Path(destination).is_absolute():
        return None
    candidate = (root / destination).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _artifact_inventory(
    step_dir: Path,
    *,
    job_id: str,
    trial_name: str,
    step_name: str,
) -> tuple[tuple[JsonObject, ...], tuple[Diagnostic, ...]]:
    artifacts_dir = step_dir / "artifacts"
    manifest_path = artifacts_dir / "manifest.json"
    diagnostics: list[Diagnostic] = []
    manifest = _read_json(
        manifest_path,
        diagnostics,
        job_id=job_id,
        trial_name=trial_name,
        step_name=step_name,
    )
    records: list[JsonObject] = []
    known_paths: set[Path] = set()

    for index, entry in enumerate(_manifest_entries(manifest)):
        destination = str(entry.get("destination") or "")
        resolved = _contained_path(step_dir, destination)
        safe = resolved is not None
        if not safe:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "unsafe_artifact_path",
                    f"Artifact destination escapes its trial step: {destination!r}",
                    manifest_path,
                    job_id,
                    trial_name,
                    step_name,
                )
            )
        exists = bool(resolved and resolved.exists())
        size = resolved.stat().st_size if resolved and resolved.is_file() else None
        if resolved:
            known_paths.add(resolved)
        records.append(
            {
                "manifest_index": index,
                "source": entry.get("source"),
                "destination": destination,
                "type": entry.get("type") or entry.get("kind"),
                "status": entry.get("status"),
                "service": entry.get("service"),
                "path": str(resolved) if safe and resolved else None,
                "safe": safe,
                "exists": exists,
                "size_bytes": size,
                "discovered": False,
            }
        )

    if artifacts_dir.is_dir():
        for path in sorted(item for item in artifacts_dir.rglob("*") if item.is_file()):
            if path == manifest_path or path.resolve() in known_paths:
                continue
            records.append(
                {
                    "manifest_index": None,
                    "source": None,
                    "destination": str(path.relative_to(step_dir)).replace("\\", "/"),
                    "type": "file",
                    "status": "discovered",
                    "service": None,
                    "path": str(path.resolve()),
                    "safe": True,
                    "exists": True,
                    "size_bytes": path.stat().st_size,
                    "discovered": True,
                }
            )
    return tuple(records), tuple(diagnostics)


def _verifier_inventory(step_dir: Path) -> tuple[JsonObject, ...]:
    verifier_dir = step_dir / "verifier"
    records: list[JsonObject] = []
    if not verifier_dir.is_dir():
        return ()
    for path in sorted(item for item in verifier_dir.rglob("*") if item.is_file()):
        preview: str | None = None
        if path.suffix.lower() in _TEXT_SUFFIXES and path.stat().st_size <= _PREVIEW_LIMIT:
            try:
                preview = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                preview = None
        records.append(
            {
                "path": str(path.resolve()),
                "relative_path": str(path.relative_to(step_dir)).replace("\\", "/"),
                "size_bytes": path.stat().st_size,
                "suffix": path.suffix.lower(),
                "preview": preview,
            }
        )
    return tuple(records)


def _step(
    directory: Path,
    name: str,
    *,
    job_id: str,
    trial_name: str,
) -> TrialStep:
    diagnostics: list[Diagnostic] = []
    trajectory_path = directory / "agent" / "trajectory.json"
    trajectory_value = _read_json(
        trajectory_path,
        diagnostics,
        job_id=job_id,
        trial_name=trial_name,
        step_name=name,
    )
    trajectory = trajectory_value if isinstance(trajectory_value, dict) else None
    if trajectory is None:
        diagnostics.append(
            Diagnostic(
                "info",
                "missing_trajectory",
                "No ATIF trajectory was found for this trial step.",
                trajectory_path,
                job_id,
                trial_name,
                name,
            )
        )
    artifacts, artifact_diagnostics = _artifact_inventory(
        directory,
        job_id=job_id,
        trial_name=trial_name,
        step_name=name,
    )
    diagnostics.extend(artifact_diagnostics)
    return TrialStep(
        name=name,
        directory=directory,
        trajectory=trajectory,
        trajectory_path=trajectory_path if trajectory is not None else None,
        artifacts=artifacts,
        verifier_files=_verifier_inventory(directory),
        diagnostics=tuple(diagnostics),
    )


def _step_names(trial_dir: Path, result: JsonObject) -> list[str]:
    steps_dir = trial_dir / "steps"
    if not steps_dir.is_dir():
        return ["trial"]
    ordered: list[str] = []
    for item in result.get("step_results") or []:
        if isinstance(item, dict):
            name = item.get("step_name") or item.get("name")
            if name and str(name) not in ordered:
                ordered.append(str(name))
    for path in sorted(item for item in steps_dir.iterdir() if item.is_dir()):
        if path.name not in ordered:
            ordered.append(path.name)
    return ordered


def _trial(
    trial_dir: Path,
    embedded_result: JsonObject,
    *,
    job_id: str,
) -> Trial:
    diagnostics: list[Diagnostic] = []
    stored = _read_json(
        trial_dir / "result.json",
        diagnostics,
        job_id=job_id,
        trial_name=str(embedded_result.get("trial_name") or trial_dir.name),
    )
    result = _object(stored) or embedded_result
    stored_config = _read_json(
        trial_dir / "config.json",
        diagnostics,
        job_id=job_id,
        trial_name=str(result.get("trial_name") or trial_dir.name),
    )
    config = _object(stored_config) or _object(result.get("config"))
    trial_name = str(result.get("trial_name") or config.get("trial_name") or trial_dir.name)
    steps = tuple(
        _step(
            trial_dir if name == "trial" else trial_dir / "steps" / name,
            name,
            job_id=job_id,
            trial_name=trial_name,
        )
        for name in _step_names(trial_dir, result)
    )
    return Trial(trial_dir, result, config, steps, tuple(diagnostics))


def load_job(path: str | Path) -> HarborJob:
    """Load one Harbor job without requiring the job to be complete."""

    directory = Path(path).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Harbor job must be a directory: {directory}")
    diagnostics: list[Diagnostic] = []
    result_value = _read_json(directory / "result.json", diagnostics)
    config_value = _read_json(directory / "config.json", diagnostics)
    result = _object(result_value)
    config = _object(config_value)
    job_id = str(result.get("id") or config.get("id") or directory.name)

    embedded: dict[str, JsonObject] = {}
    order: list[str] = []
    for item in result.get("trial_results") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("trial_name") or item.get("id") or "")
        if name:
            embedded[name] = item
            order.append(name)

    for child in sorted(item for item in directory.iterdir() if item.is_dir()):
        has_trial_data = (child / "result.json").is_file() or (child / "config.json").is_file()
        has_step_data = (child / "agent").is_dir() or (child / "steps").is_dir()
        if (has_trial_data or has_step_data) and child.name not in order:
            order.append(child.name)

    if not result and not config and not order:
        raise ValueError(f"No Harbor job data found in: {directory}")
    trials = tuple(
        _trial(directory / name, embedded.get(name, {}), job_id=job_id) for name in order
    )
    if not result:
        diagnostics.append(
            Diagnostic(
                "info",
                "incomplete_job",
                "The job has no result.json yet; discovered trial data was loaded.",
                directory,
                job_id,
            )
        )
    return HarborJob(directory, result, config, trials, tuple(diagnostics))


def resolve_job_directory(path: str | Path) -> Path:
    """Resolve a job from a job/trial directory, result file, or ATIF file."""

    requested = Path(path).expanduser().resolve()
    if not requested.exists():
        raise FileNotFoundError(f"Harbor source does not exist: {requested}")
    candidate = requested.parent if requested.is_file() else requested
    for directory in (candidate, *candidate.parents):
        result_path = directory / "result.json"
        if result_path.is_file():
            try:
                value = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                value = None
            if isinstance(value, dict) and "trial_results" in value:
                return directory
        if directory == candidate and requested.is_dir():
            child_dirs = [item for item in directory.iterdir() if item.is_dir()]
            if any(
                (item / "result.json").is_file()
                or (item / "config.json").is_file()
                or (item / "agent").is_dir()
                or (item / "steps").is_dir()
                for item in child_dirs
            ):
                return directory
    raise ValueError(f"Could not find an enclosing Harbor job for: {requested}")


def load(paths: str | Path | Iterable[str | Path]) -> AnalysisBundle:
    """Load and de-duplicate one or more Harbor sources."""

    values = [paths] if isinstance(paths, (str, Path)) else list(paths)
    if not values:
        raise ValueError("At least one Harbor job path is required.")
    requested = tuple(Path(value).expanduser().resolve() for value in values)
    job_dirs: list[Path] = []
    for value in requested:
        directory = resolve_job_directory(value)
        if directory not in job_dirs:
            job_dirs.append(directory)
    return AnalysisBundle(tuple(load_job(path) for path in job_dirs), requested)


load_jobs = load
