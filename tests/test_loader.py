from pathlib import Path
import unittest

from domain_harbor_demo.harbor_loader import (
    load_harbor_job,
    load_harbor_source,
    trajectory_metrics,
    trajectory_rows,
    workbook_grid,
)


ROOT = Path(__file__).resolve().parents[1]


class HarborLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.job = load_harbor_job(ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job")

    def test_job_summary(self):
        self.assertEqual(len(self.job.trials), 3)
        self.assertEqual([trial.reward for trial in self.job.trials], [1.0, 1.0, 0.0])
        self.assertAlmostEqual(self.job.mean_reward, 2 / 3)

    def test_artifacts_and_trajectories_are_available(self):
        for trial in self.job.trials:
            self.assertIsNotNone(trial.artifact_path)
            self.assertTrue(trial.artifact_path.exists())
            self.assertEqual(len(trajectory_rows(trial.trajectory)), 5)

    def test_demo_exposes_formula_difference(self):
        hardcoded, preserved, _ = self.job.trials
        hardcoded_formulas = workbook_grid(hardcoded.artifact_path, formulas=True)
        preserved_formulas = workbook_grid(preserved.artifact_path, formulas=True)

        self.assertEqual(hardcoded_formulas["rows"][-2][3], 47.2)
        self.assertEqual(
            preserved_formulas["rows"][-2][3], "=F8-SUM(F12:F14)"
        )

    def test_job_directory_can_be_loaded_as_a_source(self):
        loaded = load_harbor_source(
            ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"
        )

        self.assertEqual(loaded.kind, "Harbor job")
        self.assertIsNone(loaded.selected_trial_name)
        self.assertEqual(loaded.job.id, self.job.id)

    def test_atif_path_selects_its_trial(self):
        expected = self.job.trials[1]
        loaded = load_harbor_source(expected.directory / "agent" / "trajectory.json")

        self.assertEqual(loaded.kind, "Harbor ATIF")
        self.assertEqual(loaded.selected_trial_name, expected.name)
        self.assertEqual(loaded.job.id, self.job.id)

    def test_atif_metrics_are_derived_for_comparison(self):
        metrics = trajectory_metrics(self.job.trials[0].trajectory)

        self.assertEqual(metrics["steps"], 5)
        self.assertEqual(metrics["tool_calls"], 3)
        self.assertEqual(metrics["observations"], 3)
        self.assertEqual(metrics["validation_actions"], 2)
        self.assertEqual(metrics["change_actions"], 1)
        self.assertEqual(metrics["elapsed_seconds"], 197)
        self.assertEqual(metrics["total_tokens"], 7530)
        self.assertAlmostEqual(metrics["cost_per_action"], 0.14 / 3)


if __name__ == "__main__":
    unittest.main()
