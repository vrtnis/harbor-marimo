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


_COMMANDS = {"view", "edit", "export"}


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

    export = subparsers.add_parser("export", help="Export normalized evidence tables as JSON.")
    export.add_argument("paths", nargs="+", help="Harbor job, trial, result, or ATIF paths.")
    export.add_argument("-o", "--output", required=True, help="Destination JSON path.")
    export.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw Harbor and ATIF payloads in addition to normalized tables.",
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
    app_path = Path(__file__).with_name("app.py").resolve()
    marimo_mode = "run" if args.command == "view" else "edit"
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
    sources = [str(Path(value).expanduser().resolve()) for value in args.paths]
    command.extend([str(app_path), "--", "--jobs-json", json.dumps(sources)])
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
    return subprocess.call(marimo_command(args))


if __name__ == "__main__":
    raise SystemExit(main())
