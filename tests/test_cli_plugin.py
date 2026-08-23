from __future__ import annotations

import asyncio
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from harbor_marimo.cli import marimo_command, normalized_argv
from harbor_marimo.plugin import MarimoPlugin


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_path_implies_view_command(self):
        self.assertEqual(normalized_argv(["a/job"]), ["view", "a/job"])
        self.assertEqual(normalized_argv(["export", "a/job"]), ["export", "a/job"])
        self.assertEqual(normalized_argv(["--version"]), ["--version"])

    def test_marimo_command_passes_sources_as_json(self):
        args = SimpleNamespace(
            command="view",
            paths=["first", "second"],
            port=2718,
            host="127.0.0.1",
            headless=True,
            token=False,
        )
        command = marimo_command(args)
        self.assertEqual(command[3], "run")
        self.assertIn("--port", command)
        self.assertIn("--headless", command)
        self.assertIn("--no-token", command)
        payload = json.loads(command[command.index("--jobs-json") + 1])
        self.assertEqual([Path(value).name for value in payload], ["first", "second"])


class PluginTests(unittest.TestCase):
    def test_plugin_exports_without_starting_a_server(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "exports"
            plugin = MarimoPlugin(output_dir=str(output), print_command=True)
            job = SimpleNamespace(
                job_dir=ROOT
                / "examples"
                / "financial-review"
                / "demo_data"
                / "harbor_job"
            )
            stream = io.StringIO()
            with redirect_stdout(stream):
                asyncio.run(plugin.on_job_start(job))
                asyncio.run(plugin.on_job_end(SimpleNamespace()))
            exported = output / "harbor_job.harbor-marimo.json"
            self.assertTrue(exported.is_file())
            payload = json.loads(exported.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "harbor-marimo/v1")
            self.assertIn("harbor-marimo", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
