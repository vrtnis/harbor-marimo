from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from harbor_marimo import load
from harbor_marimo.domains.science import preview_artifact
from harbor_marimo.plugin import MarimoPlugin


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "tests" / "fixtures" / "coreweave_job"


class RecordedCoreWeaveIntegrationTests(unittest.TestCase):
    def test_loader_requires_no_provider_credentials(self):
        with patch.dict("os.environ", {}, clear=True):
            tables = load(JOB).tables()

        trial = tables["trials"][0]
        self.assertEqual(trial["environment_provider"], "cwsandbox")
        self.assertEqual(
            trial["environment_image"],
            "registry.example/science-runtime:2026-08",
        )
        self.assertEqual(trial["environment_cpu"], 4)
        self.assertEqual(trial["environment_memory"], "16Gi")
        self.assertEqual(len(tables["artifacts"]), 1)

    def test_downloaded_remote_artifact_is_science_previewable(self):
        artifact = load(JOB).tables()["artifacts"][0]

        preview = preview_artifact(artifact)

        self.assertEqual(preview.kind, "table")
        self.assertEqual(preview.rows[0], ("time", "measurement"))

    def test_harbor_plugin_exports_recorded_provider_output(self):
        with tempfile.TemporaryDirectory() as temp:
            plugin = MarimoPlugin(output_dir=temp, print_command=False)
            asyncio.run(plugin.on_job_start(SimpleNamespace(job_dir=JOB)))
            asyncio.run(plugin.on_job_end(SimpleNamespace()))

            exported = Path(temp) / "coreweave_job.harbor-marimo.json"
            self.assertTrue(exported.is_file())


if __name__ == "__main__":
    unittest.main()
