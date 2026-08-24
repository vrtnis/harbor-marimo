"""Acto command-line entry point for task and expert-review workflows."""

from __future__ import annotations

import sys
from typing import Sequence

from harbor_marimo.cli import main as harbor_main

from . import __version__


_COMMAND_ALIASES = {
    "studio": "author",
    "review-task": "review-task",
    "review-results": "review",
    "test-verifier": "verifier",
    "export-task": "export-task",
    "validate-task": "validate-task",
}

_HELP = """usage: acto <command> [options]

Acto domain-expert task authoring and review applications.

commands:
  studio          Create tasks, acceptance criteria, verifiers, and fixtures
  review-task     Independently review an exported benchmark task
  review-results  Grade agent results against task and domain evidence
  test-verifier   Test a verifier against known-good and known-bad fixtures
  export-task     Export an Acto draft as a standard Harbor task bundle
  validate-task   Print or run Harbor oracle, nop, and agent validations

Run `acto <command> --help` for command-specific options.
"""


def translated_argv(argv: Sequence[str]) -> list[str]:
    """Translate an Acto command into its compatibility CLI command."""

    values = list(argv)
    if not values:
        return values
    command = values[0]
    translated = _COMMAND_ALIASES.get(command)
    if translated is None:
        choices = ", ".join(_COMMAND_ALIASES)
        raise ValueError(f"Unknown Acto command {command!r}; choose one of: {choices}")
    return [translated, *values[1:]]


def main(argv: Sequence[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw or raw[0] in {"-h", "--help"}:
        print(_HELP)
        return 0
    if raw[0] == "--version":
        print(f"acto {__version__}")
        return 0
    try:
        translated = translated_argv(raw)
    except ValueError as exc:
        print(f"acto: {exc}", file=sys.stderr)
        return 2
    return harbor_main(translated)


if __name__ == "__main__":
    raise SystemExit(main())
