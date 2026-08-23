from pathlib import Path
import unittest

from harbor_marimo.domains.financial import (
    assess_financial_trial,
    trajectory_metrics,
    workbook_grid,
)
from harbor_marimo import load


ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"


class FinancialDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load(JOB)
        cls.trials = cls.bundle.jobs[0].trials

    def test_workbook_view_retains_formula_semantics(self):
        artifacts = self.bundle.tables()["artifacts"]
        workbook_paths = [Path(row["path"]) for row in artifacts if row["path"]]

        hardcoded = workbook_grid(workbook_paths[0], formulas=True)
        formula_driven = workbook_grid(workbook_paths[1], formulas=True)

        self.assertEqual(hardcoded["rows"][-2][3], 47.2)
        self.assertEqual(formula_driven["rows"][-2][3], "=F8-SUM(F12:F14)")

    def test_expert_assessment_does_not_replace_reward(self):
        context = {
            "expert_status": "Needs review",
            "expert_summary": "Formula was replaced with a hard-coded value.",
        }

        assessment = assess_financial_trial(1.0, context)

        self.assertTrue(assessment.verifier_passed)
        self.assertTrue(assessment.verifier_blind_spot)
        self.assertEqual(assessment.expert_status, "Needs review")

    def test_trajectory_metrics_accept_generic_loaded_trajectory(self):
        trajectory = self.trials[0].steps[0].trajectory

        metrics = trajectory_metrics(trajectory or {})

        self.assertEqual(metrics["steps"], 5)
        self.assertEqual(metrics["validation_actions"], 2)


if __name__ == "__main__":
    unittest.main()
