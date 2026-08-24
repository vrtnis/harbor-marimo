"""Command-line entry point for the Harbor analysis workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Sequence

from . import __version__
from .export import export_json
from .loader import load
from acto.tasks import (
    TaskDraft,
    export_task_bundle,
    harbor_validation_plan,
    run_fixture_workbench,
    run_harbor_validation,
)


_COMMANDS = {
    "view",
    "edit",
    "export",
    "review",
    "author",
    "verifier",
    "validate-task",
    "export-task",
    "review-task",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="harbor-marimo",
        description="Explore Harbor jobs and ATIF trajectories in a Marimo workspace.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command, help_text in (
        ("view", "Run the analysis workspace in read-only app mode."),
        ("edit", "Open the analysis notebook in Marimo edit mode."),
    ):
        child = subparsers.add_parser(command, help=help_text)
        child.add_argument("paths", nargs="+", help="Harbor job, trial, result, or ATIF paths.")
        child.add_argument("--port", type=int, default=None)
        child.add_argument("--host", default="127.0.0.1")
        child.add_argument("--headless", action="store_true")
        child.add_argument(
            "--token",
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Enable or disable Marimo session authentication.",
        )

    review = subparsers.add_parser(
        "review",
        help="Open an expert review workspace for one Harbor source.",
    )
    review.add_argument("paths", nargs=1, help="Harbor job, trial, result, or ATIF path.")
    review.add_argument(
        "--domain",
        choices=("financial", "science"),
        default="financial",
        help="Domain adapter name.",
    )
    review.add_argument(
        "--review-dir",
        default="reviews",
        help="Sidecar directory for persisted expert reviews.",
    )
    review.add_argument(
        "--profile",
        default=None,
        help="Optional JSON profile with expert-facing question, criteria, and labels.",
    )
    review.add_argument(
        "--task",
        default=None,
        help="Exported task directory whose criteria should guide scientific result review.",
    )
    review.add_argument(
        "--guided",
        action="store_true",
        help="Show facilitated onboarding guidance and a training banner.",
    )
    review.add_argument(
        "--developer",
        action="store_true",
        help="Expose source and persistence paths for local debugging.",
    )
    review.add_argument("--port", type=int, default=None)
    review.add_argument("--host", default="127.0.0.1")
    review.add_argument("--headless", action="store_true")
    review.add_argument(
        "--token",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable Marimo session authentication.",
    )

    export = subparsers.add_parser("export", help="Export normalized evidence tables as JSON.")
    export.add_argument("paths", nargs="+", help="Harbor job, trial, result, or ATIF paths.")
    export.add_argument("-o", "--output", required=True, help="Destination JSON path.")
    export.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw Harbor and ATIF payloads in addition to normalized tables.",
    )

    author = subparsers.add_parser(
        "author",
        help="Open the non-coder Task Studio for a new or existing scientific task.",
    )
    author.add_argument("draft", nargs="?", help="Optional task draft JSON path.")
    author.add_argument("--draft-dir", default="outputs/task-drafts")
    author.add_argument("--output-dir", default="outputs/harbor-tasks")
    author.add_argument("--port", type=int, default=None)
    author.add_argument("--host", default="127.0.0.1")
    author.add_argument("--headless", action="store_true")
    author.add_argument(
        "--token",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable Marimo session authentication.",
    )

    verifier = subparsers.add_parser(
        "verifier",
        help="Test a draft verifier against its known-good and known-bad examples.",
    )
    verifier.add_argument("draft", help="Task draft JSON path.")
    verifier.add_argument(
        "--root",
        default=None,
        help="Folder containing fixture paths; defaults to the draft's folder.",
    )

    validate = subparsers.add_parser(
        "validate-task",
        help="Print or execute the standard Harbor oracle, nop, and agent validations.",
    )
    validate.add_argument("task", help="Exported Harbor task directory.")
    validate.add_argument("--env", dest="environment", default="docker")
    validate.add_argument("--agent", action="append", default=[])
    validate.add_argument("--model", action="append", default=[])
    validate.add_argument("--run", action="store_true", help="Execute instead of only printing commands.")
    validate.add_argument("--timeout", type=float, default=None)

    export_task = subparsers.add_parser(
        "export-task",
        help="Export a task draft as a Harbor-compatible task bundle.",
    )
    export_task.add_argument("draft", help="Task draft JSON path.")
    export_task.add_argument("--output", required=True, help="Destination task directory.")
    export_task.add_argument(
        "--root",
        default=None,
        help="Folder containing the draft's oracle; defaults to the draft's folder.",
    )

    review_task = subparsers.add_parser(
        "review-task",
        help="Open an independent review workspace for an exported Harbor task.",
    )
    review_task.add_argument("task", help="Exported Harbor task directory.")
    review_task.add_argument("--review-dir", default="outputs/task-reviews")
    review_task.add_argument("--port", type=int, default=None)
    review_task.add_argument("--host", default="127.0.0.1")
    review_task.add_argument("--headless", action="store_true")
    review_task.add_argument(
        "--token",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Enable or disable Marimo session authentication.",
    )
    return parser


def normalized_argv(argv: Sequence[str]) -> list[str]:
    values = list(argv)
    if not values:
        return values
    first_non_option = next((item for item in values if not item.startswith("-")), None)
    if first_non_option is None:
        return values
    if first_non_option not in _COMMANDS:
        return ["view", *values]
    return values


def marimo_command(args: argparse.Namespace) -> list[str]:
    app_name = "analysis.py"
    if args.command == "review":
        app_name = "science_review.py" if args.domain == "science" else "expert_review.py"
    elif args.command == "author":
        app_name = "task_studio.py"
    elif args.command == "review-task":
        app_name = "task_review.py"
    if args.command in {"author", "review", "review-task"}:
        import acto

        app_path = Path(acto.__file__).with_name("apps").joinpath(app_name).resolve()
    else:
        app_path = Path(__file__).with_name("apps").joinpath(app_name).resolve()
    marimo_mode = "edit" if args.command == "edit" else "run"
    command = [sys.executable, "-m", "marimo", marimo_mode]
    if args.port is not None:
        command.extend(["--port", str(args.port)])
    if args.host:
        command.extend(["--host", args.host])
    if args.headless:
        command.append("--headless")
    if args.token is True:
        command.append("--token")
    elif args.token is False:
        command.append("--no-token")
    command.extend([str(app_path), "--"])
    if args.command == "author":
        if args.draft:
            command.extend(["--draft", str(Path(args.draft).expanduser().resolve())])
        command.extend(
            [
                "--draft-dir",
                str(Path(args.draft_dir).expanduser().resolve()),
                "--output-dir",
                str(Path(args.output_dir).expanduser().resolve()),
            ]
        )
        return command
    if args.command == "review-task":
        command.extend(
            [
                "--task",
                str(Path(args.task).expanduser().resolve()),
                "--review-dir",
                str(Path(args.review_dir).expanduser().resolve()),
            ]
        )
        return command
    sources = [str(Path(value).expanduser().resolve()) for value in args.paths]
    command.extend(["--jobs-json", json.dumps(sources)])
    if args.command == "review":
        command.extend(["--domain", args.domain])
        review_dir = str(Path(args.review_dir).expanduser().resolve())
        command.extend(["--review-dir", review_dir])
        profile = getattr(args, "profile", None)
        task = getattr(args, "task", None)
        if not profile and task:
            task_root = Path(task).expanduser().resolve()
            candidate = task_root.parent / f"{task_root.name}.review-profile.json"
            if not candidate.is_file():
                raise FileNotFoundError(
                    "The exported task has no adjacent result-review profile: "
                    f"{candidate}"
                )
            profile = str(candidate)
        if profile:
            command.extend(["--profile", str(Path(profile).expanduser().resolve())])
        if getattr(args, "guided", False):
            command.extend(["--guided", "true"])
        if getattr(args, "developer", False):
            command.extend(["--developer", "true"])
    return command


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    args = _parser().parse_args(normalized_argv(raw))
    if args.command == "export":
        destination = export_json(
            load(args.paths),
            args.output,
            include_raw=args.include_raw,
        )
        print(f"Exported Harbor analysis data to {destination}")
        return 0
    if args.command == "verifier":
        draft_path = Path(args.draft).expanduser().resolve()
        draft = _load_task_draft(draft_path)
        report = run_fixture_workbench(
            draft,
            Path(args.root).expanduser().resolve() if args.root else draft_path.parent,
        )
        print(json.dumps({"passed": report.passed, "requirements": report.requirements, "fixtures": report.rows()}, indent=2))
        return 0 if report.passed else 1
    if args.command == "export-task":
        draft_path = Path(args.draft).expanduser().resolve()
        draft = _load_task_draft(draft_path)
        result = export_task_bundle(
            draft,
            args.output,
            draft_root=(Path(args.root).expanduser().resolve() if args.root else draft_path.parent),
        )
        print(f"Exported Harbor task to {result.task_path}")
        print(f"Exported result-review profile to {result.review_profile_path}")
        return 0
    if args.command == "validate-task":
        agents = tuple(
            (agent, args.model[index] if index < len(args.model) else None)
            for index, agent in enumerate(args.agent)
        )
        plan = harbor_validation_plan(
            args.task,
            environment=args.environment,
            agents=agents,
        )
        for command in plan:
            print(" ".join(command.argv))
        if not args.run:
            return 0
        runs = [
            run_harbor_validation(command, timeout=args.timeout)
            for command in plan
        ]
        for run in runs:
            print(f"{run.kind}: {'passed' if run.passed else 'failed'}")
        return 0 if all(run.passed for run in runs) else 1
    return subprocess.call(marimo_command(args))


def _load_task_draft(path: Path) -> TaskDraft:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Task draft JSON must contain an object.")
    return TaskDraft.from_dict(value)


if __name__ == "__main__":
    raise SystemExit(main())
