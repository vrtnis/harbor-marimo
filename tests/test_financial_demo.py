from pathlib import Path
import unittest

from harbor_marimo.domains.financial import load_financial_job, workbook_grid


ROOT = Path(__file__).resolve().parents[1]


class FinancialDemoCharacterizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.job = load_financial_job(
            ROOT / "examples" / "financial-review" / "demo_data" / "harbor_job"
        )

    def test_expert_context_identifies_verifier_blind_spot(self):
        hardcoded, formula_driven, incomplete = self.job.trials

        self.assertEqual(hardcoded.reward, 1.0)
        self.assertEqual(hardcoded.context["expert_status"], "Needs review")
        self.assertEqual(formula_driven.reward, 1.0)
        self.assertEqual(formula_driven.context["expert_status"], "Aligned")
        self.assertEqual(incomplete.reward, 0.0)
        self.assertEqual(incomplete.context["expert_status"], "Aligned")

    def test_formula_view_preserves_expert_evidence(self):
        hardcoded, formula_driven, _ = self.job.trials

        hardcoded_rows = workbook_grid(hardcoded.artifact_path, formulas=True)["rows"]
        formula_rows = workbook_grid(formula_driven.artifact_path, formulas=True)["rows"]

        self.assertEqual(hardcoded_rows[-2][3], 47.2)
        self.assertEqual(formula_rows[-2][3], "=F8-SUM(F12:F14)")

    def test_every_trial_points_to_the_same_review_cell(self):
        self.assertEqual(
            {trial.context["focus_cell"] for trial in self.job.trials},
            {"Forecast!F16"},
        )


if __name__ == "__main__":
    unittest.main()
