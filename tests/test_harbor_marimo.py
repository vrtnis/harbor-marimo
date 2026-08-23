from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from harbor_marimo import load, load_job


ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class GenericFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load(
            ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"
        )
        cls.tables = cls.bundle.tables()

    def test_normalizes_complete_job(self):
        self.assertEqual(len(self.tables["jobs"]), 1)
        self.assertEqual(len(self.tables["trials"]), 3)
        self.assertEqual(len(self.tables["trajectory_steps"]), 15)
        self.assertEqual(len(self.tables["tool_calls"]), 9)
        self.assertEqual(len(self.tables["observations"]), 9)
        self.assertEqual(len(self.tables["artifacts"]), 3)

    def test_atif_path_resolves_and_deduplicates_job(self):
        trajectory = next(
            (
                ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"
            ).glob("*/agent/trajectory.json")
        )
        bundle = load(
            [
                ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job",
                trajectory,
            ]
        )
        self.assertEqual(len(bundle.jobs), 1)
        self.assertEqual(len(bundle.requested_paths), 2)

    def test_provenance_is_present_on_evidence_rows(self):
        for table in ("rewards", "tool_calls", "observations", "artifacts"):
            for row in self.tables[table]:
                self.assertTrue(row["job_id"])
                self.assertTrue(row["trial_id"])
                if table != "rewards" or row["scope"] == "step":
                    self.assertTrue(row["step_name"])

    def test_execution_environment_metadata_is_normalized(self):
        self.assertEqual(self.tables["jobs"][0]["environment_providers"], ["docker"])
        for trial in self.tables["trials"]:
            self.assertEqual(trial["environment_provider"], "docker")
            self.assertEqual(trial["verifier_environment_mode"], "separate")
            self.assertEqual(trial["task_source"], "domain-example")


class EdgeCaseTests(unittest.TestCase):
    def test_ambiguous_rewards_and_all_atif_results_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "job"
            trial = root / "trial-a"
            result = {
                "id": "trial-id",
                "trial_name": "trial-a",
                "task_name": "task-a",
                "finished_at": "2026-01-01T00:00:00Z",
                "verifier_result": {"rewards": {"quality": 0.8, "safety": 1.0}},
            }
            write_json(root / "result.json", {"id": "job-id", "trial_results": [result]})
            write_json(trial / "result.json", result)
            write_json(
                trial / "agent" / "trajectory.json",
                {
                    "schema_version": "ATIF-v1.7",
                    "trajectory_id": "trajectory-a",
                    "steps": [
                        {
                            "step_id": 1,
                            "source": "agent",
                            "message": [{"type": "text", "text": "Inspect"}],
                            "tool_calls": [
                                {"tool_call_id": "a", "function_name": "read", "arguments": {}},
                                {"tool_call_id": "b", "function_name": "check", "arguments": {}},
                            ],
                            "observation": {
                                "results": [
                                    {"source_call_id": "a", "content": "one"},
                                    {
                                        "source_call_id": "b",
                                        "content": [
                                            {"type": "text", "text": "two"},
                                            {"type": "image", "url": "ignored"},
                                        ],
                                    },
                                ]
                            },
                        }
                    ],
                },
            )

            bundle = load(root)
            loaded_trial = bundle.jobs[0].trials[0]
            tables = bundle.tables()
            self.assertIsNone(loaded_trial.primary_reward)
            self.assertEqual(len(tables["rewards"]), 2)
            self.assertEqual(len(tables["tool_calls"]), 2)
            self.assertEqual(len(tables["observations"]), 2)
            self.assertEqual(tables["observations"][1]["content"], "two\n[image]")

    def test_multi_step_trials_are_ordered_and_normalized(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "job"
            trial = root / "trial-multi"
            result = {
                "id": "trial-multi-id",
                "trial_name": "trial-multi",
                "finished_at": "2026-01-01T00:00:00Z",
                "step_results": [
                    {"step_name": "prepare", "rewards": {"ready": 1}},
                    {"step_name": "verify", "rewards": {"correct": 0.5}},
                ],
            }
            write_json(root / "result.json", {"id": "job-multi", "trial_results": [result]})
            write_json(trial / "result.json", result)
            for name in ("prepare", "verify"):
                write_json(
                    trial / "steps" / name / "agent" / "trajectory.json",
                    {
                        "schema_version": "ATIF-v1.7",
                        "trajectory_id": name,
                        "steps": [{"step_id": 1, "source": "agent", "message": name}],
                    },
                )

            bundle = load(root)
            loaded = bundle.jobs[0].trials[0]
            self.assertEqual([step.name for step in loaded.steps], ["prepare", "verify"])
            self.assertEqual(
                [row["step_name"] for row in bundle.tables()["trajectory_steps"]],
                ["prepare", "verify"],
            )
            self.assertEqual(
                {(row["step_name"], row["dimension"]) for row in bundle.tables()["rewards"]},
                {("prepare", "ready"), ("verify", "correct")},
            )

    def test_unsafe_artifact_path_and_missing_trajectory_are_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "job"
            trial = root / "trial-pending"
            write_json(root / "result.json", {"id": "job", "trial_results": []})
            write_json(trial / "config.json", {"trial_name": "trial-pending"})
            write_json(
                trial / "artifacts" / "manifest.json",
                [
                    {
                        "source": "/workspace/secret.txt",
                        "destination": "../../secret.txt",
                        "status": "ok",
                        "type": "file",
                    }
                ],
            )

            bundle = load(root)
            codes = {row["code"] for row in bundle.tables()["diagnostics"]}
            artifact = bundle.tables()["artifacts"][0]
            self.assertIn("missing_trajectory", codes)
            self.assertIn("unsafe_artifact_path", codes)
            self.assertFalse(artifact["safe"])
            self.assertIsNone(artifact["path"])
            self.assertEqual(bundle.jobs[0].trials[0].status, "pending")

    def test_in_progress_job_without_job_result_can_be_loaded_directly(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "job"
            write_json(root / "trial-a" / "config.json", {"trial_name": "trial-a"})
            job = load_job(root)
            bundle = load(root)
            self.assertEqual(len(job.trials), 1)
            self.assertEqual(len(bundle.jobs[0].trials), 1)
            self.assertIn("incomplete_job", {item.code for item in job.diagnostics})


if __name__ == "__main__":
    unittest.main()
