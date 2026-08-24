"""Plan and execute Harbor validation without owning sandbox infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Sequence


@dataclass(frozen=True)
class HarborValidationCommand:
    kind: str
    argv: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class HarborValidationRun:
    kind: str
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    started_at: str
    finished_at: str

    @property
    def passed(self) -> bool:
        return self.returncode == 0


def harbor_validation_plan(
    task_path: str | Path,
    *,
    environment: str | None = None,
    agents: Sequence[tuple[str, str | None]] = (),
    executable: str = "harbor",
) -> tuple[HarborValidationCommand, ...]:
    task = str(Path(task_path).expanduser().resolve())
    common = [executable, "run", "-p", task]
    if environment:
        common.extend(["--env", environment])
    commands = [
        HarborValidationCommand(
            "oracle",
            tuple([*common, "-a", "oracle"]),
            "Reference solution must pass the generated verifier.",
        ),
        HarborValidationCommand(
            "nop",
            tuple([*common, "-a", "nop"]),
            "Doing nothing must fail the generated verifier.",
        ),
    ]
    for agent, model in agents:
        argv = [*common, "-a", agent]
        if model:
            argv.extend(["-m", model])
        commands.append(
            HarborValidationCommand(
                "agent",
                tuple(argv),
                f"Measure task behavior with agent {agent}.",
            )
        )
    return tuple(commands)


def run_harbor_validation(
    command: HarborValidationCommand,
    *,
    cwd: str | Path | None = None,
    timeout: float | None = None,
) -> HarborValidationRun:
    started = _timestamp()
    result = subprocess.run(
        command.argv,
        cwd=str(Path(cwd).resolve()) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    return HarborValidationRun(
        kind=command.kind,
        argv=command.argv,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        started_at=started,
        finished_at=_timestamp(),
    )


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
