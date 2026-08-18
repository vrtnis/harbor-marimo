"""Optional Harbor job plugin.

The plugin follows the same small entry-point pattern as Harbor's companion
packages.  It deliberately does not launch a browser or a long-running server
from a Harbor worker process.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import warnings

from .export import export_json
from .loader import load


class MarimoPlugin:
    """Leave a reproducible analysis handoff when a Harbor job finishes."""

    def __init__(
        self,
        output_dir: str | None = None,
        include_raw: bool | str = False,
        print_command: bool | str = True,
    ) -> None:
        self.output_dir = Path(output_dir).expanduser().resolve() if output_dir else None
        self.include_raw = _as_bool(include_raw)
        self.print_command = _as_bool(print_command)
        self.job_dir: Path | None = None

    async def on_job_start(self, job: Any) -> None:
        value = getattr(job, "job_dir", None) or getattr(job, "directory", None)
        if value:
            self.job_dir = Path(value).expanduser().resolve()

    async def on_job_end(self, job_result: Any) -> None:
        try:
            directory = self.job_dir or _job_directory(job_result)
            if directory is None:
                warnings.warn("harbor-marimo could not determine the completed job directory.")
                return
            if self.output_dir:
                self.output_dir.mkdir(parents=True, exist_ok=True)
                export_json(
                    load(directory),
                    self.output_dir / f"{directory.name}.harbor-marimo.json",
                    include_raw=self.include_raw,
                )
            if self.print_command:
                print(f"Analyze this job with: harbor-marimo {directory}")
        except Exception as exc:  # A reporting plugin must not fail the Harbor job.
            warnings.warn(f"harbor-marimo analysis handoff failed: {exc}")


def _as_bool(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    return value.strip().lower() not in {"0", "false", "no", "off", ""}


def _job_directory(value: Any) -> Path | None:
    for name in ("job_dir", "directory", "trials_dir"):
        candidate = getattr(value, name, None)
        if candidate:
            return Path(candidate).expanduser().resolve()
    return None
